from flask import Flask, render_template, request, redirect
import os
import time
import requests
from flask_cors import cross_origin
from selenium import webdriver
from selenium.webdriver.common.by import By

app = Flask(__name__, static_folder='static')


def fetch_image_urls(wd, query, max_links_to_fetch, sleep_between_interactions=1):
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

def persist_image(folder_path, url, counter):
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

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/success', methods=['GET'])
def success():
    return render_template('success.html')

@app.route('/scrape', methods=['POST', 'GET'])  # route to fetch and download images
@cross_origin()
def scrape():
    if request.method == 'POST':
        try:
            search_term = request.form.get('search_term')
            number_images = int(request.form.get('number_images'))

            DRIVER_PATH = "chromedriver.exe"  # Update the path to your ChromeDriver

            target_folder = os.path.join("images", search_term.lower().replace(" ", "_"))
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = DRIVER_PATH
            with webdriver.Chrome(options=chrome_options) as wd:
                res = fetch_image_urls(wd, search_term, number_images, sleep_between_interactions=0.5)

            if res is not None and len(res) > 0:
                for counter, image_url in enumerate(res):
                    persist_image(target_folder, image_url, counter)
                return redirect('/success')
            else:
                return render_template('search_fail.html')

        except Exception as e:
            return f"An error occurred: {str(e)}"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)