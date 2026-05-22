package com.insightflow.analytics.event;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.insightflow.analytics.repository.AnalyticsRepository;
import com.insightflow.analytics.service.RecommendationEngine;
import com.insightflow.common.model.Analytics;
import com.insightflow.common.model.Dataset;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

import java.util.Map;

@Slf4j
@Component
public class DatasetEventConsumer {

    @Autowired
    private AnalyticsRepository analyticsRepository;

    @Autowired
    private RecommendationEngine recommendationEngine;

    @Autowired
    private MongoTemplate mongoTemplate;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @KafkaListener(topics = "dataset-upload", groupId = "analytics-group")
    public void consumeDatasetUpload(String message) {
        log.info("Received dataset upload event from Kafka: {}", message);
        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> event = objectMapper.readValue(message, Map.class);
            String datasetId = (String) event.get("datasetId");

            log.info("Processing analytics calculations for dataset ID: {}", datasetId);

            // 1. Generate comprehensive analytics profile
            Analytics analytics = recommendationEngine.generateAnalyticsProfile(datasetId);

            // 2. Save analytics document to MongoDB
            analyticsRepository.save(analytics);

            // 3. Update parent Dataset status in MongoDB to complete
            Dataset dataset = mongoTemplate.findById(datasetId, Dataset.class);
            if (dataset != null) {
                dataset.setStatus("complete");
                dataset.setCurrentStep(5); // Complete state
                mongoTemplate.save(dataset);
                log.info("Successfully updated dataset status to complete for ID: {}", datasetId);
            }

        } catch (Exception e) {
            log.error("Error processing dataset upload event. Reason: {}", e.getMessage());
        }
    }
}
