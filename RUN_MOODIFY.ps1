Write-Host "Starting Moodify backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @("-NoExit","-Command","cd '$PSScriptRoot\backend'; ..\.venv\Scripts\python.exe -m uvicorn main:app --reload")
Start-Sleep 2
Write-Host "Starting Moodify frontend..." -ForegroundColor Green
Start-Process powershell -ArgumentList @("-NoExit","-Command","cd '$PSScriptRoot\frontend'; npm run dev")
