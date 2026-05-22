package com.insightflow.analytics.controller;

import com.insightflow.analytics.repository.AnalyticsRepository;
import com.insightflow.analytics.service.RecommendationEngine;
import com.insightflow.common.model.Analytics;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@RestController
public class AnalyticsController {

    @Autowired
    private AnalyticsRepository analyticsRepository;

    @Autowired
    private RecommendationEngine recommendationEngine;

    @GetMapping("/api/analytics/report")
    @Cacheable(value = "reports", key = "#datasetId != null ? #datasetId : 'default_mock'", unless = "#result == null")
    public Map<String, Object> getReport(@RequestParam(value = "datasetId", required = false) String datasetId) {
        log.info("Fetching analytics report for dataset: {}", datasetId);

        Analytics analytics = getAnalyticsProfile(datasetId);
        Map<String, Object> response = new HashMap<>();
        response.put("datasetId", datasetId);
        response.put("report", analytics.getAiReportSummary());
        response.put("recommendations", analytics.getRecommendations());

        return response;
    }

    @GetMapping("/api/charts")
    @Cacheable(value = "charts", key = "#datasetId != null ? #datasetId : 'default_mock'", unless = "#result == null")
    public Map<String, Object> getCharts(@RequestParam(value = "datasetId", required = false) String datasetId) {
        log.info("Fetching visualisations for dataset: {}", datasetId);

        Analytics analytics = getAnalyticsProfile(datasetId);

        // Standard Revenue Trend Chart payloads
        List<Map<String, Object>> trendData = new ArrayList<>();
        String[] months = {"Jan", "Feb", "Mar", "Apr", "May", "Jun"};
        int[] revenues = {120000, 145000, 130000, 165000, 190000, 246000};
        int[] profits = {45000, 52000, 48000, 61000, 72000, 94000};

        for (int i = 0; i < months.length; i++) {
            Map<String, Object> dataPoint = new HashMap<>();
            dataPoint.put("name", months[i]);
            dataPoint.put("Revenue", revenues[i]);
            dataPoint.put("Profit", profits[i]);
            trendData.add(dataPoint);
        }

        Map<String, Object> response = new HashMap<>();
        response.put("kpis", analytics.getKpis());
        response.put("anomalies", analytics.getAnomalies());
        response.put("revenueTrend", trendData);

        return response;
    }

    @GetMapping("/api/predictions")
    public ResponseEntity<?> getPredictions(@RequestParam(value = "datasetId", required = false) String datasetId) {
        log.info("Fetching ML predictions for dataset: {}", datasetId);

        Analytics analytics = getAnalyticsProfile(datasetId);
        return ResponseEntity.ok(analytics.getPredictions());
    }

    @PostMapping("/api/chat")
    public ResponseEntity<?> askChatbot(
            @RequestBody Map<String, String> request,
            @RequestParam(value = "datasetId", required = false) String datasetId) {
        
        String query = request.getOrDefault("query", "");
        log.info("Conversational NLP query: {}", query);

        String answer = "I've analyzed your current metrics. ";
        if (query.toLowerCase().contains("revenue") || query.toLowerCase().contains("sales")) {
            answer += "Revenue is currently up 12.3% vs last month, showing strong performance in the retail sectors. However, North zone sales are down 18% due to competitive pricing pressures.";
        } else if (query.toLowerCase().contains("anomaly") || query.toLowerCase().contains("issue")) {
            answer += "I detected 3 active anomalies. Most critical is a 32% drop in sales in the North-East region. The recommendation is to review region marketing distribution and pricing policies.";
        } else {
            answer += "Based on standard machine learning trend models, we project revenue growth will settle at +12.3% this quarter. Let me know if you would like me to outline cluster analysis segments.";
        }

        Map<String, Object> response = new HashMap<>();
        response.put("query", query);
        response.put("answer", answer);
        response.put("timestamp", System.currentTimeMillis());

        return ResponseEntity.ok(response);
    }

    private Analytics getAnalyticsProfile(String datasetId) {
        if (datasetId != null) {
            return analyticsRepository.findByDatasetId(datasetId)
                    .orElseGet(() -> recommendationEngine.generateAnalyticsProfile(datasetId));
        }
        return recommendationEngine.generateAnalyticsProfile("default_mock");
    }
}
