# ANPR — Automatic Number Plate Recognition System

A command-line pipeline that detects a vehicle's license plate in an
image, reads the plate text with OCR, and logs every detection to a
local database for later reporting. Built for the **Computer Vision**
course "Build Your Own Project" evaluation.

## Overview

Given a photo (or a folder of photos) of a vehicle, the system:

1. **Detects** the plate region using a Haar Cascade classifier.
2. **Reads** the plate text using Tesseract OCR, after a preprocessing
   chain (denoise → contrast enhancement → adaptive threshold → deskew)
   that makes the crop easier to read.
3. **Logs** every valid detection (plate text, confidence, source
   file, timestamp) into a local SQLite database, queryable later by
   date range.

The whole system runs from the terminal — there is no GUI component.

## Features

- Single-image and batch (folder) detection modes
- Confidence-scored OCR with automatic rejection of low-confidence reads
- Persistent local storage of every detection (SQLite)
- Date-range reporting with CSV export
- Rotating log file for auditing and debugging
- 16 automated unit tests covering every module

## Technologies Used

| Purpose            | Tool / Library                     |
|--------------------|-------------------------------------|
| Language           | Python 3.10+                        |
| Plate detection    | OpenCV (Haar Cascade)               |
| Image preprocessing| OpenCV, NumPy                       |
| OCR                | Tesseract (via `pytesseract`)       |
| Storage            | SQLite (`sqlite3`, standard library)|
| Testing            | pytest                              |
| CLI                | `argparse` (standard library)       |

## Project Structure

```
anpr-system/
├── main.py                  # CLI entry point
├── requirements.txt
├── statement.md             # Problem statement, scope, target users
├── src/
│   ├── config.py            # All tunable constants
│   ├── logger_config.py     # Logging setup
│   ├── preprocessing.py     # Image preprocessing chain
│   ├── plate_detector.py    # Module 1 — plate localisation
│   ├── ocr_engine.py        # Module 2 — text recognition
│   ├── database.py          # Module 3 — persistence & reporting
│   └── pipeline.py          # Orchestrates the three modules above
├── tests/                   # pytest unit tests (16 tests)
├── data/sample_images/      # Sample input image(s) for a quick demo
├── docs/
│   └── DESIGN.md            # Architecture, UML/ER diagrams, dataset & model rationale
├── output/                  # Generated at runtime: database, CSV exports
└── logs/                    # Generated at runtime: rotating log file
```

## Setup

### 1. Prerequisites

- Python 3.10 or later
- Tesseract OCR installed on your system:
  - **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`
  - **macOS:** `brew install tesseract`
  - **Windows:** install from the [Tesseract releases page](https://github.com/UB-Mannheim/tesseract/wiki) and ensure `tesseract.exe` is on your `PATH`

### 2. Clone and install dependencies

```bash
git clone https://github.com/<your-username>/anpr-system.git
cd anpr-system
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Verify Tesseract is reachable

```bash
tesseract --version
```

If this fails, fix your Tesseract installation before continuing — the
OCR module depends on it being on your system `PATH`.

## Usage

### Detect a single image

```bash
python main.py detect --input data/sample_images/sample_car_1.jpg
```

### Batch-process a folder of images

```bash
python main.py batch --input-dir data/sample_images --export output/all_results.csv
```

### Query stored detections by date range

```bash
python main.py report --from 2026-01-01 --to 2026-12-31 --export output/report.csv
```

### View summary statistics

```bash
python main.py stats
```

## Testing

```bash
pip install pytest   # already in requirements.txt
python -m pytest tests/ -v
```

All 16 tests should pass. They cover preprocessing correctness,
detector error handling, OCR output validation, and database
insert/query/export behaviour.

## Using Your Own Images

Drop any clear photo of a vehicle (plate visible, reasonably
front-on) into `data/sample_images/` and run `detect` or `batch` on
it. Detection accuracy depends heavily on lighting, angle, and image
resolution — see `docs/DESIGN.md` for known limitations and possible
improvements.

## License

Submitted as coursework for academic evaluation.
