from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import re
import os
import random

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
    print(f"\n>>> SISTEM: Menerima request untuk Page {page}")
    
    scraped_history = load_history()
    TARGET_URL = "https://www.facebook.com/e100ss?locale=id_ID"
    
    # --- PENGATURAN WEBSOCKET (REMOTE DEBUGGING) ---
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print(f">>> EROR KONEKSI CHROME: Pastikan Chrome Debugging sudah dibuka di port 9222! \nDetail: {str(e)}")
        return jsonify({"status": "error", "message": "Gagal konek ke port 9222. Cek browser debugging-mu."})

    try:
        driver.get(TARGET_URL)
        print(f">>> SISTEM: Membuka Timeline e100 via WebSocket Terbuka...")
        time.sleep(5)  # Tunggu loading halaman awal stand by

        results = []
        current_session_links = set()
        current_session_ids = set()
        
        # --- RAHASIA ANTI-LEWAT: AMBIL BERTAHAP (HYBRID SCRAPE & SCROLL) ---
        # Kita lakukan putaran bertahap agar postingan paling atas langsung diamankan ke memori
        langkah_total = page * 6
        for putaran in range(langkah_total):
            print(f">>> SISTEM: Menyisir halaman pada putaran ke-{putaran + 1}...")
            
            # Ambil semua komponen kontainer artikel yang nampak saat ini
            articles = driver.find_elements(By.XPATH, "//div[@role='article'] | //div[@data-ad-comet-preview='message']/../../../../..")
            
            keywords = ["kebakaran", "#kebakaran", "Kebakaran" , "api", "damkar", "pmk", "hangus", "asap", "si jago merah", "kobaran", "pemadam", "meledak", "kecelakaan", "laka", "tabrakan", "truk terguling", "lalu lintas", "macet", "korban", "polisi", "kecelakaan mobil", "kecelakaan motor",
                        "ludes", "terbakar", "titik api", "#kecelakaan", "truk", "bus", "lalin", "truk bermasalah"]

            for art in articles:
                try:
                    full_text = art.get_attribute('innerText')
                    
                    # Saring postingan pinned/unggulan ("payung puitis" ter-skip otomatis)
                    if "Unggulan" in full_text or "Menjadi payung bagi banyak orang" in full_text:
                        continue
                    
                    content = clean_fb_text(full_text)
                    if len(content) < 45: 
                        continue

                    if any(key in content.lower() for key in keywords):
                        # 1. AMBIL LINK: Menggunakan metode tag_name 'a' murni (Bebas dari eror typo Mandarin)
                        link = "Link tidak ditemukan"
                        try:
                            elements_a = art.find_elements(By.TAG_NAME, "a")
                            for a in elements_a:
                                href = a.get_attribute('href')
                                if href and ('/posts/' in href or '/permalink/' in href or 'pfbid' in href):
                                    link = href.split('?')[0]
                                    break
                        except:
                            pass

                        # 2. Cek Duplikasi Terhadap File History & Sesi Berjalan
                        if link != "Link tidak ditemukan":
                            if link in scraped_history or link in current_session_links:
                                continue 

                        # 3. Ambil post_id (Gunakan fallback generator unik jika postingan terlalu baru)
                        post_id_raw = link.rstrip('/').split('/')[-1] if '/' in link and link != "Link tidak ditemukan" else f"id_{int(time.time())}_{random.randint(100,999)}"
                        
                        if post_id_raw in current_session_ids:
                            continue

                        # 4. AMBIL TANGGAL: Sasar langsung aria-label milik timestamp berita jam-jaman Facebook
                        date_text = "Baru saja"
                        try:
                            for a in elements_a:
                                href = a.get_attribute('href')
                                if href and ('/posts/' in href or '/permalink/' in href or 'pfbid' in href):
                                    aria_label = a.get_attribute('aria-label')
                                    if aria_label:
                                        date_text = aria_label
                                        break
                        except:
                            pass
                        
                        if "E100" in date_text:
                            date_text = date_text.replace("E100", "").strip()

                        # 5. Simpan Hasil Akhir ke Array jika Konten Unik
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
                                current_session_links.add(link)
                            current_session_ids.add(post_id_raw)
                except:
                    continue
            
            if len(results) >= 30:
                break
                
            # Setelah disapu bersih yang ada di layar, baru dorong scrollBy ke bawah secara bertahap
            driver.execute_script("window.scrollBy(0, 1500);")
            time.sleep(random.uniform(1.8, 2.8))
        
        print(f">>> SISTEM: Berhasil mengambil {len(results)} postingan berita baru.")
        return jsonify(results)

    except Exception as e:
        print(f">>> EROR SAAT SCRAPE: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})
        
    finally:
        # PENTING: Jangan di-quit biar tab WebSocket-mu tetep stand by melayani hit n8n berikutnya
        print(">>> SISTEM: Selesai memproses sesi scrape, browser debugging tetap stand by.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)