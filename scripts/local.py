import sys
import cv2
sys.path.append("..")

from core.hand_scan import HandScanner

# Configuration UDP
UDP_IP = "127.0.0.1"
UDP_PORT_Unity = 5055
UDP_PORT_Python = 5057

# Initialisation du scanner
scanner = HandScanner(num_hands=1)

# Boucle principale
while True:
    result = scanner.process_frame()
    
    if result and result.hand_landmarks:
        hand = result.hand_landmarks[0]
        data = scanner.extract_hand_data(hand)
        print(data)
        scanner.send_data(data, UDP_IP, UDP_PORT_Unity)
        scanner.send_data(data, UDP_IP, UDP_PORT_Python)
    
    if cv2.waitKey(1) == 27:
        break

scanner.release()
