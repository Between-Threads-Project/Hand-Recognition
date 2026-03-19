import math
import random
import time

# table de gradients pseudo-aléatoires
gradients = {}

speed = {}

# phase de chaque doigt
phase = {}

# amplitude
amplitude = {}


def clamp(v: float) -> float:
    return max(-1, min(1, v))


def perlin_like(t: float, p: float) -> float:
    return (
        math.sin(t + p) * 0.6
        + math.sin(t * 0.5 + p * 2.1) * 0.3
        + math.sin(t * 0.25 + p * 0.7) * 0.1
    )


def perlin_layer(message: dict[str, float]) -> dict[str, float]:

    fingers = message.keys()
    t = time.time()

    agent = {}

    for f in fingers:
        if f not in speed:
            speed[f] = random.uniform(1, 6)
            phase[f] = random.uniform(0, 1000)
            amplitude[f] = random.uniform(-5, 5)

        motion = perlin_like(t * speed[f], phase[f])
        motion *= amplitude[f]

        follow = message[f] * 0.25

        value = motion + follow

        agent[f] = clamp(value)

    return agent
