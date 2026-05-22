param(
    [string]$serviceName
)

if (-not $serviceName) {
    Write-Host "Usage: .\run-service.ps1 <service-name>"
    Write-Host "Available services: api-gateway, auth-service, dataset-service, analytics-service, notification-service"
    exit 1
}

# Resolve target directory
$servicePath = Join-Path $PSScriptRoot $serviceName
if (-not (Test-Path $servicePath)) {
    Write-Error "Service directory $servicePath does not exist!"
    exit 1
}

# Find all jars in local maven repository
$m2Repo = "C:\Users\admin\.m2\repository"
if (-not (Test-Path $m2Repo)) {
    $m2Repo = Join-Path $env:USERPROFILE ".m2\repository"
}

# Define preferred versions for Spring Boot 3.2.5 and Spring Framework 6.1.x compatibility
$preferredVersions = @{
    "spring-core"             = "6.1.6"
    "spring-beans"            = "6.1.6"
    "spring-context"          = "6.1.6"
    "spring-aop"              = "6.1.6"
    "spring-expression"       = "6.1.6"
    "spring-web"              = "6.1.6"
    "spring-webmvc"           = "6.1.6"
    "spring-webflux"          = "6.1.6"
    "spring-tx"               = "6.1.6"
    "spring-jdbc"             = "6.1.6"
    "spring-messaging"        = "6.1.6"
    "spring-jcl"              = "6.1.6"
    "jackson-databind"        = "2.15.4"
    "jackson-core"            = "2.15.4"
    "jackson-annotations"     = "2.15.4"
    "jackson-dataformat-yaml" = "2.15.4"
    "slf4j-api"               = "2.0.13"
    "micrometer-commons"      = "1.12.5"
    "micrometer-observation"  = "1.12.5"
    "micrometer-core"         = "1.12.5"
    "snakeyaml"               = "2.2"
    "commons-io"              = "2.11.0"
    "commons-lang3"           = "3.12.0"
    "zstd-jni"                = "1.5.5-1"
}

Write-Host "Scanning local Maven repository for jars: $m2Repo"
$allJars = Get-ChildItem -Path $m2Repo -Filter *.jar -Recurse | Where-Object { 
    $_.FullName -notmatch "sources" -and $_.FullName -notmatch "javadoc"
}

# Deduplicate JARs by choosing preferred version if defined, otherwise highest version
$groups = $allJars | Group-Object { $_.Directory.Parent.FullName }
$jars = @()
foreach ($group in $groups) {
    $artifactId = $group.Group[0].Directory.Parent.Name
    $preferred = $preferredVersions[$artifactId]
    $matchedFile = $null

    if ($preferred) {
        $matchedFile = $group.Group | Where-Object { $_.Directory.Name -eq $preferred } | Select-Object -First 1
    }

    if ($matchedFile) {
        $jars += $matchedFile.FullName
    } else {
        # Fallback to sorting and picking highest version
        $sorted = $group.Group | Sort-Object {
            $versionStr = $_.Directory.Name
            $numericVersion = $versionStr -replace '[^\d\.]', ''
            if ($numericVersion -and $numericVersion.Split('.').Length -le 4) {
                try {
                    [version]$numericVersion
                } catch {
                    $versionStr
                }
            } else {
                $versionStr
            }
        }
        $jars += $sorted[-1].FullName
    }
}
Write-Host "Selected $($jars.Count) clean libraries (aligned with Spring Boot 3.2.5 from $($allJars.Count) files)."

# We also need common-lib's compiled classes in the classpath!
$commonLibClasses = Join-Path $PSScriptRoot "common-lib\target\classes"
$serviceClasses = Join-Path $servicePath "target\classes"

# Filter classpath based on service type
$serviceJars = $jars
if ($serviceName -eq "api-gateway") {
    # Exclude Spring MVC and Tomcat embedded web server for the reactive Gateway
    $serviceJars = $jars | Where-Object {
        $_ -notmatch "spring-webmvc" -and
        $_ -notmatch "tomcat-embed" -and
        $_ -notmatch "spring-boot-starter-tomcat"
    }
    Write-Host "Filtered out Spring MVC & Tomcat from Gateway classpath to enable Reactive Netty."
} else {
    # Exclude Spring Cloud Gateway jars for standard Spring MVC servlet apps
    $serviceJars = $jars | Where-Object {
        $_ -notmatch "spring-cloud-gateway"
    }
    Write-Host "Filtered out Spring Cloud Gateway jars from $serviceName classpath to enable Servlet/Tomcat."
}

# Combine into a single classpath string
$cp = ($serviceJars -join ";") + ";" + $commonLibClasses + ";" + $serviceClasses

# Find main class based on serviceName
$mainClassMap = @{
    "api-gateway"          = "com.insightflow.gateway.ApiGatewayApplication"
    "auth-service"         = "com.insightflow.auth.AuthServiceApplication"
    "dataset-service"      = "com.insightflow.dataset.DatasetServiceApplication"
    "analytics-service"    = "com.insightflow.analytics.AnalyticsServiceApplication"
    "notification-service" = "com.insightflow.notification.NotificationServiceApplication"
}

$mainClass = $mainClassMap[$serviceName]
if (-not $mainClass) {
    Write-Error "Unknown service: $serviceName"
    Write-Host "Available services: api-gateway, auth-service, dataset-service, analytics-service, notification-service"
    exit 1
}

$excludes = @(
    "org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration",
    "org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration",
    "org.springframework.boot.autoconfigure.jdbc.DataSourceTransactionManagerAutoConfiguration"
)

if ($serviceName -ne "auth-service") {
    $excludes += "org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration"
    $excludes += "org.springframework.boot.autoconfigure.security.servlet.UserDetailsServiceAutoConfiguration"
    $excludes += "org.springframework.boot.autoconfigure.security.reactive.ReactiveSecurityAutoConfiguration"
    $excludes += "org.springframework.boot.actuate.autoconfigure.security.servlet.ManagementWebSecurityAutoConfiguration"
    $excludes += "org.springframework.boot.actuate.autoconfigure.security.reactive.ReactiveManagementWebSecurityAutoConfiguration"
}

$excludeStr = $excludes -join ","

Write-Host "Launching $serviceName ($mainClass) offline via direct JVM injection..."
java -cp $cp $mainClass --spring.autoconfigure.exclude=$excludeStr
