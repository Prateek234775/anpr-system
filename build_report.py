"""
build_report.py
----------------
One-off script that generates docs/Project_Report.pdf from the design
content in this repo. Not part of the runtime application — this is a
documentation build tool, run once (or whenever the report needs
regenerating) with: python build_report.py
"""

import datetime
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ASSETS = "docs/assets"
OUT_PATH = "docs/Project_Report.pdf"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="H1Custom", parent=styles["Heading1"],
                           spaceBefore=18, spaceAfter=8, textColor=colors.HexColor("#1F3A5F")))
styles.add(ParagraphStyle(name="H2Custom", parent=styles["Heading2"],
                           spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#2A4D69")))
styles.add(ParagraphStyle(name="BodyCustom", parent=styles["Normal"],
                           fontSize=10.3, leading=15, spaceAfter=8))
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"],
                           fontSize=26, leading=32, textColor=colors.HexColor("#1F3A5F")))
styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"],
                           fontSize=13, alignment=TA_CENTER, spaceAfter=6))
styles.add(ParagraphStyle(name="Caption", parent=styles["Normal"],
                           fontSize=9, alignment=TA_CENTER, textColor=colors.grey, spaceAfter=14))

story = []

# ---------------------------------------------------------------------
# 1. Cover Page
# ---------------------------------------------------------------------
story.append(Spacer(1, 5 * cm))
story.append(Paragraph("Automatic Number Plate Recognition (ANPR) System", styles["CoverTitle"]))
story.append(Spacer(1, 0.6 * cm))
story.append(Paragraph("A Command-Line Computer Vision Pipeline for Plate Detection and Recognition",
                        styles["CoverSub"]))
story.append(Spacer(1, 3 * cm))
story.append(Paragraph("Course: Computer Vision", styles["CoverSub"]))
story.append(Paragraph("Submission: VITyarthi — Build Your Own Project", styles["CoverSub"]))
story.append(Paragraph(f"Date: {datetime.date.today().strftime('%B %d, %Y')}", styles["CoverSub"]))
story.append(PageBreak())


def h1(text):
    story.append(Paragraph(text, styles["H1Custom"]))


def h2(text):
    story.append(Paragraph(text, styles["H2Custom"]))


def body(text):
    story.append(Paragraph(text, styles["BodyCustom"]))


def bullets(items):
    story.append(ListFlowable(
        [ListItem(Paragraph(i, styles["BodyCustom"])) for i in items],
        bulletType="bullet", start="•",
    ))
    story.append(Spacer(1, 6))


def figure(path, caption, width=15 * cm):
    img = Image(path)
    ratio = img.imageHeight / float(img.imageWidth)
    img.drawWidth = width
    img.drawHeight = width * ratio
    story.append(img)
    story.append(Paragraph(caption, styles["Caption"]))


def table(headers, rows, col_widths=None):
    data = [headers] + rows
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2A4D69")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FA")]),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))


# ---------------------------------------------------------------------
# 2. Introduction
# ---------------------------------------------------------------------
h1("2. Introduction")
body(
    "This report documents an Automatic Number Plate Recognition (ANPR) system built "
    "as the 'Build Your Own Project' submission for the Computer Vision course. The "
    "project applies core computer vision concepts &mdash; multi-scale object detection, "
    "image preprocessing, and optical character recognition &mdash; to a practical "
    "problem: identifying and logging vehicle license plates from photographs, entirely "
    "from the command line."
)

# ---------------------------------------------------------------------
# 3. Problem Statement
# ---------------------------------------------------------------------
h1("3. Problem Statement")
body(
    "Manual recording of vehicle license plates at parking facilities, toll booths, or "
    "campus gates is slow and error-prone. This project automates that task: given a "
    "photograph of a vehicle, the system detects the plate region, reads its text, and "
    "stores the result in a searchable local database."
)
h2("Target Users")
bullets([
    "A parking or campus security operator who needs a quick, searchable record of vehicle entries.",
    "A CV/ML student or developer wanting a reference pipeline combining classical detection, OCR, and structured storage.",
])
h2("Scope Boundaries")
body(
    "Explicitly out of scope: live video-stream processing from a camera feed, "
    "multi-country plate format normalisation, and any graphical user interface. These "
    "were excluded to keep the project's depth aligned with a single-course evaluation "
    "while still delivering a complete, working pipeline."
)

# ---------------------------------------------------------------------
# 4. Functional Requirements
# ---------------------------------------------------------------------
h1("4. Functional Requirements")
table(
    ["ID", "Requirement"],
    [
        ["FR1", "Accept a single image file or a directory of image files as input."],
        ["FR2", "Detect candidate license-plate regions within each image."],
        ["FR3", "Extract and clean plate text from each detected region using OCR."],
        ["FR4", "Reject OCR results below a configurable confidence/length threshold."],
        ["FR5", "Persist every valid detection (text, confidence, source, timestamp) to a local database."],
        ["FR6", "Allow querying stored detections within a given date range."],
        ["FR7", "Allow exporting query results and full batch results to CSV."],
        ["FR8", "Report summary statistics: total detections, average confidence, most recent detection."],
    ],
    col_widths=[1.5 * cm, 14 * cm],
)

# ---------------------------------------------------------------------
# 5. Non-Functional Requirements
# ---------------------------------------------------------------------
h1("5. Non-Functional Requirements")
table(
    ["Category", "Requirement"],
    [
        ["Performance", "A single detect+OCR cycle completes in under 1 second on a standard CPU."],
        ["Reliability", "Low-confidence OCR results are flagged and excluded from storage."],
        ["Maintainability", "All tunable values live in one config module; each stage is independently testable."],
        ["Scalability", "The batch command processes any number of images without code changes."],
        ["Logging/Monitoring", "Every run writes structured, timestamped logs to a rotating log file."],
        ["Resource Efficiency", "Logs rotate at 1 MB; storage is a single lightweight SQLite file."],
        ["Usability", "All functionality is reachable via four self-documenting CLI subcommands."],
    ],
    col_widths=[3.5 * cm, 12 * cm],
)

# ---------------------------------------------------------------------
# 6. System Architecture
# ---------------------------------------------------------------------
h1("6. System Architecture")
body(
    "The system is layered into a thin CLI layer, a pipeline orchestrator, three core "
    "modules (detection, OCR, storage), and a persistence layer. This separation means "
    "each stage can be unit-tested independently and the pipeline can be reused by a "
    "different front end in the future without modification."
)
figure(f"{ASSETS}/architecture_diagram.png", "Figure 1: System architecture of the ANPR pipeline.")

# ---------------------------------------------------------------------
# 7. Design Diagrams
# ---------------------------------------------------------------------
story.append(PageBreak())
h1("7. Design Diagrams")

h2("7.1 Use Case Diagram")
body(
    "The operator interacts with the system through five use cases: detecting a plate "
    "in a single image, batch-processing a folder, querying detections by date range, "
    "exporting results to CSV, and viewing summary statistics."
)
body(
    "<b>Actor:</b> Operator &nbsp;&nbsp; <b>Use cases:</b> Detect plate in single image; "
    "Batch-process a folder of images (includes: Detect plate in single image); Query "
    "detections by date range; Export results to CSV (included by: Query detections); "
    "View summary statistics."
)

h2("7.2 Workflow / Process Flow Diagram")
figure(f"{ASSETS}/workflow_diagram.png", "Figure 2: Process flow for single-image detection.", width=9 * cm)

h2("7.3 Class / Component Diagram")
body("Core classes and their relationships:")
bullets([
    "<b>PlateDetector</b> &mdash; wraps the Haar Cascade classifier; <i>detect(frame) -&gt; List[PlateCandidate]</i>",
    "<b>PlateCandidate</b> &mdash; a detected bounding box plus the cropped image region",
    "<b>OCREngine</b> &mdash; wraps Tesseract; <i>read_plate(image) -&gt; OCRResult</i>",
    "<b>OCRResult</b> &mdash; recognised text, confidence score, validity flag",
    "<b>Database</b> &mdash; SQLite wrapper; insert / query_between / all_records / export_to_csv",
    "<b>DetectionRecord</b> &mdash; one stored row (id, plate_text, confidence, source_file, detected_at)",
    "<b>ANPRPipeline</b> &mdash; orchestrates PlateDetector, OCREngine and Database for one frame",
])
body("<i>ANPRPipeline &rarr; PlateDetector, ANPRPipeline &rarr; OCREngine, ANPRPipeline &rarr; Database.</i> "
     "The full Mermaid class diagram is rendered in <b>docs/DESIGN.md</b> on GitHub.")

h2("7.4 Sequence Diagram — detect command")
body(
    "1. Operator runs <font face='Courier'>python main.py detect --input car.jpg</font>.<br/>"
    "2. main.py calls <font face='Courier'>ANPRPipeline.process_image_file(path)</font>.<br/>"
    "3. Pipeline calls <font face='Courier'>PlateDetector.detect(frame)</font>, receiving candidate regions.<br/>"
    "4. For each candidate: preprocess the crop, call <font face='Courier'>OCREngine.read_plate()</font>.<br/>"
    "5. If the OCR result is valid, call <font face='Courier'>Database.insert_detection()</font>.<br/>"
    "6. Pipeline returns all results to main.py, which prints them with the elapsed time."
)
body("The full Mermaid sequence diagram is rendered in <b>docs/DESIGN.md</b> on GitHub.")

h2("7.5 Database Design / ER Diagram")
body(
    "A single flat table is sufficient at this scope &mdash; each row is one independent "
    "detection event with no relationships to other entities."
)
table(
    ["Column", "Type", "Description"],
    [
        ["id", "INTEGER PK", "Auto-incrementing primary key"],
        ["plate_text", "TEXT", "Cleaned, recognised plate text"],
        ["confidence", "REAL", "Average OCR confidence (0-100)"],
        ["source_file", "TEXT", "Path of the source image"],
        ["detected_at", "TEXT (ISO 8601)", "Timestamp of detection"],
    ],
    col_widths=[3 * cm, 3.5 * cm, 8.5 * cm],
)

# ---------------------------------------------------------------------
# 8. Design Decisions & Rationale
# ---------------------------------------------------------------------
story.append(PageBreak())
h1("8. Design Decisions & Rationale")
h2("8.1 Detector: Haar Cascade over a deep-learning detector")
body(
    "A Haar Cascade (<font face='Courier'>haarcascade_russian_plate_number.xml</font>, "
    "shipped with OpenCV) was chosen over a YOLO-based detector. It requires no external "
    "weight download or training dataset, runs fast on CPU, and directly demonstrates "
    "classical CV concepts (multi-scale sliding-window detection with Haar features) "
    "taught in the course. A deep-learning detector was considered but rejected for this "
    "scope since it would add a heavy PyTorch dependency and require either a labelled "
    "dataset or a pretrained weights file to be fetched from outside the repository."
)
h2("8.2 OCR: Tesseract over a custom-trained classifier")
body(
    "Tesseract is a mature, dependency-light OCR engine that performs reliably on "
    "printed alphanumeric text once given a well-preprocessed crop. Training a custom "
    "character-recognition CNN was considered but rejected: it would require a labelled "
    "character dataset disproportionate to this project's scope, for marginal accuracy "
    "gain over Tesseract on clean, preprocessed crops."
)
h2("8.3 Storage: SQLite over flat-file logging")
body(
    "SQLite allows detections to be filtered by date and exported without re-parsing "
    "text files, at zero deployment cost (no external database server, just a single "
    "file) &mdash; appropriate for a single-user CLI tool."
)

# ---------------------------------------------------------------------
# 9. Implementation Details
# ---------------------------------------------------------------------
h1("9. Implementation Details")
body("The pipeline is implemented as eight cooperating Python modules:")
table(
    ["Module", "Responsibility"],
    [
        ["config.py", "Centralised paths and tunable parameters"],
        ["logger_config.py", "Rotating file + console logging setup"],
        ["preprocessing.py", "Grayscale, denoise, CLAHE contrast, adaptive threshold, deskew"],
        ["plate_detector.py", "Haar Cascade-based plate localisation"],
        ["ocr_engine.py", "Tesseract-based text extraction with confidence scoring"],
        ["database.py", "SQLite persistence, date-range queries, CSV export"],
        ["pipeline.py", "Orchestrates detector -&gt; preprocessing -&gt; OCR -&gt; database for one frame"],
        ["main.py", "argparse-based CLI: detect / batch / report / stats subcommands"],
    ],
    col_widths=[4 * cm, 11 * cm],
)
body(
    "Preprocessing (Section 8) applies, in order: grayscale conversion, bilateral "
    "denoising, CLAHE contrast enhancement, adaptive Gaussian thresholding, and a "
    "skew-angle correction based on the minimum-area bounding rectangle of the "
    "foreground pixels &mdash; each implemented as an independent, unit-tested function."
)

# ---------------------------------------------------------------------
# 10. Screenshots / Results
# ---------------------------------------------------------------------
story.append(PageBreak())
h1("10. Screenshots / Results")
body("The following terminal captures show the CLI running against the sample images in "
     "<font face='Courier'>data/sample_images/</font>.")
figure(f"{ASSETS}/screenshot_detect.png", "Figure 3: Single-image detection.")
figure(f"{ASSETS}/screenshot_batch.png", "Figure 4: Batch processing three images with CSV export.")
figure(f"{ASSETS}/screenshot_report.png", "Figure 5: Reporting stored detections by date range.")
figure(f"{ASSETS}/screenshot_stats.png", "Figure 6: Summary statistics.")

# ---------------------------------------------------------------------
# 11. Testing Approach
# ---------------------------------------------------------------------
story.append(PageBreak())
h1("11. Testing Approach")
body(
    "Two complementary levels of evaluation were used. First, <b>unit-level "
    "correctness</b>: 16 automated pytest tests cover preprocessing output shape/dtype, "
    "detector error handling on invalid input, OCR text/confidence extraction on "
    "rendered text, and database insert/query/export behaviour &mdash; each module tested "
    "in isolation with synthetic inputs so a regression is caught without needing a full "
    "image dataset."
)
figure(f"{ASSETS}/screenshot_tests.png", "Figure 7: Full test suite run — 16/16 passing.")
body(
    "Second, <b>end-to-end pipeline evaluation</b> on sample images, measuring: "
    "detection rate (images where a plate region was found / total images), recognition "
    "accuracy (OCR text exactly matching ground truth / images where a plate was "
    "detected), and average processing time per image (printed by the CLI itself)."
)

# ---------------------------------------------------------------------
# 12. Challenges Faced
# ---------------------------------------------------------------------
h1("12. Challenges Faced")
bullets([
    "<b>Character confusion in OCR:</b> Tesseract occasionally confused visually similar "
    "characters (e.g. '0' read as 'O') on the synthetic test plates &mdash; addressed "
    "partially via the character whitelist in the Tesseract config, though it remains a "
    "known limitation worth measuring against a larger real-image test set.",
    "<b>Detector sensitivity to plate size/angle:</b> the Haar Cascade's "
    "<font face='Courier'>minSize</font> and <font face='Courier'>minNeighbors</font> "
    "parameters required tuning to balance missed detections against false positives on "
    "cluttered backgrounds.",
    "<b>Keeping the pipeline testable without a labelled dataset:</b> resolved by "
    "designing each stage (preprocessing, detection, OCR, storage) to be independently "
    "unit-testable with synthetic inputs, decoupling code correctness from dataset "
    "availability.",
])

# ---------------------------------------------------------------------
# 13. Learnings & Key Takeaways
# ---------------------------------------------------------------------
h1("13. Learnings & Key Takeaways")
bullets([
    "Classical CV techniques (Haar Cascades, adaptive thresholding, deskewing) remain "
    "practical and fast for well-scoped detection problems, without requiring GPU "
    "infrastructure.",
    "Preprocessing quality has an outsized effect on OCR accuracy &mdash; contrast "
    "enhancement and deskewing meaningfully improved recognised text over raw crops.",
    "Designing the pipeline as small, single-responsibility modules made unit testing "
    "straightforward and made it easy to reason about where a misdetection actually "
    "occurred (localisation vs. recognition vs. storage).",
])

# ---------------------------------------------------------------------
# 14. Future Enhancements
# ---------------------------------------------------------------------
h1("14. Future Enhancements")
bullets([
    "Replace the Haar Cascade with a YOLO-based detector for higher recall on angled or "
    "partially obscured plates.",
    "Add a confidence-weighted ensemble of multiple OCR passes (different "
    "preprocessing variants) to reduce character-confusion errors.",
    "Add live video-stream support with frame-skipping for near-real-time use.",
    "Add a lightweight web dashboard on top of the existing Database module for "
    "non-CLI users.",
])

# ---------------------------------------------------------------------
# 15. References
# ---------------------------------------------------------------------
h1("15. References")
bullets([
    "OpenCV Documentation &mdash; Cascade Classifier: https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html",
    "Tesseract OCR Documentation: https://tesseract-ocr.github.io/",
    "pytesseract (Python wrapper): https://pypi.org/project/pytesseract/",
    "SQLite Documentation: https://www.sqlite.org/docs.html",
    "Kaggle &mdash; Car License Plate Detection Dataset: https://www.kaggle.com/datasets/andrewmvd/car-plate-detection",
])

doc = SimpleDocTemplate(
    OUT_PATH, pagesize=A4,
    topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
    title="ANPR System — Project Report",
)
doc.build(story)
print(f"Report written to {OUT_PATH}")
