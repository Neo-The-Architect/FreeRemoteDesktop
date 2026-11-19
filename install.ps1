param(
 [ValidateSet('codex','claude-desktop')][string]$Client='codex',
 [switch]$PlanOnly,
 [switch]$OpenDashboard
)
$ErrorActionPreference='Stop'
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$Python=(Get-Command python -ErrorAction Stop).Source
if ($PlanOnly) {
  & $Python (Join-Path $Root 'setup.py') plan --client $Client
  exit $LASTEXITCODE
}
& $Python (Join-Path $Root 'setup.py') install --client $Client
if ($LASTEXITCODE -ne 0) { throw 'Client setup failed' }
& $Python (Join-Path $Root 'test_product.py')
if ($LASTEXITCODE -ne 0) { throw 'Self-test failed' }
if ($OpenDashboard) { & $Python (Join-Path $Root 'dashboard.py') }
