package com.insightflow.dataset.service;

import lombok.Data;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

@Service
public class DatasetParser {

    @Data
    public static class ParseResult {
        private int rowCount;
        private int columnCount;
        private List<String> columns = new ArrayList<>();
        private String summary;
    }

    public ParseResult parse(MultipartFile file) {
        ParseResult result = new ParseResult();
        List<String[]> allRows = new ArrayList<>();

        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(file.getInputStream(), StandardCharsets.UTF_8))) {

            String line;
            boolean isFirstLine = true;
            int expectedCols = -1;

            while ((line = reader.readLine()) != null) {
                // Remove BOM if present on the first line
                if (isFirstLine && line.startsWith("\uFEFF")) {
                    line = line.substring(1);
                }

                // Skip empty lines
                if (line.trim().isEmpty()) {
                    continue;
                }

                // Split on commas outside double quotes, retaining trailing empty elements
                String[] columns = line.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", -1);

                if (isFirstLine) {
                    expectedCols = columns.length;
                    for (String col : columns) {
                        result.getColumns().add(col.replace("\"", "").trim());
                    }
                    isFirstLine = false;
                } else {
                    if (columns.length != expectedCols) {
                        throw new IllegalArgumentException("Corrupted or invalid CSV structure");
                    }
                    allRows.add(columns);
                }
            }

            // If we didn't read any lines (empty file content)
            if (isFirstLine) {
                throw new IllegalArgumentException("Uploaded file is empty");
            }

            // Rule 5: Minimum Column Check
            if (result.getColumns().size() < 2) {
                throw new IllegalArgumentException("Dataset must contain at least 2 columns");
            }

            // Rule 6: Minimum Row Check
            if (allRows.size() < 5) {
                throw new IllegalArgumentException("Dataset must contain at least 5 rows");
            }

            // Rule 7: Header Validation
            boolean allNumeric = true;
            for (String header : result.getColumns()) {
                if (header.isEmpty()) {
                    throw new IllegalArgumentException("Invalid column headers");
                }
                try {
                    Double.parseDouble(header);
                } catch (NumberFormatException e) {
                    allNumeric = false;
                }
            }
            if (allNumeric) {
                throw new IllegalArgumentException("Invalid column headers");
            }

            // // Rule 8: Duplicate Header Check
            // Set<String> seenHeaders = new HashSet<>();
            // for (String header : result.getColumns()) {
            //     if (!seenHeaders.add(header.toLowerCase())) {
            //         throw new IllegalArgumentException("Duplicate column names detected");
            //     }
            // }

            // Rule 9: Fully Empty Dataset Check (no usable values in cells)
            boolean hasUsableData = false;
            for (String[] row : allRows) {
                for (String cell : row) {
                    if (cell != null && !cell.trim().isEmpty()) {
                        hasUsableData = true;
                        break;
                    }
                }
                if (hasUsableData) {
                    break;
                }
            }
            if (!hasUsableData) {
                throw new IllegalArgumentException("Dataset contains no usable data");
            }

            result.setColumnCount(result.getColumns().size());
            result.setRowCount(allRows.size());
            result.setSummary(String.format("CSV dataset successfully parsed with %d columns and %d data rows.",
                    result.getColumnCount(), result.getRowCount()));

        } catch (IllegalArgumentException e) {
            throw e;
        } catch (Exception e) {
            throw new RuntimeException("Corrupted or invalid CSV structure", e);
        }

        return result;
    }
}
