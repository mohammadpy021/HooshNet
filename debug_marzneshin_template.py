import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://panel.vizitur.ir:443"
USERNAME = "HooshNet"
PASSWORD = "your_password_here"  # I need to find the password from config or code

# I will read the password from settings_manager or config.json first
# But for now I'll use a placeholder and ask the agent to read it from file
