$ErrorActionPreference = "Stop"
$serviceRoot = Split-Path -Parent $PSScriptRoot
$outputPath = Join-Path $serviceRoot "generated\plan_api_client"

openapi-python-client generate `
    --url "http://localhost:8080/v3/api-docs" `
    --output-path $outputPath `
    --meta none `
    --overwrite

Write-Host "OpenAPI Python client regenerated at $outputPath"
