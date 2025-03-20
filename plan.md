Discrete Steps for Sub-LLM GUI Development
Step 1: Setup GUI Framework and Basic Window

Objective: Create a basic GUI window with modern styling (unchanged from before).
Tasks:
Install ttkbootstrap and import with Tkinter.
Create a window titled “Photo Sorter” with a darkly theme.
Add a welcome label.
Output: A visible GUI window.
Stop for Feedback: Display and print “GUI window opened. Looks good? (Y/N)”
Specific Instruction for Sub-LLM:
text

Collapse

Wrap

Copy
Run `pip install ttkbootstrap` in your terminal. In a new file, import `ttkbootstrap as ttk` and `from tkinter import *`. Create `root = ttk.Window()`, set `root.title('Photo Sorter')`, apply `style = ttk.Style(theme='darkly')`. Add `label = ttk.Label(root, text='Welcome to Photo Sorter')` and `label.pack(pady=10)`. Show with `root.mainloop()`. Before the loop, print 'GUI window opened. Looks good? (Y/N)' and wait for my response (close window to answer). Stop here.
Step 2: Add GUI Input Fields with Priority Categories

Objective: Add all input widgets, including priority categories.
Tasks:
Add:
Entry for photo folder with “Browse” button.
Entry for categories (comma-separated).
Entry for confidence threshold (default 0.7, optional for adaptive).
Dropdown for ambiguity mode (Single/Multi, default Multi).
Dropdown for output mode (Move/Copy/Tag/Report, default Report).
Checkbox for “Enable Preprocessing” (default unchecked).
New: Entry for priority categories (comma-separated, optional).
“Start” button (disabled for now).
Use ttk widgets, organize with pack.
Output: GUI with all input fields.
Stop for Feedback: Display and print “Input fields added. Layout OK? (Y/N)”
Specific Instruction for Sub-LLM:
text

Collapse

Wrap

Copy
Start with Step 1 code, remove mainloop. Add `folder_entry = ttk.Entry(root)` and `browse_btn = ttk.Button(root, text='Browse')`, pack with `folder_entry.pack(pady=5)` and `browse_btn.pack(pady=5)`. Add `cat_entry = ttk.Entry(root)`, pack with `cat_entry.pack(pady=5)`. Add `thresh_entry = ttk.Entry(root)`, set `thresh_entry.insert(0, '0.7')`, pack with `thresh_entry.pack(pady=5)`. Add `ambig_combo = ttk.Combobox(root, values=['Single', 'Multi'])`, set `ambig_combo.set('Multi')`, pack with `ambig_combo.pack(pady=5)`. Add `output_combo = ttk.Combobox(root, values=['Move', 'Copy', 'Tag', 'Report'])`, set `output_combo.set('Report')`, pack with `output_combo.pack(pady=5)`. Add `preprocess_var = BooleanVar()` and `preprocess_check = ttk.Checkbutton(root, text='Enable Preprocessing', variable=preprocess_var)`, pack with `preprocess_check.pack(pady=5)`. Add `priority_entry = ttk.Entry(root)` with label `ttk.Label(root, text='Priority Categories (comma-separated, optional)').pack(pady=5)` and `priority_entry.pack(pady=5)`. Add `start_btn = ttk.Button(root, text='Start')`, pack with `start_btn.pack(pady=10)`. Show with `root.mainloop()`. Print 'Input fields added. Layout OK? (Y/N)' and stop for my response.
Step 3: Implement Folder Browsing and Input Validation

Objective: Enable folder selection and validate inputs, including priority categories.
Tasks:
Import tkinter.filedialog, link “Browse” to filedialog.askdirectory().
Define validate_inputs():
Folder exists with .jpg, .png, .webp (use validate_photo_directory).
Categories split into non-empty list (use validate_categories).
Threshold is float 0-1 or None (use validate_threshold).
Ambiguity and output modes valid (use validate_mode).
Priority categories: Split, ensure subset of main categories or empty.
Store in a settings dict.
Output: Validated settings with priority_categories.
Stop for Feedback: Print “Settings: [settings]. Valid? (Y/N)”
Specific Instruction for Sub-LLM:
text

Collapse

Wrap

Copy
Add `from tkinter import filedialog` and import your script’s `validate_photo_directory`, `validate_categories`, `validate_threshold`, `validate_mode`. Define `browse_folder()`: set `folder_path = filedialog.askdirectory()`, update `folder_entry.delete(0, END)` then `folder_entry.insert(0, folder_path)`. Link `browse_btn.config(command=browse_folder)`. Define `validate_inputs()`: get `folder = folder_entry.get()`, check with `photo_dir = validate_photo_directory(folder)`; get `categories = validate_categories(cat_entry.get())`; get `threshold_str = thresh_entry.get()`, set `threshold = None if not threshold_str.strip() else validate_threshold(threshold_str)`; get `ambig_mode = validate_mode(ambig_combo.get(), ['single', 'multi'], 'multi')`, `output_mode = validate_mode(output_combo.get(), ['move', 'copy', 'tag', 'report'], 'report')`, `preprocess = preprocess_var.get()`; get `priority_str = priority_entry.get().strip()`, set `priority_categories = [cat.strip() for cat in priority_str.split(',') if cat.strip()] if priority_str else []`, check `all(cat in categories for cat in priority_categories)` or raise ValueError("Priority categories must be a subset of main categories"). Return `settings = {'photo_dir': photo_dir, 'categories': categories, 'threshold': threshold, 'ambiguity_mode': ambig_mode, 'output_mode': output_mode, 'scan_subfolders': True, 'priority_categories': priority_categories}`. Print "Settings: [settings]. Valid? (Y/N)" after `root.mainloop()` and stop for my response.
Step 4: Initialize LM Studio and Test Single Image

Objective: Connect to LM Studio and test with priority-aware prompt.
Tasks:
Import LMStudioClient from your script, initialize with client = LMStudioClient().
Update client.analyze_image() prompt (from CLI Step 2) to favor priority categories.
Test with first image from folder, mocking if needed.
Output: Sample analysis result.
Stop for Feedback: Print “Processed [image] -> [result]. Priority OK? (Y/N)”
Specific Instruction for Sub-LLM:
text

Collapse

Wrap

Copy
Import `LMStudioClient` from your script. Create `client = LMStudioClient()` and `client.load_model('qwen2-vl-2b-instruct')`. In your script, update `analyze_image()` prompt: `priority_list = "\n".join([f"- {cat} (priority)" for cat in categories if cat in priority_categories])`; `regular_list = "\n".join([f"- {cat}" for cat in categories if cat not in priority_categories])`; `prompt = f"""Analyze this image and assign it to one or more of these EXACT categories (do not create new ones). Favor priority categories when confident:\n{priority_list}\n{regular_list}\nReturn as JSON: {{"categories": [{{"name": "category", "confidence": 0.9}}]}}"""`. Test with `settings` from Step 3, get first image from `Path(settings['photo_dir']).glob('*.jpg')`, mock `client.analyze_image()` to return `{"categories": [{"name": "Cosplay", "confidence": 0.95}, {"name": "Family", "confidence": 0.8}]}` if no real image. Print "Processed [image] -> [result]. Priority OK? (Y/N)" and stop for my response.
Step 5: Process Images with GUI Feedback

Objective: Process all images, integrating priority logic, with GUI updates.
Tasks:
Add ttk.Progressbar and ttk.Label for feedback.
Define process_images():
Scan images with scan_images(settings['photo_dir'], settings['scan_subfolders']).
Process each with client.analyze_image(), store in results.
Update progress and status.
Link to “Start” button (use your script’s process_all_images logic).
Output: results dict, updated GUI.
Stop for Feedback: Print “Processed X images. Results OK? (Y/N)”
Specific Instruction for Sub-LLM:
text

Collapse

Wrap

Copy
Add `progress = ttk.Progressbar(root, maximum=100)` and `status = ttk.Label(root, text='Ready')`, pack with `progress.pack(pady=5)` and `status.pack(pady=5)`. Define `process_images()`: call `image_list = scan_images(settings['photo_dir'], settings['scan_subfolders'])` from your script; set `results = {}`; for `i, img in enumerate(image_list)`: `result = client.analyze_image(img, settings['categories'], settings['threshold'])`, `results[img] = result`, update `progress['value'] = (i+1)/len(image_list)*100`, `status.config(text=f'Processing {i+1}/{len(image_list)}')`. Link `start_btn.config(command=process_images)`. Run and print "Processed [len(image_list)] images. Results OK? (Y/N)" and stop for my response.
Step 6: Display and Output Results with Priority Logic

Objective: Show results in GUI and apply output mode with priority.
Tasks:
Add ttk.Treeview for results (image, category, confidence).
Use your script’s output_results() with priority logic (from CLI Step 3).
Apply priority in "move" mode: If a priority category ≥ threshold, use it exclusively.
Output: Organized images, GUI with results.
Stop for Feedback: Print “Output done. Priority respected? (Y/N)”
Specific Instruction for Sub-LLM:
text

Collapse

Wrap

Copy
Add `tree = ttk.Treeview(root, columns=('Image', 'Category', 'Confidence'), show='headings')`, pack with `tree.pack(pady=10)`. Set `tree.heading('Image', text='Image')`, `tree.heading('Category', text='Category')`, `tree.heading('Confidence', text='Confidence')`. For each `img, result in results.items()`: parse `result_json = json.loads(result.strip('`').replace('json\n', ''))`, `cats = ', '.join([f"{c['name']} ({c['confidence']})" for c in result_json['categories']])`, insert `tree.insert('', 'end', values=(img.name, cats, ''))`. Call `output_results(results, settings)` from your script (with priority logic from CLI Step 3). Print "Output done. Priority respected? (Y/N)" and stop for my response.