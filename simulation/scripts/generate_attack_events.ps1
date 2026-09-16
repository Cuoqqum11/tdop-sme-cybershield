$uri = "http://localhost:8000/api/v1/wazuh/webhook"

Write-Host "Generating attack events..."

1..20 | ForEach-Object {
    $minute = $_ % 3
    $timestamp = "2026-05-10T23:0${minute}:00Z"

    $payload = @{
        timestamp = $timestamp
        rule = @{
            id = "5712"
            level = 10
            description = "SSH brute force attempt"
            groups = @(
                "sshd",
                "authentication_failures"
            )
        }
        agent = @{
            name = "sme-pc-01"
            ip = "192.168.1.20"
        }
        srcip = "203.0.113.99"
        dstip = "192.168.1.10"
        srcuser = "admin"
        full_log = "Failed password for admin"
    } | ConvertTo-Json -Depth 10

    Invoke-RestMethod -Method Post -Uri $uri -ContentType "application/json" -Body $payload | Out-Null

    Write-Host "Sent failed login event $_"
}

$successPayload = @{
    timestamp = "2026-05-10T23:03:00Z"
    rule = @{
        id = "101"
        level = 7
        description = "Login success after repeated failures"
        groups = @(
            "authentication_success"
        )
    }
    agent = @{
        name = "sme-pc-01"
        ip = "192.168.1.20"
    }
    srcip = "203.0.113.99"
    dstip = "192.168.1.10"
    srcuser = "admin"
    full_log = "Accepted password for admin"
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post -Uri $uri -ContentType "application/json" -Body $successPayload | Out-Null

Write-Host "Sent suspicious successful login event."
Write-Host "Attack event generation completed."