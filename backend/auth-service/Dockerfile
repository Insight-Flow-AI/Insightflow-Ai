# ── Stage 1: Build ──────────────────────────────────────────────────────────
FROM maven:3.9-eclipse-temurin-21 AS builder

WORKDIR /workspace

# Copy parent POM + module POMs first (layer-cache friendly)
COPY pom.xml .
COPY common-lib/pom.xml          common-lib/pom.xml
COPY auth-service/pom.xml        auth-service/pom.xml
COPY api-gateway/pom.xml         api-gateway/pom.xml
COPY dataset-service/pom.xml     dataset-service/pom.xml
COPY analytics-service/pom.xml   analytics-service/pom.xml
COPY notification-service/pom.xml notification-service/pom.xml

# Resolve all dependencies (cached unless pom.xml changes)
RUN mvn dependency:go-offline -B --no-transfer-progress

# Copy full source
COPY common-lib/src      common-lib/src
COPY auth-service/src    auth-service/src

# Build common-lib, then auth-service (skip tests in Docker)
RUN mvn -pl common-lib,auth-service -am clean package -DskipTests -B --no-transfer-progress

# ── Stage 2: Run ────────────────────────────────────────────────────────────
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

COPY --from=builder /workspace/auth-service/target/auth-service-*.jar app.jar

EXPOSE 8081

ENTRYPOINT ["java", "-jar", "app.jar"]
