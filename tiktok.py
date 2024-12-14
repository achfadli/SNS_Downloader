import os
import yt_dlp


# Fungsi untuk mengunduh video dan foto dari URL yang dibaca dari file teks
def download_from_txt(file_path, output_folder):
    # Membuat folder output jika belum ada
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Membaca URL dari file teks
    with open(file_path, 'r') as file:
        urls = file.readlines()

    # Opsi untuk yt-dlp
    ydl_opts = {
        'format': 'best',  # Mengunduh dalam kualitas terbaik
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),  # Template nama file
    }

    # Mengunduh setiap URL
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            url = url.strip()  # Menghapus spasi dan newline
            if url:  # Pastikan URL tidak kosong
                print(f'Mengunduh: {url}')
                try:
                    ydl.download([url])
                except Exception as e:
                    print(f'Gagal mengunduh {url}: {e}')


# Panggil fungsi dengan input dari pengguna
if __name__ == "__main__":
    # Input path file teks
    file_path = input("Masukkan path file teks (misal: links.txt): ")

    # Input path folder untuk menyimpan file
    output_folder = input("Masukkan path folder untuk menyimpan file (misal: ./downloads): ")

    # Mengunduh video dari URL yang ada di file teks
    download_from_txt(file_path, output_folder)