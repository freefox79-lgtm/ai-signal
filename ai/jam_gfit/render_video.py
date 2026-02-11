# Wrapper script for main.py
# Usage: source .venv/bin/activate && python render_video.py
import os
import subprocess

if __name__ == "__main__":
    print(">>> [Alias] Running main.py (Video Rendering)...")
    env = os.environ.copy()
    env["LANG"] = "ko_KR.UTF-8"
    subprocess.run(["python3", "main.py"], env=env)