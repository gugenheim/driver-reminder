# DriverReminder

DriverReminder is a safety-first Windows 10/11 desktop utility that helps users remember to manually check for important driver and firmware updates.

> **Critical safety policy:** DriverReminder **never downloads, installs, flashes, or modifies drivers/firmware/BIOS**. It only detects hardware, tracks check history, sends reminders, and opens official vendor pages.

## Supported Platform

- Windows 10
- Windows 11
- Python 3.11+

## Features

- CustomTkinter dashboard with one card per update category
- System tray mode with actions:
  - Open Dashboard
  - Check Now
  - Rescan Hardware
  - Pause Reminders
  - Resume Reminders
  - Exit
- Background reminder scheduler with anti-spam notification logic
- Reminder intervals: Daily / Weekly / Monthly
- Per-category last-checked and last-notified tracking
- Pause reminders toggle
- Optional "Start DriverReminder when Windows starts" setting (HKCU Run key)
- Minimize-to-tray preference
- WMI-based hardware and installed-version detection where feasible
- Safe fallback behavior when detection is unavailable
- Official vendor link resolution for OEM and component vendors
- Optional tray icon file with programmatic fallback icon generation if missing/invalid

## Safety Notes

### BIOS / UEFI Warning

BIOS/UEFI updates are inherently risky.

- Update BIOS only when necessary (security fix, compatibility, vendor guidance).
- Use only official OEM or motherboard vendor support pages.
- Ensure reliable power and never interrupt firmware update processes.

### Automatic Update Behavior

DriverReminder does **not** auto-update anything. Manual user action is always required.

## Version Detection & Latest Lookup Scope

### Installed versions (local machine)
DriverReminder attempts to detect:
- BIOS version
- GPU driver version
- WiFi driver version
- Bluetooth driver version
- Audio driver version
- Storage controller driver version

If not feasible, it displays: `Installed version unavailable`.

### Latest version lookup (online)
DriverReminder only performs limited latest-version lookup where a reasonably reliable official endpoint exists.

- NVIDIA GPU lookup: attempted
- AMD/Intel latest lookup: currently treated as manual check required
- Other categories: manual check required

If unavailable/offline/unreliable, it displays: `Latest version lookup unavailable`.

## Screenshots

> _Add screenshots here (dashboard, tray menu, settings controls)._ 

## Repository Layout

```text
driver-reminder/
  README.md
  LICENSE
  .gitignore
  requirements.txt
  src/
    main.py
    ui/
      app.py
      tray.py
    scanner/
      hardware_scanner.py
      version_detector.py
    reminders/
      scheduler.py
      notifier.py
    storage/
      config_manager.py
    utils/
      vendor_links.py
      startup.py
      version_compare.py
  assets/
    icon.ico  # optional placeholder only
  tests/
    conftest.py
    test_config_manager.py
    test_vendor_links.py
    test_version_compare.py
```

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python src/main.py
```

## How Tray Mode Works

- By default, closing the window minimizes DriverReminder to tray.
- Reminders continue in the background while tray mode is active.
- Use tray menu actions to reopen dashboard, pause/resume reminders, or exit.
- Choosing **Exit** from the tray fully stops background threads.

## How Start with Windows Works

- Uses current-user Windows Run key (HKCU), no admin required in normal cases.
- Toggle in UI: **Start DriverReminder when Windows starts**.
- Setting is persisted in config and synced against registry state.

## Manual vs Automatic Responsibilities

### Automatic by app
- Hardware and installed-version detection (best effort)
- Reminder scheduling and notifications
- Tracking of last checked/last notified times

### Manual by user
- Visiting official vendor pages
- Determining whether update is needed
- Downloading/installing firmware or drivers

## Roadmap

- More robust official latest-version integrations for Intel/AMD where reliable
- Optional exportable update-check report
- Improved multi-device differentiation for systems with many adapters
