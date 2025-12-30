"""
Timetable app serializers
"""
from rest_framework import serializers
from .models import Cohort, Section, Instructor, Course, TimetableEntry


class CohortSerializer(serializers.ModelSerializer):
    """Serializer for Cohort model"""
    class Meta:
        model = Cohort
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SectionSerializer(serializers.ModelSerializer):
    """Serializer for Section model"""
    cohort_name = serializers.CharField(source='cohort.name', read_only=True)
    
    class Meta:
        model = Section
        fields = ['id', 'name', 'cohort', 'cohort_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class InstructorSerializer(serializers.ModelSerializer):
    """Serializer for Instructor model"""
    class Meta:
        model = Instructor
        fields = ['id', 'name', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class TimetableEntrySerializer(serializers.ModelSerializer):
    """Serializer for TimetableEntry model"""
    cohort_name = serializers.CharField(source='cohort.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    instructor_name = serializers.CharField(source='instructor.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    
    class Meta:
        model = TimetableEntry
        fields = [
            'id', 'cohort', 'cohort_name', 'section', 'section_name',
            'instructor', 'instructor_name', 'course', 'course_name',
            'course_code', 'session', 'time_interval', 'type', 'classroom',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TimetableStudentViewSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for student view - returns only relevant fields
    """
    instructor_name = serializers.CharField(source='instructor.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    
    class Meta:
        model = TimetableEntry
        fields = [
            'id', 'session', 'time_interval', 'type', 'classroom',
            'course_name', 'course_code', 'instructor_name'
        ]


class TimetableInstructorViewSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for instructor view
    """
    cohort_name = serializers.CharField(source='cohort.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    
    class Meta:
        model = TimetableEntry
        fields = [
            'id', 'session', 'time_interval', 'type', 'classroom',
            'course_name', 'course_code', 'cohort_name', 'section_name'
        ]
