#!/usr/bin/env python3
"""
Generates update.json in the exact format required by SmartTube's AppUpdateChecker2.
Used during GitHub Actions release to publish update metadata alongside the APKs.
"""

import sys
import os
import json

def generate_update_json(version_name: str, version_code: int, repo: str, apk_filename: str, output_path: str = "update.json"):
    download_url = f"https://github.com/{repo}/releases/download/v{version_name}/{apk_filename}"

    manifest = {
        "package": {
            "downloadUrl": download_url
        },
        version_name: {
            "versionCode": int(version_code),
            "changelog": [
                f"NoDpiTube v{version_name}",
                "Три варианта обхода: Настройки → Основные → Сеть → Обход блокировок",
                "Обычно помогает вариант 1. Если видео не открывается, попробуйте 2 или 3 и запустите ролик заново",
                "Обход работает внутри приложения, без VPN и без отдельной программы"
            ]
        }
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4, ensure_ascii=False)

    print(f"[NoDpiTube] Generated {output_path} for version {version_name} (code: {version_code}) -> {download_url}")

def main():
    if len(sys.argv) < 5:
        print("Usage: python generate_update_json.py <version_name> <version_code> <github_repo> <apk_filename> [output_file]")
        sys.exit(1)

    v_name = sys.argv[1].lstrip("v")
    v_code = int(sys.argv[2])
    repo = sys.argv[3]
    apk = sys.argv[4]
    out = sys.argv[5] if len(sys.argv) > 5 else "update.json"

    generate_update_json(v_name, v_code, repo, apk, out)

if __name__ == "__main__":
    main()
