package com.insightflow.notification.event;

import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class AlertEventConsumer {

    @KafkaListener(topics = "notification-alert", groupId = "notification-group")
    public void consumeAlert(String message) {
        log.info("Received real-time alert event from Kafka stream: {}", message);
        
        // Simulating email/SMS trigger logic
        log.info("[Email Integration] Triggering automatic alert dispatch to Gurumurthy (guru@gmail.com). Dispatch Content: {}", message);
    }
}
