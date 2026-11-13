### AnyKernel3 Ramdisk Mod Script
## osm0sis @ xda-developers
## Modded for ZephyrKernel

### AnyKernel setup
# global properties
properties() { '
kernel.string=ZephyrKernel (Universal Android 14 GKI 6.1.190)
do.devicecheck=0
do.modules=0
do.systemless=0
do.cleanup=1
do.cleanuponabort=0
do.check_boot_version=0
device.name1=
device.name2=
device.name3=
device.name4=
device.name5=
supported.versions=
supported.patchlevels=
supported.vendorpatchlevels=
'; } # end properties

### AnyKernel install
## boot shell variables (Both uppercase for latest AK3 and lowercase for legacy)
BLOCK=boot
IS_SLOT_DEVICE=auto
RAMDISK_COMPRESSION=auto
PATCH_VBMETA_FLAG=auto
NO_MAGISK_CHECK=1

block=boot
is_slot_device=auto
ramdisk_compression=auto
patch_vbmeta_flag=auto
no_magisk_check=1

# import functions/variables and setup patching
. tools/ak3-core.sh
magisk_patched=0

# Detect native kernel version directly from the new Image being flashed
IMAGE_FILE="$home/Image"
[ ! -f "$IMAGE_FILE" ] && IMAGE_FILE="Image"

if [ -f "$IMAGE_FILE" ]; then
    native_kver=$(strings "$IMAGE_FILE" 2>/dev/null | grep -m1 "Linux version " | awk '{print $3}')
    [ -z "$native_kver" ] && native_kver=$(tools/busybox strings "$IMAGE_FILE" 2>/dev/null | grep -m1 "Linux version " | awk '{print $3}')
fi
[ -z "$native_kver" ] && native_kver="6.1.190-android14-11-Zephyr"

# Device GKI check (read from running system)
running_kver=$(cat /proc/version 2>/dev/null | awk -F '-' '{print $1}' | awk '{print $3}')
case $running_kver in
    5.1*) gki_supported=true ;;
    6.1*) gki_supported=true ;;
    6.6*) gki_supported=true ;;
    *) gki_supported=false ;;
esac

ui_print " "
ui_print "  -> Flashing ZephyrKernel : $native_kver"
ui_print "  -> Current Device System : GKI $running_kver"
$gki_supported || abort "  -> Non-GKI device, abort."
ui_print "  • BORE v6.8.0-rc1 + Schedutil/Workqueue Catch-up"
ui_print "  • TCP BBRv3 + FQ Pacing (No pfifo) + CAKE Qdisc"
ui_print "  • MPTCP (WiFi + Cell) + Bit-Perfect USB DAC"
ui_print "  • Paragon NTFS3 R/W OTG + Built-in Gigabit USB LAN"
ui_print "  • NTSYNC (/dev/ntsync) + Re:Kernel Port 22"
ui_print "  • LZ4 NEON + ZSTD v1.5.7 + LZ4KD + le9uo v1.15"

# boot install
split_boot

if [ -f "$SPLITIMG/ramdisk.cpio" ]; then
    unpack_ramdisk
    write_boot
else
    flash_boot
fi

ui_print " "
ui_print "  -> ZephyrKernel successfully flashed!"
ui_print "  -> Enjoy your optimized experience."
ui_print " "
