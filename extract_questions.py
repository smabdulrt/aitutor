import json 
import os
from pathlib import Path
import uuid

base_dir = Path(__name__).resolve().parents[1]

# more readable format
source_dir = base_dir / "/Users/vandanchopra/Downloads/sample_data_perseus"
dest_dir = base_dir / "/Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/aitutor/SherlockEDApi/CurriculumBuilder"

# Create destination directory if it doesn't exist
dest_dir.mkdir(parents=True, exist_ok=True)


def transform_itemdata(item_data: dict) -> dict:
    """Apply modifications:
       1. Add unique 'id' field to choices in radio widgets
       2. Add/append alt text for images
       3. Update versions to {major: 2, minor: 0}
    """

    def process_widgets(widgets: dict):
        for widget_key, widget in widgets.items():
            # --- Radio widget: add unique IDs to choices
            if widget.get("type") == "radio":
                choices = widget.get("options", {}).get("choices", [])
                for choice in choices:
                    if "id" not in choice:
                        choice["id"] = str(uuid.uuid4())

            # --- Image widget: ensure alt text
            if widget.get("type") == "image":
                options = widget.get("options", {})
                alt_text = options.get("alt", "").strip()
                if not alt_text:
                    options["alt"] = "alt text placeholder!"
                else:
                    if not alt_text.endswith("!"):
                        options["alt"] = alt_text + " !"

            # --- Recursively process nested widgets
            if "widgets" in widget:
                process_widgets(widget["widgets"])

            # --- Update version to {2,0}
            if "version" in widget:
                widget["version"] = {"major": 2, "minor": 0}

    # --- Process question widgets
    if "question" in item_data and "widgets" in item_data["question"]:
        process_widgets(item_data["question"]["widgets"])

    # --- Process hints widgets
    if "hints" in item_data:
        for hint in item_data["hints"]:
            if "widgets" in hint:
                process_widgets(hint["widgets"])

            # --- Also handle hint["images"]
            if "images" in hint and isinstance(hint["images"], dict):
                for k, v in hint["images"].items():
                    if isinstance(v, dict):
                        alt_text = v.get("alt", "").strip()
                        if not alt_text:
                            v["alt"] = "alt text placeholder!"
                        else:
                            if not alt_text.endswith("!"):
                                v["alt"] = alt_text + " !"

    # --- Handle top-level question images
    if "question" in item_data and "images" in item_data["question"]:
        for k, v in item_data["question"]["images"].items():
            if isinstance(v, dict):
                alt_text = v.get("alt", "").strip()
                if not alt_text:
                    v["alt"] = "alt text placeholder!"
                else:
                    if not alt_text.endswith("!"):
                        v["alt"] = alt_text + " !"

    # --- Update itemDataVersion
    if "itemDataVersion" in item_data:
        item_data["itemDataVersion"] = {"major": 2, "minor": 0}

    return item_data


def extract_itemdata_from_files():
    """Extract itemData from nested JSON structure and save to destination directory."""

    processed_count = 0
    error_count = 0

    # Process all JSON files in source directory
    for json_file in source_dir.rglob("*.json"):
        try:
            # Read the original file
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Navigate through nested structure: data -> assessmentItem -> item -> itemData
            if ('data' in data and
                'assessmentItem' in data['data'] and
                data['data']['assessmentItem'] and
                'item' in data['data']['assessmentItem'] and
                data['data']['assessmentItem']['item'] and
                'itemData' in data['data']['assessmentItem']['item']):

                # Extract itemData (it's a JSON string, so parse it)
                item_data_string = data['data']['assessmentItem']['item']['itemData']
                item_data = json.loads(item_data_string) 

                # Apply transformations
                item_data = transform_itemdata(item_data)

                # Save extracted itemData to destination with same filename
                dest_file = dest_dir / json_file.name
                with open(dest_file, 'w', encoding='utf-8') as f:
                    json.dump(item_data, f, indent=2, ensure_ascii=False)

                print(f"✅ Extracted & transformed itemData from {json_file.name}")
                processed_count += 1
            else:
                print(f"⚠️  Expected nested structure not found in {json_file.name}")
                print(f"    Looking for: data.assessmentItem.item.itemData")
                error_count += 1

        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error in {json_file.name}: {e}")
            error_count += 1
        except Exception as e:
            print(f"❌ Error processing {json_file.name}: {e}")
            error_count += 1

    print(f"\n📊 Summary:")
    print(f"   ✅ Successfully processed: {processed_count} files")
    print(f"   ❌ Errors/Skipped: {error_count} files")
    print(f"   📁 Output directory: {dest_dir}")


if __name__ == "__main__":
    print("🔄 Extracting itemData from Khan Academy JSON files...")
    print(f"📂 Source: {source_dir}")
    print(f"📁 Destination: {dest_dir}")
    extract_itemdata_from_files()
