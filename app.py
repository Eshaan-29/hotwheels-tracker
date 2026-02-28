import os
import random
import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

URL = "https://www.firstcry.com/hotwheels/5/0/113?sort=NewArrivals"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
]

@app.route('/')
def check_stock():
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        # We add a random number to bypass FirstCry's cache
        cache_buster = random.randint(100000, 999999)
        test_url = f"{URL}&nocache={cache_buster}"
        
        response = requests.get(test_url, headers=headers, timeout=10)
        
        # Build the X-Ray Dashboard
        html_output = f"<h1 style='font-family: Arial;'>🤖 Bot X-Ray Diagnostics</h1>"
        html_output += f"<h3 style='font-family: Arial;'>FirstCry Server Response Code: <span style='color:blue;'>{response.status_code}</span></h3>"
        
        # 403 means FirstCry blocked the Render server
        if response.status_code == 403 or response.status_code == 401:
            html_output += "<p style='color:red; font-family: Arial;'><b>❌ ERROR:</b> FirstCry's firewall has blocked Render's cloud servers. The bot is locked out.</p>"
            return html_output, 200

        soup = BeautifulSoup(response.text, 'html.parser')
        product_blocks = soup.find_all('div', class_='list_block') 
        
        html_output += f"<p style='font-family: Arial;'><b>Total Items Seen on Page 1:</b> {len(product_blocks)}</p>"
        html_output += "<h3 style='font-family: Arial;'>Top 15 Cars Currently Visible to the Bot:</h3><ul style='font-family: Arial;'>"
        
        count = 0
        for block in product_blocks:
            if count >= 15: break
            
            title_div = block.find('div', class_='li_txt1')
            out_stock_flag = block.get('data-outstock')
            
            if title_div and title_div.find('a'):
                title = title_div.find('a').get('title').strip()
                html_output += f"<li><b>{title}</b> <br><i>(FirstCry hidden out-of-stock tag says: {out_stock_flag})</i></li><br>"
                count += 1
                
        html_output += "</ul>"
        return html_output, 200

    except Exception as e:
        return f"Crash Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
