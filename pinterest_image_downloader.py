import json
import os
import requests
from tqdm import tqdm
import concurrent.futures
import re
import hashlib
import logging
import urllib.parse
from bs4 import BeautifulSoup


class PinterestDownloader:
    def __init__(self, base_folder='pinterest_downloads', max_workers=5):
        # Konfigurasi logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler('download_log.txt', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Pengaturan download
        self.base_folder = os.path.abspath(base_folder)
        self.max_workers = max_workers

        # Headers untuk request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Buat folder download
        os.makedirs(self.base_folder, exist_ok=True)

    def sanitize_filename(self, filename):
        """Membersihkan nama file dari karakter yang tidak valid"""
        return re.sub(r'[<>:"/\\|?*]', '_', str(filename))[:255]

    def create_unique_folder(self, base_name):
        """Buat folder unik"""
        sanitized_name = self.sanitize_filename(base_name)
        folder_path = os.path.join(self.base_folder, sanitized_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def extract_image_urls(self, url):
        """Ekstrak URL gambar dari halaman"""
        try:
            # Pola URL untuk pencarian
            url_patterns = [
                r'https?://[^\s<>"]*?pinimg\.com[^\s<>"]*',
                r'https?://[^\s<>"]+?\.(?:jpg|jpeg|png|gif|webp)',
            ]

            # Tangani URL pin spesifik
            if '/pin/' in url:
                try:
                    # Gunakan API atau metode scraping khusus Pinterest
                    response = requests.get(url, headers=self.headers)

                    # Coba ekstrak URL gambar dari meta tags atau JSON
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Cari meta tag og:image
                    og_image = soup.find('meta', property='og:image')
                    if og_image and og_image.get('content'):
                        return [og_image['content']]

                    # Cari script yang mengandung data JSON
                    scripts = soup.find_all('script', type='application/ld+json')
                    for script in scripts:
                        try:
                            json_data = json.loads(script.string)
                            if 'image' in json_data:
                                image_url = json_data['image']
                                if isinstance(image_url, str):
                                    return [image_url]
                                elif isinstance(image_url, list):
                                    return image_url
                        except json.JSONDecodeError:
                            continue

                    # Ekstraksi langsung dari tag img
                    img_tags = soup.find_all('img')
                    image_urls = []
                    for img in img_tags:
                        src = img.get('src') or img.get('data-src')
                        if src and any(re.search(pattern, src, re.IGNORECASE) for pattern in url_patterns):
                            image_urls.append(src)

                    return image_urls

                except Exception as pin_error:
                    self.logger.error(f"Gagal ekstrak URL pin: {pin_error}")
                    return []

            # Metode ekstraksi umum untuk halaman lain
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Ekstrak URL dari berbagai sumber
            image_urls = []
            for img in soup.find_all('img'):
                potential_urls = [
                    img.get('src', ''),
                    img.get('data-src', ''),
                    img.get('srcset', '').split()[0]
                ]

                for potential_url in potential_urls:
                    if potential_url:
                        # Lengkapi URL relatif
                        if not potential_url.startswith(('http://', 'https://')):
                            potential_url = urllib.parse.urljoin(url, potential_url)

                        # Validasi URL
                        if any(re.search(pattern, potential_url, re.IGNORECASE) for pattern in url_patterns):
                            image_urls.append(potential_url)

            return list(set(image_urls))

        except Exception as e:
            self.logger.error(f"Gagal ekstrak URL dari {url}: {e}")
            return []

    def download_image(self, image_url, source_url):
        """Download gambar dengan manajemen error"""
        try:
            # Buat folder untuk sumber URL
            download_folder = self.create_unique_folder(
                self.sanitize_filename(urllib.parse.urlparse(source_url).netloc)
            )

            # Generate nama file unik
            file_ext = os.path.splitext(image_url)[1].lower() or '.jpg'
            filename = hashlib.md5(image_url.encode()).hexdigest() + file_ext
            filepath = os.path.join(download_folder, filename)

            # Download gambar
            response = requests.get(image_url, headers=self.headers, stream=True)
            if response.status_code != 200:
                self.logger.warning(f"Gagal download: {image_url}")
                return False

            # Simpan gambar
            total_size = int(response.headers.get('content-length', 0))
            with open(filepath, 'wb') as file, tqdm(
                    total=total_size,
                    unit='iB',
                    unit_scale=True,
                    desc=filename,
                    ncols=100,
                    disable=total_size == 0  # Nonaktifkan progress bar jika ukuran tidak diketahui
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=1024):
                    size = file.write(chunk)
                    progress_bar.update(size)

            self.logger.info(f"Berhasil download: {filename}")
            return True

        except Exception as e:
            self.logger.error(f"Gagal download {image_url}: {e}")
            return False

    def process_urls(self, input_urls):
        """Proses download dari daftar URL"""
        # Ekstrak semua URL gambar
        all_image_urls = []
        for url in input_urls:
            image_urls = self.extract_image_urls(url)
            all_image_urls.extend(image_urls)

        self.logger.info(f"Total gambar yang ditemukan: {len(all_image_urls)}")

        # Download dengan concurrent
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.download_image, image_url, url)
                for image_url in set(all_image_urls)
                for url in input_urls
            ]
            concurrent.futures.wait(futures)


def read_urls_from_file(file_path):
    """Membaca URL dari file txt"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Baca setiap baris, hapus whitespace, dan filter URL yang valid
            urls = [
                url.strip() for url in f.readlines()
                if url.strip() and url.strip().startswith(('http://', 'https://'))
            ]
        return urls
    except FileNotFoundError:
        print(f"Error: File {file_path} tidak ditemukan!")
        return []
    except Exception as e:
        print(f"Error membaca file: {e}")
        return []


def main():
    print("===== Pinterest Bulk Image Downloader =====")

    # Input file URL
    while True:
        file_path = input("Masukkan path file txt berisi URL Pinterest (kosongkan untuk keluar): ").strip()

        # Cek apakah input kosong
        if not file_path:
            print("Tidak ada file yang dipilih. Keluar...")
            return

        # Validasi file
        if not os.path.exists(file_path):
            print(f"File {file_path} tidak ditemukan. Coba lagi.")
            continue

        # Baca URL dari file
        urls = read_urls_from_file(file_path)

        # Cek apakah ada URL valid
        if not urls:
            print("Tidak ada URL valid dalam file. Coba lagi.")
            continue

        # Pilihan folder download
        folder = input("Masukkan nama folder download (default: pinterest_downloads): ").strip()
        folder = folder if folder else 'pinterest_downloads'

        # Pilihan jumlah worker
        while True:
            try:
                workers = input("Masukkan jumlah worker (default: 5): ").strip()
                workers = int(workers) if workers else 5
                break
            except ValueError:
                print("Input tidak valid. Harap masukkan angka.")

        # Inisialisasi dan jalankan downloader
        downloader = PinterestDownloader(
            base_folder=folder,
            max_workers=workers
        )
        downloader.process_urls(urls)
        print("Download selesai!")
        break


if __name__ == "__main__":
    main()