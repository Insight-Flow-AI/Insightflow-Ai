package com.insightflow.dataset;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration;

@SpringBootApplication(exclude = {SecurityAutoConfiguration.class}, scanBasePackages = {"com.insightflow.dataset", "com.insightflow.common"})
public class DatasetServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(DatasetServiceApplication.class, args);
    }
}
