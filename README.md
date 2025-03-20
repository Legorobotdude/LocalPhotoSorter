# Photo Sorter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python tool that uses LM Studio's vision model to automatically categorize photos into user-defined categories.

## Prerequisites

1. Python 3.8 or higher
2. LM Studio installed and running locally
3. A vision model loaded in LM Studio (e.g., ShareGPT)

## Installation

1. Clone this repository or download the files
2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install Pillow
```

## Usage

1. Start LM Studio and load your vision model
2. Run the script:
```bash
python photo_sorter.py
```

3. Follow the prompts to:
   - Enter the path to your photo folder
   - Specify categories (comma-separated)
   - Set confidence threshold (0-1, default 0.7)
   - Choose ambiguity mode (single/multi)
   - Select output mode (move/copy/tag/report)
   - Choose whether to scan subfolders

## Output Modes

- **Move**: Moves files to category folders
- **Copy**: Copies files to category folders
- **Tag**: Adds category information to image EXIF data
- **Report**: Generates a CSV report with analysis results

## Features

- Recursive subfolder scanning
- Multiple category support
- Confidence threshold filtering
- Single/multi category assignment
- EXIF tagging support
- Detailed analysis reports

## Notes

- Files with confidence below the threshold are marked as "Uncertain"
- In single mode, only the highest confidence category is used
- The program creates category folders automatically
- Original files are preserved when using copy or report modes 