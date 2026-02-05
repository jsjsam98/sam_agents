# Download and setup PocketBase for Windows
Invoke-WebRequest -Uri "https://github.com/pocketbase/pocketbase/releases/download/v0.36.2/pocketbase_0.36.2_windows_amd64.zip" -OutFile "pb.zip"
Expand-Archive -Path "pb.zip" -DestinationPath "." -Force
Remove-Item "pb.zip"

# Create superuser
.\pocketbase.exe superuser upsert test@test.com test1234

Write-Host "Setup complete! Run: .\pocketbase.exe serve" -ForegroundColor Green
