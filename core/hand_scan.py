import json
import socket
from typing import List, Tuple

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from core.utils import wrist_distance_relative


def start_hand_tracking(address: List[Tuple[str, str, int]]) -> None:
    """
    Démarre la capture de la main et envoie les distances via UDP sur les ports spécifiés.

    Cette fonction initialise la capture vidéo, détecte les points de repère de la main,
    calcule les distances relatives des doigts par rapport au poignet, et envoie ces données
    au format JSON via UDP aux adresses spécifiées.

    Args:
        address: Liste de tuples contenant le type de message, l'adresse IP et le port.
                 Chaque tuple est de la forme (type, ip, port), où :
                 - type: `full` pour envoyer toutes les données, ou `small` pour un sous-ensemble.
                 - ip: Adresse IP de destination.
                 - port: Port de destination.

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
                thumb1 = (wrist_distance_relative(hand, wrist, 4),)
                thumb2 = (wrist_distance_relative(hand, wrist, 3),)
                index1 = (wrist_distance_relative(hand, wrist, 8),)
                index2 = (wrist_distance_relative(hand, wrist, 7),)
                middle1 = (wrist_distance_relative(hand, wrist, 12),)
                middle2 = (wrist_distance_relative(hand, wrist, 11),)
                ring1 = (wrist_distance_relative(hand, wrist, 16),)
                ring2 = (wrist_distance_relative(hand, wrist, 15),)
                pinky1 = (wrist_distance_relative(hand, wrist, 20),)
                pinky2 = (wrist_distance_relative(hand, wrist, 19),)

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
                    "index": index1,
                    "middle": middle1,
                }

                print("Hand recognized.", end=" ")

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

                    sock.sendto(message.encode(), (ip, port))
                    print(f"Sent to {ip}:{port}. ", end=" ")

                print()

    except KeyboardInterrupt:
        print("\nStopping.")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        sock.close()
