import os
import random
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
from flask import Flask

app = Flask(__name__)

SID = os.environ.get("TWILIO_SID")
TOKEN = os.environ.get("TWILIO_TOKEN")
FROM_NUM = os.environ.get("TWILIO_FROM")
TO_NUM = os.environ.get("YOUR_PHONE")

# Base URLs (We will automatically attach page numbers to these)
URLS = [
    "https://www.firstcry.com/hotwheels/5/0/113?sort=NewArrivals", 
    "https://www.firstcry.com/hotwheels/5/0/113?sort=Bestseller"                   
]

# 🎯 YOUR EXPANDED & SPELL-PROOF WISHLIST
TARGET_CARS = [
    "porsche", "bmw", "audi", "mercedes", "ford", 
    "mcmurthy", "mcmurtry", "nissan", "mazda", "f1", "formula 1", "formula one",
    "premium", "toyota", "lamborgini", "lamborghini", "rapid",
    "ferrari", "gordon murray", "barbie", "batman", "batmam", 
    "batmobile", "datsun", "pagani", "mclaren", "mc laren", "futurismo", "formula"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"
]

def send_alert(message):
    client = Client(SID, TOKEN)
    client.messages.create(body=message, from_=FROM_NUM, to=TO_NUM)

@app.route('/')
def check_stock():
    try:
        already_alerted = []
        if os.path.exists("alerted.txt"):
            with open("alerted.txt", "r") as f:
                already_alerted = f.read().splitlines()
                
        alerts_sent = 0
        items_scanned = 0
        random_agent = random.choice(USER_AGENTS)
        
        headers = {
            "User-Agent": random_agent,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Connection": "keep-alive"
        }
        
        # Loop through BOTH links
        for base_url in URLS:
            # 🚀 DEEP SCAN: Check Page 1, Page 2, and Page 3
            for page in range(1, 4):
                # Attach the page number to FirstCry's URL
                url = f"{base_url}&pageno={page}"
                
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                product_blocks = soup.find_all('div', class_='list_block') 
                items_scanned += len(product_blocks)
                
                for block in product_blocks:
                    # Ignore Out of Stock cars entirely
                    if block.get('data-outstock') == 'true':
                        continue 
                    
                    title_div = block.find('div', class_='li_txt1')
                    if title_div:
                        a_tag = title_div.find('a')
                        if a_tag:
                            full_title = a_tag.get('title').strip()
                            title_lower = full_title.lower()
                            
                            link = a_tag.get('href')
                            if not link.startswith("http"):
                                link = "https://www.firstcry.com" + link
                            
                            for target in TARGET_CARS:
                                if target in title_lower:
                                    if full_title not in already_alerted:
                                        send_alert(f"🚨 IN STOCK NOW!\nMatched: '{target.upper()}'\nItem: {full_title}\nLink: {link}")
                                        already_alerted.append(full_title)
                                        alerts_sent += 1
                                    break 
        
        # Save memory
        with open("alerted.txt", "w") as f:
            for item in already_alerted:
                f.write(f"{item}\n")
                
        if alerts_sent > 0:
            return f"Deep scan complete! Scanned {items_scanned} items. Found {alerts_sent} IN STOCK wishlist items.", 200
        else:
            return f"Deep scan complete safely. Scanned {items_scanned} items across 3 pages. No new wishlist items found.", 200

    except Exception as e:
        return f"Error checking FirstCry: {e}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
