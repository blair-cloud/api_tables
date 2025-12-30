"""
Example API usage and integration tests
"""

# ============================================================================
# EXAMPLE 1: Get Student Timetable
# ============================================================================

import requests

BASE_URL = "http://localhost:8000/api/v1"

# Get student's timetable for BAPM_2023 Section A
response = requests.get(
    f"{BASE_URL}/timetable/student/",
    params={
        'cohort_id': 1,
        'section_id': 1
    }
)

student_timetable = response.json()
print("Student Timetable:")
for entry in student_timetable:
    print(f"  {entry['session']} {entry['time_interval']}: {entry['course_name']} ({entry['instructor_name']})")

# ============================================================================
# EXAMPLE 2: Get Instructor Assignments
# ============================================================================

response = requests.get(
    f"{BASE_URL}/timetable/instructor/",
    params={'instructor_id': 1}
)

instructor_schedule = response.json()
print("\nInstructor Schedule:")
for entry in instructor_schedule:
    print(f"  {entry['session']} {entry['time_interval']}: {entry['course_name']} - {entry['cohort_name']}")

# ============================================================================
# EXAMPLE 3: Connect Camera & Start People Counting
# ============================================================================

# New camera
response = requests.post(
    f"{BASE_URL}/camera/connect/",
    json={
        "ip": "192.168.1.50",
        "name": "Main Hall Camera",
        "port": 554,
        "rtsp_path": "/stream1"
    }
)

camera_result = response.json()
print("\nCamera Connection Result:")
print(f"  Status: {camera_result['status']}")
print(f"  Camera ID: {camera_result['camera_id']}")
print(f"  Camera Name: {camera_result['camera_name']}")

# ============================================================================
# EXAMPLE 4: Get Latest People Count
# ============================================================================

camera_id = camera_result['camera_id']

response = requests.get(f"{BASE_URL}/cameras/{camera_id}/latest-count/")
latest_count = response.json()

print("\nLatest Camera Count:")
print(f"  People Count: {latest_count['people_count']}")
print(f"  Frames Processed: {latest_count['frames_processed']}")
print(f"  Inference Time: {latest_count['inference_time_ms']:.2f}ms")
print(f"  Timestamp: {latest_count['timestamp']}")

# ============================================================================
# EXAMPLE 5: Get Count History
# ============================================================================

response = requests.get(
    f"{BASE_URL}/cameras/{camera_id}/counts/",
    params={'limit': 10}
)

history = response.json()
print("\nRecent Count History:")
for count in history[:5]:
    print(f"  {count['timestamp']}: {count['people_count']} people")

# ============================================================================
# EXAMPLE 6: Filter Cohorts
# ============================================================================

response = requests.get(f"{BASE_URL}/cohorts/")
cohorts = response.json()['results']

print("\nAvailable Cohorts:")
for cohort in cohorts:
    print(f"  ID: {cohort['id']}, Name: {cohort['name']}")

# ============================================================================
# EXAMPLE 7: Search Instructors
# ============================================================================

response = requests.get(
    f"{BASE_URL}/instructors/",
    params={'search': 'John'}
)

instructors = response.json()['results']
print("\nInstructors matching 'John':")
for instructor in instructors:
    print(f"  {instructor['name']} ({instructor['email']})")

# ============================================================================
# EXAMPLE 8: Get Camera Status
# ============================================================================

response = requests.get(f"{BASE_URL}/cameras/{camera_id}/")
camera_info = response.json()

print(f"\nCamera Status:")
print(f"  Name: {camera_info['name']}")
print(f"  IP: {camera_info['ip_address']}")
print(f"  Status: {camera_info['status']}")
print(f"  Active: {camera_info['is_active']}")
print(f"  Last Connection: {camera_info['last_connection']}")

# ============================================================================
# EXAMPLE 9: List All Courses
# ============================================================================

response = requests.get(f"{BASE_URL}/courses/")
courses = response.json()['results']

print("\nAll Courses:")
for course in courses[:5]:
    print(f"  {course['code']}: {course['name']}")

# ============================================================================
# EXAMPLE 10: Frontend Integration Example (React/TypeScript)
# ============================================================================

"""
// React example
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

// Get student timetable
const getStudentTimetable = async (cohortId, sectionId) => {
  const response = await axios.get(`${API_BASE}/timetable/student/`, {
    params: { cohort_id: cohortId, section_id: sectionId }
  });
  return response.data;
};

// Connect to camera
const connectCamera = async (ip) => {
  const response = await axios.post(`${API_BASE}/camera/connect/`, {
    ip: ip,
    name: `Camera ${ip}`,
    port: 554,
    rtsp_path: '/stream1'
  });
  return response.data;
};

// Get latest count
const getLatestCount = async (cameraId) => {
  const response = await axios.get(`${API_BASE}/cameras/${cameraId}/latest-count/`);
  return response.data;
};

// Usage
const handleGetTimetable = async () => {
  const timetable = await getStudentTimetable(1, 1);
  console.log('Student Timetable:', timetable);
};

const handleConnectCamera = async () => {
  const result = await connectCamera('192.168.1.50');
  console.log('Camera ID:', result.camera_id);
};
"""

# ============================================================================
# Error Handling Examples
# ============================================================================

# Check for errors
def safe_api_call(method, url, **kwargs):
    """
    Safe API call with error handling
    """
    try:
        if method.upper() == 'GET':
            response = requests.get(url, **kwargs)
        elif method.upper() == 'POST':
            response = requests.post(url, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return {'success': True, 'data': response.json()}
    
    except requests.exceptions.HTTPError as e:
        return {'success': False, 'error': str(e), 'status': e.response.status_code}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': 'Connection failed'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


# Example: Safe timetable fetch
result = safe_api_call(
    'GET',
    f"{BASE_URL}/timetable/student/",
    params={'cohort_id': 1, 'section_id': 1}
)

if result['success']:
    print("Timetable data:", result['data'])
else:
    print("Error:", result['error'])
