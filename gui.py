import ttkbootstrap as ttk
from tkinter import *
from tkinter import filedialog
from pathlib import Path
from photo_sorter import validate_photo_directory, validate_categories, validate_threshold, validate_mode, LMStudioClient
import json
import threading
import shutil
from datetime import datetime

# Create the main window
root = ttk.Window()
root.title('Photo Sorter')
root.geometry('600x700')  # Set a reasonable initial size

# Apply darkly theme
style = ttk.Style(theme='darkly')

# Create canvas and scrollbar
canvas = Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

# Configure the canvas
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Pack the canvas and scrollbar
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Create main frame with padding inside scrollable frame
main_frame = ttk.Frame(scrollable_frame, padding=20)
main_frame.pack(fill=BOTH, expand=YES)

# Create status label for validation feedback
status_label = ttk.Label(main_frame, padding=10, wraplength=500)  # Add wraplength to prevent resizing
status_label.pack(fill=X, pady=(0, 10))

# Welcome label
welcome_label = ttk.Label(
    main_frame, 
    text='Welcome to Photo Sorter',
    font=('Helvetica', 16)
)
welcome_label.pack(pady=(0, 20))

# Initialize LM Studio client
client = LMStudioClient()
available_models_json = client.get_available_models()
available_models = [model['id'] for model in available_models_json]  # Extract just the model names

def update_status(message, status_type="info"):
    """Update status label with message and appropriate style."""
    status_label.configure(text=message)
    if status_type == "success":
        status_label.configure(bootstyle="success")
    elif status_type == "danger":
        status_label.configure(bootstyle="danger")
    else:
        status_label.configure(bootstyle="info")

def validate_inputs():
    """Validate all inputs and return settings dict if valid."""
    try:
        # Validate photo directory
        folder = folder_entry.get().strip()
        if not folder:
            raise ValueError("Please select a photo directory")
        photo_dir = validate_photo_directory(folder)
        
        # Validate categories
        categories = validate_categories(cat_entry.get().strip())
        if not categories:
            raise ValueError("Please enter at least one category")
            
        # Validate priority categories
        priority_cats = [cat.strip() for cat in priority_entry.get().split(',') if cat.strip()]
        if priority_cats and not all(cat in categories for cat in priority_cats):
            raise ValueError("Priority categories must be a subset of main categories")
            
        # Validate threshold
        threshold_str = thresh_entry.get().strip()
        threshold = None if not threshold_str else validate_threshold(threshold_str)
        
        # Validate modes
        ambig_mode = validate_mode(ambig_combo.get().lower(), ['single', 'multi'], 'multi')
        output_mode = validate_mode(output_combo.get().lower(), ['move', 'copy', 'report'], 'report')
        
        # Create settings dict
        settings = {
            'photo_dir': photo_dir,
            'categories': categories,
            'priority_categories': priority_cats,
            'threshold': threshold,
            'ambiguity_mode': ambig_mode,
            'output_mode': output_mode,
            'preprocess': preprocess_var.get(),
            'scan_subfolders': subfolder_var.get()
        }
        
        # Update status and enable start button
        update_status("All inputs valid!", "success")
        start_btn.configure(state='normal')
        return settings
        
    except ValueError as e:
        # Update status and disable start button
        update_status(str(e), "danger")
        start_btn.configure(state='disabled')
        return None

def on_input_change(*args):
    validate_inputs()

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_entry.delete(0, END)
        folder_entry.insert(0, folder)
        validate_inputs()

# Model Selection Section
model_frame = ttk.LabelFrame(main_frame, text='Model Selection', padding=10)
model_frame.pack(fill=X, pady=(0, 10))

ttk.Label(model_frame, text='Select Vision Model:').pack(anchor=W)
model_combo = ttk.Combobox(
    model_frame,
    values=available_models,
    state='readonly'
)
model_combo.set(available_models[0] if available_models else '')
model_combo.pack(fill=X, pady=(5, 0))

def load_selected_model():
    """Load the selected model from LM Studio."""
    selected_model = model_combo.get()
    if selected_model:
        try:
            if selected_model != client.model:  # Only load if different from current model
                client.load_model(selected_model)
            update_status(f"Successfully loaded model: {selected_model}", "success")
            return True
        except Exception as e:
            update_status(f"Error loading model: {str(e)}", "danger")
            return False
    return False

def ensure_model_loaded():
    """Ensure a model is loaded before processing."""
    selected_model = model_combo.get()
    if not selected_model:
        update_status("Please select a model first", "danger")
        return False
    if not client.model:  # If no model is currently loaded
        return load_selected_model()
    if selected_model != client.model:  # If selected model is different from loaded model
        return load_selected_model()
    return True

# Add load model button
load_model_btn = ttk.Button(
    model_frame,
    text='Load Selected Model',
    style='info.TButton',
    command=load_selected_model
)
load_model_btn.pack(pady=5)

# Photo Directory Section
dir_frame = ttk.LabelFrame(main_frame, text='Photo Directory', padding=10)
dir_frame.pack(fill=X, pady=(0, 10))

folder_entry = ttk.Entry(dir_frame)
folder_entry.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))

browse_btn = ttk.Button(
    dir_frame, 
    text='Browse',
    command=browse_folder
)
browse_btn.pack(side=LEFT)

# Categories Section
cat_frame = ttk.LabelFrame(main_frame, text='Categories', padding=10)
cat_frame.pack(fill=X, pady=(0, 10))

ttk.Label(cat_frame, text='Enter categories (comma-separated):').pack(anchor=W)
cat_entry = ttk.Entry(cat_frame)
cat_entry.pack(fill=X, pady=(5, 10))

ttk.Label(cat_frame, text='Priority categories (comma-separated, optional):').pack(anchor=W)
priority_entry = ttk.Entry(cat_frame)
priority_entry.pack(fill=X, pady=(5, 0))

# Confidence Threshold
thresh_frame = ttk.LabelFrame(main_frame, text='Confidence Threshold', padding=10)
thresh_frame.pack(fill=X, pady=(0, 10))

ttk.Label(thresh_frame, text='Enter threshold (0.0-1.0) or leave empty for adaptive:').pack(anchor=W)
thresh_entry = ttk.Entry(thresh_frame)
thresh_entry.pack(fill=X, pady=(5, 0))

# Mode Selection
mode_frame = ttk.LabelFrame(main_frame, text='Processing Modes', padding=10)
mode_frame.pack(fill=X, pady=(0, 10))

# Ambiguity Mode
ttk.Label(mode_frame, text='Ambiguity Mode:').pack(anchor=W)
ambig_combo = ttk.Combobox(
    mode_frame, 
    values=['Single', 'Multi'],
    state='readonly'
)
ambig_combo.set('Multi')
ambig_combo.pack(fill=X, pady=(5, 10))

# Output Mode
ttk.Label(mode_frame, text='Output Mode:').pack(anchor=W)
output_combo = ttk.Combobox(
    mode_frame, 
    values=['Move', 'Copy', 'Report'],
    state='readonly'
)
output_combo.set('Report')
output_combo.pack(fill=X, pady=(5, 0))

# Options
options_frame = ttk.LabelFrame(main_frame, text='Options', padding=10)
options_frame.pack(fill=X, pady=(0, 20))

preprocess_var = BooleanVar(value=False)
preprocess_check = ttk.Checkbutton(
    options_frame,
    text='Enable Preprocessing',
    variable=preprocess_var
)
preprocess_check.pack(anchor=W)

subfolder_var = BooleanVar(value=True)
subfolder_check = ttk.Checkbutton(
    options_frame,
    text='Scan Subfolders',
    variable=subfolder_var
)
subfolder_check.pack(anchor=W)

# Start Button
start_btn = ttk.Button(
    main_frame,
    text='Start Processing',
    style='primary.TButton',
    state='disabled'  # Will be enabled when inputs are valid
)
start_btn.pack(pady=10)

# Bind validation to input changes
folder_entry.bind('<KeyRelease>', on_input_change)
cat_entry.bind('<KeyRelease>', on_input_change)
priority_entry.bind('<KeyRelease>', on_input_change)
thresh_entry.bind('<KeyRelease>', on_input_change)
ambig_combo.bind('<<ComboboxSelected>>', on_input_change)
output_combo.bind('<<ComboboxSelected>>', on_input_change)

# Bind checkbox changes
preprocess_var.trace_add('write', on_input_change)
subfolder_var.trace_add('write', on_input_change)

# Initial validation
validate_inputs()

print('Input fields added. Layout OK? (Y/N)')

# Add mousewheel scrolling
def _on_mousewheel(event):
    # Handle both trackpad and mouse wheel events on macOS
    if event.num == 4:  # Linux scroll up
        delta = -1
    elif event.num == 5:  # Linux scroll down
        delta = 1
    else:  # macOS and Windows
        delta = -1 * (event.delta / 120)
    canvas.yview_scroll(int(delta), "units")

# Bind both mousewheel and trackpad events
canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
canvas.bind_all("<Button-4>", _on_mousewheel)    # Linux scroll up
canvas.bind_all("<Button-5>", _on_mousewheel)    # Linux scroll down

def test_single_image():
    """Test LM Studio with a single image."""
    settings = validate_inputs()
    if not settings or not ensure_model_loaded():
        return
    
    # Disable buttons during processing
    test_btn.configure(state='disabled')
    start_btn.configure(state='disabled')
    load_model_btn.configure(state='disabled')
    
    def test_in_thread():
        try:
            # Get first image from directory
            photo_dir = Path(settings['photo_dir'])
            image_files = set()  # Use a set to prevent duplicates
            for ext in ('*.jpg', '*.jpeg', '*.png', '*.webp'):
                if settings['scan_subfolders']:
                    image_files.update(photo_dir.rglob(ext))
                else:
                    image_files.update(photo_dir.glob(ext))
            
            image_files = sorted(list(image_files))  # Convert back to sorted list
            
            if not image_files:
                root.after(0, lambda: update_status("No images found in directory", "danger"))
                return
                
            test_image = image_files[0]
            try:
                result = client.analyze_image(test_image, settings['categories'], settings['threshold'], settings)
                root.after(0, lambda: update_status(f"Test result for {test_image.name}: {result}", "success"))
            except Exception as e:
                root.after(0, lambda: update_status(f"Error processing {test_image.name}: {str(e)}", "danger"))
                
        finally:
            # Re-enable buttons
            root.after(0, lambda: [
                test_btn.configure(state='normal'),
                start_btn.configure(state='normal'),
                load_model_btn.configure(state='normal')
            ])
    
    # Start testing in a separate thread
    threading.Thread(target=test_in_thread, daemon=True).start()

# Add test button in a frame to maintain layout
test_frame = ttk.Frame(main_frame)
test_frame.pack(fill=X, pady=5)

test_btn = ttk.Button(
    test_frame,
    text='Test with First Image',
    style='info.TButton',
    command=test_single_image,
    width=20  # Set fixed width
)
test_btn.pack()

# Create progress bar (initially hidden)
progress_frame = ttk.LabelFrame(main_frame, text='Progress', padding=10)
progress_frame.pack(fill=X, pady=(0, 10))
progress_frame.pack_forget()  # Hide initially

progress_bar = ttk.Progressbar(
    progress_frame,
    mode='determinate',
    length=200
)
progress_bar.pack(fill=X, pady=(0, 5))

progress_label = ttk.Label(progress_frame, text='')
progress_label.pack(fill=X)

def process_images():
    """Process all images in the directory."""
    settings = validate_inputs()
    if not settings or not ensure_model_loaded():
        return
    
    # Disable buttons during processing
    start_btn.configure(state='disabled')
    test_btn.configure(state='disabled')
    load_model_btn.configure(state='disabled')
    
    def process_in_thread():
        try:
            # Show progress frame
            root.after(0, lambda: progress_frame.pack(fill=X, pady=(0, 10)))
            
            # Collect all image files using a set to prevent duplicates
            photo_dir = Path(settings['photo_dir'])
            image_files = set()
            for ext in ('*.jpg', '*.jpeg', '*.png', '*.webp'):
                if settings['scan_subfolders']:
                    image_files.update(photo_dir.rglob(ext))
                else:
                    image_files.update(photo_dir.glob(ext))
            
            image_files = sorted(list(image_files))  # Convert back to sorted list
            
            if not image_files:
                root.after(0, lambda: [
                    update_status("No images found in directory", "danger"),
                    progress_frame.pack_forget()
                ])
                return
            
            total_images = len(image_files)
            processed = 0
            results = []
            
            # Process each image
            for image_file in image_files:
                try:
                    # Update progress
                    processed += 1
                    progress = (processed / total_images) * 100
                    root.after(0, lambda p=progress, f=image_file.name, c=processed: [
                        progress_bar.configure(value=p),
                        progress_label.configure(text=f'Processing {f} ({c}/{total_images})')
                    ])
                    
                    # Analyze image
                    result = client.analyze_image(image_file, settings['categories'], settings['threshold'], settings)
                    results.append((image_file, json.loads(result)))
                    
                except Exception as e:
                    root.after(0, lambda err=str(e), f=image_file.name: 
                        update_status(f"Error processing {f}: {err}", "danger")
                    )
            
            # Handle results based on output mode
            if settings['output_mode'] == 'report':
                # Generate report file
                report_file = photo_dir / 'photo_sort_report.txt'
                with open(report_file, 'w') as f:
                    f.write(f"Photo Sorting Report\n")
                    f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"Settings:\n")
                    f.write(f"- Categories: {', '.join(settings['categories'])}\n")
                    f.write(f"- Priority Categories: {', '.join(settings['priority_categories'])}\n")
                    f.write(f"- Threshold: {settings['threshold']}\n")
                    f.write(f"- Ambiguity Mode: {settings['ambiguity_mode']}\n\n")
                    
                    f.write(f"Results:\n")
                    f.write("-" * 80 + "\n\n")
                    
                    for image_file, result in results:
                        f.write(f"Image: {image_file.name}\n")
                        for cat in result['categories']:
                            priority = " (Priority)" if cat['name'] in settings['priority_categories'] else ""
                            f.write(f"- {cat['name']}{priority}: {cat['confidence']:.2%}\n")
                        f.write("\n")
                
                root.after(0, lambda: update_status(
                    f"Processed {processed} images successfully! Report saved to {report_file}", 
                    "success"
                ))
                
            elif settings['output_mode'] in ['move', 'copy']:
                # Create category folders and move/copy files
                for category in settings['categories']:
                    category_dir = photo_dir / category
                    category_dir.mkdir(exist_ok=True)
                
                for image_file, result in results:
                    # Get highest confidence category for the image
                    if result['categories']:
                        top_category = max(result['categories'], key=lambda x: x['confidence'])
                        if top_category['confidence'] >= (settings['threshold'] or 0.5):
                            dest_dir = photo_dir / top_category['name']
                            dest_file = dest_dir / image_file.name
                            
                            try:
                                if settings['output_mode'] == 'move':
                                    shutil.move(str(image_file), str(dest_file))
                                else:  # copy
                                    shutil.copy2(str(image_file), str(dest_file))
                            except Exception as e:
                                root.after(0, lambda err=str(e), f=image_file.name: 
                                    update_status(f"Error processing {f}: {err}", "danger")
                                )
                
                root.after(0, lambda: update_status(
                    f"Processed {processed} images successfully! Files have been {settings['output_mode']}d to category folders.", 
                    "success"
                ))
            
            # Hide progress frame
            root.after(0, lambda: progress_frame.pack_forget())
            
        finally:
            # Re-enable buttons
            root.after(0, lambda: [
                start_btn.configure(state='normal'),
                test_btn.configure(state='normal'),
                load_model_btn.configure(state='normal')
            ])
    
    # Start processing in a separate thread
    threading.Thread(target=process_in_thread, daemon=True).start()

# Update start button command
start_btn.configure(command=process_images)

root.mainloop() 