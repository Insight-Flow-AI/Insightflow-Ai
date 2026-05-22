FROM eclipse-temurin:23-jre-alpine
WORKDIR /app

# Copy aligned library jars
COPY lib/gateway/ /app/lib/

# Copy common-lib compiled classes
COPY common-lib/target/classes/ /app/common-lib-classes/

# Copy gateway compiled classes
COPY api-gateway/target/classes/ /app/classes/

EXPOSE 4000

ENTRYPOINT ["java", "-cp", "/app/classes:/app/common-lib-classes:/app/lib/*", "com.insightflow.gateway.ApiGatewayApplication", "--spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration,org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration,org.springframework.boot.autoconfigure.jdbc.DataSourceTransactionManagerAutoConfiguration,org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration,org.springframework.boot.autoconfigure.security.servlet.UserDetailsServiceAutoConfiguration,org.springframework.boot.autoconfigure.security.reactive.ReactiveSecurityAutoConfiguration,org.springframework.boot.actuate.autoconfigure.security.servlet.ManagementWebSecurityAutoConfiguration,org.springframework.boot.actuate.autoconfigure.security.reactive.ReactiveManagementWebSecurityAutoConfiguration"]
