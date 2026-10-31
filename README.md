# NoDpiTube

<div align="center">
  <img src="assets/app_icon_xxxhdpi.png" width="128" height="128" alt="YouTube Icon" />
  <h1>NoDpiTube</h1>
  <p><b>Android TV YouTube client with integrated NoDPI engine for transparent censorship circumvention</b></p>
  <p><i>A merge of <a href="https://github.com/yuliskov/SmartTube">SmartTube</a> and the <a href="https://github.com/GVCoder09/NoDPI4Android">NoDPI</a> core</i></p>
</div>

---

## 🚀 Key Features

* 🛡️ **Embedded NoDPI Bypass:**  
  Transparently fragments TLS ClientHello packets and sends initial chunks with `TTL = 1` (disorder). Completely bypasses DPI without root, without requiring VPN slots, and without configuring TV Wi-Fi proxies.
* ⚡ **Chromium (Cronet) Network Stack by Default:**  
  ExoPlayer is configured to use the high-performance Chromium Cronet data source with QUIC (HTTP/3) disabled so all media streams seamlessly pass through the NoDPI pipeline.
* 📺 **Native YouTube Branding:**  
  Displays as **YouTube** with the authentic red icon and 16:9 Leanback banner for the Android TV / Google TV home screen.
* 👯 **Side-by-side Installation:**  
  Unique `applicationId` (`com.teamsmart.videomanager.tv.nodpi`) enables installing alongside the official SmartTube or YouTube client.
* 🔄 **Automated Upstream Sync via GitHub Actions:**  
  Monitors releases on `yuliskov/SmartTube` and commits on `NoDPI` every 12 hours. Automatically rebuilds and publishes new releases.
* 📲 **In-App TV Updates:**  
  Integrates with SmartTube's built-in update checker. Television users get on-screen notifications and one-click updates via remote control.

---

## 🛠️ Quick Start (GitHub Actions)

### Step 1: Create Your Repository
1. Create a repository named **`NoDpiTube`** on GitHub.
2. Push this repository's files:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of NoDpiTube"
   git branch -M main
   git remote add origin https://github.com/commensal/NoDpiTube.git
   git push -u origin main
   ```

### Step 2: Grant Workflow Permissions
1. In your GitHub repo, go to **Settings** → **Actions** → **General**.
2. Under **Workflow permissions**, choose **Read and write permissions**.
3. Enable **Allow GitHub Actions to create and approve pull requests**.
4. Save settings.

### Step 3: Trigger First Build
1. Go to the **Actions** tab.
2. Select **Build NoDpiTube** and click **Run workflow**.
3. After ~6 minutes, open the **Releases** tab to download your APKs.

---

## 📜 License
Licensed under GNU General Public License v3 (GPL-3.0) in accordance with [SmartTube](https://github.com/yuliskov/SmartTube) and [NoDPI4Android](https://github.com/GVCoder09/NoDPI4Android).
