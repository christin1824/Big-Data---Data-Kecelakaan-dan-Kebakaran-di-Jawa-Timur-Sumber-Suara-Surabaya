from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import re
import os

app = Flask(__name__)

# Nama file untuk menyimpan history link agar tidak duplikat
HISTORY_FILE = "scraped_links.txt"

def load_history():
    """Membaca list link yang sudah pernah di-scrape sebelumnya"""
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_to_history(link):
    """Menyimpan link baru ke file history"""
    with open(HISTORY_FILE, "a") as f:
        f.write(link + "\n")

def clean_fb_text(raw_text):
    text = re.sub(r'[\n\t\r]', ' ', raw_text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\d+,\d+\s*(rb|jt)?\s*(Suka|Komentar|Bagikan).*$', '', text, flags=re.IGNORECASE)
    return text.strip()

@app.route('/scrape', methods=['GET'])
def scrape_for_llm():
    page = request.args.get('page', default=1, type=int)
    print(f">>> SISTEM: Menerima request untuk Page {page}")
    
    scraped_history = load_history()

    LOGIN_URL = "https://www.facebook.com/"
    TARGET_URL = "https://www.facebook.com/e100ss?locale=id_ID"
    
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(LOGIN_URL)
        print(">>> SISTEM: Login dulu (60 detik)...")
        time.sleep(60) 

        driver.get(TARGET_URL)
        print(f">>> SISTEM: Membuka Timeline e100 (Page {page})...")
        time.sleep(10) 

        # Scroll bertahap
        scroll_times = page * 10 
        for i in range(scroll_times):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        articles = driver.find_elements(By.XPATH, "//div[@role='article'] | //div[@data-ad-comet-preview='message']/../../../../..")
        results = []
        
        keywords = ["kebakaran", "#kebakaran",  "Kebakaran" , "api", "damkar", "pmk", "hangus", "asap", "si jago merah", "kobaran", "pemadam", "meledak", "kecelakaan", "laka", "tabrakan", "truk terguling", "lalu lintas", "macet", "korban", "polisi", "kecelakaan mobil", "kecelakaan motor",
                    "kobaran", "pemadam", "meledak", "ludes", "terbakar", "titik api","kecelakaan", "#kecelakaan", "laka", "tabrakan", "truk", "bus", "korban", "lalin", "truk bermasalah"]
        
        print(f">>> SISTEM: Memproses {len(articles)} elemen...")

        for art in articles:
            try:
                # Menggunakan innerText agar teks yang tersembunyi bisa ikut terbaca
                full_text = art.get_attribute('innerText')
                content = clean_fb_text(full_text)
                
                if len(content) < 45: 
                    continue

                if any(key in content.lower() for key in keywords):
                    # 1. Ekstrak Link
                    try:
                        link_element = art.find_element(By.XPATH, ".//a[contains(@href, '/posts/') or contains(@href, '/permalink/') or contains(@href, 'pfbid')]")
                        link = link_element.get_attribute('href').split('?')[0]
                    except:
                        link = "Link tidak ditemukan"

                    # 2. CEK DUPLIKASI
                    if link != "Link tidak ditemukan" and link in scraped_history:
                        continue 

                    # --- TAMBAHAN: Ekstrak post_id dari Link ---
                    post_id_raw = link.rstrip('/').split('/')[-1] if '/' in link else "no_id"

                    # --- PERBAIKAN LOGIKA TANGGAL ---
                    try:
                        # Mencari elemen link yang biasanya punya aria-label berisi tanggal lengkap
                        # Facebook biasanya naruh di elemen <a> yang ada link postingannya
                        date_element = art.find_element(By.XPATH, ".//a[@aria-label][contains(@href, 'posts')] | .//span[@aria-labelledby]")
                        date_text = date_element.get_attribute('aria-label')
                        
                        if not date_text:
                            # Kalau aria-label zonk, ambil teks dari elemen yang ada 'jam' atau 'menit'
                            date_text = driver.execute_script("return arguments[0].innerText;", date_element)

                        # Kalau masih dapet "E100" atau sampah, bersihkan
                        if "E100" in date_text:
                            date_text = date_text.replace("E100", "").strip()
                    except:
                        date_text = "Baru saja"

                    # 3. Simpan ke results
                    if not any(r['content'] == content for r in results):
                        results.append({
                            "post_id": post_id_raw,
                            "title": content[:120].strip() + "...",
                            "content": content,
                            "link": link,
                            "date": date_text
                        })
                        if link != "Link tidak ditemukan":
                            save_to_history(link)
                            scraped_history.add(link)
            except:
                continue
            
            if len(results) >= 30: 
                break
        
        print(f">>> SISTEM: Berhasil ambil {len(results)} postingan baru (unik).")
        return jsonify(results)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
        
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)