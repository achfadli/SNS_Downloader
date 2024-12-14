'''
Pinterest video downloader
Made by Harshit
'''
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import re
from datetime import datetime

def clear_console():
    # Clear the console screen based on the operating system
    os.system('cls' if os.name == 'nt' else 'clear')

clear_console()

# Download function
def download_file(url, folder_path, filename):
    response = requests.get(url, stream=True)

    file_size = int(response.headers.get('Content-Length', 0))
    progress = tqdm(response.iter_content(1024), f'Downloading {filename}', total=file_size, unit='B', unit_scale=True, unit_divisor=1024)

    # Create the full path for saving the file
    full_path = os.path.join(folder_path, filename)

    with open(full_path, 'wb') as f:
        for data in progress.iterable:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))

def fetch_video_url(page_url):
    if("https://pin.it/" in page_url):  # pin url short check
        print("Extracting original pin link")
        t_body = requests.get(page_url)
        if(t_body.status_code != 200):
            print(f"Entered URL '{page_url}' is invalid or not working.")
            return None
        soup = BeautifulSoup(t_body.content, "html.parser")
        href_link = (soup.find("link", rel="alternate"))['href']
        match = re.search('url=(.*?)&', href_link)
        page_url = match.group(1)  # update page url

    print(f"Fetching content from given URL: {page_url}")
    body = requests.get(page_url)  # GET response from url
    if(body.status_code != 200):  # checks status code
        print(f"Entered URL '{page_url}' is invalid or not working.")
        return None
    else:
        soup = BeautifulSoup(body.content, "html.parser")  # parsing the content
        print("Fetched content successfully.")
        # Extracting the URL
        try:
            extract_url = (soup.find("video", class_="hwa kVc MIw L4E"))['src']
            # converting m3u8 to V_720P's url
            convert_url = extract_url.replace("hls", "720p").replace("m3u8", "mp4")
            return convert_url
        except TypeError:
            print(f"No video found for URL '{page_url}'.")
            return None

def main():
    # Read URLs from a text file
    filename = input("Enter the path to the text file containing URLs: ")

    try:
        with open(filename, 'r') as file:
            urls = file.readlines()
    except FileNotFoundError:
        print("File not found. Please check the path and try again.")
        return

    # Prompt for the folder path to save videos
    folder_path = input("Enter the folder path to save downloaded videos: ")

    # Check if the folder exists, if not create it
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

    for page_url in urls:
        page_url = page_url.strip()  # Remove any leading/trailing whitespace
        if ("pinterest.com/pin/" not in page_url and "https://pin.it/" not in page_url):
            print(f"Entered URL '{page_url}' is invalid.")
            continue

        video_url = fetch_video_url(page_url)
        if video_url:
            filename = datetime.now().strftime("%d_%m_%H_%M_%S_") + ".mp4"
            print("Downloading file now!")
            download_file(video_url, folder_path, filename)

if __name__ == "__main__":
    main()