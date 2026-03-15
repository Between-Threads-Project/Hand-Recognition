import sys
import cv2
sys.path.append("..")

from core.hand_scan import HandScanner

# Configuration UDP
UDP_IP = "127.0.0.1"
UDP_PORT_Droit = 5060
UDP_PORT_Gauche = 5059

# Initialisation du scanner
scanner = HandScanner(num_hands=2)

# Boucle principale
while True:
    result = scanner.process_frame()
    
    if result and result.hand_landmarks:
        for i, hand in enumerate(result.hand_landmarks):
            data = scanner.extract_hand_data(hand)
            print(data)
            
            if result.handedness and len(result.handedness) > i:
                handedness = result.handedness[i][0].category_name
                
                if handedness == "Right":
                    scanner.send_data(data, UDP_IP, UDP_PORT_Droit)
                elif handedness == "Left":
                    scanner.send_data(data, UDP_IP, UDP_PORT_Gauche)
    
    if cv2.waitKey(1) == 27:
        break

scanner.release()
