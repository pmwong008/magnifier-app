# Magnifier App (RPi IoT Project)

## Project Goal
A Python-based magnifier application running on RPi4B, outputting to a TV through HDMI or wireless connection. This project evolves from earlier JS web prototypes into a dedicated IoT device.

## Setup Instructions
### 1. System Requirements
- Raspberry Pi4B
- Python 3.x
- USB webcam or PiCamera
- HDMI cable or wireless display option

### 2. Install Dependencies
```sudo apt update```

```sudo apt install python3-pip```

```pip3 install -r requirements.txt```

## Running
### Development mode (default)
```python3 magnifier.py```
Keyboard shortcuts:
```q``` quit program
```+``` zoom in
```-``` zoom out

### Explicit DEV mode
```MAGNIFIER_ENV=DEV python3 magnifier.py```

### Production mode
```MAGNIFIER_ENV=PROD python3 magnifier.py```