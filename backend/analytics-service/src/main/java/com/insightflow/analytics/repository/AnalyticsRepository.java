package com.insightflow.analytics.repository;

import com.insightflow.common.model.Analytics;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AnalyticsRepository extends MongoRepository<Analytics, String> {
    Optional<Analytics> findByDatasetId(String datasetId);
}
