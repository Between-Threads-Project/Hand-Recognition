import json
import socket
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from core.utils import wrist_distance_relative

class HandScanner:
    def __init__(self, model_path="model/hand_landmarker.task", num_hands=1):
        self.model_path = model_path
        self.num_hands = num_hands
        self.initialize_mediapipe()
        self.initialize_camera()
        self.timestamp = 0

    def initialize_mediapipe(self):
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=self.num_hands,
            running_mode=vision.RunningMode.VIDEO,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

    def initialize_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        self.timestamp += 1
        result = self.landmarker.detect_for_video(mp_image, self.timestamp)

        return result

    def extract_hand_data(self, hand):
        wrist = hand[0]
        
        data = {
            "thumb1": wrist_distance_relative(hand, wrist, 4),
            "thumb2": wrist_distance_relative(hand, wrist, 3),
            "index1": wrist_distance_relative(hand, wrist, 8),
            "index2": wrist_distance_relative(hand, wrist, 7),
            "middle1": wrist_distance_relative(hand, wrist, 12),
            "middle2": wrist_distance_relative(hand, wrist, 11),
            "ring1": wrist_distance_relative(hand, wrist, 16),
            "ring2": wrist_distance_relative(hand, wrist, 15),
            "pinky1": wrist_distance_relative(hand, wrist, 20),
            "pinky2": wrist_distance_relative(hand, wrist, 19),
        }
        
        return data

    def send_data(self, data, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = json.dumps(data)
        sock.sendto(message.encode(), (ip, port))

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
