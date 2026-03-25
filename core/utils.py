import math
import random
import time


def wrist_distance_relative(hand, wrist, tip_index: int) -> float:
    """
    Calculates the normalized distance between the wrist and a finger, relative to hand width.

    This function computes the distance between the wrist and a specific finger landmark,
    normalizes it using the distance between the index and pinky fingers as a reference,
    and remaps the result to the range [-1, 1] for stability.

    Args:
        hand: A list of hand landmarks, where each landmark is an object with x and y attributes.
        wrist: The wrist landmark, an object with x and y attributes.
        tip_index: The index of the finger landmark to compute the distance for.

    Returns:
        float: The normalized distance in the range [-1, 1].
    """
    tip = hand[tip_index]

    # Distance poignet <-> doigt
    dx = tip.x - wrist.x
    dy = tip.y - wrist.y
    dist = math.sqrt(dx * dx + dy * dy)

    # Distance de référence
    index_o = hand[5]  # Index
    pinky_o = hand[17]  # Auriculaire

    dx_ref = index_o.x - pinky_o.x
    dy_ref = index_o.y - pinky_o.y
    ref = math.sqrt(dx_ref * dx_ref + dy_ref * dy_ref)

    if ref < 1e-6:
        return 0.0

    dist = dist / ref

    dist = min(2.0, dist)

    # [0, 2] vers [-1, 1]
    dist = dist - 1.0

    return dist


def create_perlin_layer():
    """
    Creates a Perlin noise layer function to apply smooth random motion to hand data.

    This function generates a closure that applies Perlin-like noise to the input data,
    simulating natural motion. The noise parameters (speed, phase, and amplitude) are
    randomly initialized for each key in the input data.

    Returns:
        A function that takes a dictionary of float values and returns a modified dictionary
        with Perlin noise applied to each value.
    """
    speed: dict[str, float] = {}
    phase: dict[str, float] = {}
    amplitude: dict[str, float] = {}

    def clamp(v: float) -> float:
        """Clamps a value to the range [-1, 1]."""
        return max(-1, min(1, v))

    def perlin_like(t: float, p: float) -> float:
        """
        Generates a Perlin-like noise value.

        Args:
            t: Time parameter.
            p: Phase parameter.

        Returns:
            A noise value in the range [-1, 1].
        """
        return (
            math.sin(t + p) * 0.6
            + math.sin(t * 0.5 + p * 2.1) * 0.3
            + math.sin(t * 0.25 + p * 0.7) * 0.1
        )

    def perlin_layer(message: dict[str, float]):
        """
        Applies Perlin noise to the input data.

        Args:
            message: A dictionary of float values representing hand data.

        Returns:
            A dictionary with Perlin noise applied to each value.
        """
        t = time.time()
        agent: dict[str, float] = {}

        for f in message.keys():
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

    return perlin_layer

def low_pass_filter(alpha: float = 0.2, deadzone: float = 0.02):
    prev = {}

    def filter_fn(data: dict[str, float]) -> dict[str, float]:
        nonlocal prev

        if not prev:
            prev = data.copy()
            return data

        filtered = {}
        for key, value in data.items():
            prev_val = prev.get(key, value)

            # 1️⃣ calcul du filtre
            new_val = alpha * value + (1 - alpha) * prev_val

            # 2️⃣ deadzone (APRÈS)
            if abs(new_val - prev_val) < deadzone:
                new_val = prev_val

            filtered[key] = new_val

        prev = filtered
        return filtered

    return filter_fn