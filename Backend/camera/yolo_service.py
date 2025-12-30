"""
YOLO Camera Processing Service
Handles camera connection, frame processing, and person counting
"""
import logging
import threading
from typing import Optional, Dict, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

# Global dictionary to track active camera processors
_active_processors: Dict[int, 'CameraProcessor'] = {}


class CameraProcessor:
    """
    Handles processing for a single camera
    """
    def __init__(self, camera_id: int, camera_name: str, rtsp_url: str):
        self.camera_id = camera_id
        self.camera_name = camera_name
        self.rtsp_url = rtsp_url
        self.is_processing = False
        self.thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start processing for this camera"""
        if self.is_processing:
            logger.warning(f"Camera {self.camera_name} is already processing")
            return False
        
        self.is_processing = True
        self.thread = threading.Thread(target=self._process, daemon=True)
        self.thread.start()
        logger.info(f"Started processing for camera {self.camera_name}")
        return True
    
    def stop(self):
        """Stop processing for this camera"""
        self.is_processing = False
        logger.info(f"Stopped processing for camera {self.camera_name}")
        return True
    
    def _process(self):
        """Main processing loop (stub for camera frame processing)"""
        logger.debug(f"Processing loop started for {self.camera_name}")
        # This would contain actual YOLO inference code
        # For now, it's a placeholder


def start_camera_processing(camera_id: int, camera_name: str, rtsp_url: str) -> bool:
    """
    Start processing for a specific camera
    
    Args:
        camera_id: Database ID of the camera
        camera_name: Name of the camera
        rtsp_url: RTSP URL for the camera
    
    Returns:
        bool: True if processing started successfully
    """
    try:
        if camera_id in _active_processors:
            logger.warning(f"Camera {camera_id} is already being processed")
            return False
        
        processor = CameraProcessor(camera_id, camera_name, rtsp_url)
        _active_processors[camera_id] = processor
        processor.start()
        return True
    
    except Exception as e:
        logger.error(f"Error starting camera processing for {camera_name}: {str(e)}")
        return False


def stop_camera_processing(camera_id: int) -> bool:
    """
    Stop processing for a specific camera
    
    Args:
        camera_id: Database ID of the camera
    
    Returns:
        bool: True if processing stopped successfully
    """
    try:
        if camera_id not in _active_processors:
            logger.warning(f"Camera {camera_id} is not being processed")
            return False
        
        processor = _active_processors[camera_id]
        processor.stop()
        del _active_processors[camera_id]
        return True
    
    except Exception as e:
        logger.error(f"Error stopping camera processing for camera {camera_id}: {str(e)}")
        return False


def get_active_processors() -> Dict[int, CameraProcessor]:
    """Get all active camera processors"""
    return _active_processors.copy()


def is_camera_processing(camera_id: int) -> bool:
    """Check if a camera is currently processing"""
    return camera_id in _active_processors
