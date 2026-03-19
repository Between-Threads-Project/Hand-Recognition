import json
import math
import socket

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# =========================
# UDP CONFIG
# =========================
UDP_IP = "127.0.0.1"
UDP_PORT_Droit = 5060
UDP_PORT_Gauche = 5059

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# =========================
# MEDIAPIPE TASKS SETUP
# =========================
base_options = python.BaseOptions(model_asset_path="model/hand_landmarker.task")

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,  # MODIF : 2 mains
    running_mode=vision.RunningMode.VIDEO,
)

landmarker = vision.HandLandmarker.create_from_options(options)


# =========================
# CAMERA
# =========================
cap = cv2.VideoCapture(0)

# réduit la latence
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

timestamp = 0


# =========================
# DISTANCE FUNCTION
# =========================
def wrist_distance_relative(hand, wrist, tip_index):
    """
    Distance poignet -> doigt
    normalisée par la distance index_tip <-> pinky_tip
    """

    tip = hand[tip_index]

    dx = tip.x - wrist.x
    dy = tip.y - wrist.y
    dist = math.sqrt(dx * dx + dy * dy)

    index_o = hand[5]
    pinky_o = hand[17]

    dx_ref = index_o.x - pinky_o.x
    dy_ref = index_o.y - pinky_o.y
    ref = math.sqrt(dx_ref * dx_ref + dy_ref * dy_ref)

    if ref < 1e-6:
        return 0

    dist = dist / ref
    dist = min(2.0, dist)
    dist = dist - 1.0

    return dist


# =========================
# MAIN LOOP
# =========================
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

            data = {
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

            message = json.dumps(data)

            print(message)

            # MODIF : détection Left / Right
            handedness = result.handedness[i][0].category_name

            if handedness == "Right":
                sock.sendto(message.encode(), (UDP_IP, UDP_PORT_Droit))

            elif handedness == "Left":
                sock.sendto(message.encode(), (UDP_IP, UDP_PORT_Gauche))

    if cv2.waitKey(1) == 27:
        break


cap.release()
cv2.destroyAllWindows()
