# IceRiver and Kaspa Bot
This project is a Python bot designed to monitor *IceRiver ASICS* and *Kaspa pool workers*. The bot is configured to send alerts via Telegram when there are issues with miners or Kaspa workers, such as low hashrate or high temperatures. It also has the functionality to restart workers directly through Telegram commands. **IMPORTANT** The automatic restart in case of OFFLINE was design to work with **KASPA POOL** only!

## Features
.Monitor IceRiver miners for low hashrate or high temperature.

.Monitor Kaspa pool workers for inactivity (no shares within a 300-second window).

.Automatically restart problematic workers through a renaming mechanism.

.Send real-time alerts via Telegram.

.Configurable settings for Telegram Bot Token, User ID, and Kaspa Wallet.

.Handles API errors, connection issues, and retries automatically.
## Requirements
.Python 3.6+

.pyTelegramBotAPI

.requests library
## Installation
### Step 1: Clone the Repository
```bash
git clone https://github.com/jvxis/Iceriver-Kaspapool-Monitor.git
cd Iceriver-Kaspapool-Monitor
```
### Step 2: Install the Required Dependencies
```bash
pip3 install -r requirements.txt
```
Ensure you have the following Python libraries installed:

`telebot` (for interacting with Telegram)
`requests` (for making API calls)
### Step 3: Configure the Bot
In the script, you need to customize the following parameters:

```python
# Telegram Bot Token
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Your Telegram User ID (replace with your ID)
TELEGRAM_USER_ID = YOUR_TELEGRAM_USER_ID

# Your Kaspa Wallet (replace with your wallet address)
KASPA_WALLET = 'YOUR_KASPA_WALLET_ADDRESS'

#Your CSRF-TOKEN
CSRF_TOKEN = 'YOUR_CSRF_TOKEN'

#Your ICERIVER Login email
YOUR_EMAIL = 'YOUR_EMAIL'

```
## To configure these settings:
.Open the script file bot.py.

.Replace YOUR_TELEGRAM_BOT_TOKEN with the token from @BotFather when you create a bot.

.Replace YOUR_TELEGRAM_USER_ID with your own Telegram ID (you can get it by starting telegram @userinfobot).

.Replace YOUR_KASPA_WALLET_ADDRESS with your Kaspa wallet address.

.Replace CSRF_TOKEN with your Iceriver Session Token.

.Replace YOUR_EMAIL with the email you use to Login in Iceriver.
### Step 4: Running the Bot
You need to provide a hosting token for the IceRiver API via a command-line argument.

```bash
python3 iceriver-kp-bot-monitor.py --hk YOUR_HOSTING_TOKEN
```
Replace YOUR_HOSTING_TOKEN with your actual hosting token for the IceRiver API.

## Customization
You can also customize the behavior of the bot by modifying the following sections of the code:

Alert thresholds for hashrate and temperature (default: hashrate < 5 Th/s, temperature > 89°C).

Scheduling intervals for checks (default: every 10 minutes for both IceRiver miners and Kaspa workers).
## Available Commands
Once the bot is running, you can use the following Telegram commands:

`/restart <worker_name>` : Restart a specified worker by its name.

Example:

```bash
/restart worker_name1
```
The bot will automatically restart the specified worker using the renaming process.

You can also user for multiple workers
Example:

```bash
/restart worker_name1 worker_name2 worker_name3
```

## Graceful Shutdown
The bot handles SIGINT (Ctrl + C) for graceful shutdown. This ensures that the bot stops polling and terminates all threads safely.

## Error Handling and Retries
The bot includes error handling for:

Connection errors to both IceRiver and Kaspa APIs.
Invalid responses or unauthorized access (such as token expiration).
If an error occurs during polling or API calls, the bot will retry after 15 seconds.
