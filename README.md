# DriverReminder

DriverReminder is a safety-first Windows 10/11 desktop utility that helps users remember to manually check for important driver and firmware updates from official vendor sources.

> **Critical safety policy:** DriverReminder **never downloads, installs, flashes, or modifies drivers, firmware, or BIOS**. It only detects hardware, tracks check history, sends reminders, and opens official vendor pages.

## Supported Platform

- Windows 10
- Windows 11
- Python 3.11+

## Features

- CustomTkinter dashboard with one card per update category
- Hardware detection using WMI for:
  - GPU
  - CPU
  - motherboard
  - WiFi
  - Bluetooth
  - audio
  - storage
- Vendor identification for NVIDIA, AMD, Intel, Realtek, Qualcomm, Broadcom, and major OEMs
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
- Desktop notifications for overdue checks
- Quick links to official vendor pages
- Pause reminders toggle
- Optional "Start DriverReminder when Windows starts" setting
- BIOS/UEFI warning banner with cautionary messaging
- JSON-based local configuration storage
- Optional tray icon file with programmatic fallback icon generation if missing or invalid

## Safety Notes

### BIOS / UEFI Warning

BIOS/UEFI updates are inherently risky.

- Update BIOS only when necessary, such as for security fixes, compatibility, or official vendor guidance.
- Use only official OEM or motherboard vendor support pages.
- Ensure reliable power and never interrupt firmware update processes.

### Automatic Update Behavior

DriverReminder does **not** automatically update anything. Manual user action is always required.

## Version Detection & Latest Lookup Scope

### Installed versions (local machine)

DriverReminder attempts to detect:

- BIOS version
- GPU driver version
- WiFi driver version
- Bluetooth driver version
- Audio driver version
- Storage controller driver version

If detection is not feasible for a category, it displays: `Installed version unavailable`.

### Latest version lookup (online)

DriverReminder only performs limited latest-version lookup where a reasonably reliable official endpoint exists.

- NVIDIA GPU lookup: attempted
- AMD/Intel latest lookup: currently treated as manual check required
- Other categories: manual check required

If unavailable, offline, or unreliable, it displays: `Latest version lookup unavailable`.

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
### Installation
## 1) Clone repository
```git clone <your-repo-url>
cd driver-reminder
```
## 2) Create and activate virtual environment
```python -m venv .venv
.venv\Scripts\activate
```
## 3) Install dependencies
```pip install -r requirements.txt
```
## Run
```python src/main.py
```
### Usage

Within the app:

1. Review detected hardware and identified vendors.

2. Choose a reminder interval.

3. Use the official page buttons to visit vendor support pages.

4. Click Check Now after you manually verify updates.

5. Minimize to tray to keep reminder checks running in the background.

### How Tray Mode Works

By default, closing the window minimizes DriverReminder to the tray.

Reminders continue in the background while tray mode is active.

Use tray menu actions to reopen the dashboard, pause or resume reminders, or exit.

Choosing Exit from the tray fully stops background threads.

### How Start with Windows Works

Uses the current-user Windows Run key in normal cases.

No admin rights should be required for standard use.

The setting is toggled from the app UI.

The setting is persisted in config and synced against startup state.

### Manual vs Automatic Responsibilities
## Automatic by app

Hardware and installed-version detection on a best-effort basis

Reminder scheduling and notifications

Tracking of last checked and last notified times

## Manual by user

Visiting official vendor pages

Deciding whether an update is needed

Downloading and installing firmware or drivers

## Notes

Designed for Windows 10/11.

On non-Windows environments, hardware detection may be limited.

Vendor availability and naming can vary by hardware model.

assets/icon.ico is optional; the app should safely fall back if it is missing or invalid.

## Roadmap

More robust official latest-version integrations for Intel and AMD where reliable

Optional exportable update-check report

Improved multi-device differentiation for systems with many adapters

## Icon Handling

The tray icon file is optional in this repository. If assets/icon.ico is missing or invalid, DriverReminder generates a fallback icon at runtime so the app does not crash.