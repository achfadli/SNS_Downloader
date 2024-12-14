import yt_dlp
import os

def download_video(url, download_folder):
    ydl_opts = {
        'format': 'best',  # Mengunduh format terbaik
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),  # Menyimpan dengan nama file yang sesuai di folder yang ditentukan
        'noplaylist': True,  # Menghindari mengunduh seluruh playlist
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading: {url}")
            ydl.download([url])
            print("Download completed!")
    except Exception as e:
        print(f"An error occurred while downloading {url}: {e}")

def main():
    file_name = input("Masukkan nama file yang berisi URL video (misalnya: video_urls.txt): ")

    if not os.path.exists(file_name):
        print(f"File '{file_name}' tidak ditemukan!")
        return

    download_folder = input("Masukkan folder untuk menyimpan video (misalnya: ./downloads): ")

    # Membuat folder jika belum ada
    os.makedirs(download_folder, exist_ok=True)

    with open(file_name, 'r') as file:
        urls = file.readlines()

    for url in urls:
        url = url.strip()  # Menghapus whitespace
        if url:
            download_video(url, download_folder)

if __name__ == "__main__":
    main()