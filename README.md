# DriverReminder

DriverReminder is a lightweight Windows desktop utility that helps users remember to manually check for critical driver and firmware updates from official vendor sources.

> **Safety-first design:** DriverReminder **never installs drivers or firmware automatically**. It only reminds users and opens official vendor pages.

## Features

- Hardware detection using WMI (GPU, CPU, motherboard, WiFi, Bluetooth, audio, storage)
- Vendor identification for NVIDIA, AMD, Intel, Realtek, Qualcomm, Broadcom, and major OEMs
- Reminder intervals: Daily, Weekly, Monthly
- Per-category "last checked" tracking
- Desktop notifications for overdue checks
- Quick links to official vendor pages
- BIOS/UEFI warning banner with cautionary messaging
- System tray support for background reminders
- JSON-based local configuration storage

## Screenshots

> _Add screenshots here (UI dashboard, reminder settings, tray behavior)._ 

## Project Structure

```text
driver-reminder/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── src/
│   ├── main.py
│   ├── ui/
│   │   └── app.py
│   ├── scanner/
│   │   └── hardware_scanner.py
│   ├── reminders/
│   │   ├── scheduler.py
│   │   └── notifier.py
│   ├── storage/
│   │   └── config_manager.py
│   └── utils/
│       └── vendor_links.py
├── assets/
│   └── icon.ico  # optional placeholder; binary icon not included
└── tests/
```

## Installation

### 1) Clone repository

```bash
git clone <your-repo-url>
cd driver-reminder
```

### 2) Create and activate virtual environment (recommended)

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

Run the app:

```bash
python src/main.py
```

Within the app:

1. Review detected hardware and identified vendors.
2. Choose reminder interval (daily/weekly/monthly).
3. Use **Open Page** buttons to visit official driver/firmware pages.
4. Click **Check Now** after you manually verify updates.
5. Minimize to tray to keep reminder checks running in the background.

## BIOS / UEFI Safety Warning

BIOS/UEFI updates can be risky if interrupted or applied incorrectly.

- Only update BIOS/UEFI when necessary (security fix, hardware compatibility issue, vendor recommendation).
- Always use your motherboard/laptop manufacturer's official instructions.
- Ensure stable power and never force shutdown during firmware updates.

## Notes

- Designed for **Windows 10/11**.
- On non-Windows environments, hardware detection may be limited.
- Vendor availability and naming can vary by hardware model.
- `assets/icon.ico` is optional; app safely falls back to default tray/window visuals if missing or invalid.
