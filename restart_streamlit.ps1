Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2
Write-Host "Streamlit stopped"
