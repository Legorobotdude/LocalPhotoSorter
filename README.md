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
- **Priority Categories**: Set specific categories as priority to ensure they are favored when the model is confident about them
- **Adaptive Threshold**: Automatically adjusts confidence threshold based on priority category distribution
- **Multiple Output Modes**: 
  - Move: Organize photos into category folders
  - Copy: Create category folders while preserving original files
  - Report: Generate detailed analysis without moving files
- **Ambiguity Handling**:
  - Single: Use highest confidence category
  - Multiple: Allow multiple categories when confidence is high

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

3. Enter the directory containing your photos

4. Enter categories (comma-separated) for classification

5. Enter priority categories (comma-separated) - these will be favored when the model is confident

6. Choose confidence threshold:
   - Enter a value (0.0-1.0)
   - Or press Enter for adaptive threshold based on priority categories

7. Select ambiguity mode:
   - Single: Use highest confidence category
   - Multiple: Allow multiple categories when confidence is high

8. Choose output mode:
   - Move: Organize photos into category folders
   - Copy: Create category folders while preserving original files
   - Report: Generate detailed analysis without moving files

9. Choose whether to scan subfolders

10. Review settings and confirm

11. Wait for processing to complete

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