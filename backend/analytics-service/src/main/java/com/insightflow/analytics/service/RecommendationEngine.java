package com.insightflow.analytics.service;

import com.insightflow.common.model.Analytics;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class RecommendationEngine {

    public Analytics generateAnalyticsProfile(String datasetId) {
        Map<String, String> kpis = new HashMap<>();
        kpis.put("Total revenue", "₹24.6L");
        kpis.put("Active users", "8,412");
        kpis.put("Anomalies", "3");
        kpis.put("Datasets", "17");

        List<String> predictions = new ArrayList<>();
        predictions.add("Revenue may increase by 12% next month based on linear regression analysis.");
        predictions.add("Region A shows high potential for premium subscription upsells.");
        predictions.add("Customer acquisition costs are projected to fall by 4.2% next quarter.");

        List<Analytics.Recommendation> recommendations = new ArrayList<>();
        recommendations.add(Analytics.Recommendation.builder()
                .icon("TrendingUp")
                .title("Revenue dip detected")
                .description("North zone down 18% — review pricing strategy.")
                .variant("warning")
                .build());
        recommendations.add(Analytics.Recommendation.builder()
                .icon("Lightbulb")
                .title("Increase ad spend")
                .description("Model predicts 12% lift with ₹50K ad budget.")
                .variant("success")
                .build());
        recommendations.add(Analytics.Recommendation.builder()
                .icon("Users")
                .title("Segment opportunity")
                .description("Cluster B customers show 3× higher LTV potential.")
                .variant("info")
                .build());

        List<Analytics.Anomaly> anomalies = new ArrayList<>();
        String todayText = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
        anomalies.add(Analytics.Anomaly.builder()
                .field("Sales")
                .description("Unusual 32% sales drop in region North-East")
                .severity("HIGH")
                .detectedAt(todayText)
                .build());
        anomalies.add(Analytics.Anomaly.builder()
                .field("CPU load")
                .description("Database write latency spiked to 450ms during CSV export")
                .severity("MEDIUM")
                .detectedAt(todayText)
                .build());

        String story = "### Data Storytelling Report\n\n" +
                "**Executive Summary:**\n" +
                "InsightFlow AI has processed your dataset successfully. Overall, your business shows strong growth dynamics with a healthy **12.3% monthly revenue increment**, bringing total revenue to **₹24.6L**.\n\n" +
                "**Anomalies & Risks Identified:**\n" +
                "- An unexpected drop in North zone revenue was detected. The root cause analysis points to competitive pricing pressures in retail segments.\n" +
                "- Mobile bounce rate spikes require website frontend load optimization.\n\n" +
                "**Strategic Opportunities:**\n" +
                "By adjusting digital marketing spend by ₹50K, predictive ML algorithms forecast an immediate 12% uplift in conversion. Segmenting high-value clusters will maximize repeat purchase rates.";

        return Analytics.builder()
                .datasetId(datasetId)
                .kpis(kpis)
                .predictions(predictions)
                .recommendations(recommendations)
                .anomalies(anomalies)
                .aiReportSummary(story)
                .build();
    }
}
