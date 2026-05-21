# Color-Based-Control-Yaboom_Dogzilla

## Introduction

<div align="justify">
This project is a color-based control system for the DOGZILLA S2 robot, utilizing
Python and computer vision with the OpenCV library, allowing the robot to move
autonomously with speed adjustments based on the colors detected from the main
camera (green, purple, blue, yellow, red) and respond with specific motions (forward,
backward, left, right, or stop).
The objective is to demonstrate the integration of OpenCV-based color tracking with
real-time robotic control for future autonomous navigation and AI-enhanced robotics
experiments.
</div>

## System Overview

### Hardware
- Dogzilla S2 Robot
- Computer/Laptop with JupyterLab
  
### Software
- Python 3
- OpenCV (Computer vision library)
- NumPy
- Ipywidgets (GUI for Jupyter Notebook control)
- DOGZILLALib

<img width="672" height="347" alt="image" src="https://github.com/user-attachments/assets/c949997c-e5f5-4213-89c5-077ebc1707cf" />

## Implementation Details
- Color Detection Module: Uses HSV color ranges to detect and classify colors in the
camera frame.
     - Implemented real-time image acquisition using OpenCV’s video capture.
- Motion Control Module: Executes corresponding Dogzilla movement commands.
     - Designed with continuous movement loops with threading for non-blocking
robot control.
- Speed Controller: Provides user-adjustable speed levels (slow, normal, fast) via an
interactive widget.
- Camera Loop: Continuously captures frames and processes them for real-time
navigation.
     - Optimized performance using motion locking and frame skipping to maintain
smoothness.
- User Interface: Displays live camera feed, robot status, and speed control
interfaces.

<img width="541" height="291" alt="image" src="https://github.com/user-attachments/assets/232cc825-df54-44fc-baeb-6f7e7f871e0c" />

## Color to Movements Mapping

<img width="462" height="241" alt="image" src="https://github.com/user-attachments/assets/d85c49b0-daca-4212-9d96-caf8bff9948e" />
