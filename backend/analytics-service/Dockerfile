FROM eclipse-temurin:23-jre-alpine
WORKDIR /app

# Copy aligned library jars
COPY lib/services/ /app/lib/

# Copy common-lib compiled classes
COPY common-lib/target/classes/ /app/common-lib-classes/

# Copy service compiled classes
COPY analytics-service/target/classes/ /app/classes/

EXPOSE 8083

ENTRYPOINT ["java", "-cp", "/app/classes:/app/common-lib-classes:/app/lib/*", "com.insightflow.analytics.AnalyticsServiceApplication", "--spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration,org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration,org.springframework.boot.autoconfigure.jdbc.DataSourceTransactionManagerAutoConfiguration,org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration,org.springframework.boot.autoconfigure.security.servlet.UserDetailsServiceAutoConfiguration,org.springframework.boot.autoconfigure.security.reactive.ReactiveSecurityAutoConfiguration,org.springframework.boot.actuate.autoconfigure.security.servlet.ManagementWebSecurityAutoConfiguration,org.springframework.boot.actuate.autoconfigure.security.reactive.ReactiveManagementWebSecurityAutoConfiguration"]
