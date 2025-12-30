@echo off
REM Test timetable API endpoints
echo Testing Timetable API Endpoints...
echo.

echo 1. Testing GET /api/v1/timetable/
curl -s http://localhost:8000/api/v1/timetable/ | jq . | head -20
echo.
echo.

echo 2. Testing GET /api/v1/cohorts/
curl -s http://localhost:8000/api/v1/cohorts/ | jq . | head -20
echo.
echo.

echo 3. Testing GET /api/v1/courses/
curl -s http://localhost:8000/api/v1/courses/ | jq . | head -20
echo.
echo.

echo 4. Testing GET /api/v1/instructors/
curl -s http://localhost:8000/api/v1/instructors/ | jq . | head -20
