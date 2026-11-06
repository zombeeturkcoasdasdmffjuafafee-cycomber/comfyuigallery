import time
import os
import shutil
import subprocess
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define your paths
SOURCE_DIR = r"C:\Users\Donton\AppData\Local\ComfyUI_windows_portable\ComfyUI\output"
TARGET_DIR = r"C:\Users\Donton\AppData\Local\ComfyUI_windows_portable\WEBSITE\assets"
JSON_PATH = os.path.join(TARGET_DIR, "assets.json")
REPO_DIR = r"C:\Users\Donton\AppData\Local\ComfyUI_windows_portable\WEBSITE"

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

def run_git_sync(commit_message):
    """Stages, commits, and pushes changes to GitHub."""
    os.chdir(REPO_DIR)
    try:
        # Check if there are changes to commit
        status_result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        
        if status_result.stdout.strip():
            print("Changes detected. Pushing to GitHub...")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            subprocess.run(["git", "push"], check=True)
            print("Successfully pushed to GitHub!")
        else:
            print("No git changes to push.")
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

def initial_sync():
    """Scans and copies any existing images on startup, updates JSON, and pushes if needed."""
    print("Running initial startup sync...")
    
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
            
            if not os.path.exists(dst_file):
                shutil.copy2(src_file, dst_file)
                print(f"Copied missing image: {file_name}")
                copied_count += 1

    # Update assets.json
    all_assets = sorted([
        f for f in os.listdir(TARGET_DIR) 
        if f.lower().endswith(IMAGE_EXTENSIONS)
    ])

    with open(JSON_PATH, "w") as json_file:
        json.dump(all_assets, json_file, indent=2)
    
    print(f"Initial sync complete. Copied {copied_count} file(s). Total assets: {len(all_assets)}.")
    
    # Push initial batch if any changes were caught
    run_git_sync("Startup auto-sync: added missing ComfyUI images")
    return True


class ComfyUIHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_name = os.path.basename(event.src_path)
        if not file_name.lower().endswith(IMAGE_EXTENSIONS):
            return

        # Wait a split second to ensure the file is fully written to disk by ComfyUI
        time.sleep(1.5)
        self.sync_and_push(file_name)

    def sync_and_push(self, new_file_name):
        print(f"\n[Detected new image]: {new_file_name}")
        
        if not os.path.exists(TARGET_DIR):
            os.makedirs(TARGET_DIR)

        # 1. Copy any missing images
        source_files = os.listdir(SOURCE_DIR)
        for file_name in source_files:
            if file_name.lower().endswith(IMAGE_EXTENSIONS):
                src_file = os.path.join(SOURCE_DIR, file_name)
                dst_file = os.path.join(TARGET_DIR, file_name)
                if not os.path.exists(dst_file):
                    shutil.copy2(src_file, dst_file)
                    print(f"Copied: {file_name}")

        # 2. Update assets.json
        all_assets = sorted([
            f for f in os.listdir(TARGET_DIR) 
            if f.lower().endswith(IMAGE_EXTENSIONS)
        ])

        with open(JSON_PATH, "w") as json_file:
            json.dump(all_assets, json_file, indent=2)
        print(f"Updated assets.json ({len(all_assets)} total images).")

        # 3. Push to GitHub automatically
        run_git_sync(f"Auto-sync: added {new_file_name}")

if __name__ == "__main__":
    # 1. Run catch-up sync on startup
    if initial_sync():
        # 2. Start watching for real-time generations
        event_handler = ComfyUIHandler()
        observer = Observer()
        observer.schedule(event_handler, path=SOURCE_DIR, recursive=False)
        
        print(f"\nWatching ComfyUI output folder with GitHub Auto-Push enabled...\nPath: {SOURCE_DIR}\n")
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()