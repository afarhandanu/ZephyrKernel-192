#!/usr/bin/env python3
import os
import sys
import glob
import subprocess


def get_susfs_version() -> str:
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
                            return line.split('"')[1]
            except Exception:
                pass

    try:
        res = subprocess.run(
            ["curl", "-fsSL", "--max-time", "5", "https://gitlab.com/simonpunk/susfs4ksu/-/raw/gki-android14-6.1/kernel_patches/include/linux/susfs.h"],
            capture_output=True, text=True
        )
        for line in res.stdout.splitlines():
            if "#define SUSFS_VERSION" in line and '"' in line:
                return line.split('"')[1]
    except Exception:
        pass

    return "v2.4.0"


def main():
    ltos = os.environ.get("BUILD_LTOS", "thin")
    variants = os.environ.get("BUILD_VARIANTS", "finasu")
    kernel_ver = os.environ.get("KERNEL_VER", "6.1.192")
    susfs_ver = get_susfs_version()
    is_append = "--append" in sys.argv or os.environ.get("APPEND_RELEASE_NOTES") == "1"

    details = f"""
---

## 📖 Detailed Changelog & System Architecture

### 🛡️ Linux 6.1.192 LTS Upstream Sync & Security CVE Backports (SAGA 190 -> 6.1.192)

- **Upstream Linux {kernel_ver} LTS Base:** Full merge and integration with official Linux {kernel_ver} LTS stable release (upstreamed 1,885 commits from 6.1.190 to 6.1.192 with timer compat shims, restored `__skb_get_hash` / `__tty_port_tty_hangup` exports, and KABI struct preservation).
- **Pinctrl / Pinmux Race Fix (`8434dec94`):** Fixed race condition causing `mux_owner` to become NULL while `mux_usecount` is actively incremented.
- **Block Layer Tag Leak Fix (`26d495f0f6`):** Resolved memory leak in `blk_mq_realloc_tag_set_tags()` where request tags remained allocated when shrinking `nr_hw_queues`.
- **F2FS Checkpoint Sysfs Fix (`8b927ad2d1`):** Converted checkpoint thread priority reading to modern `IOPRIO_PRIO_LEVEL` macro for sysfs exports.
- **IPsec Zerocopy Frag Refcount Fix (`cb37596580`):** Prevented illegal unref of managed frag pages in `esp_ssg_unref()` across `esp4` and `esp6`, eliminating potential use-after-free and memory leaks in zerocopy IPsec.
- **UDP Tunnel Workqueue Sync Fix (`d53a8b927ac`):** Ensured pending delayed work is cleanly canceled synchronously via `cancel_delayed_work_sync()` upon device unregistration without deadlocking RTNL locks.
- **Bluetooth & DMA-Buf Upstream Hardening:** Integrated upstream fixes for HCI sync race conditions, L2CAP channel management, and fence synchronization races.
- **KMI Reserve Slots Preserved:** The upstream patch `FUT_OFF_MMSHARED` (`f470b7658`) was deliberately skipped to preserve critical `ANDROID_KABI_RESERVE` slots in `struct mm_struct`, maintaining 100% binary compatibility with MediaTek vendor drivers.

---

### ⚡ Performance & CPU Scheduler Enhancements

- **BORE (Burst-Oriented Response Enhancer) v6.8.0-rc1:**
  - Burst-score algorithm actively detects and prioritizes interactive, touch-driven UI threads (`kernel.sched_bore = 1`).
  - Eliminates UI frame drops, micro-stutters, and improves touchscreen input latency under heavy background load.
- **Power-Efficient Workqueues (`CONFIG_WQ_POWER_EFFICIENT_DEFAULT=y`):**
  - Dynamically routes unbound kernel workqueues to energy-efficient CPU clusters during device standby, dramatically reducing idle battery consumption.
- **Mainline Scheduler & Workqueue Catch-up:**
  - Backported upstream frequency scaling and workqueue improvements (`schedutil_catchup`, `workqueue_catchup`).
- **Frame Warning Suppressed:**
  - Disabled logcat frame-drop warnings (`FRAME_WARN=0`), eliminating kernel log buffer spam during high-FPS gaming sessions.
- **Governors Supported:** Schedutil, Ondemand, Performance.

---

### 🧠 Advanced Memory Management & ZRAM Compression

- **le9uo v1.15 Working Set Protection (MGLRU Disabled for MTK Stability):**
  - MediaTek Dimensity 7300/MT6878 lockups are prevented by cleanly disabling problematic MGLRU at runtime and defconfig level.
  - Active UI threads and foreground process working sets are safeguarded during intense memory pressure by le9uo.
- **Modern LZ4 v1.10.0 (ARM64 NEON Assembly):**
  - Fully vector-accelerated compression/decompression routines for fast ZRAM read/write cycles.
- **ZSTD v1.5.7 (Linux 6.15 Backport):**
  - Backported from Linux 6.15 mainline for state-of-the-art compression ratio on RAM-heavy multitasking.
- **LZ4K & LZ4KD High-Throughput Engines:**
  - Dedicated fast-path algorithms for compressed memory pages.
- **Memory Module Overrides:** Custom module blacklist overrides for `lzo`, `lzo_rle`, `zram`, and `zsmalloc`.

---

### 🌐 Networking, Audio & Storage Subsystem

- **Google TCP BBRv3 + Delayed-Work Boot Enforcer:**
  - Google's 3rd-generation Bottleneck Bandwidth and RTT congestion control set as default.
  - Reinforced by an active kernel daemon that overrides vendor init scripts from downgrading back to `cubic`.
- **Google FQ Pacing Default (`CONFIG_NET_SCH_FQ=y` + `CONFIG_DEFAULT_NET_SCH="fq"`):**
  - Sets Google Fair Queue pacing as the kernel default queue discipline (retiring legacy `pfifo_fast`), pairing directly with BBRv3 for zero packet drops, jitter elimination, and minimum bufferbloat.
- **Built-in Gigabit USB LAN Ethernet Drivers (`CONFIG_USB_RTL8152=y` + `CONFIG_USB_NET_AX88179_178A=y`):**
  - Native in-kernel support for Realtek RTL8152/RTL8153 and ASIX AX88179 USB-C Hub LAN adapters for instant plug-and-play wired Gigabit internet without missing vendor modules.
- **Native Paragon NTFS3 Full Read/Write (`CONFIG_NTFS3_FS=y` + `CONFIG_NTFS3_LZX_XPRESS=y`):**
  - Built-in kernel support for Windows NTFS external storage drives and flash drives via USB-C OTG with full read/write, compression, and POSIX ACL support without needing third-party mounter apps.
- **Multipath TCP (MPTCP `CONFIG_MPTCP=y`):**
  - Enables simultaneous Wi-Fi and Cellular data aggregation for faster multi-socket downloads and seamless failover.
- **CAKE Smart Queue Management (`CONFIG_NET_SCH_CAKE=y`):**
  - SQM traffic shaping eliminates bufferbloat and ping spikes in competitive online gaming.
- **TTL / HL Hop-Limit Target Bypass:**
  - Integrated `IP_NF_TARGET_TTL` and `IP6_NF_TARGET_HL` netfilter targets to bypass hotspot/tethering operator quota restrictions.
- **Built-in WireGuard VPN Acceleration:**
  - Native in-kernel cryptography for ultra-fast, low-overhead VPN tunneling.
- **Bit-Perfect & Hi-Res USB DAC Audio (`CONFIG_SND_USB_AUDIO=y`):**
  - Direct ALSA / UAC2 bit-perfect master bypass supporting up to 32-bit / 768kHz PCM and Native DSD playback without Android HAL resampler degradation.

---

### 🎮 Gaming, Hardware Addons & Root Variants

- **NTSYNC (`/dev/ntsync`):**
  - Direct Windows NT synchronization primitive driver for native high-performance gaming in Wine / Box64 / Winlator / Mobox.
- **Re:Kernel (`Port 22`):**
  - Built-in Netlink server (`/proc/rekernel/22`) monitoring Binder transactions and signals to frozen apps for instant wakeups with Millet / NoActive / Scene / Thanox.
- **Gamepad Force Feedback:**
  - Full rumble and trigger feedback support for PlayStation 5 DualSense, PS4 DualShock 4, and Xbox One / Series wireless controllers.
- **Storage Subsystem:** Mainline UFS WriteBooster catch-up and F2FS read extent cache locking optimizations.
- **Root Variants & Stealth Hiding:**
  - `finasu`: FinaSU v1.5.0+ with dual-slot signature verification + SuSFS {susfs_ver}
  - `ksunext`: KernelSU-Next with native SuSFS {susfs_ver} integration
  - `sukisu`: SukiSU-Ultra with Kernel Patch Module (`CONFIG_KPM=y`) + SuSFS {susfs_ver}
  - `ksu`: Upstream official KernelSU with SuSFS {susfs_ver}
  - `bakasu`: BakaSU root solution with SuSFS {susfs_ver}
  - `kowsu`: KowSU root solution with SuSFS {susfs_ver}
  - `vanilla`: Clean, pure GKI 2.0 image without any root modifications (for Magisk, APatch, or rootless setups)
  - **SuSFS {susfs_ver} Built-in:** Full VFS root-hiding suite (`hide_mounts`, `avc_spoof`, `uname`, `cmdline`, `path`, `map`, `dynamic_kstat`, `full_clone`, `static_kstat`, `redirect`, `logging`) to pass Play Integrity (STRONG) and banking app security checks.

---

### 📲 Flashing & Installation Instructions

> [!IMPORTANT]
> Always create a full backup of your current `boot` and `init_boot` partitions before flashing any custom kernel!

1. Download the AnyKernel3 `.zip` matching your desired root variant and LTO mode below.
2. Flash using **Kernel Flasher**, **Franco Kernel Manager (FKM)**, or via Custom Recovery (**TWRP / OrangeFox**).
3. If using KernelSU / FinaSU / SukiSU / SuSFS, install the corresponding manager APK after the first boot.
4. Reboot and enjoy the Zephyr experience!
"""

    if is_append:
        with open("release_notes.md", "a", encoding="utf-8") as f:
            f.write(details)
        print("Appended detailed release notes to release_notes.md successfully!")
        return

    header = f"""# ⚡ ZephyrKernel GKI 2.0 — `android14-6.1-Zephyr`
**High-performance, ultra-responsive, KMI-compliant Android Generic Kernel Image (GKI 2.0)**
*Built for Universal Android 14 GKI 6.1 devices (Tested on POCO X7 / Redmi Note 14 Pro 5G `malachite` — MT6878).*

---

### 📋 Release & Build Metadata

| Attribute | Specification |
| :--- | :--- |
| **Linux Kernel Base** | `Linux {kernel_ver} LTS (Upstream Stable Sync)` |
| **Kernel Branding** | `6.1.x-android14-11-Zephyr` |
| **Target Compatibility** | `Universal Android 14 GKI 6.1 (Tested: POCO X7 / Redmi Note 14 Pro 5G)` |
| **Architecture** | `ARM64 (aarch64) GKI 2.0` |
| **Builder / Host** | `kucingbalap1644@ZephyrCI` |
| **Compiler Toolchain** | `Neutron Clang 24.0.0git + LLD 24.0.0 (ccache enabled)` |
| **LTO Optimization Modes** | `{ltos}` |
| **Root Solutions Built** | `{variants}` |
| **KMI ABI Status** | `100% Android 14 KMI Compliant (0 broken symbols)` |
"""
    checksums = "\n---\n\n### 📦 SHA-256 Checksums\n```text\n"
    asset_dir = "release_assets"
    if os.path.exists(asset_dir):
        zips = sorted(glob.glob(os.path.join(asset_dir, "*.zip")))
        if zips:
            for z in zips:
                try:
                    res = subprocess.run(["sha256sum", z], capture_output=True, text=True, check=True)
                    checksums += res.stdout.replace(f"{asset_dir}/", "")
                except Exception:
                    pass
        else:
            checksums += "(No zip files found)\n"
    else:
        checksums += "(release_assets directory not present)\n"
    checksums += "```\n"

    with open("release_notes.md", "w", encoding="utf-8") as f:
        f.write(header + details + checksums)

    print("Generated release_notes.md successfully!")


if __name__ == "__main__":
    main()
