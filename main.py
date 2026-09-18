#!/usr/bin/env python3
"""
main.py
-------
Command-line entry point for the Automatic Number Plate Recognition
(ANPR) system. Fully CLI-driven — no GUI dependency — per the
assignment's executability requirement.

Usage examples
--------------
    python main.py detect --input data/sample_images/car1.jpg
    python main.py batch  --input-dir data/sample_images --export output/results.csv
    python main.py report --from 2026-01-01 --to 2026-12-31 --export output/report.csv
    python main.py stats
"""

import argparse
import glob
import os
import sys
import time

from src.config import OUTPUT_DIR, SUPPORTED_IMAGE_EXTENSIONS
from src.database import Database
from src.logger_config import get_logger
from src.pipeline import ANPRPipeline

logger = get_logger("main")


def cmd_detect(args):
    pipeline = ANPRPipeline()
    start = time.time()
    try:
        results = pipeline.process_image_file(args.input)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    elapsed = time.time() - start
    if not results:
        print(f"No plates detected in '{args.input}'.")
    for r in results:
        status = "VALID" if r.is_valid else "low-confidence, not stored"
        print(f"  Plate: '{r.plate_text}'  confidence={r.confidence:.1f}  "
              f"bbox={r.bbox}  [{status}]")
    print(f"Processed in {elapsed:.2f}s")
    return 0


def cmd_batch(args):
    pipeline = ANPRPipeline()
    files = [
        f for f in sorted(glob.glob(os.path.join(args.input_dir, "*")))
        if f.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)
    ]
    if not files:
        print(f"No supported images found in '{args.input_dir}'.", file=sys.stderr)
        return 1

    total_valid = 0
    for path in files:
        try:
            results = pipeline.process_image_file(path)
        except FileNotFoundError as exc:
            logger.error(str(exc))
            continue
        valid = [r for r in results if r.is_valid]
        total_valid += len(valid)
        print(f"{os.path.basename(path)}: {len(results)} candidate(s), "
              f"{len(valid)} valid read(s)")

    print(f"\nBatch complete: {len(files)} image(s) processed, "
          f"{total_valid} valid plate(s) stored.")

    if args.export:
        db = Database()
        db.export_to_csv(db.all_records(), args.export)
        print(f"All records exported to {args.export}")
    return 0


def cmd_report(args):
    db = Database()
    records = db.query_between(args.date_from, args.date_to)
    if not records:
        print("No records found in that date range.")
        return 0

    print(f"{'ID':<5}{'Plate':<15}{'Confidence':<12}{'Source':<30}{'Detected At'}")
    print("-" * 90)
    for r in records:
        print(f"{r.id:<5}{r.plate_text:<15}{r.confidence:<12.1f}"
              f"{os.path.basename(r.source_file):<30}{r.detected_at}")

    if args.export:
        db.export_to_csv(records, args.export)
        print(f"\nExported {len(records)} record(s) to {args.export}")
    return 0


def cmd_stats(args):
    db = Database()
    records = db.all_records()
    print(f"Total detections stored: {len(records)}")
    if records:
        avg_conf = sum(r.confidence for r in records) / len(records)
        print(f"Average OCR confidence: {avg_conf:.1f}")
        print(f"Most recent detection: {records[-1].plate_text} at {records[-1].detected_at}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="anpr",
        description="Automatic Number Plate Recognition — CLI pipeline",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_detect = sub.add_parser("detect", help="Run detection on a single image")
    p_detect.add_argument("--input", required=True, help="Path to an image file")
    p_detect.set_defaults(func=cmd_detect)

    p_batch = sub.add_parser("batch", help="Run detection on every image in a folder")
    p_batch.add_argument("--input-dir", required=True, help="Folder of images")
    p_batch.add_argument("--export", help="Optional CSV path to export all stored records")
    p_batch.set_defaults(func=cmd_batch)

    p_report = sub.add_parser("report", help="Query stored detections by date range")
    p_report.add_argument("--from", dest="date_from", required=True, help="YYYY-MM-DD")
    p_report.add_argument("--to", dest="date_to", required=True, help="YYYY-MM-DD")
    p_report.add_argument("--export", help="Optional CSV path to export the results")
    p_report.set_defaults(func=cmd_report)

    p_stats = sub.add_parser("stats", help="Show summary statistics")
    p_stats.set_defaults(func=cmd_stats)

    return parser


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
