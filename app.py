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

URLS = [
    "https://www.firstcry.com/hotwheels/5/0/113?sort=NewArrivals", 
    "https://www.firstcry.com/hotwheels/5/0/113?sort=Bestseller"                   
]

TARGET_CARS = [
    "porsche", "bmw", "audi", "mercedes", "ford", 
    "mcmurthy", "mcmurtry", "nissan", "mazda", "f1", 
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
        
        for base_url in URLS:
            for page in range(1, 7):
                cache_buster = random.randint(100000, 999999)
                url = f"{base_url}&pageno={page}&nocache={cache_buster}"
                
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                product_blocks = soup.find_all('div', class_='list_block') 
                items_scanned += len(product_blocks)
                
                for block in product_blocks:
                    # 🛑 WE DELETED THE LIAR CODE! The bot no longer trusts data-outstock.
                    
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
                                        
                                        # DOUBLE VERIFICATION: Check the actual product page directly
                                        try:
                                            prod_resp = requests.get(link, headers=headers, timeout=10)
                                            prod_text = BeautifulSoup(prod_resp.text, 'html.parser').get_text().upper()
                                            
                                            if "NOTIFY ME" in prod_text or "OUT OF STOCK" in prod_text:
                                                break # It's a ghost item. Move on.
                                                
                                            # It's a real drop! SEND THE ALERT!
                                            send_alert(f"🚨 CONFIRMED IN STOCK!\nMatched: '{target.upper()}'\nItem: {full_title}\nLink: {link}")
                                            already_alerted.append(full_title)
                                            alerts_sent += 1
                                            
                                        except Exception as e:
                                            print(f"Failed to verify {full_title}: {e}")
                                            
                                    break 
        
        with open("alerted.txt", "w") as f:
            for item in already_alerted:
                f.write(f"{item}\n")
                
        if alerts_sent > 0:
            return f"Deep scan complete! Scanned {items_scanned} items. Found {alerts_sent} CONFIRMED IN STOCK wishlist items.", 200
        else:
            return f"Deep scan complete safely. Scanned {items_scanned} items across 6 pages. No new CONFIRMED items.", 200

    except Exception as e:
        return f"Error checking FirstCry: {e}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
