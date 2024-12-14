import os
import re
import sys
import requests
import validators
from tqdm import tqdm
import yt_dlp

# Coba impor, jika gagal, install otomatis
try:
    import requests
    import validators
    from tqdm import tqdm
    import yt_dlp
except ImportError:
    import subprocess

    subprocess.check_call([sys.executable, '-m', 'pip', 'install',
                           'requests', 'validators', 'tqdm', 'yt-dlp'])
    import requests
    import validators
    from tqdm import tqdm
    import yt_dlp


class FacebookDownloader:
    def __init__(self, download_path=None):
        """
        Inisialisasi downloader dengan path default
        """
        self.download_path = download_path or os.path.join(os.getcwd(), "downloads")
        os.makedirs(self.download_path, exist_ok=True)

    def validate_facebook_url(self, url):
        """
        Validasi URL Facebook
        """
        facebook_pattern = r'^(https?://)?(www\.)?facebook\.com/.*'
        return (
                re.match(facebook_pattern, url) is not None and
                validators.url(url)
        )

    def download_media(self, url):
        """
        Download media dari URL Facebook
        """
        try:
            ydl_opts = {
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'format': 'best',
                'no_warnings': True,
                'ignoreerrors': False,
                'no_color': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return True
        except Exception as e:
            print(f"❌ Error download {url}: {e}")
            return False

    def batch_download(self, urls):
        """
        Download batch URL
        """
        successful = []
        failed = []

        print("\n🚀 Memulai Download...")
        for url in tqdm(urls, desc="Downloading"):
            result = self.download_media(url)
            if result:
                successful.append(url)
            else:
                failed.append(url)

        return successful, failed


def read_urls_from_file(file_path):
    """
    Membaca URL dari file teks
    """
    try:
        with open(file_path, 'r') as file:
            # Baca dan bersihkan URL
            urls = [
                url.strip()
                for url in file.readlines()
                if url.strip() and not url.startswith('#')
            ]
        return urls
    except FileNotFoundError:
        print(f"❌ File {file_path} tidak ditemukan.")
        return []
    except Exception as e:
        print(f"❌ Error membaca file: {e}")
        return []


def main():
    """
    Fungsi utama untuk menjalankan downloader
    """
    print("🔥 Facebook Media Downloader dari File 🔥")

    while True:
        # Input path file
        file_path = input("\n📁 Masukkan path file URL (txt): ").strip()

        # Baca URL dari file
        urls = read_urls_from_file(file_path)

        if not urls:
            print("❌ Tidak ada URL yang valid di file.")
            lanjut = input("Coba lagi? (y/n): ").lower()
            if lanjut != 'y':
                break
            continue

        # Validasi URL
        downloader = FacebookDownloader()
        valid_urls = [url for url in urls if downloader.validate_facebook_url(url)]

        if not valid_urls:
            print("❌ Tidak ada URL Facebook valid.")
            continue

        # Download langsung ke folder default
        try:
            successful, failed = downloader.batch_download(valid_urls)

            # Laporan download
            print("\n📊 Laporan Download:")
            print(f"📥 Total URL di file: {len(urls)}")
            print(f"✅ URL Valid: {len(valid_urls)}")
            print(f"✅ Berhasil: {len(successful)}")
            print(f"❌ Gagal: {len(failed)}")
            print(f"📂 Lokasi Download: {downloader.download_path}")

            # Opsi lanjut
            lanjut = input("\nIngin download lagi? (y/n): ").lower()
            if lanjut != 'y':
                break

        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
            break


def create_sample_url_file():
    """
    Membuat file contoh URL
    """
    sample_urls = [
        "# Contoh file URL Facebook",
        "https://www.facebook.com/username/videos/123456",
        "https://www.facebook.com/watch?v=789012",
        "# URL tidak valid akan diabaikan",
        "https://invalid-url.com"
    ]

    with open('facebook_urls.txt', 'w') as f:
        f.write('\n'.join(sample_urls))

    print("✅ File contoh 'facebook_urls.txt' telah dibuat.")


if __name__ == "__main__":
    # Opsional: Buat file contoh jika belum ada
    if not os.path.exists('facebook_urls.txt'):
        create_sample_url_file()

    main()