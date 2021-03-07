from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait



class VivinoScraper(object):
    def __init__(self):
        self.browser = None
        self.wait_seconds = 8
        self.wait = None
        self.base_url = 'https://www.vivino.com/'

    def start_chrome_browser(self, start_url, chrome_options=None):
        if not chrome_options:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument("--start-fullscreen")
        print(chrome_options)
        self.browser = webdriver.Chrome('venv/bin/chromedriver', options=chrome_options)
        self.wait = WebDriverWait(self.browser, self.wait_seconds)
        self.browser.get(start_url)
        self.wait.until()


if __name__ == '__main__':
    start_url = 'https://www.vivino.com/explore?e=eJzLLbI1VMvNzLM1UMtNrLA1MzBQS660DXZXSwYSLmoFQNn0NNuyxKLM1JLEHLX8JNuix' \
                'JLMvPTi-MSy1KLE9FS1fNuU1OJktfKS6FigYjBlBKGMIZQJhDKHypkAAINQJc8%3D&cart_item_source=nav-explore'
    vivino = VivinoScraper()
    vivino.start_chrome_browser(start_url)
