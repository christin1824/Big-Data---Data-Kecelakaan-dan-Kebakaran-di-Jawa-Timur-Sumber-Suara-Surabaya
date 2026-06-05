# Laporan Project Akhir Big Data: Analisis Sentimen dan Emosi Publik Terhadap Kenaikan Harga BBM pada Platform YouTube

## Pendahuluan

Project ini adalah sistem **Pipeline Big Data dan Analisis Sentimen & Emosi** yang dirancang untuk mengukur, menganalisis, dan memvisualisasikan respons serta opini publik terhadap isu kebijakan energi, khususnya terkait fluktuasi dan kenaikan harga Bahan Bakar Minyak (BBM) di Indonesia. Data opini diambil secara otomatis dari kolom komentar video terkait di platform **YouTube**.

Kebijakan harga BBM selalu memicu reaksi sensitif karena berdampak langsung pada biaya transportasi, daya beli, serta keberlangsungan usaha masyarakat. Sistem ini mengintegrasikan proses penarikan data (*data ingestion*) menggunakan Python, penyimpanan database dokumen NoSQL **MongoDB**, serta penyajian analitik interaktif melalui **Metabase**. Melalui dashboard ini, polarisasi opini publik serta spektrum emosi masyarakat dapat dipetakan secara real-time untuk kebutuhan analisis persepsi masyarakat secara mendalam.

---
## Tampilan Dashboard & Hasil Analisis

[Klik di Sini untuk Melihat Dashboard Live](https://prize-improvements-penguin-firefox.trycloudflare.com/public/dashboard/2d238ed4-babd-493f-95db-288aade7ccab) (Link belom bisa diklik karena berubah-ubah karena menggunakan domain gratis)

### Ringkasan Executive Hasil Analisis Data (N = 489 Komentar):
1. **Polarisasi Sentimen Tinggi**: Opini didominasi oleh kelompok **Menolak (54.19%)**, diikuti oleh kelompok **Mendukung (38.04%)**, dan sisanya **Netral (7.77%)**.
2. **Dominasi Emosi Negatif**: Ekspresi emosi **Marah** menempati posisi puncak sebagai penggerak utama percakapan, disusul oleh emosi **Senang** (respon terhadap stabilitas harga/penundaan kenaikan) dan **Khawatir** terkait risiko inflasi sembako di masa depan.

---

---
## PPT Presentasi 
[Klik di Sini untuk Melihat PPT](https://canva.link/24y6uuwyeux3rt5)

---

## Fitur Utama & Visualisasi Dashboard Metabase

### 1. Analisis Sentimen Komentar (Pie Chart / Donut Chart)
Menampilkan metrik persentase dari total **489 sampel data** opini publik:
* **Menolak (54.19% - Dominan)**: Didorong oleh keluhan beban ekonomi akibat potensi kenaikan harga kebutuhan pokok, penurunan daya beli masyarakat menengah ke bawah, kritik ketidakpercayaan terhadap akurasi penyaluran subsidi/bansos, serta efek domino inflasi pada sektor jasa/logistik.
* **Mendukung (38.04%)**: Didorong oleh narasi pentingnya menjaga stabilitas APBN dari beban subsidi yang membengkak, efisiensi energi (mendorong hemat BBM/transportasi umum), serta optimisme kesehatan ekonomi jangka panjang.
* **Netral (7.77%)**: Porsi kecil, menandakan isu ini sangat memicu polarisasi sehingga penonton cenderung langsung mengambil sikap pro atau kontra.

### 2. Analisis Spektrum Emosi (Horizontal Bar Chart)
Mengelompokkan data komentar ke dalam 6 kategori emosi utama untuk melihat psikologis publik:
* **Marah (Dominan > 200 komentar)**: Dipicu kritik ketidakadilan kebijakan (rakyat kecil vs pejabat), sindiran/sarkasme, dugaan korupsi anggaran, dan distrust kepada pemerintah.
* **Senang (~160 komentar)**: Muncul sebagai bentuk apresiasi kinerja pemerintah/menteri saat harga BBM terjaga stabil atau tidak jadi naik, melahirkan rasa lega dan optimisme ekonomi nasional.
* **Khawatir (~70 komentar)**: Berakar dari *uncertainty* tinggi, ketakutan kelangkaan BBM di daerah, serta efek domino kenaikan harga sembako.
* **Takut (~20 komentar)**: Berupa kecemasan ekstrem dan munculnya prediksi krisis ekonomi jangka panjang (trauma komparatif krisis 1998).
* **Sedih (< 20 komentar)**: Bentuk empati mendalam terhadap kemiskinan dan beban sosial yang dipikul rakyat kecil.

### 3. Top Influence Comment Authors (Data Table)
Menampilkan daftar 10 akun penonton YouTube paling berpengaruh berdasarkan volume kontribusi dan rasio engagement tertinggi (*Maximum Likes*) untuk mengidentifikasi *key opinion leaders* di kolom komentar.
* *Top 3 Influencers*: `@watchlisten5276` (112 Likes), `@bambangsudjatmiko9131` (95 Likes), dan `@zonatutrial` (92 Likes).

---

## Teknologi dan Dependencies

| Kategori | Teknologi | Fungsi / Peran dalam Proyek |
| :--- | :--- | :--- |
| **Automation & Scraper**| **Python, Selenium, Flask** | Mengontrol browser virtual untuk *scraping* data komentar YouTube yang bersifat dinamis (AJAX/Rendered). |
| **Database NoSQL** | **MongoDB** | Database NoSQL utama untuk menampung dokumen teks besar dan metadata komentar. |
| **Visualization Tool** | **Metabase** | BI platform untuk memproses agregasi query native MongoDB dan menyusun GUI dashboard. |
| **Environment Control** | **Docker Compose** | Orkestrasi container terisolasi untuk MongoDB, Postgres, n8n, dan Metabase dalam satu network. |

---

## Alur Kerja Scraper (`scraper_minyak.py`)

Proyek ini menerapkan automated data pipeline dinamis menggunakan Selenium WebDriver yang dibungkus ke dalam microservice Flask API (`/scrape-yt`).

### 1. Mekanisme Ekstraksi Komentar (YouTube Scraper)
Melalui endpoint `/scrape-yt`, script `scraper_minyak.py` bekerja mengekstraksi data secara paralel dari beberapa target video (kategori *Berita Nasional* dan *Opini Publik*):
* **Headless Browser Execution**: Driver berjalan dalam mode `--headless` dan `--no-sandbox` agar proses ekstraksi berjalan cepat di background tanpa membuka pop-up browser visual.
* **Dynamic Scrolling Mechanism**: Browser virtual memicu pemuatan (*lazy loading*) komentar YouTube dengan mengirimkan perintah `Keys.PAGE_DOWN` terlebih dahulu, disusul dengan perulangan eksekusi script JavaScript `window.scrollTo(0, document.documentElement.scrollHeight)` untuk menjamin komentar di layer bawah ikut ter-render.
* **DOM Element Parsing**: Sistem menyisir elemen penonton dengan menangkap selector spesifik:
  * `@author-text` -> Mengambil username/handle author (jika kosong diset `Anonymous`).
  * `@content-text` -> Mengambil narasi teks komentar mentah (hanya mengambil teks yang panjangnya > 5 karakter).
  * `@vote-count-middle` -> Mengambil jumlah akumulasi *likes* dari komentar tersebut sebagai indikator metrik engagement.

### 2. Output Data Payload (JSON API)
Data yang berhasil dikoleksi langsung distrukturkan ke dalam format array of object JSON, lengkap dengan pelabelan topik (`Kenaikan BBM`), kategori video, dan sumber URL-nya, sebelum akhirnya disinkronisasikan ke dalam cluster database MongoDB.

---

## Struktur Direktori Project

```text
Big-Data-Sentiment-BBM
├── scraper_minyak.py       # Script utama scraping komentar YouTube (Selenium + Flask)
├── docker-compose.yml      # Konfigurasi container environment (MongoDB, Metabase, n8n)
├── cookies.txt             # File kuki "cookies" untuk session (diabaikan oleh git)
├── geckodriver.log         # File log driver selenium (diabaikan oleh git)
└── .gitignore              # Konfigurasi pembatasan upload file sampah/sensitif
```
---

## Cara Instalasi dan Eksekusi

### 1. Prasyarat
* Docker & Docker Desktop terinstal aktif.
* Python 3.x terpasang di sistem lokal.

### 2. Jalankan Stack Environment (Docker)
Nyalakan seluruh service database dan dashboard menggunakan perintah Docker Compose di terminal folder project:
```bash
docker compose up -d
```
### 3. Eksekusi Scraper YouTube
Instal dependencies python yang diperlukan, kemudian jalankan script scraper untuk mulai mengoleksi data komentar ke MongoDB:  

```bash
pip install flask selenium webdriver-manager
python scraper_minyak.py
```

### 4. Eksekusi Scraper & Otomasi Pipeline n8n

Sistem ini menggunakan pengumpulan data otomatis terpusat (*Centralized Ingestion Workflow*) di mana **n8n bertindak sebagai orchestrator utama** yang mengendalikan script Python dan LLM.

#### Alur Kerja Pipeline n8n:
1. **Schedule Trigger**: Menjalankan workflow berdasarkan jadwal atau dipicu secara manual via GUI n8n.
2. **HTTP Request**: Mengirimkan request `GET` ke `http://host.docker.internal:5000/scrape-yt` untuk memicu `scraper_minyak.py` berjalan secara *headless*, menarik data komentar YouTube, dan mengembalikan data dalam bentuk array JSON.
3. **Loop Over Items**: Melakukan iterasi data dengan `Batch Size: 1` untuk memproses komentar satu per satu secara bergantian.
4. **AI Agent (Groq Chat Model)**: Mengirimkan teks komentar ke Groq LLM dengan prompt analisis sentimen, emosi, topik utama, kategori, ringkasan kalimat, prediksi aksi, serta skor intensitas, lengkap dengan aturan sinkronisasi logika yang ketat.
5. **Edit Fields**: Menggunakan mode JSON untuk merapikan skema payload, menyatukan data asli YouTube (`author`, `likes`, `comment`, `category_source`) dengan properti hasil ekstraksi dari output AI Agent.
6. **Insert Documents (MongoDB)**: Menyimpan dokumen objek yang telah diformat ke dalam koleksi `sentimen_db` di MongoDB.
7. **Wait**: Memberikan jeda waktu (*delay*) selama 5,00 detik di setiap akhir perulangan sebelum mengambil item berikutnya guna menghindari batasan *rate limiting* (TPM/RPM) pada API Groq.

#### Cara Menjalankan Sistem:
1. Pastikan seluruh container Docker (`mongodb`, `metabase`, `n8n`) sudah aktif berjalan di background.
2. Jalankan server Flask lokal untuk script scraper kamu di terminal VS Code:
   ```bash
   pip install flask selenium webdriver-manager
   python scraper_minyak.py
   ```
3. Buka editor workflow n8n kamu, lalu klik tombol Execute workflow di bagian bawah layar untuk mulai menjalankan seluruh pipeline otomatisasi dari penarikan data hingga pengisian database.

### 5. Analisis dan Visualisasi di Metabase
* Akses `http://localhost:3000`, lalu hubungkan ke database MongoDB utama Anda, ini punya saya: (`AGUSTINANATANIA@GMAIL.COM`).  
* Pilih collection `sentimen_db` untuk melihat data hasil pipeline komentar YouTube BBM.
* Gunakan query editor untuk menyusun chart sentimen (Pie Chart) dan grafik emosi (Horizontal Bar Chart) sesuai rancangan laporan.

#### Tampilan Hasil Dashboard Real-Time:

##### 1. Ringkasan Dashboard Utama
![Dashboard Metabase Utama](01.jpg)

##### 2. Distribusi Sentimen dan Spektrum Emosi Publik
![Analisis Grafik Sentimen](02.jpg)

##### 3. Top Influence Comment Authors & Engagement
![Daftar Top Influencers](03.jpg)

### 6. Langkah Konfigurasi & Cara Mendapatkan Tautan Publik Untuk Dashboard:
1. Buka dashboard utama Anda di Metabase lokal (`http://localhost:3000`).
2. Klik ikon **Sharing** (ikon berbentuk gambar gembok atau panah) di pojok kanan bawah panel dashboard untuk mengaktifkan fitur tautan publik bawaan Metabase.
3. Tambahkan konfigurasi service tunnel baru khusus untuk Metabase di dalam file `docker-compose.yml` Anda:
   ```yaml
   metabase-tunnel:
     image: cloudflare/cloudflared:latest
     container_name: metabase-cloudflare-tunnel
     restart: always
     command: tunnel --url http://metabase:3000
     depends_on:
       - metabase
   ```
4. Terapkan perubahan container dengan menjalankan perintah berikut secara berurutan di terminal folder project:
    ```Bash
    docker compose down
    docker compose up -d
     ```
5. Ambil domain publik acak yang digenerate otomatis oleh Cloudflare dengan memeriksa log kontainer tunnel:
    ```Bash
    docker logs metabase-cloudflare-tunnel
     ```
6. Cari baris URL .trycloudflare.com di dalam log tersebut, lalu gabungkan domain tersebut dengan path UUID dashboard publik Anda (/public/dashboard/2d238ed4-babd-493f-95db-288aade7ccab).
7. Tautan Akses Live (Cloudflare Tunnel):
Hasil penggabungan di atas menghasilkan tautan publik live berikut yang siap diakses secara online dari mana saja secara real-time:  

[https://prize-improvements-penguin-firefox.trycloudflare.com/public/dashboard/2d238ed4-babd-493f-95db-288aade7ccab](https://prize-improvements-penguin-firefox.trycloudflare.com/public/dashboard/2d238ed4-babd-493f-95db-288aade7ccab) (Link belom bisa diklik karena berubah-ubah karena menggunakan domain gratis)


## Limitasi Proyek

* **Klasifikasi Emosi Masih Konvensional**: Pemetaan emosi saat ini baru menggunakan metode *string matching* kasar (mencocokkan kata kunci teks mentah). Belum memakai model *Machine Learning* atau NLP untuk mendeteksi konteks kalimat secara mendalam.
* **Format Tanggal Belum Standar**: Data waktu komentar dari YouTube masih tersimpan sebagai teks (*string*) apa adanya dari web. Efeknya, fungsionalitas filter rentang waktu (*date range filter*) bawaan di Metabase belum bisa bekerja maksimal.
* **Ketergantungan pada Struktur DOM YouTube**: Script scraper sangat bergantung pada ID elemen HTML YouTube (`#author-text`, `#content-text`). Jika YouTube melakukan update struktur web, ada risiko selector scraper harus disesuaikan ulang agar tidak zonk.
* **Metrik Engagement Terbatas**: Analisis baru berfokus pada volume sentimen, emosi, dan jumlah *likes* komentar, belum mengintegrasikan metrik performa video secara makro (seperti rasio *views*, *subscribers*, atau sentimen antar-channel).
* **Link claudflare masih berubah-ubah karena gratis** : Link belom bisa diklik karena berubah-ubah karena menggunakan domain gratis

## Kesimpulan

Proyek analisis sentimen ini berhasil membangun pipeline Big Data yang mengintegrasikan Selenium Headless (Python) untuk *data ingestion*, MongoDB sebagai penyimpanan database NoSQL, n8n sebagai *orchestrator automated workflow*, hingga visualisasi interaktif lewat Metabase. Meskipun klasifikasi teksnya masih berbasis pencocokan kata kunci sederhana, sistem ini sukses memetakan polarisasi opini (54.19% Menolak vs 38.04% Mendukung) serta dominasi emosi marah dari 489 data komentar BBM secara real-time. Proyek ini dapat menjadi fondasi awal yang solid untuk dikembangkan ke arah analisis berbasis NLP yang lebih kompleks seperti IndoBERT fine-tuned.
