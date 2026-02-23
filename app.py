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

# The main FirstCry Hot Wheels page (Sorted by New Arrivals)
URL = "https://www.firstcry.com/hotwheels/5/0/113?sort=NewArrivals" 

# 🎯 YOUR WISHLIST
TARGET_CARS = [
    "porsche",
    "bmw",
    "audi",
    "mercedes",
    "ford",
    "mcmurthy",
    "mcmurtry", # Added correct spelling just in case
    "nissan",
    "mazda",
    "f1",
    "premium",
    "toyota",
    "lamborgini",
    "lamborghini", # Added correct spelling just in case
    "ferrari",
    "gordon murray",
    "batman"
    "Batmobile"
    "barbie"
    "datsun"
    "pagani"
]

def send_alert(message):
    client = Client(SID, TOKEN)
    client.messages.create(body=message, from_=FROM_NUM, to=TO_NUM)

@app.route('/')
def check_stock():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Scrape EVERY product title on the page
        products = soup.find_all('div', class_='li_txt1') 
        
        # Load our memory file of cars we've already alerted you about
        already_alerted = []
        if os.path.exists("alerted.txt"):
            with open("alerted.txt", "r") as f:
                already_alerted = f.read().splitlines()
                
        alerts_sent = 0
        
        # 2. Check each product on the page
        for p in products:
            a_tag = p.find('a')
            if a_tag:
                full_title = a_tag.get('title').strip()
                title_lower = full_title.lower()
                
                link = a_tag.get('href')
                if not link.startswith("http"):
                    link = "https://www.firstcry.com" + link
                
                # 3. Does it match your Wishlist?
                for target in TARGET_CARS:
                    if target in title_lower:
                        # Found a match! Have we alerted you about this exact car yet?
                        if full_title not in already_alerted:
                            # SEND ALERT!
                            send_alert(f"🚨 WISHLIST FOUND!\nMatched: '{target.upper()}'\nItem: {full_title}\nLink: {link}")
                            
                            # Add to memory so we don't spam you next time
                            already_alerted.append(full_title)
                            alerts_sent += 1
                        
                        # Stop checking other keywords for this specific car
                        break 
        
        # Save the updated memory list
        with open("alerted.txt", "w") as f:
            for item in already_alerted:
                f.write(f"{item}\n")
                
        if alerts_sent > 0:
            return f"Checked successfully: Found and sent {alerts_sent} wishlist alerts!", 200
        else:
            return "Checked successfully: No new wishlist items found.", 200

    except Exception as e:
        return f"Error checking FirstCry: {e}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
