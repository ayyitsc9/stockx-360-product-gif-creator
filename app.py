import requests, platform, imageio, uuid, os, re, shutil, json, time
from datetime import datetime
from colorama import init, Fore, Style
from art import text2art
from PIL import Image
from pathlib import Path

class GIFCreator:
    def __init__(self, product_to_search):
        self.product_to_search = product_to_search
        self.format = self.detect_format()
        if self.format == "Link":
            Logger.normal("Detected Link!")
            self.api_url = f"https://stockx.com/api/products/{self.product_to_search.split('stockx.com/')[1]}?includes=market,360&currency=USD"
            if self.get_image_urls():
                self.generated_uuid = uuid.uuid4()
                os.mkdir(f"./{self.generated_uuid}")
                Logger.normal(f"Generated folder '{self.generated_uuid}' for 360 images! It will be automatically deleted upon completion.")
                self.filenames = []
                for image_url in self.image_urls:
                    self.download_image(image_url)
                self.generate_gif()
                shutil.rmtree(f"./{self.generated_uuid}")
            else:
                Logger.error("No 360 images found!")
        elif self.format == "Name":
            Logger.normal("Detected Name!")
            self.product_to_search = self.get_product_link()
            if self.product_to_search != None:
                self.api_url = f"https://stockx.com/api/products/{self.product_to_search}?includes=market,360&currency=USD"
                if self.get_image_urls():
                    self.generated_uuid = uuid.uuid4()
                    os.mkdir(f"./{self.generated_uuid}")
                    Logger.normal(f"Generated folder '{self.generated_uuid}' for 360 images! It will be automatically deleted upon completion.")
                    self.filenames = []
                    for image_url in self.image_urls:
                        self.download_image(image_url)
                    self.generate_gif()
                    shutil.rmtree(f"./{self.generated_uuid}")
                else:
                    Logger.error("No 360 images found!")

        else:
            Logger.error("Link provided is invalid!")

    def detect_format(self):
        url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        match = re.search("((https|http)://stockx.com/.{1,})",self.product_to_search)
        if match != None:
            return "Link"
        elif match == None and re.search(url_regex,self.product_to_search):
            return "Invalid Link"
        else:
            return "Name"

    def get_product_link(self):
        words = re.findall(r'\w+', self.product_to_search)
        keywords = ''
        for word in words:
            keywords += word + '%20'
        json_string = json.dumps({"params": f"query={keywords}&hitsPerPage=20&facets=*"})
        byte_payload = bytes(json_string, 'utf-8')
        algolia = {"x-algolia-agent": "Algolia%20for%20JavaScript%20(4.8.4)%3B%20Browser", "x-algolia-application-id": "XW7SBCT9V6", "x-algolia-api-key": "6b5e76b49705eb9f51a06d3c82f7acee"}
        r = requests.post("https://xw7sbct9v6-dsn.algolia.net/1/indexes/products/query", params=algolia, data=byte_payload, timeout=30)
        if r.status_code == 200:
            try:
                results = r.json()["hits"][0]
                Logger.normal(f"Product found : {results['name']}")
                return results['url']
            except IndexError:
                Logger.error(f"Did not find any products matching your query! Query : {words}")
                return None
        else:
            Logger.error(f"Failed to get product link! Status Code : {r.status_code}")

    def get_image_urls(self):
        r = requests.get(self.api_url, headers=headers)
        self.image_urls = [media for media in r.json()['Product']['media']['360']]
        if len(self.image_urls) != 0:
            return True  
        else:
            return False

    def download_image(self, url):
        r = requests.get(url)
        if r.status_code == 200:
            filename = f"./{self.generated_uuid}/{url.split('/')[7].split('?')[0][:-3]}png"
            with open(filename, "wb") as save_file:
                save_file.write(r.content)
            self.filenames.append(filename)
            if Path('./overlay.png').exists():
                im1 = Image.open(filename)
                im2 = Image.open('overlay.png').resize(im1.size).convert(mode=im1.mode)
                try:
                    im = Image.blend(im1, im2, 0.1)
                    im.save(filename, quality=100)
                except ValueError:
                    Logger.error("Could not blend image with overlay. Images do not match. Try a different image! Proceeding with saving without overlay...")
        else:
            Logger.error(f"Failed to download image! Status Code : {r.status_code}")

    def generate_gif(self):
        images = [imageio.imread(filename) for filename in self.filenames]
        imageio.mimsave(f'./gifs/{self.generated_uuid}.gif', images, fps=15)
        Logger.success(f"Successfully generated {self.generated_uuid}.gif in gifs folder!")

lightblue = "\033[94m"
orange = "\033[33m"

class Logger:
    @staticmethod
    def timestamp():
        return str(datetime.now())[:-7]
    @staticmethod
    def normal(message):
        print(f"{lightblue}[{Logger.timestamp()}] {message}")
    @staticmethod
    def other(message):
        print(f"{orange}[{Logger.timestamp()}] {message}")
    @staticmethod
    def error(message):
        print(f"{Fore.RED}[{Logger.timestamp()}] {message}")
    @staticmethod
    def success(message):
        print(f"{Fore.GREEN}[{Logger.timestamp()}] {message}")

# - - - -  - - - - - - - - - - - - - - - - - - -  - - - - - - - -
# Initializing Colorama || Utils
init(convert=True) if platform.system() == "Windows" else init()
print(f"{Fore.CYAN}{Style.BRIGHT}{text2art('Created by @ayyitsc9')}\n")
headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7,la;q=0.6',
    'appos': 'web',
    'appversion': '0.1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}

while True:
    print(Style.RESET_ALL)
    print("Notes")
    print("- Search Query can either be product keywords or a StockX direct link!")
    print("- Overlay image must be PNG and named 'overlay.png'. For best results, resize it to 1118x745!")
    user_input = input("Enter Search Query : ")
    start = time.time()
    GIFCreator(user_input)
    end = time.time()
    Logger.success(f"Execution time : {end-start}s")
    

# TO DO
# Refactor Code
# Add notes
