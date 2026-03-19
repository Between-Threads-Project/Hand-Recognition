import json
import math
import random
import socket
import time

# =========================
# UDP CONFIG
# =========================

INPUT_PORT = 5057
OUTPUT_PORT = 5056
UDP_IP = "127.0.0.1"

sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_in.bind((UDP_IP, INPUT_PORT))

sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Perlin Agent listening on", INPUT_PORT)
print("Sending to Unity on", OUTPUT_PORT)

# =========================
# FINGERS
# =========================

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

# =========================
# PERLIN PARAMETERS
# =========================

# vitesse du mouvement
speed = {}

# phase de chaque doigt
phase = {}

# amplitude
amplitude = {}

for f in fingers:
    speed[f] = random.uniform(1, 3)
    phase[f] = random.uniform(0, 1000)
    amplitude[f] = random.uniform(0.4, 0.8)

# =========================
# UTILS
# =========================


def clamp(v):
    return max(-1, min(1, v))


# "fake perlin" très léger
# sinus combinés = mouvement organique
def perlin_like(t, p):

    return (
        math.sin(t + p) * 0.6
        + math.sin(t * 0.5 + p * 2.1) * 0.3
        + math.sin(t * 0.25 + p * 0.7) * 0.1
    )


# =========================
# MAIN LOOP
# =========================

while True:
    # reçoit ta main
    data_bytes, addr = sock_in.recvfrom(4096)

    try:
        text = data_bytes.decode()
        hand = json.loads(text)
    except Exception:
        continue

    t = time.time()

    agent = {}

    for f in fingers:
        # mouvement perlin autonome
        motion = perlin_like(t * speed[f], phase[f])

        motion *= amplitude[f]

        # attraction légère vers ta main
        follow = hand[f] * 0.25

        value = motion + follow

        agent[f] = clamp(value)

    message = json.dumps(agent)
    print(message)

    sock_out.sendto(message.encode(), (UDP_IP, OUTPUT_PORT))
