# Problem Statement

Manual recording of vehicle license plates — at parking facilities,
toll booths, or campus gates — is slow and error-prone. An automated
system that can detect a plate in an image and read its text removes
that manual step and creates a searchable log of vehicle movement.

## Scope

This project implements a command-line **Automatic Number Plate
Recognition (ANPR)** pipeline that:

- Accepts a single image or a folder of images as input
- Detects the license plate region within each image
- Extracts the plate text via OCR
- Stores every valid detection in a local database
- Supports querying and exporting detections by date range

**Out of scope:** real-time video stream processing from a live
camera feed, multi-country plate format normalisation, and a
graphical user interface — all explicitly excluded to keep the
project's scope aligned with a single-course evaluation.

## Target Users

- A parking or campus security operator who needs a quick record of
  which vehicles entered on a given day
- A developer/student wanting a reference CV pipeline that combines
  classical detection (Haar Cascades), OCR, and structured storage

## High-Level Features

1. **Plate Detection** — locate the plate region in an image using a
   Haar Cascade classifier
2. **Text Recognition** — preprocess the cropped region and run OCR to
   extract the plate number, with a confidence threshold to reject
   unreliable reads
3. **Detection Logging & Reporting** — persist every valid detection
   with a timestamp, and allow filtering/exporting past detections by
   date range
