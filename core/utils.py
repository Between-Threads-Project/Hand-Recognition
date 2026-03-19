import math


def wrist_distance_relative(hand, wrist, tip_index: int) -> float:
    """
    Calcule la distance normalisée entre le poignet et un doigt, relative à la largeur de la main.

    Cette fonction normalise la distance entre le poignet et un doigt spécifique en utilisant
    la distance entre l'index et l'auriculaire comme référence. La valeur résultante est
    ensuite remappée dans l'intervalle `[-1, 1]`.

    Args:
        hand: Unknown.
        wrist: Unknown.
        tip_index: Index du doigt pour lequel calculer la distance.

    Returns:
        float: Distance normalisée et remappée dans l'intervalle [-1, 1].
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
