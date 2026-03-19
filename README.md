# Hand Recognition

Hand tracking and gesture recognition module using MediaPipe. This module captures hand landmarks in real-time, computes relative finger distances normalized to hand size, and transmits the data via UDP for integration with external control systems.

## Features

- **Real-time Hand Tracking**: Uses MediaPipe's hand landmark detection to capture 21 hand landmarks per frame
- **Normalized Distance Calculation**: Computes finger distances relative to hand width (index-to-pinky distance) and remaps to [-1, 1] range
- **UDP Data Transmission**: Sends structured JSON data to configurable endpoints
- **Dual Output Modes**: Supports both full hand data (10 values) and simplified data (2 values) for different use cases

## Installation

### 1. Clone the repo

```bash
cd ~
git clone https://github.com/Between-Threads-Project/RaspberryPi-Software
cd RaspberryPi-Software
```

## 2. Install dependencies with uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

### 3. Run a script

```bash
uv run python -m scripts.local
```

This sends:
- Full hand data to `127.0.0.1:5055` (Unity)
- Full hand data to `127.0.0.1:5057` (Python scripts)
- Simplified data to `RASPBERRY_IP:5000` (configure target IP)

## Data Format

### Full Data Structure (Unity/Python Consumers)

```json
{
  "thumb1": [0.45],      // Tip of thumb (landmark 4)
  "thumb2": [0.32],      // Second joint of thumb (landmark 3)
  "index1": [0.87],      // Tip of index finger (landmark 8)
  "index2": [0.65],      // Second joint of index (landmark 7)
  "middle1": [0.92],     // Tip of middle finger (landmark 12)
  "middle2": [0.71],     // Second joint of middle (landmark 11)
  "ring1": [0.78],       // Tip of ring finger (landmark 16)
  "ring2": [0.56],       // Second joint of ring (landmark 15)
  "pinky1": [0.63],      // Tip of pinky finger (landmark 20)
  "pinky2": [0.41]       // Second joint of pinky (landmark 19)
}
```

All distances are normalized relative to hand width (distance between index base and pinky base) and remapped to the [-1, 1] range where:
- `-1` represents a fully closed finger (touching wrist)
- `1` represents maximum extension
- `0` represents the reference hand width

### Simplified Data Structure (Raspberry Pi)

```json
{
  "index": [0.87],       // Tip of index finger only
  "middle": [0.92]       // Tip of middle finger only
}
```

## MediaPipe Hand Landmark Reference

```
        8   12   16   20
        |    |    |    |
        7   11   15   19
        |    |    |    |
        6   10   14   18
        |    |    |    |
        5    9   13   17
        \    |    |   /
               0
             Wrist
```

## Configuration

Modify the target addresses in the script files:

```python
# In scripts/local.py or scripts/remote.py
start_hand_tracking([
    ("full", "127.0.0.1", 5055),    # Unity application
    ("full", "127.0.0.1", 5057),    # Python consumer scripts
    ("small", "192.168.1.100", 5000), # Raspberry Pi
])
```

## Technical Details

### Distance Calculation

The `wrist_distance_relative()` function in `core/utils.py`:
1. Calculates Euclidean distance between wrist and target landmark
2. Normalizes by hand width (distance between index base and pinky base)
3. Clamps to maximum of 2.0 (twice hand width)
4. Remaps from [0, 2] range to [-1, 1] range

### Network Protocol

- **Transport**: UDP for low-latency transmission
- **Format**: JSON-encoded strings
- **Frequency**: ~30fps (depends on camera and system performance)

## Dependencies

- Python 3.14+
- MediaPipe 0.10.32+
- OpenCV 4.13.0+

## License

MIT License - See [LICENSE.md](LICENSE.md) for details
