package com.insightflow.common.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "datasets")
public class Dataset {

    @Id
    private String id;

    private String name;

    private String size;

    private String uploadedAt;

    private int currentStep; // 1 to 5 based on PIPELINE_STEPS in React frontend

    private String status; // "processing", "complete", "failed"

    private int rowCount;

    private int columnCount;

    private List<String> columns;

    private String summary;

    private String userId;

    private String fileId;
}
