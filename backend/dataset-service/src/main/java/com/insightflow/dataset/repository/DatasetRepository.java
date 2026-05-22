package com.insightflow.dataset.repository;

import com.insightflow.common.model.Dataset;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DatasetRepository extends MongoRepository<Dataset, String> {
    List<Dataset> findByUserId(String userId);
}
