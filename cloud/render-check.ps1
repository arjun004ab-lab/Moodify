param(
  [Parameter(Mandatory=$true)]
  [string]$BackendUrl,
  [Parameter(Mandatory=$true)]
  [string]$FrontendUrl
)

$ErrorActionPreference = 'Stop'

$BackendUrl = $BackendUrl.TrimEnd('/')
$FrontendUrl = $FrontendUrl.TrimEnd('/')

Write-Host "Checking backend live health..." -ForegroundColor Cyan
$live = Invoke-RestMethod -Uri "$BackendUrl/health/live" -Method Get
$live | ConvertTo-Json -Depth 5

Write-Host "Checking backend readiness..." -ForegroundColor Cyan
try {
  $ready = Invoke-RestMethod -Uri "$BackendUrl/health/ready" -Method Get
  $ready | ConvertTo-Json -Depth 5
} catch {
  Write-Host "Readiness endpoint returned an error:" -ForegroundColor Yellow
  Write-Host $_.Exception.Message
}

Write-Host "Checking Swagger..." -ForegroundColor Cyan
$docs = Invoke-WebRequest -Uri "$BackendUrl/docs" -Method Get
Write-Host "Swagger status: $($docs.StatusCode)"

Write-Host "Checking frontend..." -ForegroundColor Cyan
$front = Invoke-WebRequest -Uri $FrontendUrl -Method Get
Write-Host "Frontend status: $($front.StatusCode)"

Write-Host "Cloud boundary check complete." -ForegroundColor Green
Write-Host "Backend:  $BackendUrl"
Write-Host "Frontend: $FrontendUrl"
