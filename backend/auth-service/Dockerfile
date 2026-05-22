FROM eclipse-temurin:23-jre-alpine
WORKDIR /app

# Copy aligned library jars
COPY lib/services/ /app/lib/

# Copy common-lib compiled classes
COPY common-lib/target/classes/ /app/common-lib-classes/

# Copy service compiled classes
COPY auth-service/target/classes/ /app/classes/

EXPOSE 8081

ENTRYPOINT ["java", "-cp", "/app/classes:/app/common-lib-classes:/app/lib/*", "com.insightflow.auth.AuthServiceApplication", "--spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration,org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration,org.springframework.boot.autoconfigure.jdbc.DataSourceTransactionManagerAutoConfiguration"]
