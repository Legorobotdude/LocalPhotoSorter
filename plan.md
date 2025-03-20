
### Updated Plan with Simplified Priority Categories
- **Priority Categories**:
  - Users specify a subset of categories as "priority" (e.g., "Cosplay") during input.
  - No separate priority threshold; use the existing `threshold` (fixed or adaptive).
  - In "move" mode:
    - If a priority category meets/exceeds the threshold, move the image to that category exclusively (highest confidence if multiple priorities qualify).
    - Otherwise, fall back to standard ambiguity mode logic.
- **LLM Prompt**: Modify to emphasize priority categories, encouraging the model to assign higher confidence to them when applicable.
- **Post-Processing**: Reinforce priority in code if the LLM doesn’t fully comply.
- **User Experience**: No extra inputs beyond listing priority categories, keeping it simple.

---

### Discrete Steps for Sub-LLM Development

#### Step 1: Update User Input Collection for Priority Categories
- **Objective**: Add priority categories to `collect_user_inputs()` without a separate threshold.
- **Tasks**:
  - After collecting `categories`, prompt for priority categories (comma-separated subset).
  - Validate they’re a subset of `categories`.
  - Store in `settings` as `priority_categories`.
  - Update the summary to show them.
- **Output**: Updated `settings` with `priority_categories`.
- **Stop for Feedback**: Print settings and ask “Settings correct? (Y/N)”
- **Specific Instruction for Sub-LLM**:
  ```
  Open your script, find `collect_user_inputs()`. After `categories = validate_categories(categories_str)`, add: print("Enter priority categories (comma-separated subset of previous categories, or none): "); get `priority_categories_str = input().strip()`; if empty, set `priority_categories = []`, else split `priority_categories = [cat.strip() for cat in priority_categories_str.split(',') if cat.strip()]`; check `all(cat in categories for cat in priority_categories)` or raise ValueError("Priority categories must be a subset of main categories"). Update return dict with `'priority_categories': priority_categories`. In summary, add `print(f"Priority Categories: {', '.join(priority_categories) if priority_categories else 'None'}")`. Print "Settings correct? (Y/N)" and wait for my response.
  ```

---

#### Step 2: Modify LLM Prompt to Emphasize Priority Categories
- **Objective**: Update `analyze_image()` to bias the LLM toward priority categories.
- **Tasks**:
  - Adjust the prompt in `LMStudioClient.analyze_image()`:
    - List priority categories first and instruct the model to favor them.
    - Keep JSON output format.
  - Test with a mock image path to ensure the LLM understands.
- **Output**: Updated prompt and a sample response.
- **Stop for Feedback**: Print “New prompt: [prompt]. Sample: [response]. OK? (Y/N)”
- **Specific Instruction for Sub-LLM**:
  ```
  Find `analyze_image()` in `LMStudioClient`. Replace the prompt with: `priority_list = "\n".join([f"- {cat} (priority)" for cat in categories if cat in priority_categories])`; `regular_list = "\n".join([f"- {cat}" for cat in categories if cat not in priority_categories])`; `prompt = f"""Analyze this image and assign it to one or more of these EXACT categories (do not create new ones). Favor priority categories when confident:\n{priority_list}\n{regular_list}\nReturn as JSON: {{"categories": [{{"name": "category", "confidence": 0.9}}]}}"""`. Use a mock `image_path = 'test.jpg'`, `categories = ['Family', 'Cosplay']`, `priority_categories = ['Cosplay']`, skip file read with a dummy `image_data = "mock_base64"`, and print the `prompt` (don’t send to LLM yet). Print "New prompt: [prompt]. Sample: (not run yet). OK? (Y/N)" and wait for my response.
  ```

---

#### Step 3: Add Priority Logic to Output Processing
- **Objective**: Update `output_results()` to enforce priority in "move" mode.
- **Tasks**:
  - After parsing `result_json`, check for priority categories:
    - If any meet/exceed `threshold`, use the highest-confidence priority category only.
    - Else, use standard logic (all categories above threshold, or Uncertain).
  - Test with a mock result.
- **Output**: Updated move logic.
- **Stop for Feedback**: Print “Mock move: [image] -> [category]. Logic OK? (Y/N)”
- **Specific Instruction for Sub-LLM**:
  ```
  Find `output_results()`. After `result_json = json.loads(json_str)`, add: if `settings['output_mode'] == 'move'` and `settings['priority_categories']`: `priority_hits = [cat for cat in categories if cat['name'] in settings['priority_categories'] and cat['confidence'] >= threshold]`; if `priority_hits`, set `categories = [max(priority_hits, key=lambda x: x['confidence'])]`. Test with mock `results = {'img1': '{"categories": [{"name": "Cosplay", "confidence": 0.95}, {"name": "Family", "confidence": 0.8}]}'}`, `settings = {'output_mode': 'move', 'priority_categories': ['Cosplay'], 'threshold': 0.7, 'ambiguity_mode': 'multi', 'photo_dir': Path('test')}`; process and print "Mock move: img1 -> [categories[0]['name']]". Print "Mock move: [image] -> [category]. Logic OK? (Y/N)" and stop for my response.
  ```

---

#### Step 4: Integrate with Adaptive Threshold
- **Objective**: Ensure adaptive threshold works with priority logic.
- **Tasks**:
  - In `output_results()`, calculate adaptive threshold as before.
  - Apply priority logic after threshold determination.
  - Test with sample results.
- **Output**: Consistent threshold and priority behavior.
- **Stop for Feedback**: Print “Threshold: [value]. Priority applied. OK? (Y/N)”
- **Specific Instruction for Sub-LLM**:
  ```
  In `output_results()`, keep `threshold = settings['threshold'] if settings['threshold'] is not None else calculate_adaptive_threshold(results)`. After this, apply Step 3’s priority logic. Test with `results = {'img1': '{"categories": [{"name": "Cosplay", "confidence": 0.95}, {"name": "Family", "confidence": 0.8}]}', 'img2': '{"categories": [{"name": "Family", "confidence": 0.7}]}'}`, `settings['threshold'] = None`, `settings['priority_categories'] = ['Cosplay']`, `settings['output_mode'] = 'move'`. Print "Threshold: [threshold]. Priority applied. OK? (Y/N)" and stop for my response.
  ```

---

#### Step 5: Full Test Run with Priority Categories
- **Objective**: Run the script end-to-end with priority logic.
- **Tasks**:
  - Use existing `main` block.
  - Input sample settings with "Cosplay" as priority.
  - Process a small image set (mock or real).
- **Output**: Sorted images with priority respected.
- **Stop for Feedback**: Print “Full run complete. Results as expected? (Y/N)”
- **Specific Instruction for Sub-LLM**:
  ```
  Run the script with: `photo_dir = 'test_photos'`, `categories = ['Family', 'Cosplay', 'Pets']`, `priority_categories = ['Cosplay']`, `threshold = None`, `ambiguity_mode = 'multi'`, `output_mode = 'move'`, `scan_subfolders = False`. Mock `client.analyze_image()` to return `json.dumps({"categories": [{"name": "Cosplay", "confidence": 0.95}, {"name": "Family", "confidence": 0.8}]})` for simplicity if no real images. Print "Full run complete. Results as expected? (Y/N)" and stop for my response.
  ```

---

### Notes
- **Simplicity**: No extra threshold; priority uses the same threshold, reducing user confusion.
- **LLM Bias**: Prompt tweak encourages priority focus, backed by code enforcement.
- **Fallback**: Standard logic applies if priorities don’t qualify, keeping it robust.