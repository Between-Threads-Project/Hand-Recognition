import json
import socket
from typing import Callable, List, Tuple

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from core.utils import wrist_distance_relative


def start_hand_tracking(
    address: List[Tuple[str, str, int]],
    modifier: Callable[[dict[str, float]], dict[str, float]] | None = None,
) -> None:
    """
    Starts hand tracking and sends hand landmark data via UDP to specified endpoints.

    This function initializes video capture, detects hand landmarks using MediaPipe,
    calculates relative distances of fingers from the wrist, and sends this data as JSON
    via UDP to the specified addresses. It supports both full and small data formats.

    Args:
        address: A list of tuples containing the message type, IP address, and port.
                 Each tuple is in the form (type, ip, port), where:
                 - type: "full" to send all finger data, or "small" to send a subset.
                 - ip: Destination IP address.
                 - port: Destination port.
        modifier: An optional function to modify the data before sending.
                  If provided, it will be applied to both full and small data.

    Returns:
        None
    """
    # Socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # MediaPipe
    base_options = python.BaseOptions(model_asset_path="model/hand_landmarker.task")
    options = vision.HandLandmarkerOptions(
        base_options=base_options, num_hands=1, running_mode=vision.RunningMode.VIDEO
    )
    landmarker = vision.HandLandmarker.create_from_options(options)

    # Capture vidéo
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    timestamp = 0

    try:
        while True:
            # Frame vidéo
            ret, frame = cap.read()
            if not ret:
                break

            # Traitement de l'image
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            # Détection des points de repère de la main
            timestamp += 1
            result = landmarker.detect_for_video(mp_image, timestamp)

            if result.hand_landmarks:
                hand = result.hand_landmarks[0]
                wrist = hand[0]

                # Calcul des distances relatives pour chaque doigt
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

                # Données pour Unity et scripts
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

                # Données pour Raspberry
                small_data = {
                    "index": round(index1, 1),
                    "middle": round(middle1, 1),
                }

                print("Hand recognized.", end=" ")

                # Applique la fonction sur le dict
                if modifier is not None:
                    full_message = modifier(full_data)
                    small_message = modifier(small_data)

                # Conversion en JSON
                full_message = json.dumps(full_data)
                small_message = json.dumps(small_data)

                # Envoi via UDP
                for type_, ip, port in address:
                    if type_ == "full":
                        message = full_message
                    elif type_ == "small":
                        message = small_message
                    else:
                        raise ValueError(f"Unknown message type: {type_}")

                    try:
                        sock.sendto(message.encode(), (ip, port))
                        print(f"Sent to {ip}:{port}.", end=" ")
                    except socket.gaierror, OSError:
                        print(f"SKIP {ip}:{port} not reachable.")

                print()

    except KeyboardInterrupt:
        print("\nStopping.")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        sock.close()
        print("Clean exit.")
