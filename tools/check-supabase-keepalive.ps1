param(
  [string]$SupabaseUrl = "https://ztpftxwfcppsqosilssq.supabase.co",
  [string]$SupabaseKey = "sb_publishable_VpBNIGGpvSXkuMYiLv_rDA_fUiptxNC",
  [string]$Table = "defender_leaderboard",
  [string]$GitHubRepo = "zhenggdove-artist/-2",
  [string]$WorkflowFile = "supabase-keepalive.yml"
)

$ErrorActionPreference = "Stop"

try {
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
} catch {
  # Older PowerShell hosts may not expose every TLS enum. Continue with default.
}

function Write-Section {
  param([string]$Title)
  Write-Host ""
  Write-Host "== $Title =="
}

function Write-Fail {
  param([string]$Message)
  Write-Host "FAIL: $Message" -ForegroundColor Red
}

function Write-Ok {
  param([string]$Message)
  Write-Host "OK: $Message" -ForegroundColor Green
}

function Write-Warn {
  param([string]$Message)
  Write-Host "WARN: $Message" -ForegroundColor Yellow
}

function Invoke-GitHubJson {
  param(
    [string]$Uri,
    [hashtable]$Headers
  )

  try {
    return Invoke-RestMethod -Uri $Uri -Headers $Headers -TimeoutSec 30
  } catch {
    $raw = & curl.exe -fsS -L $Uri `
      -H "Accept: application/vnd.github+json" `
      -H "X-GitHub-Api-Version: 2026-03-10"

    if ($LASTEXITCODE -ne 0) {
      throw "GitHub request failed through Invoke-RestMethod and curl.exe"
    }

    return ($raw -join "`n") | ConvertFrom-Json
  }
}

Write-Section "Supabase DNS"
$hostName = ([Uri]$SupabaseUrl).Host
try {
  $dns = Resolve-DnsName $hostName
  $addresses = $dns | Where-Object { $_.IPAddress } | Select-Object -ExpandProperty IPAddress
  Write-Ok "$hostName resolves: $($addresses -join ', ')"
} catch {
  Write-Fail "$hostName does not resolve. The Supabase project may be paused, deleted, still restoring, or using a changed project ref."
}

Write-Section "Supabase REST"
$endpoint = "$($SupabaseUrl.TrimEnd('/'))/rest/v1/$Table`?select=id&limit=1"
try {
  $response = Invoke-WebRequest -Uri $endpoint -Headers @{
    "apikey" = $SupabaseKey
    "Authorization" = "Bearer $SupabaseKey"
    "Cache-Control" = "no-store"
  } -TimeoutSec 30
  Write-Ok "REST query returned HTTP $($response.StatusCode)"
} catch {
  $status = $_.Exception.Response.StatusCode.value__
  if ($status) {
    Write-Fail "REST query returned HTTP $status"
  } else {
    Write-Fail "REST query failed: $($_.Exception.Message)"
  }
}

Write-Section "GitHub Workflow"
$headers = @{
  "Accept" = "application/vnd.github+json"
  "X-GitHub-Api-Version" = "2026-03-10"
}

try {
  $workflows = Invoke-GitHubJson -Uri "https://api.github.com/repos/$GitHubRepo/actions/workflows" -Headers $headers
  $workflow = $workflows.workflows | Where-Object { $_.path -eq ".github/workflows/$WorkflowFile" } | Select-Object -First 1

  if (-not $workflow) {
    Write-Fail "Workflow .github/workflows/$WorkflowFile was not found on GitHub."
  } else {
    if ($workflow.state -eq "active") {
      Write-Ok "Workflow state is active."
    } else {
      Write-Fail "Workflow state is $($workflow.state). If this says disabled_inactivity, GitHub stopped it after 60 days without repository activity."
    }
    Write-Host "Updated at: $($workflow.updated_at)"
    Write-Host "URL: $($workflow.html_url)"
  }

  $runs = Invoke-GitHubJson -Uri "https://api.github.com/repos/$GitHubRepo/actions/workflows/$WorkflowFile/runs?per_page=1" -Headers $headers
  $latest = $runs.workflow_runs | Select-Object -First 1
  if ($latest) {
    Write-Host "Latest run: $($latest.created_at) / $($latest.conclusion) / $($latest.html_url)"
  } else {
    Write-Warn "No workflow runs found."
  }
} catch {
  Write-Fail "GitHub API check failed: $($_.Exception.Message)"
}

Write-Section "Interpretation"
Write-Host "Primary durable fix: deploy ops/supabase-keepalive-worker to Cloudflare Workers Cron."
Write-Host "GitHub Actions should remain only as a backup because public-repo schedules can be disabled after 60 inactive days."
