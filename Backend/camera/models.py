"""
Camera app models
"""
from django.db import models
from django.utils import timezone


class Room(models.Model):
    """
    Represents a physical room with a camera for people counting
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('offline', 'Offline'),
    ]
    
    name = models.CharField(max_length=255, unique=True, help_text="Unique room name")
    camera_ip = models.CharField(max_length=255, help_text="Camera IP address or URL")
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(null=True, blank=True, help_text="Last time counts were updated")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.camera_ip})"
    
    def get_latest_count(self):
        """Get the most recent people count for this room"""
        latest = self.counts.first()
        return latest.people_count if latest else 0
    
    def get_latest_count_timestamp(self):
        """Get the timestamp of the most recent count"""
        latest = self.counts.first()
        return latest.timestamp if latest else None


class Camera(models.Model):
    """
    Represents an IP camera for attendance monitoring
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('offline', 'Offline'),
        ('error', 'Error'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    ip_address = models.CharField(max_length=50)  # IPv4/IPv6
    port = models.IntegerField(default=554)
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=255, blank=True)
    rtsp_path = models.CharField(max_length=255, blank=True, help_text="e.g., /stream1")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    is_active = models.BooleanField(default=True)
    
    # Configuration
    resolution_width = models.IntegerField(default=1920)
    resolution_height = models.IntegerField(default=1080)
    fps = models.IntegerField(default=30, help_text="Frames per second")
    
    # Metadata
    location = models.CharField(max_length=255, blank=True, help_text="e.g., Main Hall, Lab 1")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_connection = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Cameras'
    
    def __str__(self):
        return f"{self.name} ({self.ip_address})"
    
    def get_rtsp_url(self):
        """
        Construct RTSP URL from camera parameters
        """
        if self.username and self.password:
            return f"rtsp://{self.username}:{self.password}@{self.ip_address}:{self.port}{self.rtsp_path}"
        return f"rtsp://{self.ip_address}:{self.port}{self.rtsp_path}"


class CameraCount(models.Model):
    """
    Stores people count data from camera
    Each entry represents aggregate count over a time period (default 60 seconds)
    Can be associated with either a Camera or a Room
    """
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='counts', null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='counts', null=True, blank=True)
    people_count = models.IntegerField(default=0)
    
    # Processing metadata
    frames_processed = models.IntegerField(default=0)
    inference_time_ms = models.FloatField(default=0.0, help_text="Average inference time in milliseconds")
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Camera Counts'
        indexes = [
            models.Index(fields=['camera', '-timestamp']),
            models.Index(fields=['room', '-timestamp']),
        ]
    
    def __str__(self):
        if self.room:
            return f"{self.room.name} - {self.people_count} people at {self.timestamp}"
        return f"{self.camera.name} - {self.people_count} people at {self.timestamp}"
