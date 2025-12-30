"""
Django project URL configuration for Nava Table API
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Import viewsets
from timetable.views import (
    CohortViewSet, SectionViewSet, InstructorViewSet,
    CourseViewSet, TimetableEntryViewSet
)
from camera.views import (
    CameraViewSet, CameraCountViewSet, CameraConnectAPIView, RoomViewSet
)

# Initialize router
router = DefaultRouter()
router.register(r'cohorts', CohortViewSet, basename='cohort')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'instructors', InstructorViewSet, basename='instructor')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'timetable', TimetableEntryViewSet, basename='timetable')
router.register(r'cameras', CameraViewSet, basename='camera')
router.register(r'camera-counts', CameraCountViewSet, basename='camera-count')
router.register(r'rooms', RoomViewSet, basename='room')


@api_view(['GET'])
def api_root(request):
    """API root endpoint with documentation"""
    return Response({
        'message': 'Nava Table API Backend',
        'version': '1.0.0',
        'endpoints': {
            'timetable': {
                'all_timetable': 'GET /api/v1/timetable/',
                'by_term': 'GET /api/v1/timetable/by-term/?term=Term_1_AY_2025/2026_Timetable',
                'by_section': 'GET /api/v1/timetable/by-section/?term=Term_1_AY_2025/2026_Timetable&section=BAPM_2023_Section_A',
                'student_timetable': 'GET /api/v1/timetable/student/?term=Term_1_AY_2025/2026_Timetable&section=BAPM_2023_Section_A',
                'instructor_timetable': 'GET /api/v1/timetable/instructor/?instructor_name=Dieudonne, U.',
                'cohorts': 'GET /api/v1/cohorts/',
                'sections': 'GET /api/v1/sections/?cohort_id=',
                'instructors': 'GET /api/v1/instructors/',
                'courses': 'GET /api/v1/courses/',
            },
            'camera': {
                'connect': 'POST /api/v1/camera/connect/',
                'list': 'GET /api/v1/cameras/',
                'detail': 'GET /api/v1/cameras/{id}/',
                'latest_count': 'GET /api/v1/cameras/{id}/latest-count/',
                'count_history': 'GET /api/v1/cameras/{id}/counts/',
            },
            'rooms': {
                'list': 'GET /api/v1/rooms/',
                'create': 'POST /api/v1/rooms/',
                'detail': 'GET /api/v1/rooms/{id}/',
                'counts': 'GET /api/v1/rooms/{id}/counts/',
                'stop': 'POST /api/v1/rooms/{id}/stop/',
            }
        },
        'admin': '/admin/',
        'docs': '/README.md'
    })


urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', api_root, name='api-root'),
    path('api/v1/', include(router.urls)),
    path('api/v1/camera/connect/', CameraConnectAPIView.as_view(), name='camera-connect'),
    
    # Authentication (optional, for future use)
    # path('api/v1/auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
