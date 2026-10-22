param(
    [string]$OpenApiUrl = "http://localhost:8080/v3/api-docs"
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$outputPath = Join-Path $projectRoot "generated/plan_api_client"

openapi-python-client generate `
    --url $OpenApiUrl `
    --output-path $outputPath `
    --meta none `
    --overwrite

if ($LASTEXITCODE -ne 0) {
    throw "OpenAPI Python Client 生成失败"
}

Write-Host "OpenAPI Python Client 已生成：$outputPath"
