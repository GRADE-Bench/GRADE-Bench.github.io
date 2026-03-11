#!/usr/bin/env python3
"""Prepare sample images and JSON data for the GRADE project page."""

import json
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(BASE_DIR, "static", "images", "samples")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(SAMPLES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Data sources
SUBSET_JSON = "/mnt/nas-new/home/yangxue/lmx/image/subset/data.json"
SIMPLE_JSON = "/mnt/nas-new/home/yangxue/lmx/image/simple_instruction/data.json"

# Consistency display mapping
CONSISTENCY_MAP = {
    "overall": "Localized",
    "style": "Style",
    "none": "Independence",
}

# Selected samples: (data_source, index, discipline, display_taxonomy)
SAMPLES = [
    # Mathematics
    (SUBSET_JSON, 0, "Mathematics", "2D Geometry"),
    (SUBSET_JSON, 16, "Mathematics", "3D Geometry"),
    (SUBSET_JSON, 26, "Mathematics", "Functions"),
    (SUBSET_JSON, 34, "Mathematics", "Statistics"),
    (SUBSET_JSON, 36, "Mathematics", "Graph Theory"),
    # Physics
    (SUBSET_JSON, 82, "Physics", "Mechanics"),
    (SUBSET_JSON, 84, "Physics", "Optics"),
    (SUBSET_JSON, 87, "Physics", "Electromagnetism"),
    (SUBSET_JSON, 88, "Physics", "Thermodynamics"),
    (SUBSET_JSON, 94, "Physics", "Engineering Drawing"),
    # Chemistry
    (SUBSET_JSON, 68, "Chemistry", "GHS Pictogram"),
    (SUBSET_JSON, 69, "Chemistry", "Laboratory Techniques"),
    (SUBSET_JSON, 70, "Chemistry", "Structural Transformation"),
    (SUBSET_JSON, 71, "Chemistry", "Gas Laws"),
    # Biology
    (SUBSET_JSON, 96, "Biology", "Food Chain & Energy Flow"),
    (SUBSET_JSON, 97, "Biology", "Cellular Metabolism"),
    (SUBSET_JSON, 98, "Biology", "Endocytosis & Exocytosis"),
    (SUBSET_JSON, 99, "Biology", "Central Dogma"),
    # Computer Science
    (SUBSET_JSON, 114, "Computer Science", "Singly Linked List"),
    (SUBSET_JSON, 115, "Computer Science", "Graph Theory"),
    (SUBSET_JSON, 116, "Computer Science", "Deep Learning"),
    # Economics
    (SUBSET_JSON, 38, "Economics", "Supply & Demand"),
    (SUBSET_JSON, 39, "Economics", "Macro"),
    (SUBSET_JSON, 40, "Economics", "Consumer Choice"),
    (SUBSET_JSON, 41, "Economics", "Labor"),
    (SUBSET_JSON, 42, "Economics", "Costs & Production"),
    (SUBSET_JSON, 45, "Economics", "Market Power & IO"),
    (SUBSET_JSON, 46, "Economics", "Public Economics"),
    (SUBSET_JSON, 50, "Economics", "Finance"),
    # History
    (SUBSET_JSON, 54, "History", "History"),
    # Geography
    (SUBSET_JSON, 60, "Geography", "Earth Geometry"),
    (SUBSET_JSON, 61, "Geography", "Ocean & Hydrology"),
    (SUBSET_JSON, 62, "Geography", "Atmosphere & Climate"),
    (SUBSET_JSON, 65, "Geography", "Lithosphere & Pedosphere"),
    # Music (from simple_instruction/data.json - need to find by task_id)
    (SIMPLE_JSON, "music_task_4", "Music", "Pitch & Transposition"),
    (SIMPLE_JSON, "music_task_10", "Music", "Performance Markings"),
    (SIMPLE_JSON, "music_task_21", "Music", "Rhythm & Meter"),
    (SIMPLE_JSON, "music_task_45", "Music", "Harmony & Theory"),
    # Sports
    (SUBSET_JSON, 106, "Sports", "Sports Anatomy"),
    (SUBSET_JSON, 108, "Sports", "Sports Tactic"),
    (SUBSET_JSON, 110, "Sports", "Sports Nutrition"),
    (SUBSET_JSON, 111, "Sports", "Board (Chess)"),
    (SUBSET_JSON, 112, "Sports", "Board (Go)"),
    (SUBSET_JSON, 113, "Sports", "Board (Chinese Chess)"),
]

# Discipline order and icons
DISCIPLINE_META = {
    "Mathematics": {"icon": "📐", "order": 0},
    "Physics": {"icon": "⚡", "order": 1},
    "Chemistry": {"icon": "🧪", "order": 2},
    "Biology": {"icon": "🧬", "order": 3},
    "Computer Science": {"icon": "💻", "order": 4},
    "Economics": {"icon": "📊", "order": 5},
    "History": {"icon": "📜", "order": 6},
    "Geography": {"icon": "🌍", "order": 7},
    "Music": {"icon": "🎵", "order": 8},
    "Sports": {"icon": "⚽", "order": 9},
}


def copy_image(src_path, task_id, suffix):
    """Copy image to samples dir. Returns relative path from static/images/."""
    ext = os.path.splitext(src_path)[1]
    dst_name = f"{task_id}_{suffix}{ext}"
    dst_path = os.path.join(SAMPLES_DIR, dst_name)
    shutil.copy2(src_path, dst_path)
    return f"samples/{dst_name}"


def main():
    # Load data sources
    data_cache = {}
    for path in [SUBSET_JSON, SIMPLE_JSON]:
        with open(path) as f:
            data_cache[path] = json.load(f)

    # Build output structure
    output = {}

    for source, idx_or_tid, discipline, display_taxonomy in SAMPLES:
        data_list = data_cache[source]

        # Get the item
        if isinstance(idx_or_tid, int):
            item = data_list[idx_or_tid]
        else:
            # Search by task_id
            item = next(x for x in data_list if x["task_id"] == idx_or_tid)

        task_id = item["task_id"]
        input_rel = copy_image(item["image_path"], task_id, "input")
        gt_rel = copy_image(item["gt"], task_id, "gt")

        if discipline not in output:
            output[discipline] = {
                "display_name": discipline,
                "icon": DISCIPLINE_META[discipline]["icon"],
                "order": DISCIPLINE_META[discipline]["order"],
                "taxonomies": {},
            }

        output[discipline]["taxonomies"][display_taxonomy] = {
            "task_id": task_id,
            "text": item["text"],
            "input_img": input_rel,
            "gt_img": gt_rel,
            "consistency": CONSISTENCY_MAP.get(item["consistency"], item["consistency"]),
            "questions": item["questions"],
        }

    # Write samples.json
    out_path = os.path.join(DATA_DIR, "samples.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Stats
    total_samples = sum(len(v["taxonomies"]) for v in output.values())
    print(f"Generated {total_samples} samples across {len(output)} disciplines")
    print(f"Images saved to: {SAMPLES_DIR}")
    print(f"JSON saved to: {out_path}")


if __name__ == "__main__":
    main()
