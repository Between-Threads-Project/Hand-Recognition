import sys
import json
import math
import random
import socket
import time

sys.path.append("..")

# Configuration UDP
INPUT_PORT = 5057
OUTPUT_PORT = 5056
UDP_IP = "127.0.0.1"

sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_in.bind((UDP_IP, INPUT_PORT))

sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Perlin Agent listening on", INPUT_PORT)
print("Sending to Unity on", OUTPUT_PORT)

# Doigts
fingers = [
    "thumb1",
    "thumb2",
    "index1",
    "index2",
    "middle1",
    "middle2",
    "ring1",
    "ring2",
    "pinky1",
    "pinky2",
]

# Paramètres Perlin
speed = {}
phase = {}
amplitude = {}

for f in fingers:
    speed[f] = random.uniform(1, 3)
    phase[f] = random.uniform(0, 1000)
    amplitude[f] = random.uniform(0.4, 0.8)

# Fonctions utilitaires
def clamp(v):
    return max(-1, min(1, v))

def perlin_like(t, p):
    return (
        math.sin(t + p) * 0.6
        + math.sin(t * 0.5 + p * 2.1) * 0.3
        + math.sin(t * 0.25 + p * 0.7) * 0.1
    )

# Boucle principale
while True:
    data_bytes, addr = sock_in.recvfrom(4096)

    try:
        text = data_bytes.decode()
        hand = json.loads(text)
    except Exception:
        continue

    t = time.time()
    agent = {}

    for f in fingers:
        motion = perlin_like(t * speed[f], phase[f])
        motion *= amplitude[f]
        follow = hand[f] * 0.25
        value = motion + follow
        agent[f] = clamp(value)

    message = json.dumps(agent)
    print(message)
    sock_out.sendto(message.encode(), (UDP_IP, OUTPUT_PORT))
