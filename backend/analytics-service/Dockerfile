# ── Stage 1: Build ──────────────────────────────────────────────────────────
FROM maven:3.9-eclipse-temurin-21 AS builder

WORKDIR /workspace

COPY pom.xml .
COPY common-lib/pom.xml          common-lib/pom.xml
COPY auth-service/pom.xml        auth-service/pom.xml
COPY api-gateway/pom.xml         api-gateway/pom.xml
COPY dataset-service/pom.xml     dataset-service/pom.xml
COPY analytics-service/pom.xml   analytics-service/pom.xml
COPY notification-service/pom.xml notification-service/pom.xml

RUN mvn dependency:go-offline -B --no-transfer-progress

COPY common-lib/src       common-lib/src
COPY analytics-service/src analytics-service/src

RUN mvn -pl common-lib,analytics-service -am clean package -DskipTests -B --no-transfer-progress

# ── Stage 2: Run ────────────────────────────────────────────────────────────
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

COPY --from=builder /workspace/analytics-service/target/analytics-service-*.jar app.jar

EXPOSE 8083

ENTRYPOINT ["java", "-jar", "app.jar"]
