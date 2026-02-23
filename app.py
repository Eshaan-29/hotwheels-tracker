import os
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
from flask import Flask

app = Flask(__name__)

# Grab your Twilio info from Render Environment Variables
SID = os.environ.get("TWILIO_SID")
TOKEN = os.environ.get("TWILIO_TOKEN")
FROM_NUM = os.environ.get("TWILIO_FROM")
TO_NUM = os.environ.get("YOUR_PHONE")

URL = "https://www.firstcry.com/hotwheels/5/0/113?sort=NewArrivals" 

def send_alert(message):
    client = Client(SID, TOKEN)
    client.messages.create(body=message, from_=FROM_NUM, to=TO_NUM)

# This route acts as the trigger. Every time the page is visited, it checks FirstCry.
@app.route('/')
def check_stock():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
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
                return f"Checked successfully: Found new item - {product_name}", 200
            else:
                return f"Checked successfully: No changes. Top item is still {product_name}", 200
        else:
            return "Checked: Could not find products. FirstCry might be blocking.", 500
    except Exception as e:
        return f"Error checking FirstCry: {e}", 500

if __name__ == '__main__':
    # Render assigns a dynamic port, so we must use this setup
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
