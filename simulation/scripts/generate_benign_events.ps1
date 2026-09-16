$uri = "http://localhost:8000/api/v1/wazuh/webhook"

Write-Host "Generating benign events..."

1..30 | ForEach-Object {
    $minute = $_ % 5
    $timestamp = "2026-05-10T09:0${minute}:00Z"

    $payload = @{
        timestamp = $timestamp
        rule = @{
            id = "100"
            level = 2
            description = "Normal authentication success"
            groups = @(
                "authentication_success"
            )
        }
        agent = @{
            name = "sme-pc-01"
            ip = "192.168.1.20"
        }
        srcip = "192.168.1.20"
        dstip = "192.168.1.10"
        srcuser = "user01"
        full_log = "Accepted password for user01"
    } | ConvertTo-Json -Depth 10

    Invoke-RestMethod -Method Post -Uri $uri -ContentType "application/json" -Body $payload | Out-Null

    Write-Host "Sent benign event $_"
}

Write-Host "Benign event generation completed."