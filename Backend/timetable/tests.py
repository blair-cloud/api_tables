"""
Timetable tests
"""
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Cohort, Section, Instructor, Course, TimetableEntry


class TimetableAPITests(TestCase):
    """Test timetable API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test data
        self.cohort = Cohort.objects.create(name='Test Cohort 2024')
        self.section = Section.objects.create(name='Section A', cohort=self.cohort)
        self.instructor = Instructor.objects.create(name='Dr. Test', email='test@test.edu')
        self.course = Course.objects.create(code='TEST101', name='Test Course')
    
    def test_get_cohorts(self):
        """Test getting cohorts list"""
        response = self.client.get('/api/v1/cohorts/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_get_sections(self):
        """Test getting sections by cohort"""
        response = self.client.get(f'/api/v1/sections/?cohort_id={self.cohort.id}')
        self.assertEqual(response.status_code, 200)
    
    def test_student_timetable_view(self):
        """Test student timetable endpoint"""
        response = self.client.get(
            f'/api/v1/timetable/student/?cohort_id={self.cohort.id}&section_id={self.section.id}'
        )
        self.assertEqual(response.status_code, 200)
