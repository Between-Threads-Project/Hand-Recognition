from core.hand_scan import start_hand_tracking

start_hand_tracking(
    [
        ("full", "127.0.0.1", 5056),  # Unity
        ("small", "10.0.0.45", 5001),  # Raspberry
    ],
    True,
)
