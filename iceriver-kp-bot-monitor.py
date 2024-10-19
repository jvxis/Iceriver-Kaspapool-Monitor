import time
import requests
import telebot
import signal
import sys
import threading
import argparse

# Argument parser to handle command-line arguments
parser = argparse.ArgumentParser(description='IceRiver Bot')
parser.add_argument('--hk', type=str, required=True, help='Hosting token for the IceRiver API')
args = parser.parse_args()

# Use the hosting_token from the arguments
hosting_token = args.hk

# Telegram Bot Token
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Your Telegram ID
TELEGRAM_USER_ID = YOUR_TELEGRAM_USER_ID

#Your Kaspa Wallet
KASPA_WALLET = 'YOUR_KASPA_WALLET_ADDRESS'

print("Bot Started")

headers_basic = {
    "accept":"application/json,text/javascript,*/*;q=0.01",
    "accept-language": "pt-BR;pt;q=0.6",
    "content-type": "application/json; charset=UTF-8",
    "priority": "u=0,i",
    "sec-ch-ua": "\"Not)A;Brand\";v=\"99\",\"Brave\";v=\"127\",\"Chromium\";v=\"127\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-gpc": "1",
    "x-csrf-token": "7093b8bbd05c5020e55771bcf12fa7a14c5b43aa6b26cef471793a36462e6653s%3A32%3A%22gywSGgfdeAv8QWEdaIPTYFTb9huQ23zs%22%3B",
    "x-requested-with": "XMLHttpRequest",
    "cookie": f"lan=en-US; hosting_token={hosting_token}; hosting_email=jaimevbarros@gmail.com",
    "Referer": "https://host.iceriver.io/rig/miners-list",
    "Referer-Policy": "strict-origin-when-cross-origin"
}

# Function to check if the user is authorized
def is_authorized_user(user_id):
    return str(user_id) == str(TELEGRAM_USER_ID)

# Decorator function for authorization check
def authorized_only(func):
    def wrapper(message):
        if is_authorized_user(message.from_user.id):
            func(message)
        else:
            bot.reply_to(message, "⛔️ You are not authorized to execute this command.")
    return wrapper

# Function to get data from IceRiver with improved error handling
def get_data():
    url = "https://host.iceriver.io/rig/list"
    headers = headers_basic

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
        print(f"-------------------------------------REQUEST--------------------------------------------\n{response}\n-------------------------------------END---------------------------------------------")
        return response.json()
    
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        bot.send_message(TELEGRAM_USER_ID, "❌ Unable to connect to IceRiver API. Please check the network connection.")
        time.sleep(60)  # Retry after 1 minute if there's a connection error
        return None
    
    except requests.exceptions.HTTPError as e:
        # Handle 401 Unauthorized (token expired)
        if response.status_code == 401:
            print(f"Unauthorized access - Token expired: {e}")
            bot.send_message(TELEGRAM_USER_ID, "🔑 Host Token expired. Please update the token.")
        else:
            print(f"HTTP error occurred: {e}")
            bot.send_message(TELEGRAM_USER_ID, f"❌ HTTP error: {response.status_code} - {response.reason}")
        return None

    except requests.exceptions.RequestException as e:
        # Any other request exception
        print(f"An error occurred: {e}")
        bot.send_message(TELEGRAM_USER_ID, f"❌ An unexpected error occurred while retrieving data: {e}")
        return None

# Function to restart a worker
def restart_worker(worker_name):
    try:
        # Fetch the data to get the inner_name
        data = get_data()
        if data is None:
            bot.send_message(TELEGRAM_USER_ID, f"❌ Could not retrieve data for {worker_name} from IceRiver.")
            return

        miners = data['data']['rigs']
        inner_name = None
        for miner in miners:
            if miner['name'] == worker_name:
                inner_name = miner['inner_name']
                break

        if not inner_name:
            bot.send_message(TELEGRAM_USER_ID, f"❌ Worker with name {worker_name} not found.")
            return

        # Proceed with renaming using inner_name
        url = "https://host.iceriver.io/rig/set-miner-name"
        headers = headers_basic
        temp_name = worker_name + '1'

        # Step 1: Rename to a temporary name
        json_data = {'name': inner_name, 'worker_name': temp_name}
        response = requests.post(url, headers=headers, json=json_data)
        if response.status_code == 200:
            bot.send_message(TELEGRAM_USER_ID, f"🔄 Renaming {worker_name} to {temp_name}...")
            time.sleep(2)

            # Step 2: Rename back to the original name
            json_data = {'name': inner_name, 'worker_name': worker_name}
            response = requests.post(url, headers=headers, json=json_data)
            if response.status_code == 200:
                bot.send_message(TELEGRAM_USER_ID, f"✅ Successfully restarted worker {worker_name}.")
            else:
                bot.send_message(TELEGRAM_USER_ID, f"❌ Failed to rename {temp_name} back to {worker_name}.")
        else:
            bot.send_message(TELEGRAM_USER_ID, f"❌ Failed to rename {worker_name} to {temp_name}.")

    except Exception as e:
        bot.send_message(TELEGRAM_USER_ID, f"❌ Error while restarting worker {worker_name}: {e}")

# Function to check miners for IceRiver
def check_miners():
    data = get_data()
    if data is None:
        print("No data retrieved from IceRiver.")
        return

    miners = data['data']['rigs']
    
    for miner in miners:
        hash_rate_15min = miner['hash_rate_15min']
        avg_temp1 = miner['shutdownInfo']['avgtemp1']  # Assuming avgtemp1 is under shutdownInfo
        
        # Check for low hash rate
        if hash_rate_15min < 5:
            message = (
                f"⚠️ Attention! Miner {miner['name']} has a low 15-min hashrate: {hash_rate_15min} Th/s"
            )
            print(message)
            bot.send_message(TELEGRAM_USER_ID, message)

        # Check for high temperature
        if avg_temp1 > 89:
            message = (
                f"🌡️ High Temperature Warning! Miner {miner['name']} has a high avg temp: {avg_temp1}°C"
            )
            print(message)
            bot.send_message(TELEGRAM_USER_ID, message)

# Function to check workers in Kaspa Pool
def check_kaspa_pool_workers():
    KASPA_POOL_API_URL = f"https://kaspa-pool.org/api/user/workers/?wallet={KASPA_WALLET}"
    
    try:
        response = requests.get(KASPA_POOL_API_URL)
        response.raise_for_status()
        data = response.json()

        if data.get('error'):
            print(f"Kaspa Pool API Error: {data['error']}")
            bot.send_message(TELEGRAM_USER_ID, f"❌ Kaspa Pool API Error: {data['error']}")
            return

        current_time = int(time.time())
        workers = data.get('workers', [])

        for worker in workers:
            worker_name = worker.get('name', 'Unknown')
            last_share_time = worker.get('last_share_time', 0)

            if current_time - last_share_time > 300:
                message = f"⚠️ Worker {worker_name} is off (last share > 300 seconds). Restarting..."
                print(message)
                bot.send_message(TELEGRAM_USER_ID, message)

                # Execute the restart command for the worker
                restart_worker(worker_name)
            else:
                print(f"✅ Worker {worker_name} is ok (last share within 300 seconds).")

    except requests.exceptions.ConnectionError as e:
        print(f"Kaspa Pool Connection Error: {e}")
        bot.send_message(TELEGRAM_USER_ID, "❌ Unable to connect to Kaspa Pool API. Please check the network connection.")
    except requests.exceptions.HTTPError as e:
        print(f"Kaspa Pool HTTP Error: {e}")
        bot.send_message(TELEGRAM_USER_ID, f"❌ Kaspa Pool API HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Kaspa Pool Request Error: {e}")
        bot.send_message(TELEGRAM_USER_ID, f"❌ Kaspa Pool API Request Error: {e}")
    except Exception as e:
        print(f"Kaspa Pool Error: {e}")
        bot.send_message(TELEGRAM_USER_ID, f"❌ An unexpected error occurred while checking Kaspa Pool: {e}")

# Schedule the Kaspa Pool check every 10 minutes
def schedule_kaspa_pool_checks():
    def perform_checks():
        print("\nPerforming Kaspa Pool workers check...")
        check_kaspa_pool_workers()
        threading.Timer(600, perform_checks).start()  # Schedule the next check after 10 minutes

    perform_checks()

# Command to restart a worker by renaming it twice
@bot.message_handler(commands=['restart'])
@authorized_only
def restart_worker_command(message):
    try:
        miner_names = message.text.split()[1:]  # Get all miner names from the command
        
        for miner_name in miner_names:
            restart_worker(miner_name)  # Reuse the restart_worker function
            
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error occurred: {e}. Please use the command as /restart miner_name1 miner_name2 ...")

# Schedule the miner check every 10 minutes with a countdown using threading.Timer
def schedule_checks():
    def perform_checks():
        print("\nPerforming miner checks...")
        check_miners()
        # Schedule the next check after 10 minutes
        threading.Timer(600, perform_checks).start()

    perform_checks()  # Start the first check immediately

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print('Graceful shutdown initiated...')
    bot.stop_polling()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Start the bot in a separate thread
thread = threading.Thread(target=schedule_checks)
thread.start()

# Schedule the Kaspa pool checks
schedule_kaspa_pool_checks()

# Function to handle retries for bot polling
def start_bot_with_retries():
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(f"Error occurred: {e}")
            print("Retrying in 15 seconds...")
            time.sleep(15)

# Start the bot with retry mechanism
start_bot_with_retries()
