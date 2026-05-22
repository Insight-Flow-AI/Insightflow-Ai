package com.insightflow.dataset.event;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Component
public class DatasetEventPublisher {

    @Autowired(required = false)
    private KafkaTemplate<String, String> kafkaTemplate;

    private final ObjectMapper objectMapper = new ObjectMapper();

    public void publishUploadEvent(String datasetId, String filename, String userId) {
        Map<String, Object> event = new HashMap<>();
        event.put("datasetId", datasetId);
        event.put("filename", filename);
        event.put("userId", userId);
        event.put("timestamp", System.currentTimeMillis());

        try {
            String jsonMessage = objectMapper.writeValueAsString(event);
            
            if (kafkaTemplate != null) {
                log.info("Publishing upload event to Kafka for dataset: {}", datasetId);
                kafkaTemplate.send("dataset-upload", datasetId, jsonMessage);
            } else {
                log.warn("Kafka Template not active. Simulating in-memory dataset event for: {}", datasetId);
            }
        } catch (Exception e) {
            log.error("Failed to publish event to Kafka. Continuing gracefully. Reason: {}", e.getMessage());
        }
    }
}
