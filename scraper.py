import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By


def fetch_image_urls(query: str, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: int = 1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # Get all image elements
        image_elements = wd.find_elements(By.XPATH, "//img[@class='rg_i Q4LuWd']")
        number_results = len(image_elements)

        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in image_elements[results_start:number_results]:
            img.click()
            time.sleep(sleep_between_interactions)

            try:
                # Extract image URL from the src attribute of the img tag
                actual_image = img.get_attribute('src')
                if actual_image and 'http' in actual_image:
                    image_urls.add(actual_image)
            except Exception as e:
                print(f"Error extracting image URL: {e}")

            image_count = len(image_urls)
            print(image_count)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return

        results_start = number_results

    return image_urls


def persist_image(folder_path: str, url: str, counter):
    try:
        image_content = requests.get(url).content
    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")
        return

    try:
        file_path = os.path.join(folder_path, f"image_{counter}.jpg")
        with open(file_path, 'wb') as f:
            f.write(image_content)
        print(f"SUCCESS - saved {url} as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")


def search_and_download(search_term: str, driver_path: str, target_path='./images', number_images=10):
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Create ChromeOptions instance and set executable_path
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = driver_path

    # Create ChromeDriver instance with the specified options
    with webdriver.Chrome(options=chrome_options) as wd:
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=0.5)

    for counter, image_url in enumerate(res):
        persist_image(target_folder, image_url, counter)

        # How to execute this code
        # Step 1 : pip install selenium. pillow, requests
        # Step 2 : make sure you have chrome installed on your machine
        # Step 3 : Check your chrome version ( go to three dot then help then about google chrome )
        # Step 4 : Download the same chrome driver from here  " https://chromedriver.storage.googleapis.com/index.html "
        # Step 5 : put it inside the same folder of this code


# Provide the path to your ChromeDriver executable
DRIVER_PATH = r"D:\UB\Summer'23\Project\Final_Projects\Walmart_Reviews_Scraper\chromedriver.exe"
search_term = 'data science'
number_images = 10
search_and_download(search_term=search_term, driver_path=DRIVER_PATH, number_images=number_images)
