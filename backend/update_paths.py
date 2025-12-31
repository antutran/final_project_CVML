#!/usr/bin/env python3
"""
Script to update all meta.json files to use Mac paths instead of Windows paths.
Replaces D:\\CVML\\ITEMS_CLEAN\\ with /Users/tuantran/Downloads/CVML/dataset/ITEM_OFFICIAL/
"""

import json
from pathlib import Path

# Find all meta.json files
backend_dir = Path("/Users/tuantran/Downloads/CVML/backend")
meta_files = list(backend_dir.glob("ITEM_EMB/**/meta.json"))

print(f"Found {len(meta_files)} meta.json files to update:\n")

total_updated = 0

for meta_file in meta_files:
    print(f"Processing: {meta_file.relative_to(backend_dir)}")
    
    # Read the file
    with open(meta_file, 'r') as f:
        data = json.load(f)
    
    # Track if any changes were made
    changes_made = 0
    
    # Update each item's image_path
    for item in data:
        if "image_path" in item:
            old_path = item["image_path"]
            new_path = old_path
            
            # Replace Windows path with Mac path
            if "D:\\\\CVML\\\\ITEMS_CLEAN" in new_path:
                new_path = new_path.replace(
                    "D:\\\\CVML\\\\ITEMS_CLEAN",
                    "/Users/tuantran/Downloads/CVML/dataset/ITEM_OFFICIAL"
                )
            elif "D:\\CVML\\ITEMS_CLEAN" in new_path:
                new_path = new_path.replace(
                    "D:\\CVML\\ITEMS_CLEAN",
                    "/Users/tuantran/Downloads/CVML/dataset/ITEM_OFFICIAL"
                )
            elif "D:\\\\CVML" in new_path:
                new_path = new_path.replace(
                    "D:\\\\CVML",
                    "/Users/tuantran/Downloads/CVML/dataset/ITEM_OFFICIAL"
                )
            elif "D:" in new_path:
                new_path = new_path.replace(
                    "D:",
                    "/Users/tuantran/Downloads/CVML/dataset/ITEM_OFFICIAL"
                )
            
            # Convert backslashes to forward slashes
            new_path = new_path.replace("\\\\", "/")
            new_path = new_path.replace("\\", "/")
            
            # Capitalize gender folder
            for gender in ["male", "female", "unisex"]:
                old_pattern = f"/{gender}/"
                if old_pattern in new_path:
                    new_path = new_path.replace(old_pattern, f"/{gender.capitalize()}/")
                    break
            
            # Update if changed
            if new_path != old_path:
                item["image_path"] = new_path
                changes_made += 1
    
    # Write back to file if changes were made
    if changes_made > 0:
        with open(meta_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"  ✅ Updated {changes_made} paths")
        total_updated += changes_made
    else:
        print(f"  ℹ️  No changes needed")
    print()

print(f"\n{'='*60}")
print(f"✅ DONE! Updated {total_updated} image paths across {len(meta_files)} files")
print(f"{'='*60}")
