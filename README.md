# Silverbullet Proxy Engine v7.0

A fast, lightweight, and completely dependency-free multi-api proxy aggregator written in pure Python. It extracts live HTTP, SOCKS4, SOCKS5, MTProto, and V2Ray configurations directly from verified cluster nodes. Perfect for both desktop Linux systems and mobile Termux environments.

## Features
- **Zero Dependencies:** Runs on pure Python built-in libraries (no `pip install` required).
- **Multi-Threaded:** Lightning-fast concurrent network handshake routines.
- **Auto-Formatting:** Automatically cleans, filters, and formats structural proxy logs.
- **Dual Export:** Saves unique extracted endpoints instantly to both `.txt` and `.json` formats.

---

## Installation & Setup

### For Termux (Android)
Open your Termux app and execute the following commands one by one:

```bash
# Update package database
pkg update && pkg upgrade -y

# Install required packages
pkg install git python -y

# Setup storage permissions (to allow file exports)
termux-setup-storage

# Clone the repository
git clone [https://github.com/Silverbullets1/silverbullet-proxy-engine.git](https://github.com/Silverbullets1/silverbullet-proxy-engine.git)

# Navigate into the directory
cd silverbullet-proxy-engine

# Run the engine
python silverbullet.py

For Linux (Ubuntu/Debian/Kali)
​Open your terminal and execute the following commands:

# Update and install Git & Python
sudo apt update
sudo apt install git python3 -y

# Clone the repository
git clone [https://github.com/Silverbullets1/silverbullet-proxy-engine.git](https://github.com/Silverbullets1/silverbullet-proxy-engine.git)

# Navigate into the directory
cd silverbullet-proxy-engine

# Run the engine
python3 silverbullet.py
