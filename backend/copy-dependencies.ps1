# Resolve local maven repository
$m2Repo = "C:\Users\admin\.m2\repository"
if (-not (Test-Path $m2Repo)) {
    $m2Repo = Join-Path $env:USERPROFILE ".m2\repository"
}

if (-not (Test-Path $m2Repo)) {
    Write-Error "Could not find local Maven repository at $m2Repo"
    exit 1
}

# Preferred versions for Spring Boot 3.2.5 and Spring Framework 6.1.x compatibility
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
Write-Host "Selected $($jars.Count) clean libraries aligned with Spring Boot."

# Re-create targets
$libDir = Join-Path $PSScriptRoot "lib"
$gatewayDir = Join-Path $libDir "gateway"
$servicesDir = Join-Path $libDir "services"

if (Test-Path $libDir) {
    Write-Host "Cleaning existing lib directory: $libDir"
    Remove-Item -Path $libDir -Recurse -Force -ErrorAction SilentlyContinue
}

New-Item -ItemType Directory -Path $gatewayDir -Force | Out-Null
New-Item -ItemType Directory -Path $servicesDir -Force | Out-Null

$copiedToGateway = 0
$copiedToServices = 0

foreach ($jarPath in $jars) {
    $filename = Split-Path $jarPath -Leaf
    
    # Check exclusions for gateway (reactive exclusions: no spring-webmvc or tomcat)
    $isExcludedFromGateway = ($jarPath -match "spring-webmvc" -or $jarPath -match "tomcat-embed" -or $jarPath -match "spring-boot-starter-tomcat")
    
    # Check exclusions for servlet services (no spring-cloud-gateway)
    $isExcludedFromServices = ($jarPath -match "spring-cloud-gateway")

    if (-not $isExcludedFromGateway) {
        Copy-Item -Path $jarPath -Destination (Join-Path $gatewayDir $filename)
        $copiedToGateway++
    }
    
    if (-not $isExcludedFromServices) {
        Copy-Item -Path $jarPath -Destination (Join-Path $servicesDir $filename)
        $copiedToServices++
    }
}

Write-Host "Successfully exported dependencies:"
Write-Host " - Gateway lib folder: $copiedToGateway jars copied to $gatewayDir"
Write-Host " - Services lib folder: $copiedToServices jars copied to $servicesDir"
