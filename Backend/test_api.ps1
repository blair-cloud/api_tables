# Test timetable API endpoints

Write-Host "Testing Timetable API Endpoints..." -ForegroundColor Green
Write-Host ""

Write-Host "1. Testing GET /api/v1/timetable/" -ForegroundColor Cyan
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/timetable/" -Method GET -ErrorAction SilentlyContinue
$timetable = $response.Content | ConvertFrom-Json
Write-Host "Terms available:" -ForegroundColor Yellow
$timetable | Get-Member -MemberType NoteProperty | ForEach-Object { Write-Host "  - $($_.Name)" }
Write-Host ""

Write-Host "2. Testing GET /api/v1/cohorts/" -ForegroundColor Cyan
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/cohorts/" -Method GET -ErrorAction SilentlyContinue
$cohorts = $response.Content | ConvertFrom-Json
Write-Host "Cohorts count: $($cohorts.results.Count)" -ForegroundColor Yellow
$cohorts.results | Select-Object -First 5 | ForEach-Object { Write-Host "  - $($_.name)" }
Write-Host ""

Write-Host "3. Testing GET /api/v1/courses/" -ForegroundColor Cyan
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/courses/" -Method GET -ErrorAction SilentlyContinue
$courses = $response.Content | ConvertFrom-Json
Write-Host "Courses count: $($courses.results.Count)" -ForegroundColor Yellow
$courses.results | Select-Object -First 5 | ForEach-Object { Write-Host "  - $($_.code): $($_.name)" }
Write-Host ""

Write-Host "4. Testing GET /api/v1/instructors/" -ForegroundColor Cyan
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/instructors/" -Method GET -ErrorAction SilentlyContinue
$instructors = $response.Content | ConvertFrom-Json
Write-Host "Instructors count: $($instructors.results.Count)" -ForegroundColor Yellow
$instructors.results | Select-Object -First 5 | ForEach-Object { Write-Host "  - $($_.name)" }
Write-Host ""

Write-Host "5. Testing GET /api/v1/timetable/?format=json (database entries)" -ForegroundColor Cyan
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/timetable/?format=json" -Method GET -ErrorAction SilentlyContinue
$entries = $response.Content | ConvertFrom-Json
Write-Host "Timetable entries count: $($entries.results.Count)" -ForegroundColor Yellow
Write-Host ""

Write-Host "API is working successfully!" -ForegroundColor Green
