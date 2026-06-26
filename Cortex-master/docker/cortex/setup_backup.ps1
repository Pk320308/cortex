$ErrorActionPreference = 'Stop'

Write-Host "Waiting for Elasticsearch to be available..."
$maxRetries = 30
$retryCount = 0
$esUrl = "http://localhost:9201"

while ($retryCount -lt $maxRetries) {
    try {
        $response = Invoke-RestMethod -Uri "$esUrl/_cluster/health" -Method Get
        if ($response.status -in @("green", "yellow")) {
            Write-Host "Elasticsearch is up and running!"
            break
        }
    } catch {
        # Ignore errors and retry
    }
    Start-Sleep -Seconds 2
    $retryCount++
}

if ($retryCount -eq $maxRetries) {
    Write-Error "Elasticsearch did not become available in time."
    exit 1
}

Write-Host "Configuring Backup Repository..."
$repoBody = @{
    type = "fs"
    settings = @{
        location = "/usr/share/elasticsearch/backup"
        compress = $true
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "$esUrl/_snapshot/cortex_backup" -Method Put -Body $repoBody -ContentType "application/json"

Write-Host "Configuring Snapshot Lifecycle Management (SLM) Policy..."
$slmBody = @{
    schedule = "0 0 0 * * ?" # Every day at midnight
    name = "<cortex-snap-{now/d}>"
    repository = "cortex_backup"
    config = @{
        indices = @("*")
        ignore_unavailable = $false
        include_global_state = $true
    }
    retention = @{
        expire_after = "30d"
        min_count = 5
        max_count = 50
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "$esUrl/_slm/policy/daily-snapshots" -Method Put -Body $slmBody -ContentType "application/json"

Write-Host "Backup and Sync successfully configured! Backups will run daily at midnight and be stored in docker/cortex/backup."
