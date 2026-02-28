# Unstats for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration to monitor your Unsplash developer statistics!

Instead of relying on an external cron-job or python script, this integration polls the Unsplash API directly from within Home Assistant and natively provisions persist sensors for your Views, Downloads, and Likes.

## Installation

### Method 1: HACS (Recommended)
1. Open HACS in your Home Assistant.
2. Go to Integrations > Tap the three dots (top right) > Custom repositories.
3. Add the URL to this repository (`https://github.com/nicx17/unstats`).
4. Select "Integration" as the category and tap Add.
5. Close the prompt, search for "Unstats" in HACS, and click Download.
6. Restart Home Assistant.

### Method 2: Manual Installation
1. Download the `unstats` folder from the `custom_components` directory in this repository.
2. Copy the folder into your Home Assistant's `config/custom_components/` directory.
3. Restart Home Assistant.

## Configuration & UI Setup

You no longer need to manage a `.env` file!

1. Go to **Settings > Devices & Services** in Home Assistant.
2. Click **Add Integration** at the bottom right.
3. Search for "Unstats".
4. Enter your Unsplash `Username`.
5. The integration will verify your credentials and automatically create three new sensors:
    - `sensor.unsplash_views`
    - `sensor.unsplash_downloads`
    - `sensor.unsplash_likes`

The sensors update every 60 minutes automatically.

## Default HACS Store Listing

For the official default HACS store listing process, follow:

- `DEFAULT_HACS_LISTING.md`
