# DriverReminder

DriverReminder is a safety-first Windows 10/11 desktop utility that helps users remember to manually check for important driver and firmware updates from official vendor sources.

> **Critical safety policy:** DriverReminder **never downloads, installs, flashes, or modifies drivers, firmware, or BIOS**. It only detects hardware, tracks check history, sends reminders, and opens official vendor pages.

---

## Supported Platform

- Windows 10
- Windows 11
- Python 3.11+

---

## Features

- CustomTkinter dashboard with one card per update category
- Hardware detection using WMI for:
  - GPU
  - CPU
  - Motherboard
  - WiFi
  - Bluetooth
  - Audio
  - Storage
- Vendor identification for:
  - NVIDIA
  - AMD
  - Intel
  - Realtek
  - Qualcomm
  - Broadcom
  - Major OEM manufacturers
- System tray mode with actions:
  - Open Dashboard
  - Check Now
  - Rescan Hardware
  - Pause Reminders
  - Resume Reminders
  - Exit
- Background reminder scheduler with anti-spam notification logic
- Reminder intervals:
  - Daily
  - Weekly
  - Monthly
- Per-category last-checked and last-notified tracking
- Desktop notifications for overdue checks
- Quick links to official vendor pages
- Pause reminders toggle
- Optional "Start DriverReminder when Windows starts" setting
- BIOS/UEFI warning banner with cautionary messaging
- JSON-based local configuration storage
- Optional tray icon file with programmatic fallback icon generation if missing or invalid

---

## Safety Notes

### BIOS / UEFI Warning

BIOS/UEFI updates are inherently risky.

- Update BIOS only when necessary (security fixes, compatibility updates, or vendor guidance).
- Use only official OEM or motherboard vendor support pages.
- Ensure reliable power and never interrupt firmware update processes.

### Automatic Update Behavior

DriverReminder **does not automatically update anything**.  
Manual user action is always required.

---

## Version Detection & Latest Lookup Scope

### Installed Versions (Local Machine)

DriverReminder attempts to detect:

- BIOS version
- GPU driver version
- WiFi driver version
- Bluetooth driver version
- Audio driver version
- Storage controller driver version

If detection is not feasible for a category, it displays:

`Installed version unavailable`

---

### Latest Version Lookup (Online)

DriverReminder only performs limited latest-version lookup where a reasonably reliable official endpoint exists.

- NVIDIA GPU lookup: attempted
- AMD / Intel latest lookup: manual check required
- Other categories: manual check required

If unavailable, offline, or unreliable, it displays:

`Latest version lookup unavailable`

---

## Screenshots

> Add screenshots here (dashboard, tray menu, settings controls).

---

## Repository Layout
```
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
icon.ico # optional placeholder only
tests/
conftest.py
test_config_manager.py
test_vendor_links.py
test_version_compare.py
```

---

## Installation

### 1. Clone Repository
```
git clone <your-repo-url>
cd driver-reminder
```

### 2. Create and Activate Virtual Environment
```
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

---

## Run
```
python src/main.py
```

---

## Usage

Within the app:

1. Review detected hardware and identified vendors.
2. Choose a reminder interval.
3. Use the official page buttons to visit vendor support pages.
4. Click **Check Now** after manually verifying updates.
5. Minimize to tray to keep reminder checks running in the background.

---

## How Tray Mode Works

- Closing the window minimizes DriverReminder to the system tray.
- Reminders continue running in the background.
- Tray menu allows you to reopen the dashboard, pause reminders, resume reminders, or exit the application.
- Choosing **Exit** from the tray fully stops background threads.

---

## Start with Windows

DriverReminder can optionally start automatically when Windows launches.

- Uses the current-user Windows Run key
- No administrator privileges required
- Toggle available in the app UI
- Setting is stored in the configuration file

---

## Manual vs Automatic Responsibilities

### Automatic (Handled by the App)

- Hardware detection
- Installed-version detection (best effort)
- Reminder scheduling and notifications
- Tracking of last checked and last notified times

### Manual (User Responsibility)

- Visiting official vendor pages
- Deciding whether updates are necessary
- Downloading and installing drivers or firmware

---

## Notes

- Designed for **Windows 10/11**
- Hardware detection may be limited on non-Windows systems
- Vendor naming may vary depending on hardware model
- `assets/icon.ico` is optional — the app will fall back safely if it is missing or invalid

---

## Roadmap

Future improvements may include:

- Better official latest-version integrations for Intel and AMD
- Optional exportable driver check reports
- Improved multi-device differentiation for systems with many adapters

---

## Icon Handling

The tray icon file is optional.

If `assets/icon.ico` is missing or invalid, DriverReminder automatically generates a fallback icon so the application does not crash.
