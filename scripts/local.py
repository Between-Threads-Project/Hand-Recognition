from core.hand_scan import start_hand_tracking

start_hand_tracking(
    [
        ("full", "127.0.0.1", 5055),  # Unity
        ("full", "127.0.0.1", 5057),  # Other python
        ("small", "10.0.0.45", 5000),  # Raspberry
    ],
    False,
)
