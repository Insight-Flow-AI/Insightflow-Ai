package com.insightflow.dataset.controller;

import com.insightflow.common.model.Dataset;
import com.insightflow.common.security.JwtUtils;
import com.insightflow.dataset.event.DatasetEventPublisher;
import com.insightflow.dataset.repository.DatasetRepository;
import com.insightflow.dataset.service.DatasetParser;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/dataset")
public class DatasetController {

    @Autowired
    private DatasetRepository datasetRepository;

    @Autowired
    private DatasetParser datasetParser;

    @Autowired
    private DatasetEventPublisher eventPublisher;

    @Autowired
    private JwtUtils jwtUtils;

    @PostMapping("/upload")
    public ResponseEntity<?> upload(
            @RequestParam("file") MultipartFile file,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        log.info("Received dataset upload request for file: {}", file.getOriginalFilename());

        String userId = "user001"; // Fallback default
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            if (jwtUtils.validateToken(token)) {
                userId = jwtUtils.getUsernameFromToken(token);
            }
        }

        // Parse dataset details
        DatasetParser.ParseResult parseResult = datasetParser.parse(file);

        // Calculate size in readable format
        double sizeInMb = (double) file.getSize() / (1024 * 1024);
        String sizeText = String.format("%.2f MB", sizeInMb);

        // Construct Dataset metadata document
        Dataset dataset = Dataset.builder()
                .name(file.getOriginalFilename())
                .size(sizeText)
                .uploadedAt(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")))
                .currentStep(3) // Initial progress state: Schema & Preprocessing
                .status("processing")
                .rowCount(parseResult.getRowCount())
                .columnCount(parseResult.getColumnCount())
                .columns(parseResult.getColumns())
                .summary(parseResult.getSummary())
                .userId(userId)
                .build();

        Dataset savedDataset = datasetRepository.save(dataset);

        // Trigger asynchronous event streaming on Kafka
        eventPublisher.publishUploadEvent(savedDataset.getId(), savedDataset.getName(), savedDataset.getUserId());

        return ResponseEntity.ok(savedDataset);
    }

    @GetMapping("/history")
    public ResponseEntity<List<Dataset>> getHistory(
            @RequestHeader(value = "Authorization", required = false) String authHeader) {
        
        String userId = "user001"; // Fallback default
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            if (jwtUtils.validateToken(token)) {
                userId = jwtUtils.getUsernameFromToken(token);
            }
        }

        List<Dataset> history = datasetRepository.findByUserId(userId);
        return ResponseEntity.ok(history);
    }
}
