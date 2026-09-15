#!/usr/bin/env python3
"""
Strict Face and Voice Monitoring for Exam Security
Automatic logout for no face detection or excessive voice activity
"""

import cv2
import numpy as np
import threading
import time
import json
from datetime import datetime
import speech_recognition as sr
from collections import deque
import base64
import io

class StrictFaceVoiceMonitor:
    def __init__(self):
        # Initialize face detection
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            if self.face_cascade.empty():
                print("❌ Failed to load face cascade")
                self.face_cascade = None
            else:
                print("✅ Face cascade loaded successfully")
        except Exception as e:
            print(f"❌ Error initializing face detection: {e}")
            self.face_cascade = None
            
        # Initialize speech recognition
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            print("✅ Speech recognition initialized")
        except Exception as e:
            print(f"❌ Error initializing speech recognition: {e}")
            
        # Monitoring state
        self.is_running = False
        self.current_face_count = 0
        self.voice_detected = False
        self.multiple_faces_detected = False
        self.excessive_voice_detected = False
        self.no_face_detected = False
        
        # History for detection
        self.face_history = deque(maxlen=10)
        self.voice_activity_history = deque(maxlen=20)
        
        # Detection thresholds
        self.face_detection_threshold = 3  # Need 3 consecutive detections
        self.multiple_face_threshold = 1.5  # Average > 1.5 faces
        self.no_face_threshold = 0.5  # Average < 0.5 faces (no face)
        self.voice_activity_threshold = 10  # More than 10 voice activities in 20 checks
        self.logout_detection_count = 3  # Need 3 violations before logout
        self.current_violation_count = 0  # Track consecutive violations
        
        # Callback for violations
        self.violation_callback = None
        
        # Latest frame for web display
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        
        print("🔍 Strict Face and Voice Monitor initialized")
        
    def start_monitoring(self, violation_callback=None):
        """Start face and voice monitoring"""
        self.violation_callback = violation_callback
        self.is_running = True
        
        # Start face monitoring thread
        face_thread = threading.Thread(target=self._monitor_faces_strict)
        face_thread.daemon = True
        face_thread.start()
        
        # Start voice monitoring thread
        voice_thread = threading.Thread(target=self._monitor_voices_strict)
        voice_thread.daemon = True
        voice_thread.start()
        
        print("🚀 Strict face and voice monitoring started")
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_running = False
        print("⏹️ Strict face and voice monitoring stopped")
        
    def _monitor_faces_strict(self):
        """Strict face monitoring with no-face detection"""
        print("🎥 Starting strict face monitoring...")
        
        # Try to open camera with multiple indices
        cap = None
        camera_indices = [0, 1, 2]
        
        for camera_index in camera_indices:
            try:
                print(f"📷 Trying camera index {camera_index}...")
                cap = cv2.VideoCapture(camera_index)
                
                # Test if camera is working
                if cap.isOpened():
                    ret, test_frame = cap.read()
                    if ret and test_frame is not None:
                        print(f"✅ Camera {camera_index} is working!")
                        break
                    else:
                        print(f"❌ Camera {camera_index} can't read frame")
                        cap.release()
                        cap = None
                else:
                    print(f"❌ Camera {camera_index} not available")
                    if cap:
                        cap.release()
                        cap = None
            except Exception as e:
                print(f"❌ Error with camera {camera_index}: {e}")
                if cap:
                    cap.release()
                    cap = None
        
        if cap is None:
            print("❌ No working camera found! Face detection disabled.")
            # Create a dummy frame when no camera is available
            self._create_no_camera_frame()
            return
            
        print("✅ Camera opened successfully")
        
        # Set basic camera properties
        try:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
        except Exception as e:
            print(f"⚠️ Could not set camera properties: {e}")
        
        consecutive_detections = 0
        frame_count = 0
        
        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to capture frame")
                time.sleep(1)
                continue
                
            frame_count += 1
            
            try:
                # Only process if face cascade is available
                if self.face_cascade is not None:
                    # Convert to grayscale
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Apply histogram equalization for better contrast
                    gray = cv2.equalizeHist(gray)
                    
                    # Detect faces with sensitive parameters
                    faces = self.face_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.05,
                        minNeighbors=3,
                        minSize=(20, 20),
                        maxSize=(300, 300)
                    )
                    
                    # If no faces detected, try with even more relaxed parameters
                    if len(faces) == 0:
                        faces = self.face_cascade.detectMultiScale(
                            gray,
                            scaleFactor=1.03,
                            minNeighbors=2,
                            minSize=(15, 15),
                            maxSize=(400, 400)
                        )
                    
                    current_face_count = len(faces)
                    
                    # Log every 20 frames
                    if frame_count % 20 == 0:
                        print(f"📊 Frame {frame_count}: {current_face_count} faces detected")
                    
                    # Update face history
                    self.face_history.append(current_face_count)
                    
                    # Check for stable detection
                    if len(self.face_history) >= self.face_detection_threshold:
                        recent_faces = list(self.face_history)[-self.face_detection_threshold:]
                        avg_faces = sum(recent_faces) / len(recent_faces)
                        
                        self.current_face_count = round(avg_faces)
                        
                        # Check for NO FACE (strict violation)
                        if avg_faces < self.no_face_threshold:
                            consecutive_detections += 1
                            self.current_violation_count += 1
                            self.no_face_detected = True
                            
                            print(f"🚨 NO FACE violation #{self.current_violation_count}: {avg_faces:.1f} faces")
                            
                            # Trigger violation after 2 consecutive no-face detections
                            if consecutive_detections >= 2 and self.current_violation_count >= 2:
                                if not self.no_face_detected:
                                    self.no_face_detected = True
                                    self._trigger_violation("no_face", f"No face detected for {consecutive_detections} consecutive checks - LOGOUT")
                                    print("🔴 LOGOUT TRIGGERED: No face detected!")
                        # Check for MULTIPLE FACES
                        elif avg_faces > self.multiple_face_threshold:
                            consecutive_detections += 1
                            self.current_violation_count += 1
                            self.multiple_faces_detected = True
                            self.no_face_detected = False
                            
                            print(f"🚨 MULTIPLE FACES violation #{self.current_violation_count}: {avg_faces:.1f} faces")
                            
                            # Trigger violation after 3 consecutive detections
                            if consecutive_detections >= 3 and self.current_violation_count >= 3:
                                if not self.multiple_faces_detected:
                                    self.multiple_faces_detected = True
                                    self._trigger_violation("multiple_faces", f"Multiple faces detected: {avg_faces:.1f} faces - LOGOUT")
                                    print("🔴 LOGOUT TRIGGERED: Multiple faces detected!")
                        else:
                            consecutive_detections = 0
                            # Reset violation count if faces are normal
                            if self.current_violation_count > 0 and 0.5 <= avg_faces <= 1.5:
                                print(f"✅ Violation count reset: {avg_faces:.1f} faces (normal)")
                                self.current_violation_count = 0
                            self.multiple_faces_detected = False
                            self.no_face_detected = False
                    
                    # Draw rectangles on faces
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Add status text
                    if self.no_face_detected:
                        status_text = f"NO FACE DETECTED! | Violations: {self.current_violation_count}/3"
                        color = (0, 0, 255)
                    elif self.multiple_faces_detected:
                        status_text = f"MULTIPLE FACES! | Violations: {self.current_violation_count}/3"
                        color = (0, 0, 255)
                    else:
                        status_text = f"Faces: {self.current_face_count} | Status: SECURE"
                        color = (0, 255, 0)
                    
                    cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                else:
                    # No face detection available
                    cv2.putText(frame, "Face detection not available", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Store latest frame
                with self.frame_lock:
                    self.latest_frame = frame.copy()
                    
            except Exception as e:
                print(f"❌ Face detection error: {e}")
                
            time.sleep(0.2)  # Process every 200ms
            
        cap.release()
        print("🎥 Face monitoring stopped")
        
    def _create_no_camera_frame(self):
        """Create a dummy frame when no camera is available"""
        print("🖼️ Creating no-camera frame...")
        
        while self.is_running:
            try:
                # Create a black frame with text
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                
                # Add text
                cv2.putText(frame, "CAMERA NOT AVAILABLE", (120, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, "Face detection disabled", (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, f"Violations: {self.current_violation_count}/3", (250, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Store latest frame
                with self.frame_lock:
                    self.latest_frame = frame.copy()
                    
            except Exception as e:
                print(f"❌ Error creating no-camera frame: {e}")
                
            time.sleep(1)  # Update every second
        
    def _monitor_voices_strict(self):
        """Strict voice monitoring with excessive voice detection"""
        print("🎤 Starting strict voice monitoring...")
        
        voice_activity_count = 0
        check_count = 0
        
        while self.is_running:
            try:
                with self.microphone as source:
                    # Adjust for ambient noise with shorter duration
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    
                    # Listen for audio with shorter timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=2)
                    
                    # Try to recognize speech
                    try:
                        text = self.recognizer.recognize_google(audio)
                        if text.strip():
                            voice_activity_count += 1
                            self.voice_detected = True
                            self.voice_activity_history.append(1)
                            
                            print(f"🎤 Voice activity detected: {text[:30]}... (Total: {voice_activity_count})")
                            
                            # Check for excessive voice activity
                            check_count += 1
                            if check_count >= 10:  # Check every 10 voice activities
                                recent_activity = list(self.voice_activity_history)[-10:]
                                activity_rate = sum(recent_activity) / len(recent_activity)
                                
                                if activity_rate > self.voice_activity_threshold:
                                    self.excessive_voice_detected = True
                                    self.current_violation_count += 1
                                    
                                    print(f"🚨 EXCESSIVE VOICE violation #{self.current_violation_count}: {activity_rate:.1f} activities")
                                    
                                    # Trigger violation after excessive voice
                                    if self.current_violation_count >= 2:
                                        self._trigger_violation("excessive_voice", f"Excessive voice activity detected - LOGOUT")
                                        print("🔴 LOGOUT TRIGGERED: Excessive voice activity!")
                                
                                check_count = 0
                                        
                    except sr.UnknownValueError:
                        # No speech detected
                        self.voice_activity_history.append(0)
                        check_count += 1
                    except sr.RequestError:
                        # API error
                        print("⚠️ Speech recognition API error")
                        pass
                        
            except sr.WaitTimeoutError:
                # Timeout is normal, just continue
                pass
            except Exception as e:
                print(f"❌ Voice monitoring error: {e}")
                
            time.sleep(3)  # Check every 3 seconds
            
    def _trigger_violation(self, violation_type, details):
        """Trigger violation callback"""
        print(f"🚨 STRICT VIOLATION: {violation_type} - {details}")
        if self.violation_callback:
            violation_data = {
                'type': violation_type,
                'details': details,
                'timestamp': datetime.now().isoformat(),
                'auto_logout': True
            }
            self.violation_callback(violation_data)
            
    def get_status(self):
        """Get current monitoring status"""
        return {
            'is_running': self.is_running,
            'face_count': self.current_face_count,
            'voice_detected': self.voice_detected,
            'multiple_faces_detected': self.multiple_faces_detected,
            'no_face_detected': self.no_face_detected,
            'excessive_voice_detected': self.excessive_voice_detected,
            'face_history': list(self.face_history),
            'voice_history': list(self.voice_activity_history),
            'violation_count': self.current_violation_count,
            'max_violations': self.logout_detection_count
        }
        
    def get_frame_as_base64(self):
        """Get latest frame as base64 encoded string"""
        with self.frame_lock:
            if self.latest_frame is not None:
                try:
                    _, buffer = cv2.imencode('.jpg', self.latest_frame)
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    return frame_base64
                except Exception as e:
                    print(f"❌ Error encoding frame: {e}")
        return None

# Global strict monitor instance
strict_monitor = StrictFaceVoiceMonitor()
