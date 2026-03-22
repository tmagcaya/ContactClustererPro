# Contact Clusterer Pro

> ⚠️ **macOS ONLY:** This application intrinsically relies on Apple's native macOS Objective-C frameworks (`pyobjc`) to interface live with your iCloud/Mac Contacts database. It **will not** work on Windows, Linux, or non-Apple operating systems.

A beautiful, local web application to cluster and categorize your Mac Contacts based on custom Turkish short handles (e.g. Reis [Leader], Hoca [Mentor], Çırak [Mentee], Müşavir [Advisor], Ahbap [Buddy], Dost [Friend]) and geographically tag their Area Codes natively inside Apple Contacts.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/ContactClustererPro.git
   cd ContactClustererPro
   ```

2. **Create a Virtual Environment:**
   Run the following commands to isolate the project's packages from your system:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   Install the required Python libraries to interface with Apple Contacts and run the web server:
   ```bash
   pip install -r requirements.txt
   ```
   
## Prerequisites

1. **Terminal Privacy Access**: Because this app modifies your contacts locally, Apple requires explicit human permission.
   - Go to your Mac's **System Settings** -> **Privacy & Security** -> **Contacts**.
   - Make sure your terminal application (e.g. Terminal, iTerm, VS Code, or Cursor) is toggled **ON**.

## How to Run

1. Open your Terminal application.
2. Navigate to the downloaded folder and activate the python environment:
   ```bash
   cd path/to/folder
   source .venv/bin/activate
   ```
3. Start the web application server:
   ```bash
   python app.py
   ```
4. Open your web browser (Chrome, Safari, etc.) and go to **[http://127.0.0.1:5001](http://127.0.0.1:5001)**.

## Features
- **Visual Excellence**: A breathtaking, dark-mode glassmorphism interface built from scratch natively.
- **Auto-Geocoding**: US Phone numbers are parsed to identify their Area Codes and map them instantly to 2-letter state abbreviations (like `VA`, `MD` or `NC`). 
- **Native Sync Tooling**: Safely categorizes multiple contacts by modifying their specific "Company" field without overwriting existing jobs.
- **One-Click Backups**: Uses native `CNContactVCardSerialization` to package and download your entire Rolodex into a single `.vcf` file with one click for easy macOS restoration.

## Stopping the App
To turn off the web server, simply return to your terminal window where you typed `python app.py` and press `Ctrl + C` on your keyboard.

## ⚖️ Disclaimer
> **Use at your own risk.** This application hooks directly into Apple's native databases. While it includes robust fallback checks and a "Backup All Contacts" feature, we assume zero responsibility for data loss, accidental overrides, or iCloud sync conflicts depending on your system configuration. ***Please always use the included Backup button to preserve a `.vcf` copy of your contacts before running multi-select changes spanning hundreds of people.***
