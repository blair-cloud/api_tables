"""
Camera app views and viewsets
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
import logging

from .models import Camera, CameraCount, Room
from .serializers import (
    CameraSerializer, CameraCountSerializer,
    CameraCountDetailSerializer, CameraConnectSerializer,
    RoomSerializer, RoomCountSerializer
)
from .yolo_service import start_camera_processing, stop_camera_processing

logger = logging.getLogger(__name__)


class CameraViewSet(viewsets.ModelViewSet):
    """
    Camera ViewSet
    GET /api/v1/cameras/ - List all cameras
    GET /api/v1/cameras/{id}/ - Retrieve specific camera
    POST /api/v1/cameras/ - Create new camera
    PATCH /api/v1/cameras/{id}/ - Update camera
    DELETE /api/v1/cameras/{id}/ - Delete camera
    
    POST /api/v1/cameras/{id}/start/ - Start processing
    POST /api/v1/cameras/{id}/stop/ - Stop processing
    GET /api/v1/cameras/{id}/latest-count/ - Get latest count
    """
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_active', 'location']
    search_fields = ['name', 'ip_address', 'location']
    ordering_fields = ['created_at', 'name', 'status']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start processing for this camera"""
        camera = self.get_object()
        
        if not camera.is_active:
            return Response(
                {'error': 'Camera is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            success = start_camera_processing(camera)
            if success:
                return Response({'status': 'Processing started'})
            else:
                return Response(
                    {'error': 'Processing already running'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Error starting camera processing: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """Stop processing for this camera"""
        camera = self.get_object()
        
        try:
            success = stop_camera_processing(camera)
            if success:
                return Response({'status': 'Processing stopped'})
            else:
                return Response(
                    {'error': 'No processing running'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Error stopping camera processing: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def latest_count(self, request, pk=None):
        """Get latest people count for this camera"""
        camera = self.get_object()
        
        try:
            latest = camera.counts.first()
            if latest:
                serializer = CameraCountSerializer(latest)
                return Response(serializer.data)
            else:
                return Response(
                    {'message': 'No counts available yet'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            logger.error(f"Error fetching latest count: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def counts(self, request, pk=None):
        """Get count history for this camera"""
        camera = self.get_object()
        limit = request.query_params.get('limit', 100)
        
        try:
            counts = camera.counts.all()[:int(limit)]
            serializer = CameraCountDetailSerializer(counts, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching camera counts: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CameraCountViewSet(viewsets.ReadOnlyModelViewSet):
    """
    CameraCount ViewSet (Read-only)
    GET /api/v1/camera-counts/ - List all counts
    GET /api/v1/camera-counts/?camera_id={id} - Filter by camera
    GET /api/v1/camera-counts/{id}/ - Retrieve specific count
    """
    queryset = CameraCount.objects.select_related('camera')
    serializer_class = CameraCountSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['camera']
    ordering_fields = ['timestamp', 'people_count']
    ordering = ['-timestamp']


class CameraConnectAPIView(APIView):
    """
    Camera connection endpoint
    POST /api/v1/camera/connect/
    
    Request body:
    {
        "camera_id": 1
    }
    OR
    {
        "ip": "192.168.1.50",
        "name": "Lab Camera",
        "port": 554,
        "rtsp_path": "/stream1"
    }
    
    Response:
    {
        "status": "connected",
        "camera_id": 1,
        "message": "Camera connected and processing started"
    }
    """
    
    def post(self, request):
        """Connect to camera and start processing"""
        serializer = CameraConnectSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        camera_id = serializer.validated_data.get('camera_id')
        
        try:
            # Case 1: Existing camera
            if camera_id:
                camera = Camera.objects.get(id=camera_id)
                logger.info(f"Connecting to existing camera: {camera.name}")
            
            # Case 2: New camera
            else:
                ip = serializer.validated_data.get('ip')
                name = serializer.validated_data.get('name', f"Camera_{ip}")
                port = serializer.validated_data.get('port', 554)
                rtsp_path = serializer.validated_data.get('rtsp_path', '')
                
                camera, created = Camera.objects.get_or_create(
                    ip_address=ip,
                    defaults={
                        'name': name,
                        'port': port,
                        'rtsp_path': rtsp_path,
                        'is_active': True,
                    }
                )
                
                action_text = "Created" if created else "Found existing"
                logger.info(f"{action_text} camera: {camera.name}")
            
            # Start processing
            if start_camera_processing(camera):
                camera.status = 'active'
                camera.last_connection = timezone.now()
                camera.save(update_fields=['status', 'last_connection'])
                
                return Response({
                    'status': 'connected',
                    'camera_id': camera.id,
                    'camera_name': camera.name,
                    'ip_address': camera.ip_address,
                    'message': 'Camera connected and processing started'
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Failed to start camera processing'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except Camera.DoesNotExist:
            logger.error(f"Camera not found: {camera_id}")
            return Response(
                {'error': f'Camera with ID {camera_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            logger.error(f"Error connecting camera: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RoomViewSet(viewsets.ModelViewSet):
    """
    Room ViewSet for room-based camera management
    GET /api/rooms/ - List all rooms
    POST /api/rooms/ - Create new room and start camera worker
    GET /api/rooms/{id}/ - Get room details
    PATCH /api/rooms/{id}/ - Update room
    DELETE /api/rooms/{id}/ - Delete room
    GET /api/rooms/{id}/counts/ - Get time-series counts for room
    POST /api/rooms/{id}/stop/ - Stop camera worker for room
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_active']
    search_fields = ['name', 'camera_ip']
    ordering_fields = ['created_at', 'name', 'status']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Create room and automatically start camera processing"""
        room = serializer.save()
        logger.info(f"Room created: {room.name}")
        
        # Start camera processing for this room
        try:
            _start_room_camera_processing(room)
            logger.info(f"Camera processing started for room: {room.name}")
        except Exception as e:
            logger.error(f"Failed to start camera processing for room {room.name}: {str(e)}")
            room.status = 'offline'
            room.save(update_fields=['status'])
    
    @action(detail=True, methods=['get'])
    def counts(self, request, pk=None):
        """
        Get time-series counts for a room
        GET /api/rooms/{id}/counts/?limit=100
        """
        room = self.get_object()
        limit = request.query_params.get('limit', 100)
        
        try:
            counts = room.counts.all()[:int(limit)]
            serializer = RoomCountSerializer(counts, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching room counts: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """
        Stop camera processing for a room
        POST /api/rooms/{id}/stop/
        """
        room = self.get_object()
        
        try:
            success = _stop_room_camera_processing(room)
            if success:
                room.status = 'inactive'
                room.save(update_fields=['status'])
                return Response({'status': 'Camera processing stopped'})
            else:
                return Response(
                    {'error': 'No processing running'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Error stopping camera processing for room {room.name}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def _start_room_camera_processing(room):
    """
    Start YOLOv8 worker for a room
    This creates a background thread or Celery task to process the room's camera
    """
    from .yolo_service import start_room_processing
    
    try:
        success = start_room_processing(room)
        if success:
            room.status = 'active'
            room.save(update_fields=['status'])
            return True
        else:
            room.status = 'offline'
            room.save(update_fields=['status'])
            return False
    except Exception as e:
        logger.error(f"Error starting room camera processing: {str(e)}")
        room.status = 'offline'
        room.save(update_fields=['status'])
        raise


def _stop_room_camera_processing(room):
    """
    Stop YOLOv8 worker for a room
    """
    from .yolo_service import stop_room_processing
    
    try:
        success = stop_room_processing(room)
        if success:
            room.status = 'inactive'
            room.save(update_fields=['status'])
            return True
        return False
    except Exception as e:
        logger.error(f"Error stopping room camera processing: {str(e)}")
        raise
