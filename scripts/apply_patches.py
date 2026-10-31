#!/usr/bin/env python3
"""
Master Patching Script for NoDpiTube.
Applies all NoDPI integrations, network modifications, branding, package rename,
and update URL redirection to a cloned SmartTube repository.
"""

import os
import sys
import shutil
import re

def log(msg: str):
    print(f"[NoDpiTube] {msg}")

def patch_file(file_path: str, find_pattern: str, replace_text: str, is_regex: bool = False):
    if not os.path.exists(file_path):
        log(f"WARNING: File {file_path} not found for patching!")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if is_regex:
        new_content, count = re.subn(find_pattern, replace_text, content)
        if count == 0:
            log(f"Regex pattern '{find_pattern}' not matched in {file_path}")
            return False
    else:
        if find_pattern not in content:
            log(f"Pattern '{find_pattern[:60]}...' not found in {file_path}")
            return False
        new_content = content.replace(find_pattern, replace_text)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    log(f"Successfully patched {os.path.basename(file_path)}")
    return True

def apply_nodpi_core(root_dir: str, src_nodpi_dir: str):
    log("Copying NoDPI core classes into SmartTube common module...")
    target_dir = os.path.join(root_dir, "common", "src", "main", "java", "com", "liskovsoft", "smartyoutubetv2", "common", "nodpi")
    os.makedirs(target_dir, exist_ok=True)

    for item in os.listdir(src_nodpi_dir):
        if item.endswith(".kt") or item.endswith(".java"):
            shutil.copy2(os.path.join(src_nodpi_dir, item), os.path.join(target_dir, item))
            log(f"Installed {item}")

def hook_main_application(root_dir: str):
    log("Hooking NoDpiManager into MainApplication.java...")
    app_file = os.path.join(root_dir, "smarttubetv", "src", "main", "java", "com", "liskovsoft", "smartyoutubetv2", "tv", "ui", "main", "MainApplication.java")

    if not os.path.exists(app_file):
        log(f"ERROR: {app_file} does not exist!")
        return

    with open(app_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add import
    import_stmt = "import com.liskovsoft.smartyoutubetv2.common.nodpi.NoDpiManager;\n"
    if "NoDpiManager;" not in content:
        content = re.sub(r"(package [^;]+;\s*)", r"\1" + import_stmt, content, count=1)

    # 2. Add start in onCreate
    start_call = "        NoDpiManager.start(this);\n"
    if "NoDpiManager.start(" not in content:
        content = content.replace("super.onCreate();", "super.onCreate();\n" + start_call)

    with open(app_file, "w", encoding="utf-8") as f:
        f.write(content)

    log("MainApplication.java hooked with NoDpiManager.start(this)")

def patch_cronet_manager(root_dir: str):
    log("Configuring CronetManager (disabling QUIC and hooking proxy)...")
    cronet_file = os.path.join(root_dir, "SharedModules", "sharedutils", "src", "main", "java", "com", "liskovsoft", "sharedutils", "cronet", "CronetManager.kt")

    if not os.path.exists(cronet_file):
        log(f"WARNING: CronetManager.kt not found at {cronet_file}")
        return

    with open(cronet_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Disable QUIC
    content = content.replace(".enableQuic(true)", ".enableQuic(false)")

    # 2. Trigger ProxyManager.configureSystemProxy() when engine is built
    proxy_hook = """
                engine = builder.build()

                try {
                    val pmCls = Class.forName("com.liskovsoft.smartyoutubetv2.common.proxy.ProxyManager")
                    val pmObj = pmCls.getConstructor(android.content.Context::class.java).newInstance(context)
                    pmCls.getMethod("configureSystemProxy").invoke(pmObj)
                } catch (_: Throwable) {
                }
"""

    if "builder.build()" in content:
        content = content.replace("engine = builder.build()", proxy_hook.strip())

    with open(cronet_file, "w", encoding="utf-8") as f:
        f.write(content)

    log("CronetManager.kt configured: QUIC disabled & ProxyManager hook installed")

def patch_default_data_source(root_dir: str):
    log("Setting default player data source to CRONET...")
    tweaks_file = os.path.join(root_dir, "common", "src", "main", "java", "com", "liskovsoft", "smartyoutubetv2", "common", "prefs", "PlayerTweaksData.java")

    if not os.path.exists(tweaks_file):
        log(f"WARNING: {tweaks_file} not found")
        return

    patch_file(
        tweaks_file,
        "mPlayerDataSource = Helpers.parseInt(split, 26, Utils.getFasterDataSource());",
        "mPlayerDataSource = Helpers.parseInt(split, 26, PLAYER_DATA_SOURCE_CRONET); // NoDpiTube default"
    )

def patch_package_name(root_dir: str, new_pkg: str = "com.youtube.commensal"):
    log(f"Changing applicationId to {new_pkg} for side-by-side installation...")
    build_gradle = os.path.join(root_dir, "smarttubetv", "build.gradle")

    if os.path.exists(build_gradle):
        with open(build_gradle, "r", encoding="utf-8") as f:
            content = f.read()

        # Update default and flavor applicationIds
        content = re.sub(r'applicationId\s+["\']app\.smarttube["\']', f'applicationId "{new_pkg}"', content)
        content = re.sub(r'applicationId\s+["\']org\.smarttube\.stable["\']', f'applicationId "{new_pkg}"', content)
        content = re.sub(r'applicationId\s+["\']org\.smarttube\.beta["\']', f'applicationId "{new_pkg}.beta"', content)
        content = re.sub(r'applicationId\s+["\']app\.smarttube\.fdroid["\']', f'applicationId "{new_pkg}.fdroid"', content)

        with open(build_gradle, "w", encoding="utf-8") as f:
            f.write(content)
        log(f"Updated applicationIds in smarttubetv/build.gradle to {new_pkg}")

def patch_google_services_json(root_dir: str, new_pkg: str = "com.youtube.commensal"):
    gs_file = os.path.join(root_dir, "smarttubetv", "google-services.json")
    if os.path.exists(gs_file):
        with open(gs_file, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace('"org.smarttube.stable"', f'"{new_pkg}"')
        content = content.replace('"app.smarttube.stable"', f'"{new_pkg}"')
        content = content.replace('"org.smarttube.beta"', f'"{new_pkg}.beta"')
        with open(gs_file, "w", encoding="utf-8") as f:
            f.write(content)
        log("Updated google-services.json with new package names")

def patch_app_name(root_dir: str, app_name: str = "YouTube"):
    log(f"Changing app name to '{app_name}' across all resource files...")
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if f == "strings.xml":
                sf = os.path.join(root, f)
                try:
                    with open(sf, "r", encoding="utf-8") as file:
                        c = file.read()
                    orig = c
                    # Replace app_name (handles CDATA and plain text)
                    c = re.sub(r'<string\b([^>]*?\bname="app_name"[^>]*)>.*?</string>', f'<string\\1>{app_name}</string>', c, flags=re.DOTALL)
                    # Replace browse_title
                    c = re.sub(r'<string\b([^>]*?\bname="browse_title"[^>]*)>.*?</string>', f'<string\\1>{app_name}</string>', c, flags=re.DOTALL)
                    if c != orig:
                        with open(sf, "w", encoding="utf-8") as file:
                            file.write(c)
                        log(f"Updated app_name in {os.path.relpath(sf, root_dir)}")
                except Exception as e:
                    pass

def patch_update_urls(root_dir: str, github_repo: str):
    log(f"Redirecting update URLs to {github_repo}...")
    manifest_url = f"https://github.com/{github_repo}/releases/latest/download/update.json"

    update_files = [
        os.path.join(root_dir, "common", "src", "main", "res", "values", "update_urls.xml"),
        os.path.join(root_dir, "common", "src", "ststable", "res", "values", "update_urls.xml"),
        os.path.join(root_dir, "common", "src", "stbeta", "res", "values", "update_urls.xml"),
    ]

    new_xml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string-array name="update_urls">
        <item>{manifest_url}</item>
    </string-array>
</resources>
"""

    for uf in update_files:
        os.makedirs(os.path.dirname(uf), exist_ok=True)
        with open(uf, "w", encoding="utf-8") as f:
            f.write(new_xml_content)
        log(f"Updated {uf} -> {manifest_url}")

def apply_branding_assets(root_dir: str, assets_dir: str):
    log("Installing YouTube branding icons & TV banners across all flavors...")
    smarttube_res = os.path.join(root_dir, "smarttubetv", "src")

    icon_512 = os.path.join(assets_dir, "app_icon_xxxhdpi.png")
    banner = os.path.join(assets_dir, "app_banner_320x180.png")

    target_paths = [
        # Flavor ststable
        os.path.join(smarttube_res, "ststable", "res", "mipmap-nodpi", "app_icon.png"),
        os.path.join(smarttube_res, "ststable", "res", "mipmap-nodpi", "app_banner.png"),
        os.path.join(smarttube_res, "ststable", "res", "mipmap-nodpi", "app_logo.png"),
        os.path.join(smarttube_res, "ststable", "res", "mipmap-nodpi", "app_logo_semi_red.png"),
        os.path.join(smarttube_res, "ststable", "res", "mipmap-nodpi-v30", "app_icon.png"),
        os.path.join(smarttube_res, "ststable", "res", "mipmap-nodpi-v30", "app_banner.png"),

        # Flavor stbeta
        os.path.join(smarttube_res, "stbeta", "res", "mipmap-nodpi", "app_icon.png"),
        os.path.join(smarttube_res, "stbeta", "res", "mipmap-nodpi", "app_banner.png"),
        os.path.join(smarttube_res, "stbeta", "res", "mipmap-nodpi", "app_logo.png"),
        os.path.join(smarttube_res, "stbeta", "res", "mipmap-nodpi-v30", "app_icon.png"),
        os.path.join(smarttube_res, "stbeta", "res", "mipmap-nodpi-v30", "app_banner.png"),

        # Main density mipmaps
        os.path.join(smarttube_res, "main", "res", "mipmap-mdpi", "app_icon.png"),
        os.path.join(smarttube_res, "main", "res", "mipmap-hdpi", "app_icon.png"),
        os.path.join(smarttube_res, "main", "res", "mipmap-xhdpi", "app_icon.png"),
        os.path.join(smarttube_res, "main", "res", "mipmap-xxhdpi", "app_icon.png"),
        os.path.join(smarttube_res, "main", "res", "mipmap-xxxhdpi", "app_icon.png"),
        os.path.join(smarttube_res, "main", "res", "mipmap-xhdpi", "app_banner.png"),
        os.path.join(smarttube_res, "main", "res", "mipmap-xhdpi", "app_logo.png"),
    ]

    for target in target_paths:
        src = banner if "banner" in target else icon_512
        if os.path.exists(src):
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(src, target)
            log(f"Installed {os.path.basename(src)} -> {os.path.relpath(target, root_dir)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python apply_patches.py <path_to_smarttube_root> [github_repo]")
        sys.exit(1)

    smarttube_dir = os.path.abspath(sys.argv[1])
    github_repo = sys.argv[2] if len(sys.argv) > 2 else "commensal/NoDpiTube"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    src_nodpi = os.path.join(project_root, "src", "nodpi")
    assets_dir = os.path.join(project_root, "assets")

    # Generate PNGs if needed
    png_gen = os.path.join(assets_dir, "generate_pngs.py")
    if os.path.exists(png_gen):
        import subprocess
        subprocess.run([sys.executable, png_gen], cwd=project_root)

    log(f"Starting patching process on {smarttube_dir}...")
    apply_nodpi_core(smarttube_dir, src_nodpi)
    hook_main_application(smarttube_dir)
    patch_cronet_manager(smarttube_dir)
    patch_default_data_source(smarttube_dir)
    patch_package_name(smarttube_dir)
    patch_google_services_json(smarttube_dir)
    patch_app_name(smarttube_dir, "YouTube")
    patch_update_urls(smarttube_dir, github_repo)
    apply_branding_assets(smarttube_dir, assets_dir)
    log("All patches successfully applied!")

if __name__ == "__main__":
    main()
