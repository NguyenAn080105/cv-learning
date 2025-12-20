# 🚗 Vehicle Counting & Classification System using YOLOv8

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![YOLOv8](https://img.shields.io/badge/YOLO-v8-green)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red)
![Status](https://img.shields.io/badge/Status-Development-yellow)

## 📖 Introduction

This project is a computer vision system designed to detect, track, and count vehicles in a specific Region of Interest (ROI). Using a fine-tuned **YOLOv8** model, the system can classify vehicles into 4 categories: **Bus, Car, Motor, and Truck**.

As a 3rd-year student project, my goal was not just to train a model, but to build a complete **Data Processing Pipeline**—handling everything from raw messy datasets to a working inference script.

## ✨ Key Features

* **Custom Object Detection:** Fine-tuned YOLOv8s model on a mixed dataset to detect 4 classes: `bus`, `car`, `motor`, `truck`.
* **Object Tracking:** Implemented **BoT-SORT/ByteTrack** to stably track vehicles across frames.
* **Polygon Zone Counting:** precise counting logic using a Polygon ROI to avoid double-counting or counting parked vehicles.
* **Data Pipeline:** A set of automated scripts to clean, merge, and validate datasets before training.
* **Automated Reporting:** Generates an output video `.mp4` and a text report `.txt` automatically after execution.

## 🛠️ Project Structure

This repo is organized to simulate a standard production environment:

```text
YOLOv8-Vehicle-Counting/
│
├── assets/                  # Demo videos, ROI images, and results
├── configs/                 # Configuration files (tracker.yaml, data.yaml)
├── src/                     # Source code
│   ├── data_preprocessing/  # Scripts for cleaning and preparing data
│   ├── train.py             # Training script
│   └── utils.py             # Helper functions
├── main.py                  # Main inference script
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation