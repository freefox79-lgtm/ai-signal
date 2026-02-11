import os
import subprocess

if __name__ == "__main__":
    print(">>> [Alias] Running generate_voices.py...")
    env = os.environ.copy()
    env["LANG"] = "ko_KR.UTF-8"
    subprocess.run(["python3", "generate_voices.py"], env=env)
