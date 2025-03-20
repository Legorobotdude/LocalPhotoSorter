# Photo Sorter

A Python tool that uses LM Studio's vision models to automatically organize photos into categories based on their content.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- Uses LM Studio's vision models to analyze photos
- Supports multiple categories per photo
- Handles ambiguous cases with single/multi category modes
- Moves, copies, or tags photos based on content
- Generates detailed CSV reports
- Adaptive confidence thresholding
- Supports subfolder scanning
- Handles various image formats (JPG, PNG, WEBP)

## Prerequisites

- Python 3.6 or higher
- LM Studio installed and running locally
- A vision model loaded in LM Studio

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/photo-sorter.git
cd photo-sorter
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start LM Studio and load a vision model
2. Run the script:
```bash
python photo_sorter.py
```

3. Follow the prompts to:
   - Enter your photo directory path
   - Specify categories (comma-separated)
   - Set confidence threshold (or use adaptive thresholding)
   - Choose ambiguity mode (single/multi)
   - Select output mode (move/copy/tag/report)
   - Choose whether to scan subfolders

### Adaptive Thresholding

The tool includes an adaptive thresholding feature that automatically determines the optimal confidence threshold based on the distribution of confidence scores across all analyzed images. This helps ensure consistent categorization across different types of images and models.

When using adaptive thresholding (default):
1. The tool analyzes all images first
2. Calculates confidence scores for each image
3. Identifies the steepest drop in confidence scores
4. Uses this point as the threshold for categorization

You can still specify a fixed threshold (0-1) if you prefer manual control.

### Output Modes

- **Move**: Moves photos to category folders (original files are deleted)
- **Copy**: Copies photos to category folders (original files are preserved)
- **Tag**: Adds category information to photo EXIF data
- **Report**: Generates a CSV report with category assignments

### Ambiguity Modes

- **Single**: Uses only the highest confidence category
- **Multi**: Allows multiple categories if confidence is high enough

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 