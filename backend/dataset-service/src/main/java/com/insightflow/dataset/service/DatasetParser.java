package com.insightflow.dataset.service;

import lombok.Data;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

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
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(file.getInputStream(), StandardCharsets.UTF_8))) {
            
            String headerLine = reader.readLine();
            if (headerLine != null) {
                // Remove UTF-8 BOM if present
                if (headerLine.startsWith("\uFEFF")) {
                    headerLine = headerLine.substring(1);
                }
                
                String[] headers = headerLine.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)"); // Splitting on commas outside quotes
                for (String header : headers) {
                    result.getColumns().add(header.replace("\"", "").trim());
                }
                result.setColumnCount(result.getColumns().size());
                
                int rows = 0;
                while (reader.readLine() != null) {
                    rows++;
                }
                result.setRowCount(rows);
                result.setSummary(String.format("CSV dataset successfully parsed with %d columns and %d data rows.", 
                        result.getColumnCount(), result.getRowCount()));
            } else {
                throw new IllegalArgumentException("Uploaded file is empty");
            }
        } catch (IllegalArgumentException e) {
            throw e;
        } catch (Exception e) {
            throw new RuntimeException("Corrupted dataset file: Unable to parse contents.", e);
        }
        return result;
    }
}
