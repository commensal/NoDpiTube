#!/usr/bin/env python3
"""
Local build helper for NoDpiTube.
Clones SmartTube, applies NoDPI patches, and runs Gradle build.
"""

import os
import sys
import subprocess
import shutil

def run_cmd(cmd, cwd=None):
    print(f">> Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    res = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str))
    if res.returncode != 0:
        print(f"Command failed with return code {res.returncode}")
        sys.exit(res.returncode)

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    smarttube_dir = os.path.join(root_dir, "smarttube_src")

    # 1. Clone SmartTube if not exists
    if not os.path.exists(smarttube_dir):
        print("Cloning SmartTube repository with submodules...")
        run_cmd(["git", "clone", "--recurse-submodules", "https://github.com/yuliskov/SmartTube.git", "smarttube_src"], cwd=root_dir)

    # 2. Generate assets
    print("Generating assets...")
    run_cmd([sys.executable, os.path.join("assets", "generate_pngs.py")], cwd=root_dir)

    # 3. Apply patches
    print("Applying patches...")
    run_cmd([sys.executable, os.path.join("scripts", "apply_patches.py"), smarttube_dir, "local/NoDpiTube"], cwd=root_dir)

    # 4. Build APK with Gradle
    print("Building APK with Gradle...")
    gradle_cmd = "./gradlew" if os.name != "nt" else "gradlew.bat"
    gradle_path = os.path.join(smarttube_dir, gradle_cmd)
    run_cmd(f"{gradle_cmd} assembleDebug", cwd=smarttube_dir)

    print("\n✅ Build complete! APK files can be found in:")
    print(os.path.join(smarttube_dir, "smarttubetv", "build", "outputs", "apk", "debug"))

if __name__ == "__main__":
    main()
