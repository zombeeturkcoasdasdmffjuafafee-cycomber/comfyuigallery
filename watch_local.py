import time
import os
import shutil
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define your paths
SOURCE_DIR = r"C:\Users\Donton\AppData\Local\ComfyUI_windows_portable\ComfyUI\output"
TARGET_DIR = r"C:\Users\Donton\AppData\Local\ComfyUI_windows_portable\WEBSITE\assets"
JSON_PATH = os.path.join(TARGET_DIR, "assets.json")

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

def initial_sync():
    """Scans and copies any existing images from ComfyUI output that are missing from assets."""
    print("Running initial sync of existing images...")
    
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory not found: {SOURCE_DIR}")
        return False

    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)

    source_files = os.listdir(SOURCE_DIR)
    copied_count = 0

    for file_name in source_files:
        if file_name.lower().endswith(IMAGE_EXTENSIONS):
            src_file = os.path.join(SOURCE_DIR, file_name)
            dst_file = os.path.join(TARGET_DIR, file_name)
            
            # If the file exists in ComfyUI output but not in assets, copy it over
            if not os.path.exists(dst_file):
                shutil.copy2(src_file, dst_file)
                print(f"Copied missing existing image: {file_name}")
                copied_count += 1

    # Re-scan target directory to update assets.json with everything
    all_assets = sorted([
        f for f in os.listdir(TARGET_DIR) 
        if f.lower().endswith(IMAGE_EXTENSIONS)
    ])

    with open(JSON_PATH, "w") as json_file:
        json.dump(all_assets, json_file, indent=2)
    
    print(f"Initial sync complete. Copied {copied_count} missing file(s). Total assets: {len(all_assets)}.\n")
    return True


class ComfyUIHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_name = os.path.basename(event.src_path)
        if not file_name.lower().endswith(IMAGE_EXTENSIONS):
            return

        # Wait a split second to ensure the file is fully written to disk
        time.sleep(1.5)
        self.sync_assets(file_name)

    def sync_assets(self, new_file_name):
        print(f"\n[Detected new image]: {new_file_name}")
        
        if not os.path.exists(TARGET_DIR):
            os.makedirs(TARGET_DIR)

        # 1. Copy any missing images over
        source_files = os.listdir(SOURCE_DIR)
        for file_name in source_files:
            if file_name.lower().endswith(IMAGE_EXTENSIONS):
                src_file = os.path.join(SOURCE_DIR, file_name)
                dst_file = os.path.join(TARGET_DIR, file_name)
                if not os.path.exists(dst_file):
                    shutil.copy2(src_file, dst_file)
                    print(f"Copied: {file_name}")

        # 2. Re-scan the target folder and rewrite assets.json
        all_assets = sorted([
            f for f in os.listdir(TARGET_DIR) 
            if f.lower().endswith(IMAGE_EXTENSIONS)
        ])

        with open(JSON_PATH, "w") as json_file:
            json.dump(all_assets, json_file, indent=2)
        print(f"Updated assets.json successfully ({len(all_assets)} total images). Refresh your browser gallery!")

if __name__ == "__main__":
    # 1. Run the initial catch-up sync immediately on startup
    if initial_sync():
        # 2. Start watching for any new images generated going forward
        event_handler = ComfyUIHandler()
        observer = Observer()
        observer.schedule(event_handler, path=SOURCE_DIR, recursive=False)
        
        print(f"Watching ComfyUI output folder for new images...\nPath: {SOURCE_DIR}\n")
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()