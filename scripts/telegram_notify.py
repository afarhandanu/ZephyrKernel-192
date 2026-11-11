#!/usr/bin/env python3
import os
import sys
import glob
import json
import random
import urllib.request
import subprocess

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
RELEASE_URL = os.environ.get("RELEASE_URL", "https://github.com/afarhandanu/ZephyrKernel/releases")
KERNEL_VER = os.environ.get("KERNEL_VER", "6.1.190")
LTO_MODE = os.environ.get("LTO_MODE", "thin")

if not BOT_TOKEN or not CHAT_ID:
    print("[WARN] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing. Skipping Telegram post.")
    sys.exit(0)

# 1. Resolve LTO display
lto_raw = LTO_MODE.lower()
if lto_raw == "all":
    lto_html = '<tg-button type="disabled" style="success">ThinLTO</tg-button> <tg-button type="disabled" style="primary">FullLTO</tg-button> <tg-button type="disabled" style="danger">NoLTO</tg-button>'
elif lto_raw == "full":
    lto_html = '<tg-button type="disabled" style="primary">FullLTO</tg-button>'
elif lto_raw == "none":
    lto_html = '<tg-button type="disabled" style="danger">NoLTO</tg-button>'
else:
    lto_html = '<tg-button type="disabled" style="success">ThinLTO</tg-button>'

# 2. Resolve Banner (Pick random real HD cat meme banner from banner pool)
BANNER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "release", "telegram", "banner")
banner_candidates = sorted(glob.glob(os.path.join(BANNER_DIR, "banner_*.*")))
if not banner_candidates:
    banner_candidates = sorted([
        f for f in glob.glob(os.path.join(BANNER_DIR, "*"))
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])
banner_path = random.choice(banner_candidates) if banner_candidates else None
if banner_path:
    print(f"[Telegram] Selected random cat meme banner: {os.path.basename(banner_path)}")

# Resolve SUSFS version dynamically
susfs_ver = "v2.4.0"
for header_candidate in [
    "kernel/include/linux/susfs.h",
    "include/linux/susfs.h",
    "susfs/kernel_patches/include/linux/susfs.h",
]:
    if os.path.exists(header_candidate):
        try:
            with open(header_candidate) as f:
                for line in f:
                    if "#define SUSFS_VERSION" in line and '"' in line:
                        susfs_ver = line.split('"')[1]
                        break
            break
        except Exception:
            pass

if susfs_ver == "v2.4.0" and not os.path.exists("kernel/include/linux/susfs.h"):
    try:
        res = subprocess.run(
            ["curl", "-fsSL", "--max-time", "5", "https://gitlab.com/simonpunk/susfs4ksu/-/raw/gki-android14-6.1/kernel_patches/include/linux/susfs.h"],
            capture_output=True, text=True
        )
        for line in res.stdout.splitlines():
            if "#define SUSFS_VERSION" in line and '"' in line:
                susfs_ver = line.split('"')[1]
                break
    except Exception:
        pass

# 3. Build Rich Message Payload
rich_markdown = f"""<tg-slideshow>
<img src="tg://photo?id=banner1" />
</tg-slideshow>

# ⚡ ZephyrKernel | {KERNEL_VER}
> GKI Kernel | Android 14 | Linux 6.1.x

<details>
<summary><tg-button type="disabled" style="primary">What's Inside?</tg-button></summary>

<tg-button-row><tg-button type="disabled">Core Features</tg-button></tg-button-row>

<details>
<summary>Filesystem</summary>

- Mountify / OverlayFS
- F2FS Extended Attributes
- POSIX ACL
</details>

<details>
<summary>Memory</summary>

- ZRAM (LZ4 compression)
- Memory Tracking
- Writeback Support
</details>

<details>
<summary>CPU & Scheduler</summary>

- Ondemand Governor (included)
- Frame Warning Disabled
- I/O Scheduler (MQ-Deadline, Kyber)
</details>

<details>
<summary>Network</summary>

- TCP Congestion Control: BBR, BIC, CUBIC, Westwood, HTCP
- Network Schedulers: FQ, FQ_CoDel, CAKE, PIE, FQ-PIE
- IP Set
- IPv6 NAT
- TTL Target (Netfilter)
</details>

<details>
<summary>Debug</summary>

- Full Kallsyms
- UBSAN Disabled
- Page Owner Disabled
- RCU Trace Disabled
</details>

<details>
<summary>Zephyr & Luminaire Tuning</summary>

<table bordered>
<tr><td>BORE v6.8.0-rc1</td></tr>
<tr><td>BBRv3 + FQ Default (No pfifo) + CAKE</td></tr>
<tr><td>MPTCP (WiFi + Cell Aggregation)</td></tr>
<tr><td>Paragon NTFS3 R/W OTG</td></tr>
<tr><td>Built-in USB Gigabit LAN</td></tr>
<tr><td>Bit-Perfect USB DAC Audio</td></tr>
<tr><td>BBG</td></tr>
<tr><td>WireGuard</td></tr>
<tr><td>le9uo v1.15 (MGLRU Off)</td></tr>
<tr><td>Workqueue Catch-up</td></tr>
<tr><td>Schedutil Catch-up</td></tr>
<tr><td>UFS WriteBooster Catch-up</td></tr>
<tr><td>NTSYNC /dev/ntsync</td></tr>
<tr><td>Re:Kernel Port 22</td></tr>
<tr><td>LZ4 v1.10.0 + ZSTD v1.5.7</td></tr>
<tr><td>SYSVIPC Droidspaces</td></tr>
<tr><td>SUSFS {susfs_ver} Built-in</td></tr>
</table>
</details>
</details>

<details>
<summary><tg-button type="disabled" style="primary">Changelog & Backports</tg-button></summary>

<details>
<summary>Upstream 6.1.190 LTS & CVE Backports</summary>

- Linux LTS: Synced cleanly to upstream Linux 6.1.190 LTS (SAGA stable MTK architecture with timer/fwnode shims)
- Pinmux (8434dec94): Fix race causing mux_owner NULL with active mux_usecount
- Block blk-mq (26d495f0f6): Fix tag memory leak when shrinking nr_hw_queues
- F2FS Sysfs (8b927ad2d1): Use modern IOPRIO_PRIO_LEVEL macro for checkpoint sysfs
- IPsec ESP4/ESP6 (cb37596580): Prevent managed frag page refcount leak in esp_ssg_unref
- UDP Tunnel (d53a8b927ac): Synchronous cancel of delayed work to avoid UAF on unregister
- Futex Note: FUT_OFF_MMSHARED deferred to protect mm_struct KABI reserve slots
- Bluetooth & DMA-Buf: Upstream stability, race condition, and UAF mitigations
</details>

<details>
<summary>Features & System Tuning</summary>

- BORE (Burst-Oriented Response Enhancer) v6.8.0-rc1 (kernel.sched_bore = 1)
- Power-Efficient Workqueues (CONFIG_WQ_POWER_EFFICIENT_DEFAULT=y)
- le9uo v1.15 Working Set Protection (MGLRU disabled for MTK stability)
- LZ4 v1.10.0 ARM64 NEON + ZSTD v1.5.7 (from Linux 6.15)
- LZ4K & LZ4KD high-throughput compression engines
- Google TCP BBRv3 + Default FQ Pacing (legacy pfifo retired)
- Built-in Gigabit USB LAN Ethernet (Realtek RTL8152 + ASIX AX88179)
- Native Paragon NTFS3 Full R/W support for Windows USB OTG drives
- Multipath TCP (CONFIG_MPTCP=y) simultaneous WiFi + Cellular aggregation
- CAKE Smart Queue Management (CONFIG_NET_SCH_CAKE=y)
- Netfilter TTL / HL hop-limit target bypass (unlimited hotspot tethering)
- Bit-Perfect & Hi-Res USB DAC Audio bypass (CONFIG_SND_USB_AUDIO=y)
- NTSYNC (/dev/ntsync) Windows NT sync driver for Wine/Winlator
- Re:Kernel Port 22 + Gamepad Force Feedback + BBG
- SuSFS {susfs_ver} VFS root cloaking (Play Integrity STRONG / Banking hide)
- Compatibility: Universal Android 14 GKI 6.1 (Tested on POCO X7 / Redmi Note 14 Pro 5G)
</details>
</details>

<table bordered>
<tr><td>Kernel</td><td>Linux {KERNEL_VER}</td></tr>
<tr><td>Source</td><td><tg-button type="url" url="https://github.com/afarhandanu/ZephyrKernel">ZephyrKernel</tg-button></td></tr>
<tr><td>Branch</td><td><tg-button type="url" url="https://github.com/afarhandanu/ZephyrKernel">main</tg-button></td></tr>
<tr><td>Toolchain</td><td>Neutron Clang 24.0.0git + LLD 24.0.0</td></tr>
<tr><td>LTO</td><td>{lto_html}</td></tr>
</table>

<table bordered>
<tr><td>Mountless Engine</td><td><tg-button type="disabled">None</tg-button></td></tr>
<tr><td>MPTCP</td><td><tg-button type="disabled" style="success">Enable</tg-button></td></tr>
<tr><td>Power-Efficient WQ</td><td><tg-button type="disabled" style="success">Enable</tg-button></td></tr>
<tr><td>Google FQ Pacing</td><td><tg-button type="disabled" style="success">Enable</tg-button></td></tr>
<tr><td>Hi-Res USB Audio</td><td><tg-button type="disabled" style="success">Enable</tg-button></td></tr>
<tr><td>Droidspaces</td><td><tg-button type="disabled" style="success">Enable</tg-button></td></tr>
<tr><td>Re:Kernel</td><td><tg-button type="disabled" style="success">Enable</tg-button></td></tr>
<tr><td>NTSync</td><td><tg-button type="disabled" style="success">Enable</tg-button></td></tr>
<tr><td>LZ4+ZSTD</td><td><tg-button type="disabled" style="success">Enable</tg-button></td></tr>
<tr><td>LZ4KD</td><td><tg-button type="disabled" style="success">Enable</tg-button></td></tr>
<tr><td>MGLRU</td><td><tg-button type="disabled" style="danger">Disable</tg-button></td></tr>
</table>

<tg-button-row><tg-button type="url" style="primary" url="https://t.me/FinaSU/">FinaSU v1.5.0+ · SuSFS {susfs_ver}</tg-button></tg-button-row>
<tg-button-row><tg-button type="url" style="primary" url="https://t.me/ksunext_ci/">KernelSU-Next · SuSFS {susfs_ver}</tg-button></tg-button-row>
<tg-button-row><tg-button type="url" style="primary" url="https://t.me/Sukiksu/7121/">SukiSU-Ultra · SuSFS {susfs_ver}</tg-button></tg-button-row>
<tg-button-row><tg-button type="url" style="primary" url="https://t.me/KernelSU_group/3234/">KernelSU · SuSFS {susfs_ver}</tg-button></tg-button-row>
<tg-button-row><tg-button type="url" style="primary" url="https://t.me/BakaSU_Grp/4/">BakaSU · SuSFS {susfs_ver}</tg-button></tg-button-row>
<tg-button-row><tg-button type="url" style="primary" url="https://t.me/kowsu_build/">KowSU · SuSFS {susfs_ver}</tg-button></tg-button-row>
<tg-button-row><tg-button type="callback_data" data="vanilla" style="primary">Vanilla (Non-Root / Pure GKI)</tg-button></tg-button-row>

<tg-button-row>
  <tg-button type="url" style="primary" url="{RELEASE_URL}">📦 GitHub Release</tg-button>
  <tg-button type="url" style="primary" url="https://github.com/afarhandanu/ZephyrKernel">⚡ Repository</tg-button>
</tg-button-row>

\\#GKI \\#Kernel \\#Zephyr"""

payload = {
    "markdown": rich_markdown,
    "media": [
        {"id": "banner1", "media": {"type": "photo", "media": "attach://banner_file1"}}
    ] if banner_path else []
}

payload_file = "/tmp/rich_payload.json"
with open(payload_file, "w", encoding="utf-8") as f:
    json.dump(payload, f)

# 3. Send Rich Message via Telegram API
cmd = [
    "curl", "-s", "-X", "POST", f"https://api.telegram.org/bot{BOT_TOKEN}/sendRichMessage",
    "-F", f"chat_id={CHAT_ID}",
    "-F", f"rich_message=<{payload_file}"
]
if banner_path:
    cmd.extend(["-F", f"banner_file1=@{banner_path}"])

print("Sending rich message with banner...")
res = subprocess.run(cmd, capture_output=True, text=True)
print("Rich message response:", res.stdout[:200])

# 4. Upload Built ZIP Packages
zip_files = sorted(glob.glob("release_assets/*.zip") + glob.glob("*.zip"))
seen = set()
unique_zips = []
for z in zip_files:
    bname = os.path.basename(z)
    if bname not in seen:
        seen.add(bname)
        unique_zips.append(z)

print(f"Uploading {len(unique_zips)} kernel zip files to Telegram...")
for zpath in unique_zips:
    fname = os.path.basename(zpath)
    doc_cmd = [
        "curl", "-s", "-X", "POST", f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
        "-F", f"chat_id={CHAT_ID}",
        "-F", f"document=@{zpath}",
        "-F", f"caption=📦 <b>{fname}</b>",
        "-F", "parse_mode=HTML"
    ]
    subprocess.run(doc_cmd, capture_output=True, text=True)

print("Telegram notification complete!")
