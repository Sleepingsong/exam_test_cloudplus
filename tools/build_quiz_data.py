from __future__ import annotations

import asyncio
import json
import math
import re
import shutil
import subprocess
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image
from winsdk.windows.graphics.imaging import BitmapDecoder
from winsdk.windows.media.ocr import OcrEngine
from winsdk.windows.storage import FileAccessMode, StorageFile

from enrich_explanations import build_choice_explanation, build_question_explanation


ROOT = Path(__file__).resolve().parents[1]
QUESTION_DIR = ROOT / "Question"
TMP_DIR = ROOT / "tmp" / "pdfs" / "rendered"
ASSET_QUESTION_DIR = ROOT / "assets" / "questions"
ASSET_ANSWER_DIR = TMP_DIR / "answer-crops"
DATA_DIR = ROOT / "data"
OUTPUT_JSON = DATA_DIR / "questions.json"

PDF_PATTERN = re.compile(r"cloud_quiz(0[1-9]|1[0-2])\.pdf$", re.IGNORECASE)
OPTION_LABELS = tuple("ABCDEFGH")

MANUAL_CHOICE_FALLBACKS = {
    "cloud_quiz01_q018": [
        ("A", "WAF"),
        ("B", "ACL"),
        ("C", "PC"),
        ("D", "SSH"),
    ],
    "cloud_quiz01_q015": [
        ("A", "IPS"),
        ("B", "OLP"),
        ("C", "ACL"),
        ("D", "WAF"),
    ],
    "cloud_quiz01_q019": [
        ("A", "Dedicated connection"),
        ("B", "VPN"),
        ("C", "VLAN"),
        ("D", "ACL"),
    ],
    "cloud_quiz01_q036": [
        ("A", "IaaS"),
        ("B", "PaaS"),
        ("C", "DBaaS"),
        ("D", "SaaS"),
    ],
    "cloud_quiz02_q040": [
        ("A", "A SAN works only with fiber-based networks."),
        ("B", "A SAN works with any Ethernet-based network."),
        ("C", "A NAS uses a faster protocol than a SAN."),
        ("D", "A NAS uses a slower protocol than a SAN."),
    ],
    "cloud_quiz02_q014": [
        ("A", "Rebooting the engineering VM"),
        ("B", "Reviewing the administrator's permissions to access the engineering VM"),
        ("C", "Allowing connections from 0.0.0.0/0 to the engineering VM"),
        ("D", "Performing a packet capture on the engineering VM"),
    ],
    "cloud_quiz02_q016": [
        ("A", "Warm"),
        ("B", "Hot"),
        ("C", "Archive"),
        ("D", "Cold"),
    ],
    "cloud_quiz02_q017": [
        ("A", "SaaS"),
        ("B", "IaaS"),
        ("C", "FaaS"),
        ("D", "PaaS"),
    ],
    "cloud_quiz02_q022": [
        ("A", "VM"),
        ("B", "Containers"),
        ("C", "Remote desktops"),
        ("D", "Bare-metal servers"),
    ],
    "cloud_quiz02_q026": [
        ("A", "Merging code often"),
        ("B", "Pushing code directly to production"),
        ("C", "Performing code deployment"),
        ("D", "Maintaining one branch for all features"),
        ("E", "Committing code often"),
        ("F", "Initiating a pull request"),
    ],
    "cloud_quiz02_q032": [
        ("A", "Recoverability"),
        ("B", "Retention"),
        ("C", "Encryption"),
        ("D", "Integrity"),
    ],
    "cloud_quiz02_q038": [
        ("A", "Log retention"),
        ("B", "Tracing"),
        ("C", "Log aggregation"),
        ("D", "Log rotation"),
        ("E", "Hashing"),
        ("F", "Encryption"),
    ],
    "cloud_quiz03_q013": [
        ("A", "Drift detection"),
        ("B", "Repeatability"),
        ("C", "Documentation"),
        ("D", "Versioning"),
    ],
    "cloud_quiz03_q009": [
        ("A", "Archive"),
        ("B", "Hot"),
        ("C", "Cold"),
        ("D", "Warm"),
    ],
    "cloud_quiz03_q025": [
        ("A", "VPN"),
        ("B", "VPC peering"),
        ("C", "BGP"),
        ("D", "Transit gateway"),
    ],
    "cloud_quiz03_q029": [
        ("A", "Operating system patches"),
        ("B", "Table-level permissions"),
        ("C", "Minor database engine updates"),
        ("D", "Cluster configuration"),
        ("E", "Row-level encryption"),
        ("F", "Availability of hardware for scaling"),
    ],
    "cloud_quiz03_q030": [
        ("A", "Cryptojacking"),
        ("B", "Human error"),
        ("C", "DDoS"),
        ("D", "Phishing"),
    ],
    "cloud_quiz04_q017": [
        ("A", "VPC"),
        ("B", "Application load balancer"),
        ("C", "CDN"),
        ("D", "API gateway"),
    ],
    "cloud_quiz04_q028": [
        ("A", "Snapshot"),
        ("B", "Full"),
        ("C", "Differential"),
        ("D", "Incremental"),
    ],
    "cloud_quiz05_q007": [
        ("A", "Private container repository access requires authorization, while public repository access does not require authorization."),
        ("B", "Private container repositories are hidden by default and containers must be directly referenced, while public container repositories allow browsing of container images."),
        ("C", "Private container repositories must use proprietary licenses, while public container repositories must have open-source licenses."),
        ("D", "Private container repositories are used to obfuscate the content of the Dockerfile, while public container repositories allow for Dockerfile inspection."),
    ],
    "cloud_quiz05_q001": [
        ("A", "File"),
        ("B", "Object"),
        ("C", "Block"),
        ("D", "Ephemeral"),
    ],
    "cloud_quiz05_q005": [
        ("A", "IPS"),
        ("B", "ACL"),
        ("C", "DLP"),
        ("D", "WAF"),
    ],
    "cloud_quiz05_q013": [
        ("A", "Option A"),
        ("B", "Option B"),
        ("C", "Option C"),
        ("D", "Option D"),
    ],
    "cloud_quiz05_q031": [
        ("A", "Resource tagging"),
        ("B", "Discretionary access control"),
        ("C", "Multifactor authentication"),
        ("D", "Role-based access control"),
        ("E", "Token-based authentication"),
        ("F", "Bastion host"),
    ],
    "cloud_quiz08_q005": [
        ("A", "Hashing"),
        ("B", "Encoding"),
        ("C", "SAML"),
        ("D", "AES"),
        ("E", "TLS"),
        ("F", "SSL"),
    ],
    "cloud_quiz08_q013": [
        ("A", "Mount the volume in Docker using --user=myapp."),
        ("B", "Add USER myapp to the Dockerfile and rebuild the container."),
        ("C", "Run chown myapp:myapp /project-files with cron every minute."),
        ("D", "Modify the container application to execute sudo -u myapp myapp."),
    ],
    "cloud_quiz09_q010": [
        ("A", "Private"),
        ("B", "Community"),
        ("C", "Public"),
        ("D", "Hybrid"),
    ],
    "cloud_quiz09_q017": [
        ("A", "Disabling Gigabit Ethernet 1/0/7"),
        ("B", "Changing the MTU on Gigabit Ethernet 1/0/2"),
        ("C", "Changing the access VLAN for Gigabit Ethernet 1/0/2 to 25"),
        ("D", "Enabling jumbo frames on Gigabit Ethernet 1/0/6 and Gigabit Ethernet 1/0/7"),
    ],
    "cloud_quiz10_q002": [
        ("A", "Cold"),
        ("B", "Hot"),
        ("C", "Warm"),
        ("D", "Archive"),
    ],
    "cloud_quiz10_q006": [
        ("A", "NVMe"),
        ("B", "Serial-attached SCSI"),
        ("C", "SATA"),
        ("D", "iSCSI"),
    ],
    "cloud_quiz06_q006": [
        ("A", "SQL injection"),
        ("B", "Cross-site scripting"),
        ("C", "Leaked credentials"),
        ("D", "DDoS"),
    ],
    "cloud_quiz06_q014": [
        ("A", "Hot"),
        ("B", "Warm"),
        ("C", "Cold"),
        ("D", "Offline"),
    ],
    "cloud_quiz07_q007": [
        ("A", "Event trigger"),
        ("B", "Load trigger"),
        ("C", "Vertical scaling"),
        ("D", "Horizontal scaling"),
    ],
    "cloud_quiz07_q008": [
        ("A", "Hot"),
        ("B", "Warm"),
        ("C", "Cold"),
        ("D", "Offline"),
    ],
    "cloud_quiz08_q003": [
        ("A", "PaaS"),
        ("B", "SaaS"),
        ("C", "DBaaS"),
        ("D", "IaaS"),
    ],
    "cloud_quiz09_q015": [
        ("A", "Create a new VM with more CPU and RAM; have the developer install and configure the database application."),
        ("B", "Stop the VM; change the data disk storage type to high performance; start the VM."),
        ("C", "Create a new VM with a high-performance data disk; have the developer install and configure the database application."),
        ("D", "Stop the VM; detach the data disk; create and attach a new high-performance data disk; start the VM."),
    ],
    "cloud_quiz10_q010": [
        ("A", "YUM"),
        ("B", "DNF"),
        ("C", "Pacman"),
        ("D", "APT"),
    ],
    "cloud_quiz10_q015": [
        ("A", "Hot"),
        ("B", "Archive"),
        ("C", "Warm"),
        ("D", "Cold"),
    ],
    "cloud_quiz11_q008": [
        ("A", "WAF"),
        ("B", "DLP"),
        ("C", "ACL"),
        ("D", "IDS"),
    ],
    "cloud_quiz11_q020": [
        ("A", "Training and vendor support"),
        ("B", "Management overhead and environment"),
        ("C", "Regulations and availability"),
        ("D", "Vendor lock-in and refactoring"),
    ],
    "cloud_quiz12_q005": [
        ("A", "Option A"),
        ("B", "Option B"),
        ("C", "Option C"),
        ("D", "Option D"),
    ],
    "cloud_quiz12_q009": [
        ("A", "Cluster"),
        ("B", "Container"),
        ("C", "Serverless"),
        ("D", "Snapshot"),
    ],
    "cloud_quiz12_q013": [
        ("A", "Increasing network bandwidth"),
        ("B", "Autoscaling"),
        ("C", "Cloud bursting"),
        ("D", "Obtaining additional hardware"),
    ],
}

MANUAL_LABEL_FALLBACKS = {
    "cloud_quiz01_q018": ["C"],
    "cloud_quiz01_q015": ["B"],
    "cloud_quiz01_q019": ["B"],
    "cloud_quiz01_q036": ["D"],
    "cloud_quiz02_q040": ["D"],
    "cloud_quiz02_q014": ["B"],
    "cloud_quiz02_q016": ["C"],
    "cloud_quiz02_q017": ["B"],
    "cloud_quiz02_q022": ["B"],
    "cloud_quiz02_q026": ["A", "E"],
    "cloud_quiz02_q032": ["B"],
    "cloud_quiz02_q038": ["A", "C"],
    "cloud_quiz03_q013": ["D"],
    "cloud_quiz03_q009": ["A"],
    "cloud_quiz03_q025": ["B"],
    "cloud_quiz03_q029": ["B", "E"],
    "cloud_quiz03_q030": ["C"],
    "cloud_quiz04_q007": ["A"],
    "cloud_quiz04_q017": ["C"],
    "cloud_quiz04_q028": ["D"],
    "cloud_quiz04_q034": ["D"],
    "cloud_quiz05_q001": ["C"],
    "cloud_quiz05_q005": ["D"],
    "cloud_quiz05_q007": ["A"],
    "cloud_quiz05_q023": ["A"],
    "cloud_quiz05_q031": ["B", "D"],
    "cloud_quiz05_q040": ["A"],
    "cloud_quiz06_q006": ["D"],
    "cloud_quiz06_q014": ["A"],
    "cloud_quiz07_q007": ["C"],
    "cloud_quiz07_q008": ["A"],
    "cloud_quiz08_q003": ["D"],
    "cloud_quiz08_q005": ["D", "E"],
    "cloud_quiz08_q013": ["B"],
    "cloud_quiz09_q015": ["B"],
    "cloud_quiz09_q010": ["B"],
    "cloud_quiz09_q017": ["B"],
    "cloud_quiz10_q002": ["D"],
    "cloud_quiz10_q006": ["A"],
    "cloud_quiz10_q010": ["D"],
    "cloud_quiz10_q015": ["C"],
    "cloud_quiz11_q008": ["A"],
    "cloud_quiz11_q020": ["C"],
    "cloud_quiz12_q005": ["D"],
    "cloud_quiz12_q009": ["B"],
    "cloud_quiz12_q013": ["C"],
}

MANUAL_TEXT_FALLBACKS = {
    "cloud_quiz05_q013": "Option A",
    "cloud_quiz12_q005": "Option D",
}

MANUAL_PROMPT_FALLBACKS = {
    "cloud_quiz01_q008": "A cloud engineer wants to run a script that increases the volume storage size if it is below 100GB. Which of the following should the engineer run?",
    "cloud_quiz01_q039": "An administrator is creating a cron job that shuts down the virtual machines at night to save on costs. Which of the following is the best way to achieve this task?",
    "cloud_quiz02_q014": "A junior cloud administrator was recently promoted to cloud administrator and has been added to the cloud administrator group. The cloud administrator group is the only one that can access the engineering VM. The new administrator unsuccessfully attempts to access the engineering VM. However, the other administrators can access it without issue. Which of the following is the best way to identify the root cause?",
    "cloud_quiz04_q007": "An on-premises data center is located in an earthquake-prone location. The workload consists of real-time, online transaction processing. Which of the following data protection strategies should be used to back up on-premises data to the cloud while also being cost effective?",
    "cloud_quiz04_q034": "An administrator needs to provide a backup solution for a cloud infrastructure that enables the resources to run from another data center in case of an outage. Connectivity to the backup data center is via a third-party, untrusted network. Which of the following is the most important feature required for this solution?",
    "cloud_quiz05_q007": "Which of the following describes the main difference between public and private container repositories?",
    "cloud_quiz05_q013": "A systems administrator needs to configure a script that will monitor whether an application is healthy and stop the VM if an unsuccessful code is returned. Which of the following scripts should the systems administrator use to achieve this goal?",
    "cloud_quiz05_q023": "A newly configured VM fails to run application updates despite having internet access. The updates download automatically from a third-party network. Given the following output: dig +short apac.updateserver.net returns 38.102.218.7; dig +short na.updateserver.net returns request timeout. Which of the following troubleshooting steps would be best to take?",
    "cloud_quiz10_q007": "A cloud solutions architect wants to deploy a three-tier web application that requires the minimum amount of operational overhead. Which of the following is the best template given these requirements?",
    "cloud_quiz11_q007": "A cloud engineer is selecting a model for a data center that will host a workload. The database must reside within the data center on the company's SAN solution. However, the workload will be hosted by a third-party vendor. Which of the following models should the cloud engineer select to meet these requirements?",
    "cloud_quiz12_q005": "A cloud solutions architect needs to deploy a simple, public-facing website with the following requirements: Cost-effective, highly available, self-healing, and secure. Which of the following is the most appropriate template to use?",
}

MANUAL_MEDIA_FALLBACKS = {
    "cloud_quiz01_q008": ("assets/media/cloud_quiz01_q008_options.png", "ตัวเลือกสคริปต์ A-D สำหรับข้อ 8"),
    "cloud_quiz01_q039": ("assets/media/cloud_quiz01_q039_options.png", "ตัวเลือกสคริปต์ A-D สำหรับข้อ 39"),
    "cloud_quiz05_q013": ("assets/media/cloud_quiz05_q013_options.png", "ตัวเลือกสคริปต์ A-D สำหรับข้อ 13"),
    "cloud_quiz10_q007": ("assets/media/cloud_quiz10_q007_options.png", "ตัวเลือก template A-D สำหรับข้อ 7"),
    "cloud_quiz12_q005": ("assets/media/cloud_quiz12_q005_options.png", "ตัวเลือก template A-D สำหรับข้อ 5"),
}

DUPLICATE_QUESTION_IDS = {
    "cloud_quiz06_q008",
    "cloud_quiz07_q002",
    "cloud_quiz08_q014",
    "cloud_quiz06_q009",
    "cloud_quiz07_q003",
    "cloud_quiz07_q004",
    "cloud_quiz07_q005",
    "cloud_quiz07_q006",
    "cloud_quiz07_q007",
    "cloud_quiz07_q008",
    "cloud_quiz07_q009",
    "cloud_quiz07_q010",
    "cloud_quiz08_q006",
    "cloud_quiz08_q003",
    "cloud_quiz07_q001",
}


@dataclass
class Line:
    text: str
    x: float
    y: float
    width: float
    height: float


@dataclass
class CropRef:
    quiz: str
    page: int
    y1: int
    y2: int
    image_path: Path
    ocr_text: str
    lines: list[Line]


def normalize(value: str) -> str:
    value = value.lower()
    value = value.replace("’", "'")
    value = re.sub(r"[^a-z0-9+.#/\- ]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def list_source_pdfs() -> list[Path]:
    return [p for p in sorted(QUESTION_DIR.glob("cloud_quiz*.pdf")) if PDF_PATTERN.match(p.name)]


def run_pdftoppm(pdf: Path, out_dir: Path, dpi: int = 300) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(out_dir.glob("page-*.png"), key=page_number)
    if existing:
        return existing

    prefix = out_dir / "page"
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(dpi), str(pdf), str(prefix)],
        check=True,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return sorted(out_dir.glob("page-*.png"), key=page_number)


def page_number(path: Path) -> int:
    match = re.search(r"-(\d+)\.png$", path.name)
    return int(match.group(1)) if match else 0


def row_runs(mask: np.ndarray, threshold: int, min_height: int) -> list[tuple[int, int]]:
    counts = mask.sum(axis=1)
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for idx, count in enumerate(counts):
        if count > threshold and start is None:
            start = idx
        elif (count <= threshold or idx == len(counts) - 1) and start is not None:
            end = idx
            if end - start >= min_height:
                runs.append((start, end))
            start = None
    return runs


def detect_x_bounds(arr: np.ndarray) -> tuple[int, int]:
    height, width = arr.shape[:2]
    blue = (
        (arr[:, :, 1] > arr[:, :, 0] + 8)
        & (arr[:, :, 2] > arr[:, :, 0] + 8)
        & (arr[:, :, 0] < 235)
    )
    counts = blue.sum(axis=0)
    threshold = max(35, int(height * 0.02))
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for idx, count in enumerate(counts):
        if count > threshold and start is None:
            start = idx
        elif (count <= threshold or idx == len(counts) - 1) and start is not None:
            end = idx
            if end - start > width * 0.25:
                runs.append((start, end))
            start = None

    if not runs:
        return round(width * 0.334), round(width * 0.897)

    def score(run: tuple[int, int]) -> tuple[int, float]:
        x1, x2 = run
        center = (x1 + x2) / 2 / width
        center_penalty = abs(center - 0.62)
        return (x2 - x1, -center_penalty)

    x1, x2 = max(runs, key=score)
    return max(0, x1 - 8), min(width, x2 + 8)


def detect_runs(image_path: Path) -> tuple[tuple[int, int], list[tuple[int, int]], list[tuple[int, int]]]:
    image = Image.open(image_path).convert("RGB")
    arr = np.asarray(image)
    x1, x2 = detect_x_bounds(arr)
    sub = arr[:, x1:x2, :]
    col_width = x2 - x1
    threshold = max(120, int(col_width * 0.35))

    blue = (
        (sub[:, :, 1] > sub[:, :, 0] + 8)
        & (sub[:, :, 2] > sub[:, :, 0] + 8)
        & (sub[:, :, 0] < 235)
    )
    beige = (
        (sub[:, :, 0] > sub[:, :, 2] + 10)
        & (sub[:, :, 1] > sub[:, :, 2] + 5)
        & (sub[:, :, 0] > 235)
        & (sub[:, :, 1] > 220)
        & (sub[:, :, 2] < 240)
    )

    blue_runs = row_runs(blue, threshold, min_height=35)
    answer_runs = row_runs(beige, threshold, min_height=22)
    return (x1, x2), blue_runs, answer_runs


def save_web_crop(
    page_path: Path,
    x_bounds: tuple[int, int],
    y_bounds: tuple[int, int],
    out_path: Path,
    max_width: int = 1120,
) -> None:
    image = Image.open(page_path).convert("RGB")
    x1, x2 = x_bounds
    y1, y2 = y_bounds
    pad_x = 10
    pad_y = 8
    crop = image.crop(
        (
            max(0, x1 - pad_x),
            max(0, y1 - pad_y),
            min(image.width, x2 + pad_x),
            min(image.height, y2 + pad_y),
        )
    )
    if crop.width > max_width:
        ratio = max_width / crop.width
        crop = crop.resize((max_width, max(1, round(crop.height * ratio))), Image.Resampling.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    crop.save(out_path, optimize=True)


def merge_crop_refs(first: CropRef, second: CropRef, out_path: Path) -> CropRef:
    first_image = Image.open(first.image_path).convert("RGB")
    second_image = Image.open(second.image_path).convert("RGB")
    gap = 18
    width = max(first_image.width, second_image.width)
    height = first_image.height + second_image.height + gap
    merged = Image.new("RGB", (width, height), (255, 255, 255))
    merged.paste(first_image, (0, 0))
    merged.paste(second_image, (0, first_image.height + gap))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.save(out_path, optimize=True)

    shifted_lines = [
        Line(line.text, line.x, line.y + first_image.height + gap, line.width, line.height)
        for line in second.lines
    ]
    return CropRef(
        first.quiz,
        first.page,
        first.y1,
        second.y2,
        out_path,
        f"{first.ocr_text}\n{second.ocr_text}".strip(),
        first.lines + shifted_lines,
    )


def stack_page_crops(
    parts: list[tuple[Path, tuple[int, int], tuple[int, int]]],
    out_path: Path,
    max_width: int = 1120,
) -> None:
    crops: list[Image.Image] = []
    for page_path, x_bounds, y_bounds in parts:
        page = Image.open(page_path).convert("RGB")
        x1, x2 = x_bounds
        y1, y2 = y_bounds
        crops.append(page.crop((x1, y1, x2, y2)))

    gap = 18
    width = max(crop.width for crop in crops)
    height = sum(crop.height for crop in crops) + gap * (len(crops) - 1)
    merged = Image.new("RGB", (width, height), (255, 255, 255))
    y = 0
    for crop in crops:
        merged.paste(crop, (0, y))
        y += crop.height + gap

    if merged.width > max_width:
        ratio = max_width / merged.width
        merged = merged.resize((max_width, max(1, round(merged.height * ratio))), Image.Resampling.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.save(out_path, optimize=True)


def manual_adjustments(
    quiz_id: str,
    page_paths: list[Path],
    card_refs: list[CropRef],
    answer_refs: list[CropRef],
) -> None:
    if quiz_id == "cloud_quiz05" and len(card_refs) >= 13 and len(page_paths) >= 3:
        page2 = page_paths[1]
        page3 = page_paths[2]
        x2_bounds, _, _ = detect_runs(page2)
        x3_bounds, _, _ = detect_runs(page3)
        out = ASSET_QUESTION_DIR / "cloud_quiz05_manual_q013.png"
        stack_page_crops(
            [
                (page2, x2_bounds, (3185, Image.open(page2).height)),
                (page3, x3_bounds, (0, 1188)),
            ],
            out,
        )
        prompt = MANUAL_PROMPT_FALLBACKS["cloud_quiz05_q013"]
        card_refs[12] = CropRef(
            quiz_id,
            2,
            3185,
            1188,
            out,
            f"{prompt} Select one: A. Option A B. Option B C. Option C D. Option D",
            [
                Line(prompt, 20, 20, 900, 24),
                Line("Select one:", 20, 70, 120, 20),
                Line("A.", 42, 110, 24, 20),
                Line("Option A", 86, 110, 120, 20),
                Line("B.", 42, 150, 24, 20),
                Line("Option B", 86, 150, 120, 20),
                Line("C.", 42, 190, 24, 20),
                Line("Option C", 86, 190, 120, 20),
                Line("D.", 42, 230, 24, 20),
                Line("Option D", 86, 230, 120, 20),
            ],
        )

    if quiz_id == "cloud_quiz06" and len(answer_refs) == 15 and len(page_paths) >= 3:
        page3 = page_paths[2]
        x_bounds, _, _ = detect_runs(page3)
        out = ASSET_ANSWER_DIR / "cloud_quiz06_manual_p03_top_answer.png"
        save_web_crop(page3, x_bounds, (0, 145), out)
        answer_refs.insert(
            12,
            CropRef(
                quiz_id,
                3,
                0,
                145,
                out,
                "The correct answer is: Vertical scaling",
                [Line("The correct answer is: Vertical scaling", 20, 20, 500, 20)],
            ),
        )

    if quiz_id == "cloud_quiz10" and len(card_refs) == 19 and len(answer_refs) == 20 and len(page_paths) >= 2:
        page1 = page_paths[0]
        page2 = page_paths[1]
        x1_bounds, _, _ = detect_runs(page1)
        x2_bounds, _, _ = detect_runs(page2)
        out = ASSET_QUESTION_DIR / "cloud_quiz10_manual_q007.png"
        stack_page_crops(
            [
                (page1, x1_bounds, (3300, Image.open(page1).height)),
                (page2, x2_bounds, (0, 2865)),
            ],
            out,
        )
        prompt = (
            "A cloud solutions architect wants to deploy a three-tier web application that requires "
            "the minimum amount of operational overhead. Which of the following is the best template "
            "given these requirements?"
        )
        card_refs.insert(
            6,
            CropRef(
                quiz_id,
                1,
                3300,
                2865,
                out,
                f"{prompt} Select one: A. Option A B. Option B C. Option C D. Option D",
                [
                    Line(prompt, 20, 20, 900, 24),
                    Line("Select one:", 20, 70, 120, 20),
                    Line("A.", 42, 110, 24, 20),
                    Line("Option A", 86, 110, 120, 20),
                    Line("B.", 42, 150, 24, 20),
                    Line("Option B", 86, 150, 120, 20),
                    Line("C.", 42, 190, 24, 20),
                    Line("Option C", 86, 190, 120, 20),
                    Line("D.", 42, 230, 24, 20),
                    Line("Option D", 86, 230, 120, 20),
                ],
            ),
        )
        answer_refs[6].ocr_text = "The correct answer is: Option B"

    if quiz_id == "cloud_quiz12" and len(card_refs) >= 5 and len(page_paths) >= 2:
        page1 = page_paths[0]
        page2 = page_paths[1]
        x1_bounds, _, _ = detect_runs(page1)
        x2_bounds, _, _ = detect_runs(page2)
        out = ASSET_QUESTION_DIR / "cloud_quiz12_manual_q005.png"
        stack_page_crops(
            [
                (page1, x1_bounds, (2835, Image.open(page1).height)),
                (page2, x2_bounds, (0, 2760)),
            ],
            out,
        )
        prompt = MANUAL_PROMPT_FALLBACKS["cloud_quiz12_q005"]
        card_refs[4] = CropRef(
            quiz_id,
            1,
            2835,
            2760,
            out,
            f"{prompt} Select one: A. Option A B. Option B C. Option C D. Option D",
            [
                Line(prompt, 20, 20, 900, 24),
                Line("Select one:", 20, 70, 120, 20),
                Line("A.", 42, 110, 24, 20),
                Line("Option A", 86, 110, 120, 20),
                Line("B.", 42, 150, 24, 20),
                Line("Option B", 86, 150, 120, 20),
                Line("C.", 42, 190, 24, 20),
                Line("Option C", 86, 190, 120, 20),
                Line("D.", 42, 230, 24, 20),
                Line("Option D", 86, 230, 120, 20),
            ],
        )


async def ocr_image(path: Path) -> tuple[str, list[Line]]:
    storage_file = await StorageFile.get_file_from_path_async(str(path.resolve()))
    stream = await storage_file.open_async(FileAccessMode.READ)
    decoder = await BitmapDecoder.create_async(stream)
    bitmap = await decoder.get_software_bitmap_async()
    engine = OcrEngine.try_create_from_user_profile_languages()
    result = await engine.recognize_async(bitmap)

    lines: list[Line] = []
    for raw_line in result.lines:
        words = list(raw_line.words)
        if not words:
            continue
        xs: list[float] = []
        ys: list[float] = []
        for word in words:
            rect = word.bounding_rect
            xs.extend([rect.x, rect.x + rect.width])
            ys.extend([rect.y, rect.y + rect.height])
        lines.append(
            Line(
                text=raw_line.text.strip(),
                x=min(xs),
                y=min(ys),
                width=max(xs) - min(xs),
                height=max(ys) - min(ys),
            )
        )
    lines.sort(key=lambda line: (line.y, line.x))
    return result.text.strip(), lines


def parse_question(lines: list[Line]) -> tuple[str, str, list[dict[str, str]]]:
    select_idx = None
    for idx, line in enumerate(lines):
        if re.search(r"\bselect\s+one\b", line.text, re.IGNORECASE):
            select_idx = idx

    first_option_idx = None
    for idx, line in enumerate(lines):
        text = line.text.strip()
        if line.x < 320 and re.match(r"^[A-H][\.\)](?:\s+.+)?$|^[A-H][\.\)]?$", text, re.IGNORECASE):
            first_option_idx = idx
            break

    split_idx = select_idx if select_idx is not None else first_option_idx
    question_lines = lines[: split_idx if split_idx is not None else len(lines)]
    prompt = " ".join(line.text for line in question_lines).strip()

    mode = "single"
    option_lines = lines[(select_idx + 1) if select_idx is not None else (first_option_idx or 0) :]
    if select_idx is not None and "more" in lines[select_idx].text.lower():
        mode = "multiple"

    choices = parse_choices(option_lines)
    return prompt, mode, choices


def parse_choices(lines: list[Line]) -> list[dict[str, str]]:
    labels: list[tuple[str, float, int]] = []
    for idx, line in enumerate(lines):
        text = line.text.strip()
        match = re.match(r"^([A-H])[\.\)]?$", text, re.IGNORECASE)
        inline = re.match(r"^([A-H])[\.\)]\s+(.+)$", text, re.IGNORECASE)
        if match and line.x < 260:
            labels.append((match.group(1).upper(), line.y, idx))
        elif inline and line.x < 320:
            labels.append((inline.group(1).upper(), line.y, idx))

    if not labels:
        return fallback_choices(" ".join(line.text for line in lines))

    choices: list[dict[str, str]] = []
    for pos, (label, y, idx) in enumerate(labels):
        next_y = labels[pos + 1][1] if pos + 1 < len(labels) else math.inf
        parts: list[str] = []
        inline = re.match(r"^[A-H][\.\)]\s+(.+)$", lines[idx].text.strip(), re.IGNORECASE)
        if inline:
            parts.append(inline.group(1).strip())

        label_x = lines[idx].x
        for line in lines:
            if y - 8 <= line.y < next_y - 5 and line.x > 120:
                if not re.match(r"^[A-H][\.\)]?$", line.text.strip(), re.IGNORECASE):
                    parts.append(line.text.strip())
            elif y - 8 <= line.y < next_y - 5 and line.x > label_x + 18:
                if not re.match(r"^[A-H][\.\)]?$", line.text.strip(), re.IGNORECASE):
                    parts.append(line.text.strip())

        text = re.sub(r"\s+", " ", " ".join(parts)).strip()
        choices.append({"label": label, "text": text or f"Option {label}"})

    deduped: list[dict[str, str]] = []
    seen = set()
    for choice in choices:
        if choice["label"] not in seen:
            deduped.append(choice)
            seen.add(choice["label"])
    return deduped


def fallback_choices(text: str) -> list[dict[str, str]]:
    choices: list[dict[str, str]] = []
    pattern = re.compile(r"\b([A-H])[\.\)]\s+([^A-H]+?)(?=\s+[A-H][\.\)]\s+|$)")
    for label, value in pattern.findall(text):
        choices.append({"label": label.upper(), "text": re.sub(r"\s+", " ", value).strip()})
    return choices


def parse_answer(answer_text: str) -> tuple[str, list[str]]:
    text = re.sub(r"\s+", " ", answer_text).strip()
    match = re.search(r"(?:The correct\s+|correct\s+)?answers? (?:is|are)\s*:\s*(.+)$", text, re.IGNORECASE)
    raw = match.group(1).strip() if match else text
    raw = raw.strip(" .")
    values = [part.strip(" .") for part in re.split(r"\s*,\s*", raw) if part.strip(" .")]
    return raw, values or ([raw] if raw else [])


def best_label_for_answer(answer: str, choices: list[dict[str, str]]) -> str | None:
    answer_norm = normalize(answer)
    option_match = re.match(r"option\s+([A-H])$", answer_norm)
    if option_match:
        return option_match.group(1).upper()

    best_label = None
    best_score = 0.0
    for choice in choices:
        choice_norm = normalize(choice["text"])
        if not choice_norm:
            continue
        if answer_norm == choice_norm or answer_norm in choice_norm or choice_norm in answer_norm:
            return choice["label"]
        score = SequenceMatcher(None, answer_norm, choice_norm).ratio()
        if score > best_score:
            best_score = score
            best_label = choice["label"]
    return best_label if best_score >= 0.78 else None


def build_explanations(
    choices: list[dict[str, str]],
    correct_labels: Iterable[str],
    correct_answer: str,
) -> dict[str, str]:
    correct = set(correct_labels)
    explanations: dict[str, str] = {}
    for choice in choices:
        label = choice["label"]
        if label in correct:
            explanations[label] = f"ถูก เพราะตัวเลือกนี้ตรงกับแนวคิดหลักของคำตอบ: {correct_answer}"
        else:
            explanations[label] = f"ยังไม่เหมาะ เพราะตัวเลือกนี้ไม่ตอบโจทย์หลักเท่ากับ {correct_answer}"
    return explanations


def apply_manual_label_fallbacks(questions: list[dict]) -> None:
    for question in questions:
        item_id = question["id"]
        question["media"] = []
        if item_id in MANUAL_PROMPT_FALLBACKS:
            question["prompt"] = MANUAL_PROMPT_FALLBACKS[item_id]
        if item_id in MANUAL_CHOICE_FALLBACKS:
            question["choices"] = [
                {"label": label, "text": text}
                for label, text in MANUAL_CHOICE_FALLBACKS[item_id]
            ]
        if item_id in MANUAL_TEXT_FALLBACKS:
            question["correctAnswerText"] = MANUAL_TEXT_FALLBACKS[item_id]
            question["correctAnswers"] = [MANUAL_TEXT_FALLBACKS[item_id]]
        if item_id in MANUAL_LABEL_FALLBACKS:
            question["correctLabels"] = MANUAL_LABEL_FALLBACKS[item_id]
            question["choiceExplanations"] = build_explanations(
                question["choices"],
                question["correctLabels"],
                question["correctAnswerText"],
            )
        if item_id in MANUAL_MEDIA_FALLBACKS:
            src, alt = MANUAL_MEDIA_FALLBACKS[item_id]
            question["media"] = [{"type": "image", "src": src, "alt": alt}]


def dedupe_questions(questions: list[dict]) -> list[dict]:
    seen: set[tuple[str, tuple[str, ...], tuple[str, ...]]] = set()
    unique: list[dict] = []
    for question in questions:
        if question["id"] in DUPLICATE_QUESTION_IDS:
            continue

        prompt = normalize(question.get("prompt", ""))
        if not prompt or prompt.startswith("prompt missing from ocr"):
            unique.append(question)
            continue

        choices = tuple(normalize(choice.get("text", "")) for choice in question.get("choices", []))
        answers = tuple(normalize(answer) for answer in question.get("correctAnswers", []))
        key = (prompt, choices, answers)
        if key in seen:
            continue

        seen.add(key)
        unique.append(question)
    return unique


def generate_manual_media_assets() -> None:
    media_dir = ROOT / "assets" / "media"
    media_dir.mkdir(parents=True, exist_ok=True)

    crops = {
        "assets/media/cloud_quiz01_q008_options.png": ("assets/questions/cloud_quiz01_p02_c02.png", (18, 72, 650, 518)),
        "assets/media/cloud_quiz01_q039_options.png": ("assets/questions/cloud_quiz01_p07_c04.png", (18, 74, 415, 740)),
        "assets/media/cloud_quiz05_q013_options.png": ("assets/questions/cloud_quiz05_manual_q013.png", (0, 0, 1120, 1515)),
        "assets/media/cloud_quiz10_q007_options.png": ("assets/questions/cloud_quiz10_manual_q007.png", (0, 118, 1120, 2475)),
        "assets/media/cloud_quiz12_q005_options.png": ("assets/questions/cloud_quiz12_manual_q005.png", (0, 175, 1120, 2760)),
    }
    for dst, (src, box) in crops.items():
        src_path = ROOT / src
        if not src_path.exists():
            continue
        Image.open(src_path).convert("RGB").crop(box).save(ROOT / dst, optimize=True)


async def build() -> None:
    ASSET_QUESTION_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_ANSWER_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for directory in (ASSET_QUESTION_DIR, ASSET_ANSWER_DIR):
        for png in directory.glob("*.png"):
            png.unlink()

    questions: list[dict] = []
    warnings: list[str] = []

    for pdf in list_source_pdfs():
        quiz = pdf.stem.replace("cloud_quiz", "Quiz ")
        quiz_id = pdf.stem
        render_dir = TMP_DIR / quiz_id
        page_paths = run_pdftoppm(pdf, render_dir)

        card_refs: list[CropRef] = []
        answer_refs: list[CropRef] = []
        raw_cards: list[dict] = []

        for page_path in page_paths:
            page = page_number(page_path)
            page_height = Image.open(page_path).height
            x_bounds, card_runs, answer_runs = detect_runs(page_path)

            for idx, (y1, y2) in enumerate(card_runs, start=1):
                out = ASSET_QUESTION_DIR / f"{quiz_id}_p{page:02d}_c{idx:02d}.png"
                save_web_crop(page_path, x_bounds, (y1, y2), out)
                text, lines = await ocr_image(out)
                if text.strip():
                    raw_cards.append(
                        {
                            "ref": CropRef(quiz_id, page, y1, y2, out, text, lines),
                            "complete": bool(re.search(r"\bselect\s+one\b", text, re.IGNORECASE)),
                            "top": y1 < 360,
                            "bottom": y2 > page_height - 260,
                        }
                    )

            for idx, (y1, y2) in enumerate(answer_runs, start=1):
                out = ASSET_ANSWER_DIR / f"{quiz_id}_p{page:02d}_a{idx:02d}.png"
                save_web_crop(page_path, x_bounds, (y1, y2), out)
                text, lines = await ocr_image(out)
                if re.search(r"(?:correct\s+)?answers?\s+(?:is|are)", text, re.IGNORECASE):
                    answer_refs.append(CropRef(quiz_id, page, y1, y2, out, text, lines))

        idx = 0
        while idx < len(raw_cards):
            current = raw_cards[idx]
            ref = current["ref"]
            if current["complete"]:
                card_refs.append(ref)
                idx += 1
                continue

            next_card = raw_cards[idx + 1] if idx + 1 < len(raw_cards) else None
            if current["bottom"] and next_card and next_card["top"] and not next_card["complete"]:
                merged_out = ASSET_QUESTION_DIR / f"{quiz_id}_split_p{ref.page:02d}_{idx + 1:02d}.png"
                card_refs.append(merge_crop_refs(ref, next_card["ref"], merged_out))
                idx += 2
                continue

            idx += 1

        manual_adjustments(quiz_id, page_paths, card_refs, answer_refs)

        if len(card_refs) != len(answer_refs):
            warnings.append(f"{pdf.name}: question cards={len(card_refs)}, answer strips={len(answer_refs)}")

        for number, (card, answer) in enumerate(zip(card_refs, answer_refs), start=1):
            prompt, mode, choices = parse_question(card.lines)
            answer_raw, correct_values = parse_answer(answer.ocr_text)
            correct_labels = [
                label
                for label in (best_label_for_answer(value, choices) for value in correct_values)
                if label is not None
            ]
            item_id = f"{quiz_id}_q{number:03d}"
            questions.append(
                {
                    "id": item_id,
                    "quizId": quiz_id,
                    "quiz": quiz,
                    "number": number,
                    "sourcePdf": pdf.name,
                    "prompt": prompt,
                    "mode": mode,
                    "choices": choices,
                    "correctAnswerText": answer_raw,
                    "correctAnswers": correct_values,
                    "correctLabels": correct_labels,
                    "choiceExplanations": build_explanations(choices, correct_labels, answer_raw),
                    "ocrText": card.ocr_text,
                    "answerOcrText": answer.ocr_text,
                }
            )

    generate_manual_media_assets()
    apply_manual_label_fallbacks(questions)
    questions = dedupe_questions(questions)
    for question in questions:
        question["explanation"] = build_question_explanation(question)
        question["choiceExplanations"] = {
            choice["label"]: build_choice_explanation(question, choice)
            for choice in question.get("choices", [])
        }

    payload = {
        "generatedFrom": [pdf.name for pdf in list_source_pdfs()],
        "ignored": ["cloud_quiz_final.pdf"],
        "answerSource": "Correct answers are OCR-extracted from the visible answer strips in the source PDFs; answer images are not displayed in the web app.",
        "explanationSource": "Thai helper explanations are generated from vendor-neutral Cloud+ concepts, including NIST cloud characteristics/service models, CompTIA Cloud+ domains, and major cloud provider documentation. They explain the concept; the answer key still follows the source PDFs.",
        "explanationReferences": [
            "https://csrc.nist.gov/pubs/sp/800/145/final",
            "https://www.comptia.org/en-us/certifications/cloud/",
            "https://www.ibm.com/think/topics/iaas-paas-saas",
            "https://cloud.google.com/learn/paas-vs-iaas-vs-saas",
        ],
        "warnings": warnings,
        "count": len(questions),
        "questions": questions,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON.relative_to(ROOT)} with {len(questions)} questions.")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    asyncio.run(build())
