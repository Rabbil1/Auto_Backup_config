# Auto_Backup_config
# 🔄 Proscend Device Auto Backup Script

This Python script automates the login and configuration backup process for **Proscend devices** using **Selenium**. It reads a list of branches from a file, logs into each device via browser automation, and downloads the configuration as a `.tgz` file.

---

## 📦 Features

- Automates login and navigation using Selenium
- Bypasses SSL certificate warnings
- Downloads running configuration backups
- Organizes backups by bank/branch name
- Captures screenshots on error for troubleshooting

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/proscend-auto-backup.git
cd proscend-auto-backup
