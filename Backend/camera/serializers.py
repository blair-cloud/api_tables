"""
Camera app serializers
"""
from rest_framework import serializers
from .models import Camera, CameraCount, Room


class CameraSerializer(serializers.ModelSerializer):
    """
    Main serializer for Camera model
    """
    rtsp_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Camera
        fields = [
            'id', 'name', 'ip_address', 'port', 'username', 'password',
            'rtsp_path', 'status', 'is_active', 'resolution_width',
            'resolution_height', 'fps', 'location', 'created_at',
            'updated_at', 'last_connection', 'rtsp_url'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_connection']
    
    def get_rtsp_url(self, obj):
        """Get the RTSP URL from the camera"""
        return obj.get_rtsp_url()


class CameraCountSerializer(serializers.ModelSerializer):
    """
    Serializer for camera counts (basic)
    """
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    
    class Meta:
        model = CameraCount
        fields = [
            'id', 'camera', 'room', 'camera_name', 'room_name',
            'people_count', 'frames_processed', 'inference_time_ms',
            'timestamp'
        ]
        read_only_fields = ['timestamp']


class CameraCountDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for camera counts with nested objects
    """
    camera = CameraSerializer(read_only=True)
    room = serializers.SerializerMethodField()
    
    class Meta:
        model = CameraCount
        fields = [
            'id', 'camera', 'room', 'people_count',
            'frames_processed', 'inference_time_ms', 'timestamp'
        ]
        read_only_fields = ['timestamp']
    
    def get_room(self, obj):
        """Get room serialized data"""
        if obj.room:
            return RoomSerializer(obj.room).data
        return None


class CameraConnectSerializer(serializers.Serializer):
    """
    Serializer for camera connection testing
    """
    ip_address = serializers.CharField()
    port = serializers.IntegerField(required=False, default=554)
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True)
    rtsp_path = serializers.CharField(required=False, allow_blank=True)


class RoomSerializer(serializers.ModelSerializer):
    """
    Main serializer for Room model
    """
    latest_count = serializers.SerializerMethodField()
    latest_count_timestamp = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'camera_ip', 'is_active', 'status',
            'created_at', 'updated_at', 'last_updated',
            'latest_count', 'latest_count_timestamp'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_latest_count(self, obj):
        """Get the latest people count for the room"""
        return obj.get_latest_count()
    
    def get_latest_count_timestamp(self, obj):
        """Get the timestamp of the latest count"""
        return obj.get_latest_count_timestamp()


class RoomCountSerializer(serializers.ModelSerializer):
    """
    Serializer for room counts (recent counts for a room)
    """
    class Meta:
        model = CameraCount
        fields = ['id', 'people_count', 'frames_processed', 'inference_time_ms', 'timestamp']
        read_only_fields = ['timestamp']
