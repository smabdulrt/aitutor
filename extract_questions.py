import json
import os
from pathlib import Path

# Source and destination directories
source_dir = Path("/Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/khanacademyscrapper/questionbankscrapper/data/NCERT Math Class 6 (Bridge)/Addition and subtraction/Place values/exercises/Identify value of a digit/items")
dest_dir = Path("/Users/vandanchopra/Vandan_Personal_Folder/CODE_STUFF/Projects/aitutor/SherlockEDApi/CurriculumBuilder")

# Create destination directory if it doesn't exist
dest_dir.mkdir(parents=True, exist_ok=True)

def extract_itemdata_from_files():
    """Extract itemData from nested JSON structure and save to destination directory."""

    processed_count = 0
    error_count = 0i

    # Process all JSON files in source directory
    for json_file in source_dir.glob("*.json"):
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

                # Save extracted itemData to destination with same filename
                dest_file = dest_dir / json_file.name
                with open(dest_file, 'w', encoding='utf-8') as f:
                    json.dump(item_data, f, indent=2, ensure_ascii=False)

                print(f"✅ Extracted itemData from {json_file.name}")
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
    print()
    extract_itemdata_from_files()