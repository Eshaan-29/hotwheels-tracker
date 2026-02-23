import os
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

# Grab your Twilio info from GitHub Secrets
SID = os.environ.get("TWILIO_SID")
TOKEN = os.environ.get("TWILIO_TOKEN")
FROM_NUM = os.environ.get("TWILIO_FROM")
TO_NUM = os.environ.get("YOUR_PHONE")

# FirstCry Hot Wheels URL
URL = "https://www.firstcry.com/hotwheels/5/0/113?sort=NewArrivals" 

def send_alert(message):
    client = Client(SID, TOKEN)
    client.messages.create(
        body=message,
        from_=FROM_NUM,
        to=TO_NUM
    )

try:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Custom targeted search based on your HTML code
    first_product_div = soup.find('div', class_='li_txt1') 
    
    if first_product_div and first_product_div.find('a'):
        product_name = first_product_div.find('a').get('title').strip()
        
        last_seen = ""
        if os.path.exists("last_seen.txt"):
            with open("last_seen.txt", "r") as f:
                last_seen = f.read().strip()
                
        if product_name != last_seen:
            send_alert(f"🚨 NEW HOT WHEELS DROP!\n{product_name}\nLink: {URL}")
            
            with open("last_seen.txt", "w") as f:
                f.write(product_name)
    else:
        print("Could not find any products. FirstCry might be blocking the connection.")
except Exception as e:
    print(f"Error checking FirstCry: {e}")
