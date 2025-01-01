from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import urlparse, parse_qs
import os
import requests
import time
import os
from PyPDF2 import PdfMerger

def merge_pdfs(folder_path):
    merger = PdfMerger()
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

    # Sort the PDF files based on the first four digits
    def extract_number(filename):
        parts = filename.split('-')
        return int(parts[1].split()[0]) if len(parts) > 1 and parts[1].split()[0].isdigit() else float('inf')
    
    pdf_files.sort(key=extract_number)

    for pdf in pdf_files:
        merger.append(os.path.join(folder_path, pdf))

    # Save the merged PDF to a file
    output_path = os.path.join(folder_path, 'merged_output.pdf')
    merger.write(output_path)
    merger.close()

    print(f"Merged PDF saved as: {output_path}")


def download_pdf_from_drive_link(drive_link, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Set up Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        driver.get(drive_link)

        # Wait for the page to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Download"]'))
        )

        # Simulate pressing the tab key twice with a 2-second gap
        action = ActionChains(driver)
        action.send_keys('\ue004').perform()  # Press Tab key
        time.sleep(2)
        action.send_keys('\ue004').perform()  # Press Tab key again
        time.sleep(2)

        # Click the download button
        download_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Download"]'))
        )
        download_button.click()
        time.sleep(2)
        # Add an explicit wait to ensure the download starts
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "will start") or contains(text(), "Downloading")]'))
        )
        print(f"Initiated download for: {drive_link}")
        
    except Exception as e:
        print(f"Exception: {e}")
        print(f"Failed to download: {drive_link}")
    
    driver.quit()

def download_pdfs_from_drive_links(drive_links, download_folder):
    arr = []
    for link in drive_links:
        arr.append(link)
        download_pdf_from_drive_link(link, download_folder)
        # Print done and array size
        print(f"done for link {link}, arr.size: {len(arr)}")





def extract_google_drive_link(redirect_url):
    try:
        # Parse the redirect URL
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        
        # Extract the Google Drive link from the query parameters
        google_drive_link = query_params.get('q', ['No Google Drive link available'])[0]
        return google_drive_link
    except Exception as e:
        print(f"Exception: {e}")
        return 'No Google Drive link available'

def get_playlist_videos(playlist_url):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(playlist_url)
    
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'a#video-title'))
    )
    
    video_elements = driver.find_elements(By.CSS_SELECTOR, 'a#video-title')
    
    video_urls = []
    for video in video_elements:
        video_url = video.get_attribute('href')
        video_urls.append(video_url)
    
    driver.quit()
    return video_urls

def get_video_description(video_url, download_folder):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(video_url)
    try:
        # Wait for the "More" button to be clickable and click it
        more_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'expand'))
        )
        more_button.click()
        
        # Find the Google Drive link in the description using XPath
        drive_link_element = driver.find_element(By.XPATH, "//a[contains(@class, 'yt-core-attributed-string__link') and contains(@class, 'yt-core-attributed-string__link--call-to-action-color')]")
        drive_link = drive_link_element.get_attribute('href')
        drive_link = extract_google_drive_link(drive_link)
    except Exception as e:
        print(f"Exception: {e}")
        drive_link = 'No Google Drive link available'
    
    driver.quit()
    return drive_link

def download_files_from_urls(urls, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    for url in urls:
        try:
            # Extract file name from URL
            file_name = url.split('/')[-1].split('?')[0]
            file_path = os.path.join(download_folder, file_name)
            
            # Download the file
            response = requests.get(url)
            if response.status_code == 200:
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded: {file_path}")
            else:
                print(f"Failed to download: {url}")
        except Exception as e:
            print(f"Exception: {e}")
            print(f"Failed to download: {url}")

def main():
    # playlist_url = 'https://www.youtube.com/playlist?list=PLOG_8OlGMp73hMyn-WX1M2Q4ON98DmaRq'
    # download_folder = "Downloaded_Files"
    # video_urls = get_playlist_videos(playlist_url)
    # arr=[]
    # arr for 25 links
    # arr=['https://drive.google.com/drive/folders/1YTc4nsdzRaSesRP8ZKtBtYwUWdyMsUxC', 'https://drive.google.com/drive/folders/1fUri-LUU3NKSlLP4-paLPaNtcF0dJV4U', 'https://drive.google.com/drive/folders/13zVBKuNJdj-sD-451P4ZQ1jkzH7Bfx8g?usp=drive_link', 'https://drive.google.com/drive/folders/1Z0bnAwTd0ONyqOp_5x6hPIGWVR_4FlQF?usp=drive_link', 'https://drive.google.com/drive/folders/1kHDmRY9y4dBc4POg-mcSsidwWAQl_KAh?usp=drive_link', 'https://drive.google.com/drive/folders/10i5zC0GX7kpAEQQa_Iq301InBJhpu0j6?usp=drive_link', 'https://drive.google.com/drive/folders/1IMhbVjPfNHmyjsgnzu6E2fi8SPhgpFZi?usp=drive_link', 'https://drive.google.com/drive/folders/1_hXeJcM8Xb4ou1o1S13xOq545VGk0nRB?usp=drive_link', 'https://drive.google.com/drive/folders/18vFF1jrWY6FwkNzSmeJ4L84BQrUqKqPc?usp=drive_link', 'https://drive.google.com/drive/folders/1iR-g-m-uY0qMYRFIAbXvSqwGGTyWNN_0?usp=drive_link', 'https://drive.google.com/drive/folders/1TWxd9alNC9hNGJOJhTNSrUoWyTUOCj8h?usp=drive_link', 'https://drive.google.com/drive/folders/1CEdIi6qGMWutwx2yvXwwA29DY8ay4oKQ?usp=drive_link', 'https://drive.google.com/drive/folders/1BJEtjtpSu-DlDHoseRKBZ_Q73AfiwHcp?usp=drive_link', 'https://drive.google.com/drive/folders/10mRsQywxFNCiqedI72Ax9Nq_y0S15pAt?usp=drive_link', 'https://drive.google.com/drive/folders/1qostGBd21l0OCmI7_uikTfdsSd3olPyZ?usp=drive_link', 'https://unacademy.com/scholarship/UGSTOCT25', 'https://drive.google.com/drive/folders/14MeRZk2CYihBYa3n9JrImm1kINYS8af2?usp=drive_link', 'https://drive.google.com/drive/folders/1QIxkHF7toOlbYq-TWCdyA8zAbfd75WMk?usp=drive_link', 'https://drive.google.com/drive/folders/1khuonOUGc9m96H7ksOY5DbUOKSxAGXFH?usp=sharing', 'https://unacademy.com/goal/gate-csit-dsai-placements/NVLIA/subscribe?plan_type=plus&referral_code=CSDA', 'https://unacademy.com/goal/gate-csit-dsai-placements/NVLIA/subscribe?plan_type=plus&referral_code=CSDA', 'https://unacademy.com/goal/gate-csit-dsai-placements/NVLIA/subscribe?plan_type=plus&referral_code=CSDA', 'https://drive.google.com/drive/folders/1EtAXbcYGatUf8ub_f_EspxsUkPMaQwIS?usp=drive_link', 'https://drive.google.com/drive/folders/1it_PI0y3Mvan6RtdzM_h9NSqfx4Ez3xC?usp=drive_link', 'https://unacademy.com/goal/gate-csit-dsai-placements/NVLIA/subscribe?plan_type=plus&referral_code=CSDA']
   
    # for video_url in video_urls:
    #     drive_link = get_video_description(video_url, download_folder)
    #     print(f"Drive URL: {drive_link} \n")
    #     arr.append(drive_link)
    #     if(len(arr)>=25):  # to get only first 25 links
    #         break

    # print(arr)
    # download_folder = "c:\\Users\\USER\\OneDrive\\Desktop\\TestTube\\Scrapy\\Downloads"
    # download_pdfs_from_drive_links(arr[4:], download_folder)
    # Usage
    folder_path = r'C:\Users\USER\OneDrive\Desktop\TestTube\Scrapy\Downloads'
    merge_pdfs(folder_path)

if __name__ == '__main__':
    main()
