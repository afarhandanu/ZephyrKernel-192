<div align="center">

# ⚡ ZephyrKernel — GKI 2.0 (`android14-6.1.192`)

[![Build ZephyrKernel (GKI 6.1.192)](https://github.com/afarhandanu/ZephyrKernel-192/actions/workflows/build-zephyr.yml/badge.svg)](https://github.com/afarhandanu/ZephyrKernel-192/actions/workflows/build-zephyr.yml)
[![Latest Release](https://img.shields.io/github/v/release/afarhandanu/ZephyrKernel-192?label=Latest%20Release&color=00b4d8)](https://github.com/afarhandanu/ZephyrKernel-192/releases/latest)
![Kernel Version](https://img.shields.io/badge/Linux-6.1.192%20LTS-blue?logo=linux)
![KMI](https://img.shields.io/badge/KMI-android14--11--Zephyr-success?logo=android)
![Compiler](https://img.shields.io/badge/Compiler-Neutron%20Clang%2024.0.0%20%2B%20ThinLTO-purple?logo=llvm)
![Builder](https://img.shields.io/badge/Builder-kucingbalap1644%40ZephyrCI-orange)

**High-performance, KABI-compliant Android Generic Kernel Image (GKI 2.0) built for `android14-6.1` devices (tested on Xiaomi POCO X7 / Redmi Note 14 Pro 5G `malachite` — MediaTek Dimensity 7300-Ultra `mt6878`), upstreamed to Linux 6.1.192 LTS.**

[📥 **Download Latest Release**](https://github.com/afarhandanu/ZephyrKernel-192/releases/latest) · [⚙️ **Run CI Build**](https://github.com/afarhandanu/ZephyrKernel-192/actions/workflows/build-zephyr.yml)

</div>

---

## ✨ Key Features & Enhancements

### 🔥 CPU, Scheduler, & Toolchain
- **Upstream Linux 6.1.192 LTS Core:** Synced from 6.1.190 to upstream Linux 6.1.192 LTS (+1,885 commits) with verified Android Common Kernel (ACK) fixups, timer compat shims (`timer_delete`, `timer_shutdown`, `timer_shutdown_sync`), restored GKI/MTK exports, and KABI struct layout preservation.
- **Power-Efficient Workqueues (`CONFIG_WQ_POWER_EFFICIENT_DEFAULT=y`):** Shifts workqueues to energy-efficient CPU cores when idle, reducing background battery drain significantly.
- **BORE CPU Scheduler (`v6.8.0-rc1`):** *Burst-Oriented Response Enhancer* (`kernel.sched_bore = 1`) for ultra-responsive UI rendering, low touch latency, and smooth multitasking under heavy load.
- **Neutron Clang `24.0.0git` + LLD `24.0.0`:** Configurable Link-Time Optimization supporting **ThinLTO (`CONFIG_LTO_CLANG_THIN=y`)**, **FullLTO (`CONFIG_LTO_CLANG_FULL=y`)**, or **NoLTO (`CONFIG_LTO_NONE=y`)**, paired with **Clang Control Flow Integrity (`CONFIG_CFI_CLANG=y`)** and persistent **`ccache`** compiler caching.
- **Mainline Catch-up Backports:** Includes `schedutil_catchup`, `workqueue_catchup`, and `ufs_writebooster_catchup` for optimal frequency scaling and UFS storage throughput.

### 🧠 Memory & Compression Architecture
- **le9uo Working Set Protection (`v1.15`):** Protects active anonymous and clean file pages (`vm.workingset_protection = 1`, `anon_min_ratio = 5`, `clean_min_ratio = 5`) from premature eviction while keeping MGLRU disabled (`CONFIG_LRU_GEN_ENABLED=n`) to guarantee 100% stability on MediaTek platforms.
- **LZ4 `v1.10.0` (ARM64 NEON Assembly) + ZSTD `v1.5.7` (Linux 6.15 Backport):** Hardware-accelerated compression/decompression across the kernel.
- **ZRAM `LZ4K` & `LZ4KD` + `Kcompressd v0.5`:** Built-in ZRAM with `lz4`, `lz4hc`, `lz4k`, `lz4kd`, `zstd`, `lzo-rle`, `deflate` support, paired with `kcompressd` background compression daemon and vendor module conflict bypass.

### 🌐 Networking, Audio, Storage, & Tethering
- **TCP BBRv3 (`bbr3`) + Boot Enforcer:** Google's 3rd-generation BBR congestion control set as default, reinforced by a delayed-work boot enforcer so vendor init scripts cannot revert it to `cubic`.
- **Google FQ Pacing Default (`CONFIG_NET_SCH_FQ=y` + `CONFIG_DEFAULT_NET_SCH="fq"`):** Sets Google Fair Queue pacing as the kernel default queue discipline (retiring legacy `pfifo_fast`), pairing directly with BBRv3 for zero packet drops, jitter elimination, and minimum bufferbloat in online gaming.
- **Built-in Gigabit USB LAN Ethernet Drivers (`CONFIG_USB_RTL8152=y` + `CONFIG_USB_NET_AX88179_178A=y`):** Native in-kernel support for Realtek RTL8152/RTL8153 and ASIX AX88179 USB-C Hub LAN adapters for instant plug-and-play wired Gigabit internet without missing vendor modules.
- **Paragon NTFS3 Native Full Read/Write (`CONFIG_NTFS3_FS=y` + `CONFIG_NTFS3_LZX_XPRESS=y`):** Built-in kernel support for Windows NTFS external storage drives and flash drives via USB-C OTG with full read/write, compression, and POSIX ACL support without needing third-party mounter apps.
- **Multipath TCP (`CONFIG_MPTCP=y`):** Simultaneous WiFi + Cellular data aggregation for ultra-fast downloads and seamless connection failover.
- **TCP Fast Open (`CONFIG_INET_TCP_DIAG=y`):** Accelerates subsequent HTTP/HTTPS handshakes by transmitting data in SYN packets.
- **Bit-Perfect & Hi-Res USB Audio (`CONFIG_SND_USB_AUDIO=y`):** Native hardware bypass support for external USB DACs (up to 32-bit / 768kHz and DSD).
- **CAKE Queue Discipline (`CONFIG_NET_SCH_CAKE=y`):** Smart Queue Management (SQM) to eliminate bufferbloat and ping spikes during online gaming.
- **TTL / HL Mangling (`IP_NF_TARGET_TTL` & `IP6_NF_TARGET_HL`):** Native packet hop-limit/TTL modification support for hotspot/tethering quota bypass.

### 🎮 Gaming, Containers, & Hardware Security
- **NTSYNC (`/dev/ntsync`):** Native Windows NT synchronization primitive driver for **Winlator / Mobox / Wine / Proton** PC gaming emulators.
- **Droidspaces / System V IPC (KABI-Safe):** `CONFIG_SYSVIPC=y` mapped into `ANDROID_KABI_USE(6, 7, 8)` padding slots, preserving exact MediaTek `struct task_struct` offsets (`#0x988`) for Linux containers/Docker without breaking vendor modules.
- **Re:Kernel (` Port 22 `):** Built-in Netlink server (`/proc/rekernel/22`) monitoring Binder transactions and signals to frozen apps for instant wakeups with **Millet / NoActive / Scene / Thanox**.
- **Full Gamepad + Force Feedback Support:** Built-in drivers with vibration support for **PlayStation 5 DualSense (`HID_PLAYSTATION` + `PLAYSTATION_FF`)**, **PlayStation 4 DualShock 4 (`HID_SONY` + `SONY_FF`)**, and **Xbox Controllers (`JOYSTICK_XPAD` + `JOYSTICK_XPAD_FF`)**.
- **Baseband Security Guard (`CONFIG_BBG=y`):** Linux Security Module protecting critical modem/IMEI partitions (`nvram`, `nvdata`, `persist`, `efs`) from unauthorized tampering.

### 🛡️ Multi-Variant Root & Stealth Integration
- **7 Selectable Root Variants (Single or Parallel `all` Matrix Build):**
  - **FinaSU (`v1.5.0+`):** Next-generation kernel-based root with dual-slot signature verification (supports both official **FinaSU Manager** and **KernelSU Manager**).
  - **KernelSU-Next (`dev-susfs`):** Feature-rich KernelSU fork by `KernelSU-Next` with native SUSFS integration.
  - **SukiSU-Ultra (`builtin` + KPM):** Enhanced root solution with built-in **Kernel Patch Module (`CONFIG_KPM=y`)** support.
  - **Official KernelSU (`tiann`):** Classic upstream KernelSU with full SUSFS patches.
  - **BakaSU:** Lightweight, performant root solution with full SUSFS integration.
  - **KowSU:** Enhanced root variant with native SUSFS cloaking support.
  - **Vanilla (`Non-Root`):** Clean, unrooted GKI 2.0 image without KernelSU or SUSFS (ideal for **Magisk**, **APatch**, or pure rootless setups).
- **SUSFS (`v2.4.0 Built-in`):** Full built-in VFS root-hiding suite (`hide_mounts`, `avc_spoof`, `uname`, `cmdline`, `path`, `map`, `dynamic_kstat`, `full_clone`, `static_kstat`, `redirect`, `logging`) on all rooted variants.
- **Full Vendor Module Compatibility:** Includes `check_version()` CRC bypass and GKI protected-exports bypass so all `/system_dlkm` and `/vendor_dlkm` modules (WiFi, Bluetooth, NFC, Camera, Audio SmartPA, GPU) load cleanly.

---

## 🚀 How to Build & Release via GitHub Actions

1. Open the [**Actions**](https://github.com/afarhandanu/ZephyrKernel-192/actions/workflows/build-zephyr.yml) tab.
2. Select **Build ZephyrKernel (GKI 6.1.192)** and click **Run workflow**.
3. Choose your desired options (Branding is permanently locked to `6.1.192-android14-11-Zephyr` / `kucingbalap1644@ZephyrCI` and protected by owner verification):
   - **Root Variant (`root_variant`):**
     - `finasu` — **FinaSU v1.5.0+** + SUSFS v2.4.0 Built-in (Default)
     - `ksunext` — **KernelSU-Next (`dev-susfs`)** + SUSFS Built-in
     - `sukisu` — **SukiSU-Ultra (`builtin` + KPM)** + SUSFS Built-in
     - `ksu` — **Official KernelSU (`tiann`)** + SUSFS Built-in
     - `bakasu` — **BakaSU** + SUSFS Built-in
     - `kowsu` — **KowSU** + SUSFS Built-in
     - `vanilla` — **Non-Root / Pure GKI** (for Magisk / APatch / rootless users)
     - `all` — **Parallel Matrix Build** (builds all 7 variants simultaneously on parallel runners and publishes them into a single unified GitHub Release!)
   - **LTO Optimization (`lto_mode`):**
     - `thin` — **ThinLTO** (Default)
     - `full` — **FullLTO**
     - `none` — **NoLTO**
     - `all` — **Parallel Matrix Build** (builds ThinLTO, FullLTO, and NoLTO simultaneously!)
   - **Compiler Cache (`ccache`):** Automatically caches compiled object files (`~/.ccache`, up to 5 GB compressed) across builds for ultra-fast incremental rebuilds!
4. When the workflow finishes, all flashable AnyKernel3 `.zip` packages are automatically published to [**GitHub Releases**](https://github.com/afarhandanu/ZephyrKernel-192/releases) and uploaded to workflow **Artifacts**!

---

## 📦 Flashing Instructions

> [!IMPORTANT]
> Always back up your stock `boot` and `init_boot` images before flashing any custom kernel.

1. Download the latest `Zephyr-GKI-6.1.192-*.zip` from [**Releases**](https://github.com/afarhandanu/ZephyrKernel-192/releases/latest).
2. Flash the `.zip` using **Franco Kernel Manager (FKM)**, **Kernel Flasher**, **Bolt**, or Custom Recovery.
3. Reboot and enjoy!

---

## 🙏 Credits & Acknowledgments
- [**chainonyourdoor / LuminaireKernel-6.1**](https://github.com/chainonyourdoor/LuminaireKernel-6.1) & [**dikafarabian / workbench**](https://github.com/dikafarabian/workbench) — Kernel base & patch integration suite
- [**LyraVoid / FinaSU**](https://github.com/LyraVoid/FinaSU) — Kernel root solution
- [**simonpunk / susfs4ksu**](https://gitlab.com/simonpunk/susfs4ksu) — SUSFS root-hiding subsystem
- [**WildKernels / kernel_patches**](https://github.com/WildKernels/kernel_patches) & [**SukiSU-Ultra**](https://github.com/SukiSU-Ultra/SukiSU_patch) — KABI fixes, BBRv3, NTSYNC, & LZ4KD patches
- [**Neutron-Toolchains**](https://github.com/Neutron-Toolchains/clang-build-catalogue) — Bleeding-edge LLVM/Clang 24 toolchain
