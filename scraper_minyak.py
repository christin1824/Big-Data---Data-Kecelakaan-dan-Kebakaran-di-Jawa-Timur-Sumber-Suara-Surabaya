from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

app = Flask(__name__)

def get_yt_comments(url, driver):
    driver.get(url)
    time.sleep(5) 
    
    try:
        # Scroll down untuk memicu loading komentar
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(3)

        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)

        # Mengambil elemen kontainer komentar
        comment_sections = driver.find_elements(By.ID, "comment")
        
        results = []
        for section in comment_sections:
            try:
                # Ambil Nama User (Author)
                author = section.find_element(By.ID, "author-text").text.strip()
                # Ambil Isi Komentar
                comment_text = section.find_element(By.ID, "content-text").text.strip()
                # Ambil Jumlah Like (Vote Count)
                likes = section.find_element(By.ID, "vote-count-middle").text.strip()
                
                if len(comment_text) > 5:
                    results.append({
                        "author": author if author else "Anonymous",
                        "comment": comment_text,
                        "likes": likes if likes else "0"
                    })
            except:
                continue
                
        return results
    except Exception as e:
        print(f"Error di {url}: {e}")
        return []

@app.route('/scrape-yt', methods=['GET'])
def scrape_all():
    sources = [
        {"url": "https://www.youtube.com/watch?v=ufTpx4zL1VI", "category": "Berita Nasional"}, 
        {"url": "https://www.youtube.com/watch?v=efq-7Lv0Sws", "category": "Opini Publik"}
    ]
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    all_data = []
    try:
        for src in sources:
            comments = get_yt_comments(src['url'], driver)
            
            for c in comments:
                c['category'] = src['category']
                c['source_url'] = src['url']
                c['topic'] = "Kenaikan BBM"
            
            all_data.extend(comments)
        
        return jsonify(all_data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)