# Unstats for Home Assistant

[![GitHub Release](https://img.shields.io/github/v/release/nicx17/unstats?style=for-the-badge)](https://github.com/nicx17/unstats/releases)
[![License](https://img.shields.io/github/license/nicx17/unstats?style=for-the-badge)](LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

A Home Assistant custom integration to fetch your Unsplash statistics natively. Instead of relying on external cron-jobs or scripts, this integration polls your Unsplash stats directly from within Home Assistant and provisions persistent sensors for your Views, Downloads, and Likes.

---

## Provided Sensors
When configured, this integration provisions three total-increasing sensors:
* `sensor.unsplash_views` - Total lifetime views of your photos
* `sensor.unsplash_downloads` - Total lifetime photo downloads
* `sensor.unsplash_likes` - Total lifetime likes on your photos

**Note:** The sensors automatically update every 60 minutes.

---

## Installation

### Method 1: HACS (Recommended)
1. Navigate to **HACS** in Home Assistant.
2. Click **Integrations**.
3. Search for "Unstats" and click **Download**.
4. Restart Home Assistant.

*(Note: Currently pending addition to the HACS default store. Until merged, you may add `https://github.com/nicx17/unstats` as a custom integration repository.)*

### Method 2: Manual
1. Download the latest release from the [Releases](https://github.com/nicx17/unstats/releases) page.
2. Unzip and copy the `custom_components/unstats` folder into your Home Assistant's `config/custom_components/` directory.
3. Restart Home Assistant.

---

## Configuration

Setup is done entirely through the Home Assistant UI. No `.env` files or YAML configuration required!

1. Go to **Settings** > **Devices & Services** in Home Assistant.
2. Click **Add Integration** in the bottom right corner.
3. Search for **"Unstats"**.
4. Enter your Unsplash **Username**.
5. Click **Submit**. The integration will verify your username and setup your sensors automatically.

---

## Data & Privacy

To fetch statistics without requiring users to set up complex Unsplash Developer OAuth applications, this integration utilizes a proxy server hosted by the developer.

**How it works:**
1. The integration sends a request containing *only your Unsplash Username* to `https://un.hyclotron.com`. 
2. The proxy server attaches the required Unsplash API credentials and queries the public Unsplash API.
3. The proxy server returns the exact stripped JSON response back to Home Assistant.

**Privacy Guarantee:**
* **No personal data** is stored, logged, or tracked on the proxy server.
* **No passwords or API keys** are ever required from the user.

---

## Issues & Support
If you run into any issues or want to request a feature, please [open an issue](https://github.com/nicx17/unstats/issues) on GitHub.

**License:** This project utilizes the [GPL-3.0 License](LICENSE).
