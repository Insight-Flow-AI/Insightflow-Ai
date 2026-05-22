package com.insightflow.dataset;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = {"com.insightflow.dataset", "com.insightflow.common"})
public class DatasetServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(DatasetServiceApplication.class, args);
    }
}
