import secrets
import string
import time
import os
import sys
from datetime import date
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import threading
import json

# Logo in paarse kleur
logo = """
\033[95m
▄▄▄        ▄▄▄▄· ▄▄▌        ▐▄• ▄    ▄▄▄·  ▄▄·  ▄▄·       ▄• ▄▌ ▐ ▄ ▄▄▄▄▄   ▄▄ • ▄▄▄ . ▐ ▄
▀▄ █· ▄█▀▄ ▐█ ▀█▪██•   ▄█▀▄  █▌█▌▪  ▐█ ▀█ ▐█ ▌▪▐█ ▌▪ ▄█▀▄ █▪██▌•█▌▐█•██    ▐█ ▀ ▪▀▄.▀·•█▌▐█
▐▀▀▄ ▐█▌.▐▌▐█▀▀█▄██ ▪ ▐█▌.▐▌ ·██·   ▄█▀▀█ ██ ▄▄██ ▄▄▐█▌.▐▌█▌▐█▌▐█▐▐▌ ▐█.▪  ▄█ ▀█▄▐▀▀▪▄▐█▐▐▌
▐█•█▌▐█▌.▐▌██▄▪▐█▐█▌ ▄▐█▌.▐▌▪▐█·█▌  ▐█▪ ▐▌▐███▌▐███▌▐█▌.▐▌▐█▄█▌██▐█▌ ▐█▌·  ▐█▄▪▐█▐█▄▄▌██▐█▌
.▀  ▀ ▀█▄▀▪·▀▀▀▀ .▀▀▀  ▀█▄▀▪•▀▀ ▀▀   ▀  ▀ ·▀▀▀ ·▀▀▀  ▀█▄▀▪ ▀▀▀ ▀▀ █▪ ▀▀▀   ·▀▀▀▀  ▀▀▀ ▀▀ █▪
"""

# Titel in gewenste kleuren
title = """
\033[92m[✔]    https://github.com/coderjb1         [✔]
\033[92m[✔]            Version 1.1.0               [✔]
\033[97m⚠️ This script is made for educational purposes only ⚠️
"""

def print_logo_and_title():
    # Clear console
    os.system('cls' if os.name == 'nt' else 'clear')

    # Print logo
    print(logo)

    # Print title
    print(title)

def status(text):
    # Clear console and print logo/title before status
    print_logo_and_title()
    print("\033[1;32m" + text + "\033[0m")

# Config
MaxWindows = 1
ActualWindows = 0

# URLs
first_names_url = "https://raw.githubusercontent.com/coderjb1/roblox-account-gen/main/firstnames.txt"
last_names_url = "https://raw.githubusercontent.com/coderjb1/roblox-account-gen/main/lastname.txt"
roblox_url = "https://www.roblox.com/"

# Vragen om vertraging tussen accountcreatie
try:
    delay_seconds = int(input("Enter delay in seconds between creating each account: "))
except ValueError:
    print("Invalid input. Using default delay of 1 second.")
    delay_seconds = 1

# Vragen of Discord Webhook gebruikt moet worden
use_discord_webhook = input("Do you want to use a Discord webhook for notifications? (y/n): ").lower().strip()
discord_webhook_url = ""

if use_discord_webhook == 'y':
    discord_webhook_url = input("Enter your Discord webhook URL: ").strip()

# Controleren of namen succesvol geladen zijn
status("Getting first names...")
first_names_response = requests.get(first_names_url)
status("Getting last names...")
last_names_response = requests.get(last_names_url)

if first_names_response.status_code == 200 and last_names_response.status_code == 200:
    first_names = list(set(first_names_response.text.splitlines()))
    last_names = list(set(last_names_response.text.splitlines()))
else:
    status("Name loading failed. Re-Execute the script.")
    sys.exit()

# Bestandspad
account_file = "account.txt"

# Lijsten van dagen, maanden en jaren
days = [str(i + 1) for i in range(10, 28)]
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
years = [str(i + 1) for i in range(1980, 2004)]

# Wachtwoordgenerator (precies 23 tekens lang, alleen alfanumeriek)
def gen_password(length):
    status("Generating a password...")
    chars = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(chars) for _ in range(length))
    return password[:23]  # Beperk wachtwoord tot 23 tekens

# Gebruikersnaamgenerator
def gen_user(first_names, last_names):
    status("Generating a username...")
    first = secrets.choice(first_names)
    last = secrets.choice(last_names)
    full = f"{first}{last}_{secrets.choice([i for i in range(1, 999)]):03}"
    return full

def create_account(url, first_names, last_names, delay_seconds):
    global ActualWindows
    try:
        while True:
            status("Starting to create an account...")
            cookie_found = False
            username_found = False
            elapsed_time = 0

            # Open Microsoft Edge if not already open
            if ActualWindows < MaxWindows:
                status("Initializing webdriver...")
                driver = webdriver.Edge()
                driver.set_window_size(1200, 800)
                driver.set_window_position(0, 0)
                ActualWindows += 1
            else:
                # Wait for a free window if all are occupied
                status(f"Waiting... {ActualWindows}/{MaxWindows}")
                time.sleep(1)
                continue

            try:
                driver.get(url)
                time.sleep(2)

                # HTML items
                status("Searching for items on the website")
                username_input = driver.find_element("id", "signup-username")
                username_error = driver.find_element("id", "signup-usernameInputValidation")
                password_input = driver.find_element("id", "signup-password")
                day_dropdown = driver.find_element("id", "DayDropdown")
                month_dropdown = driver.find_element("id", "MonthDropdown")
                year_dropdown = driver.find_element("id", "YearDropdown")

                # Wait for gender buttons to be clickable
                male_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "MaleButton")))
                female_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "FemaleButton")))

                register_button = driver.find_element("id", "signup-button")

                status("Selecting day...")
                Selection = Select(day_dropdown)
                Selection.select_by_value(secrets.choice(days))
                time.sleep(0.3)

                status("Selecting month...")
                Selection = Select(month_dropdown)
                Selection.select_by_value(secrets.choice(months))
                time.sleep(0.3)

                status("Selecting year...")
                Selection = Select(year_dropdown)
                Selection.select_by_value(secrets.choice(years))
                time.sleep(0.3)

                while not username_found:
                    status("Selecting username...")
                    username = gen_user(first_names, last_names)
                    username_input.clear()
                    username_input.send_keys(username)
                    time.sleep(1)
                    if username_error.text.strip() == "":
                        username_found = True
                
                status("Selecting password...")
                password = gen_password(23)  # Generate a 23-character password
                password_input.send_keys(password)
                time.sleep(0.3)

                status("Selecting gender...")
                gender = secrets.choice([1, 2])
                if gender == 1:
                    male_button.click()
                else:
                    female_button.click()
                time.sleep(0.5)

                status("Registering account...")
                register_button.click()
                time.sleep(3)

                # Wait until the account creation limit is reset
                try:
                    driver.find_element("id", "GeneralErrorText")
                    driver.quit()
                    ActualWindows -= 1
                    for i in range(360):
                        status(f"Limit reached, waiting... {i+1}/{360}")
                        time.sleep(1)
                    continue  # Skip the rest of the loop if limit reached
                except:
                    pass

                # Wait until the cookie is found or the maximum time has passed
                while not cookie_found and elapsed_time < 180:
                    status("Waiting for the cookie...")
                    time.sleep(3)
                    elapsed_time += 3
                    for cookie in driver.get_cookies():
                        if cookie.get('name') == '.ROBLOSECURITY':
                            cookie_found = True
                            break
                if cookie_found:
                    status("Cookie found...")
                    result = [username, password]
                    save_account_info(result)
                    send_discord_message(username, password)
                    if result is not None:
                        status("Successfully created!")
                        time.sleep(3)
                        ActualWindows -= 1
                        status(f"Open windows: {ActualWindows}")
                        pass

            except Exception as e:
                status(f"Error: {e}")
                ActualWindows -= 1
                driver.quit()

    except Exception as e:
        status(f"Error: {e}")
        ActualWindows -= 1

# Save account information to text file
def save_account_info(account_info):
    try:
        status("Saving account info...")
        with open(account_file, 'a') as file:
            file.write(f"Username: {account_info[0]}\nPassword: {account_info[1]}\n\n")
        status("Account info saved successfully.")
    except Exception as e:
        status(f"Error saving account info: {e}")
        # Print traceback for debugging purposes if needed
        import traceback
        traceback.print_exc()

# Function to send Discord webhook message
def send_discord_message(username, password):
    try:
        if discord_webhook_url:
            status("Sending Discord webhook message...")
            webhook_data = {
                "content": ":white_check_mark: Account successfully generated!",
                "embeds": [
                    {
                        "title": "Account Details",
                        "description": f"Username: {username}\nPassword: {password}"
                    }
                ]
            }
            headers = {'Content-Type': 'application/json'}
            response = requests.post(discord_webhook_url, data=json.dumps(webhook_data), headers=headers)
            if response.status_code == 204:
                status("Discord webhook message sent successfully.")
            else:
                status(f"Failed to send Discord webhook message. Status code: {response.status_code}")
    except Exception as e:
        status(f"Error sending Discord webhook message: {e}")

# Start het script door het maken van accounts
while True:
    create_account(roblox_url, first_names, last_names, delay_seconds)
