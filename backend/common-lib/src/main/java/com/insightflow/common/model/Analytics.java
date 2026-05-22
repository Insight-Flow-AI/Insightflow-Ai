package com.insightflow.common.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.io.Serializable;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "analytics")
public class Analytics implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    private String id;

    private String datasetId;

    private Map<String, String> kpis; // e.g. "Total revenue" -> "₹24.6L"

    private List<String> predictions; // trend forecasting statements

    private List<Recommendation> recommendations;

    private List<Anomaly> anomalies;

    private String aiReportSummary;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Recommendation implements Serializable {
        private static final long serialVersionUID = 1L;

        private String icon; // "TrendingUp", "Users", "Lightbulb"
        private String title;
        private String description;
        private String variant; // "warning", "success", "info"
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Anomaly implements Serializable {
        private static final long serialVersionUID = 1L;

        private String field;
        private String description;
        private String severity; // "HIGH", "MEDIUM", "LOW"
        private String detectedAt;
    }
}
