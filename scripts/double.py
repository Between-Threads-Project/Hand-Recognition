import json
import socket

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from core.utils import wrist_distance_relative, low_pass_filter

UDP_IP_full = "127.0.0.1"
UDP_PORT_Droit_full = 5060
UDP_PORT_Gauche_full = 5059

UDP_IP_small = "100.127.151.6"
UDP_PORT_Droit_small = 5000
UDP_PORT_Gauche_small = 5001


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

base_options = python.BaseOptions(model_asset_path="model/hand_landmarker.task")

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,  # MODIF : 2 mains
    running_mode=vision.RunningMode.VIDEO,
)

landmarker = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

# réduit la latence
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

timestamp = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    timestamp += 1

    result = landmarker.detect_for_video(mp_image, timestamp)

    if result.hand_landmarks:
        filter_small_right = low_pass_filter()
        filter_small_left = low_pass_filter()
        for i, hand in enumerate(result.hand_landmarks):  # MODIF : itération mains
            wrist = hand[0]

            thumb1 = wrist_distance_relative(hand, wrist, 4)
            thumb2 = wrist_distance_relative(hand, wrist, 3)
            index1 = wrist_distance_relative(hand, wrist, 8)
            index2 = wrist_distance_relative(hand, wrist, 7)
            middle1 = wrist_distance_relative(hand, wrist, 12)
            middle2 = wrist_distance_relative(hand, wrist, 11)
            ring1 = wrist_distance_relative(hand, wrist, 16)
            ring2 = wrist_distance_relative(hand, wrist, 15)
            pinky1 = wrist_distance_relative(hand, wrist, 20)
            pinky2 = wrist_distance_relative(hand, wrist, 19)

            full_data = {
                "thumb1": thumb1,
                "thumb2": thumb2,
                "index1": index1,
                "index2": index2,
                "middle1": middle1,
                "middle2": middle2,
                "ring1": ring1,
                "ring2": ring2,
                "pinky1": pinky1,
                "pinky2": pinky2,
            }
            handedness = result.handedness[i][0].category_name
            
            small_data = {"index": round(index1, 1), "middle": round(middle1, 1)}
            if handedness == "Right":
                small_data = filter_small_right(small_data)

            elif handedness == "Left":
                small_data = filter_small_left(small_data)

            full_message = json.dumps(full_data)
            small_message = json.dumps(small_data)

            # MODIF : détection Left / Right
            

            if handedness == "Right":
                sock.sendto(full_message.encode(), (UDP_IP_full, UDP_PORT_Droit_full))
                sock.sendto(
                    small_message.encode(), (UDP_IP_small, UDP_PORT_Droit_small)
                )

            elif handedness == "Left":
                sock.sendto(full_message.encode(), (UDP_IP_full, UDP_PORT_Gauche_full))
                sock.sendto(
                    small_message.encode(), (UDP_IP_small, UDP_PORT_Gauche_small)
                )


cap.release()
cv2.destroyAllWindows()
