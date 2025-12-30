"""
Timetable app views and viewsets
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.conf import settings
import logging
import json
import os

from .models import Cohort, Section, Instructor, Course, TimetableEntry
from .serializers import (
    CohortSerializer, SectionSerializer, InstructorSerializer,
    CourseSerializer, TimetableEntrySerializer,
    TimetableStudentViewSerializer, TimetableInstructorViewSerializer
)

logger = logging.getLogger(__name__)


def load_timetable_json():
    """Load timetable data from JSON file"""
    try:
        # Load from Backend/timetable/timetable.json
        json_path = os.path.join(settings.BASE_DIR, 'timetable', 'timetable.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        # Fallback to Backend directory root
        json_path = os.path.join(settings.BASE_DIR, 'timetable.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        logger.warning("Timetable JSON file not found")
        return {}
    except Exception as e:
        logger.error(f"Error loading timetable JSON: {str(e)}")
        return {}


class CohortViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Cohort ViewSet
    GET /api/v1/cohorts/ - List all cohorts
    GET /api/v1/cohorts/{id}/ - Retrieve specific cohort
    """
    queryset = Cohort.objects.all()
    serializer_class = CohortSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Section ViewSet
    GET /api/v1/sections/ - List all sections
    GET /api/v1/sections/?cohort_id={id} - Filter by cohort
    GET /api/v1/sections/{id}/ - Retrieve specific section
    """
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['cohort']
    ordering_fields = ['name', 'created_at']
    ordering = ['cohort', 'name']


class InstructorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Instructor ViewSet
    GET /api/v1/instructors/ - List all instructors
    GET /api/v1/instructors/?search={name} - Search by name
    GET /api/v1/instructors/{id}/ - Retrieve specific instructor
    """
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Course ViewSet
    GET /api/v1/courses/ - List all courses
    GET /api/v1/courses/?search={code_or_name} - Search by code or name
    GET /api/v1/courses/{id}/ - Retrieve specific course
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']


class TimetableEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    TimetableEntry ViewSet with custom actions for student and instructor views
    
    GET /api/v1/timetable/ - Get all timetable data from JSON
    GET /api/v1/timetable/by-term/ - Get timetable by term
    GET /api/v1/timetable/by-section/ - Get timetable by section (requires section parameter)
    """
    queryset = TimetableEntry.objects.select_related(
        'cohort', 'section', 'instructor', 'course'
    )
    serializer_class = TimetableEntrySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['cohort', 'section', 'instructor', 'course', 'session', 'type']
    ordering_fields = ['session', 'time_interval', 'created_at']
    ordering = ['session', 'time_interval']
    
    def list(self, request, *args, **kwargs):
        """
        Override list to return timetable from JSON
        GET /api/v1/timetable/
        """
        try:
            timetable_data = load_timetable_json()
            if timetable_data:
                return Response(timetable_data)
            return Response({'error': 'No timetable data available'}, status=400)
        except Exception as e:
            logger.error(f"Error retrieving timetable: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve timetable'},
                status=HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def by_term(self, request):
        """
        Get timetable for a specific term
        Example: GET /api/v1/timetable/by-term/?term=Term_1_AY_2025/2026_Timetable
        """
        term = request.query_params.get('term')
        
        if not term:
            return Response(
                {'error': 'term parameter is required'},
                status=HTTP_400_BAD_REQUEST
            )
        
        try:
            timetable_data = load_timetable_json()
            if term in timetable_data:
                return Response({term: timetable_data[term]})
            return Response(
                {'error': f'Term "{term}" not found'},
                status=HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error retrieving timetable by term: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve timetable'},
                status=HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def by_section(self, request):
        """
        Get timetable for a specific section
        Example: GET /api/v1/timetable/by-section/?term=Term_1_AY_2025/2026_Timetable&section=BAPM_2023_Section_A
        """
        term = request.query_params.get('term')
        section = request.query_params.get('section')
        
        if not term or not section:
            return Response(
                {'error': 'Both term and section parameters are required'},
                status=HTTP_400_BAD_REQUEST
            )
        
        try:
            timetable_data = load_timetable_json()
            if term in timetable_data and section in timetable_data[term]:
                return Response({
                    'term': term,
                    'section': section,
                    'data': timetable_data[term][section]
                })
            return Response(
                {'error': f'Term "{term}" or section "{section}" not found'},
                status=HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error retrieving timetable by section: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve timetable'},
                status=HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def student(self, request):
        """
        Student timetable view - returns section-specific timetable from JSON
        
        Example: GET /api/v1/timetable/student/?term=Term_1_AY_2025/2026_Timetable&section=BAPM_2023_Section_A
        """
        term = request.query_params.get('term')
        section = request.query_params.get('section')
        
        # Legacy support for cohort_id and section_id
        cohort_id = request.query_params.get('cohort_id')
        section_id = request.query_params.get('section_id')
        
        if (not term or not section) and (not cohort_id or not section_id):
            return Response(
                {'error': 'Either (term and section) or (cohort_id and section_id) are required'},
                status=HTTP_400_BAD_REQUEST
            )
        
        try:
            # If using new parameters
            if term and section:
                timetable_data = load_timetable_json()
                if term in timetable_data and section in timetable_data[term]:
                    return Response({
                        'term': term,
                        'section': section,
                        'timetable': timetable_data[term][section]
                    })
                return Response(
                    {'error': f'Term "{term}" or section "{section}" not found'},
                    status=HTTP_400_BAD_REQUEST
                )
            # Legacy support
            else:
                queryset = self.queryset.filter(cohort_id=cohort_id, section_id=section_id)
                serializer = TimetableStudentViewSerializer(queryset, many=True)
                return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in student timetable view: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve timetable'},
                status=HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def instructor(self, request):
        """
        Instructor timetable view
        Required: instructor_id (legacy) or instructor_name
        
        Example: GET /api/v1/timetable/instructor/?instructor_name=Dieudonne, U.
        """
        instructor_id = request.query_params.get('instructor_id')
        instructor_name = request.query_params.get('instructor_name')
        
        if not instructor_id and not instructor_name:
            return Response(
                {'error': 'Either instructor_id or instructor_name is required'},
                status=HTTP_400_BAD_REQUEST
            )
        
        try:
            # If using instructor_name, search in JSON
            if instructor_name:
                timetable_data = load_timetable_json()
                instructor_schedule = {}
                
                # Search through all terms and sections
                for term, sections in timetable_data.items():
                    for section, days in sections.items():
                        for day, sessions in days.items():
                            for session_key, session_data in sessions.items():
                                if session_data.get('Instructor') == instructor_name:
                                    key = f"{term} - {section}"
                                    if key not in instructor_schedule:
                                        instructor_schedule[key] = {}
                                    if day not in instructor_schedule[key]:
                                        instructor_schedule[key][day] = {}
                                    instructor_schedule[key][day][session_key] = session_data
                
                if instructor_schedule:
                    return Response(instructor_schedule)
                return Response(
                    {'error': f'No schedule found for instructor "{instructor_name}"'},
                    status=HTTP_400_BAD_REQUEST
                )
            # Legacy support for instructor_id
            else:
                queryset = self.queryset.filter(instructor_id=instructor_id)
                serializer = TimetableInstructorViewSerializer(queryset, many=True)
                return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in instructor timetable view: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve assignments'},
                status=HTTP_400_BAD_REQUEST
            )
