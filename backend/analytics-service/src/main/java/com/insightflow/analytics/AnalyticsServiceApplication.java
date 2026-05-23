package com.insightflow.analytics;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

import org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration;

@EnableCaching
@SpringBootApplication(exclude = {SecurityAutoConfiguration.class}, scanBasePackages = {"com.insightflow.analytics", "com.insightflow.common"})
public class AnalyticsServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(AnalyticsServiceApplication.class, args);
    }
}
