param(
  [string]$Message = "Update game UI layout",
  [string]$ExportPath = "",
  [switch]$NoPush,
  [switch]$ValidateOnly,
  [switch]$SkipClipboard
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

$indexPath = Join-Path $repoRoot "urban-legend-framework\index.html"
if (!(Test-Path -LiteralPath $indexPath)) {
  throw "Cannot find urban-legend-framework\index.html from $repoRoot"
}

function Get-ConstPattern([string]$Name) {
  $escaped = [regex]::Escape($Name)
  return "(?ms)^const\s+$escaped\s*=\s*.*?^\s*[\}\]]\s*;\s*(?:\r?\n)?"
}

function Get-FirstConstBlock([string]$Text, [string]$Name) {
  $match = [regex]::Match($Text, (Get-ConstPattern $Name))
  if ($match.Success) {
    return $match.Value.TrimEnd()
  }
  return $null
}

function Set-SingleConstBlock([string]$Text, [string]$Name, [string]$Block) {
  $pattern = Get-ConstPattern $Name
  $matches = [regex]::Matches($Text, $pattern)
  if ($matches.Count -eq 0) {
    throw "Cannot find $Name in index.html"
  }

  for ($i = $matches.Count - 1; $i -ge 1; $i--) {
    $m = $matches[$i]
    $Text = $Text.Remove($m.Index, $m.Length)
  }

  $first = [regex]::Match($Text, $pattern)
  $replacement = $Block.TrimEnd() + "`r`n`r`n"
  return $Text.Substring(0, $first.Index) + $replacement + $Text.Substring($first.Index + $first.Length)
}

function Assert-SingleConst([string]$Text, [string]$Name) {
  $count = ([regex]::Matches($Text, (Get-ConstPattern $Name))).Count
  if ($count -ne 1) {
    throw "$Name appears $count times. Expected exactly 1."
  }
}

function Test-ModuleSyntax([string]$Path) {
  $html = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
  $match = [regex]::Match($html, '(?s)<script type="module">(.*?)</script>')
  if (!$match.Success) {
    throw "Cannot find the module script in index.html"
  }

  $tmp = Join-Path $env:TEMP ("run-artist-run-check-" + [guid]::NewGuid().ToString("N") + ".mjs")
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($tmp, $match.Groups[1].Value, $utf8NoBom)
  try {
    & node --check $tmp
    if ($LASTEXITCODE -ne 0) {
      throw "node --check failed"
    }
  } finally {
    Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
  }
}

function Invoke-Git([string[]]$ArgsList) {
  & git @ArgsList
  if ($LASTEXITCODE -ne 0) {
    throw "git $($ArgsList -join ' ') failed"
  }
}

$exportText = ""
if ($SkipClipboard) {
  $exportText = ""
} elseif ($ExportPath) {
  $exportText = Get-Content -LiteralPath $ExportPath -Raw -Encoding UTF8
} else {
  try {
    $exportText = Get-Clipboard -Raw
  } catch {
    $exportText = ""
  }
}

$content = Get-Content -LiteralPath $indexPath -Raw -Encoding UTF8
$appliedExport = $false

foreach ($name in @("UI_LAYOUT_DEFAULTS", "RIVER_REGION_DEFAULTS", "SCENE_OBJECT_DEFAULTS")) {
  $block = Get-FirstConstBlock $exportText $name
  if ($block) {
    $content = Set-SingleConstBlock $content $name $block
    $appliedExport = $true
  }
}

if ($appliedExport) {
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($indexPath, $content, $utf8NoBom)
  Write-Host "Applied UI export to urban-legend-framework\index.html"
} else {
  Write-Host "No export block found in clipboard/file. Publishing current index.html edits."
}

$content = Get-Content -LiteralPath $indexPath -Raw -Encoding UTF8
Assert-SingleConst $content "UI_LAYOUT_DEFAULTS"
Assert-SingleConst $content "RIVER_REGION_DEFAULTS"
Assert-SingleConst $content "SCENE_OBJECT_DEFAULTS"
Test-ModuleSyntax $indexPath

if ($ValidateOnly) {
  Write-Host "Validation passed."
  exit 0
}

Invoke-Git @("add", "--", "urban-legend-framework/index.html")

& git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
  Write-Host "No UI changes to commit."
  exit 0
}

Invoke-Git @("commit", "-m", $Message)

if (!$NoPush) {
  Invoke-Git @("push", "origin", "main")
}

Write-Host "Done."
