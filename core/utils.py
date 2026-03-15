import math

def wrist_distance_relative(hand, wrist, tip_index):
    """
    Distance poignet -> doigt
    normalisée par la distance index_tip <-> pinky_tip
    """
    tip = hand[tip_index]

    # distance wrist -> doigt
    dx = tip.x - wrist.x
    dy = tip.y - wrist.y
    dist = math.sqrt(dx * dx + dy * dy)

    # distance de référence (largeur de la main)
    index_o = hand[5]
    pinky_o = hand[17]

    dx_ref = index_o.x - pinky_o.x
    dy_ref = index_o.y - pinky_o.y
    ref = math.sqrt(dx_ref * dx_ref + dy_ref * dy_ref)

    if ref < 1e-6:
        return 0

    # normalisation
    dist = dist / ref

    # clamp pour stabilité
    dist = min(2.0, dist)

    # remap [0,2] -> [-1,1]
    dist = dist - 1.0

    return dist
