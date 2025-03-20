import os
from pathlib import Path
import requests
import json
import base64
import shutil

class LMStudioClient:
    def __init__(self, base_url="http://localhost:1234"):
        self.base_url = base_url
        self.model = None
        self.available_models = []
    
    def get_available_models(self):
        """Get list of available models from LM Studio."""
        try:
            response = requests.get(f"{self.base_url}/v1/models")
            if response.status_code == 200:
                models = response.json().get('data', [])
                return models
            return []
        except Exception as e:
            print(f"Error getting available models: {str(e)}")
            return []
    
    def load_model(self, model_name=None):
        """Load the specified model in LM Studio."""
        try:
            # Check if LM Studio is running
            self.available_models = self.get_available_models()
            if not self.available_models:
                raise ValueError("No models found in LM Studio. Please load a model first.")
            
            # If no model specified, let user choose
            if not model_name:
                print("\nAvailable models:")
                for i, model in enumerate(self.available_models, 1):
                    print(f"{i}. {model['id']}")
                
                while True:
                    try:
                        choice = int(input("\nSelect a model number (or 0 to exit): "))
                        if choice == 0:
                            raise ValueError("No model selected")
                        if 1 <= choice <= len(self.available_models):
                            model_name = self.available_models[choice-1]['id']
                            break
                        print("Invalid selection. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")
            
            # Load the model
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": "Hello"}]
                }
            )
            
            if response.status_code != 200:
                raise ValueError(f"Failed to load model: {response.text}")
            
            self.model = model_name
            print(f"\nSuccessfully loaded model: {model_name}")
            return True
            
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Could not connect to LM Studio. Is it running?")
        except Exception as e:
            raise Exception(f"Error loading model: {str(e)}")
    
    def test_connection(self):
        """Test the connection to LM Studio."""
        try:
            response = requests.get(f"{self.base_url}/v1/models")
            return response.status_code == 200
        except:
            return False
    
    def analyze_image(self, image_path, categories, threshold, settings):
        """Analyze a single image and return category assignments."""
        try:
            # Read the image file and encode as base64
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Create the prompt with priority categories first
            priority_list = "\n".join([f"- {cat} (priority)" for cat in categories if cat in settings.get('priority_categories', [])])
            regular_list = "\n".join([f"- {cat}" for cat in categories if cat not in settings.get('priority_categories', [])])
            
            prompt = f"""Analyze this image and assign it to one or more of these EXACT categories (do not create new ones). Favor priority categories when confident:

{priority_list}
{regular_list}

Return the category(ies) and a confidence score (0-1) for each.
Format your response as JSON: {{"categories": [{{"name": "category", "confidence": 0.9}}]}}
IMPORTANT: Only use the categories listed above. Do not create or suggest new categories."""
            
            # Send request to LM Studio with base64 image data
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_data}"
                                    }
                                }
                            ]
                        }
                    ]
                }
            )
            
            if response.status_code != 200:
                raise ValueError(f"Failed to analyze image: {response.text}")
            
            # Parse the response
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Validate that only user-specified categories are used
            try:
                json_str = content.strip('`').strip()
                if json_str.startswith('json\n'):
                    json_str = json_str[5:].strip()
                result_json = json.loads(json_str)
                
                # Filter out any hallucinated categories
                valid_categories = []
                for cat in result_json['categories']:
                    if cat['name'] in categories:
                        valid_categories.append(cat)
                    else:
                        print(f"Warning: Ignoring hallucinated category '{cat['name']}' for {image_path.name}")
                
                # Update the response with only valid categories
                result_json['categories'] = valid_categories
                return json.dumps(result_json)
                
            except Exception as e:
                print(f"Error validating categories: {str(e)}")
                return json.dumps({"categories": []})
            
        except Exception as e:
            raise Exception(f"Error analyzing image: {str(e)}")

def validate_photo_directory(path):
    """Validate if the directory exists and contains image files."""
    # Remove any quotes from the path
    path = path.strip("'\"")
    photo_dir = Path(path)
    
    if not photo_dir.exists():
        raise ValueError(f"Directory does not exist: {path}")
    
    if not photo_dir.is_dir():
        raise ValueError(f"Path is not a directory: {path}")
    
    # Check for images in the directory and all subfolders
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    has_images = False
    
    # Check top-level directory
    has_images = any(f.suffix.lower() in image_extensions for f in photo_dir.iterdir())
    
    # If no images in top directory, check subfolders
    if not has_images:
        for root, dirs, files in os.walk(photo_dir):
            if any(f.lower().endswith(tuple(image_extensions)) for f in files):
                has_images = True
                break
    
    if not has_images:
        raise ValueError(f"No image files found in directory or its subfolders: {path}")
    
    return photo_dir

def validate_categories(categories_str):
    """Validate and process the categories string."""
    if not categories_str.strip():
        raise ValueError("Categories cannot be empty")
    
    categories = [cat.strip() for cat in categories_str.split(',')]
    categories = [cat for cat in categories if cat]  # Remove empty strings
    if not categories:
        raise ValueError("No valid categories provided")
    
    return categories

def validate_threshold(threshold_str):
    """Validate the confidence threshold."""
    try:
        threshold = float(threshold_str)
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        return threshold
    except ValueError:
        raise ValueError("Threshold must be a valid number between 0 and 1")

def validate_mode(mode, valid_modes, default_mode):
    """Validate the mode input."""
    mode = mode.strip().lower()
    if not mode:
        return default_mode
    if mode not in valid_modes:
        raise ValueError(f"Mode must be one of: {', '.join(valid_modes)}")
    return mode

def collect_user_inputs():
    """Collect and validate all user inputs."""
    print("\n=== Photo Sorter Setup ===\n")
    
    # Get photo directory
    while True:
        photo_dir = input("Enter the path to your photo folder: ").strip()
        try:
            photo_dir = validate_photo_directory(photo_dir)
            break
        except ValueError as e:
            print(f"Error: {e}")
    
    # Get categories
    while True:
        categories_str = input("Enter categories (comma-separated, e.g., 'Family, Vacation, Pets'): ").strip()
        try:
            categories = validate_categories(categories_str)
            break
        except ValueError as e:
            print(f"Error: {e}")
    
    # Get priority categories
    while True:
        priority_categories_str = input("Enter priority categories (comma-separated subset of previous categories, or none): ").strip()
        try:
            if not priority_categories_str:
                priority_categories = []
            else:
                priority_categories = [cat.strip() for cat in priority_categories_str.split(',') if cat.strip()]
                if not all(cat in categories for cat in priority_categories):
                    raise ValueError("Priority categories must be a subset of main categories")
            break
        except ValueError as e:
            print(f"Error: {e}")
    
    # Get confidence threshold
    while True:
        threshold_str = input("Enter confidence threshold (0-1, default adaptive): ").strip()
        try:
            if not threshold_str:
                threshold = None  # Will use adaptive threshold
            else:
                threshold = validate_threshold(threshold_str)
            break
        except ValueError as e:
            print(f"Error: {e}")
    
    # Get ambiguity mode
    while True:
        ambiguity_mode = input("Enter ambiguity mode (single/multi, default multi): ").strip()
        try:
            ambiguity_mode = validate_mode(ambiguity_mode, ['single', 'multi'], 'multi')
            break
        except ValueError as e:
            print(f"Error: {e}")
    
    # Get output mode
    while True:
        output_mode = input("Enter output mode (move/copy/tag/report, default report): ").strip()
        try:
            output_mode = validate_mode(output_mode, ['move', 'copy', 'tag', 'report'], 'report')
            break
        except ValueError as e:
            print(f"Error: {e}")
    
    # Get scan subfolders option
    while True:
        scan_subfolders = input("Scan subfolders for images? (yes/no, default yes): ").strip().lower()
        try:
            scan_subfolders = validate_mode(scan_subfolders, ['yes', 'no'], 'yes') == 'yes'
            break
        except ValueError as e:
            print(f"Error: {e}")
    
    # Print summary
    print("\n=== Settings Summary ===")
    print(f"Photo Directory: {photo_dir}")
    print(f"Categories: {', '.join(categories)}")
    print(f"Priority Categories: {', '.join(priority_categories) if priority_categories else 'None'}")
    print(f"Confidence Threshold: {'Adaptive' if threshold is None else threshold}")
    print(f"Ambiguity Mode: {ambiguity_mode}")
    print(f"Output Mode: {output_mode}")
    print(f"Scan Subfolders: {'Yes' if scan_subfolders else 'No'}")
    
    # Ask for confirmation
    while True:
        confirm = input("\nAre these settings correct? (Y/N): ").strip().upper()
        if confirm in ['Y', 'N']:
            break
        print("Please enter Y or N")
    
    if confirm == 'N':
        print("Please run the program again with correct settings.")
        return None
    
    return {
        'photo_dir': photo_dir,
        'categories': categories,
        'priority_categories': priority_categories,
        'threshold': threshold,
        'ambiguity_mode': ambiguity_mode,
        'output_mode': output_mode,
        'scan_subfolders': scan_subfolders
    }

def scan_images(photo_dir, scan_subfolders=True):
    """Scan for images in the specified directory and optionally its subfolders."""
    print("\n=== Scanning Images ===\n")
    
    image_list = []
    skipped_files = []
    
    if scan_subfolders:
        # Walk through all subdirectories
        for root, dirs, files in os.walk(photo_dir):
            for file in files:
                file_path = Path(root) / file
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    image_list.append(file_path)
                else:
                    skipped_files.append(f"{file_path}: Not an image file")
    else:
        # Only scan the specified directory
        for file_path in photo_dir.iterdir():
            if file_path.is_file():
                if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                    image_list.append(file_path)
                else:
                    skipped_files.append(f"{file_path}: Not an image file")
    
    print(f"Found {len(image_list)} valid images")
    
    if skipped_files:
        print("\nSkipped files:")
        for file in skipped_files:
            print(f"- {file}")
    
    return image_list

def initialize_lm_studio():
    """Initialize connection to LM Studio."""
    print("\n=== Initializing LM Studio ===\n")
    
    try:
        client = LMStudioClient()
        if client.load_model():
            return client
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def process_single_image(client, image_path, settings):
    """Process a single image as a test case."""
    print(f"\n=== Processing Test Image: {image_path.name} ===\n")
    
    try:
        # Analyze the image
        result = client.analyze_image(
            image_path,
            settings['categories'],
            settings['threshold'],
            settings
        )
        
        # Print the result
        print(f"Analysis Result:\n{result}")
        return result
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None

def process_all_images(client, image_list, settings):
    """Process all images in the list."""
    print("\n=== Processing All Images ===\n")
    results = {}
    
    # Process all images, including the first one
    for i, image_path in enumerate(image_list, 1):
        print(f"\nProcessing image {i}/{len(image_list)}: {image_path.name}")
        try:
            result = client.analyze_image(
                image_path,
                settings['categories'],
                settings['threshold'],
                settings
            )
            if result:
                # Extract JSON from markdown code block
                json_str = result.strip('`').strip()
                if json_str.startswith('json\n'):
                    json_str = json_str[5:].strip()
                results[image_path] = json_str
                print(f"Result: {json_str}")
            else:
                print(f"Failed to analyze {image_path.name}")
        except Exception as e:
            print(f"Error processing {image_path.name}: {str(e)}")
    
    print("\nProcessing complete!")
    return results

def calculate_adaptive_threshold(results, settings):
    """Calculate an adaptive threshold based on confidence score distribution."""
    all_confidences = []
    priority_confidences = []
    
    # Collect all confidence scores
    for result in results.values():
        try:
            json_str = result.strip('`').strip()
            if json_str.startswith('json\n'):
                json_str = json_str[5:].strip()
            result_json = json.loads(json_str)
            
            # Separate priority and non-priority confidences
            for cat in result_json['categories']:
                if cat['name'] in settings.get('priority_categories', []):
                    priority_confidences.append(cat['confidence'])
                all_confidences.append(cat['confidence'])
        except Exception:
            continue
    
    if not all_confidences:
        return 0.7  # Default threshold if no valid scores
    
    # If we have priority categories, use their distribution
    if priority_confidences:
        sorted_confidences = sorted(priority_confidences, reverse=True)
    else:
        sorted_confidences = sorted(all_confidences, reverse=True)
    
    # Find the steepest drop in confidence scores
    max_drop = 0
    threshold_idx = 0
    
    for i in range(len(sorted_confidences) - 1):
        drop = sorted_confidences[i] - sorted_confidences[i + 1]
        if drop > max_drop:
            max_drop = drop
            threshold_idx = i
    
    # Use the confidence score at the steepest drop as threshold
    adaptive_threshold = sorted_confidences[threshold_idx]
    
    print(f"\nAdaptive threshold calculated: {adaptive_threshold:.3f}")
    if priority_confidences:
        print(f"Based on priority categories distribution")
    return adaptive_threshold

def output_results(results, settings):
    """Organize images based on user-selected output mode."""
    print("\n=== Processing Output ===\n")
    
    base_dir = settings['photo_dir']
    
    # Create category directories
    for category in settings['categories']:
        category_dir = base_dir / category
        category_dir.mkdir(exist_ok=True)
    
    # Create Uncertain directory
    uncertain_dir = base_dir / 'Uncertain'
    uncertain_dir.mkdir(exist_ok=True)
    
    # Calculate threshold (adaptive or fixed)
    threshold = settings['threshold'] if settings['threshold'] is not None else calculate_adaptive_threshold(results, settings)
    
    # Process each image based on output mode
    import csv
    from PIL import Image
    from PIL.ExifTags import TAGS
    
    for image_path, result in results.items():
        try:
            # Parse the JSON result
            json_str = result.strip('`').strip()
            if json_str.startswith('json\n'):
                json_str = json_str[5:].strip()
            result_json = json.loads(json_str)
            categories = result_json['categories']
            
            # Handle single mode
            if settings['ambiguity_mode'] == 'single':
                # Get highest confidence category
                top_category = max(categories, key=lambda x: x['confidence'])
                categories = [top_category]
            
            if settings['output_mode'] == 'report':
                # Report mode: No file operations needed
                continue
                
            elif settings['output_mode'] in ['move', 'copy']:
                # Check if any category meets the threshold
                has_valid_category = False
                
                # Handle priority categories in move mode
                if settings['output_mode'] == 'move' and settings.get('priority_categories'):
                    priority_hits = [cat for cat in categories if cat['name'] in settings['priority_categories'] and cat['confidence'] >= threshold]
                    if priority_hits:
                        # Use highest confidence priority category
                        best_priority = max(priority_hits, key=lambda x: x['confidence'])
                        target_dir = base_dir / best_priority['name']
                        target_path = target_dir / image_path.name
                        shutil.move(str(image_path), str(target_path))
                        has_valid_category = True
                
                # If no priority category met threshold, use standard logic
                if not has_valid_category:
                    # Process each category
                    for cat_info in categories:
                        # Only use categories that were specified by the user
                        if cat_info['name'] not in settings['categories']:
                            continue
                            
                        if cat_info['confidence'] >= threshold:
                            has_valid_category = True
                            target_dir = base_dir / cat_info['name']
                            target_path = target_dir / image_path.name
                            if settings['output_mode'] == 'move':
                                shutil.move(str(image_path), str(target_path))
                            else:  # copy
                                shutil.copy2(str(image_path), str(target_path))
                
                # If no valid categories or none meet threshold, move to Uncertain
                if not has_valid_category:
                    target_path = uncertain_dir / image_path.name
                    if settings['output_mode'] == 'move':
                        shutil.move(str(image_path), str(target_path))
                    else:  # copy
                        shutil.copy2(str(image_path), str(target_path))
                
            elif settings['output_mode'] == 'tag':
                # Add categories to EXIF data
                img = Image.open(image_path)
                exif = img.getexif()
                
                # Convert categories to string
                category_str = ','.join([
                    f"{cat['name']}({cat['confidence']:.2f})"
                    for cat in categories
                ])
                
                # Add custom tag for categories
                exif[0x9286] = category_str  # Using a custom tag number
                img.save(image_path, exif=exif)
                
        except Exception as e:
            print(f"Error processing {image_path.name}: {str(e)}")
            # Move to Uncertain on error
            if settings['output_mode'] in ['move', 'copy']:
                target_path = uncertain_dir / image_path.name
                if settings['output_mode'] == 'move':
                    shutil.move(str(image_path), str(target_path))
                else:  # copy
                    shutil.copy2(str(image_path), str(target_path))
    
    # Generate report if in report mode
    if settings['output_mode'] == 'report':
        report_path = base_dir / 'analysis_report.csv'
        with open(report_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Image', 'Categories', 'Confidence', 'Threshold'])
            
            for image_path, result in results.items():
                try:
                    json_str = result.strip('`').strip()
                    if json_str.startswith('json\n'):
                        json_str = json_str[5:].strip()
                    result_json = json.loads(json_str)
                    categories = result_json['categories']
                    
                    # Format categories and confidence scores
                    cat_str = ', '.join([
                        f"{cat['name']} ({cat['confidence']:.2f})"
                        for cat in categories
                    ])
                    
                    writer.writerow([image_path.name, cat_str, f"{threshold:.3f}"])
                except Exception as e:
                    writer.writerow([image_path.name, f"Error: {str(e)}", f"{threshold:.3f}"])
        
        print(f"\nReport generated: {report_path}")
    
    print("\nOutput processing complete!")

def move_or_copy_file(src, dst, mode="move"):
    """Move or copy a file to a destination directory."""
    try:
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        
        # Move or copy the file
        if mode == "move":
            shutil.move(src, dst)
        else:  # copy
            shutil.copy2(src, dst)
            
        return True
    except Exception as e:
        print(f"Error {mode}ing file: {str(e)}")
        return False

if __name__ == "__main__":
    settings = collect_user_inputs()
    if settings:
        client = initialize_lm_studio()
        if client:
            image_list = scan_images(settings['photo_dir'], settings['scan_subfolders'])
            if image_list:
                # Process all images
                results = process_all_images(client, image_list, settings)
                if results:
                    output_results(results, settings)
                print("\nAll processing complete!") 