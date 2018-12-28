from scrapy import Spider, Selector
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.firefox.options import Options


class Firefox:
    def __init__(self):
        options = Options()
        options.headless = True
        firefox_profile = self._new_profile()
        self.driver = webdriver.Firefox(firefox_profile, options=options)

    def __enter__(self):
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def _new_profile(self):
        profile = FirefoxProfile()
        profile.set_preference('permissions.default.stylesheet', 2)
        profile.set_preference('permissions.default.image', 2)
        profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        return profile


class PaperSpider(Spider):
    name = 'paper_spider'
    start_urls = [
        'https://www.semanticscholar.org/paper/Coordinated-actor-model-of-self-adaptive-traffic-Bagheri-Sirjani/45ee43eb193409c96107c5aa76e8668a62312ee8',
        'https://www.semanticscholar.org/paper/Automatic-Access-Control-Based-on-Face-and-Hand-in-Jahromi-Bonderup/2199cb39adbf22b2161cd4f65662e4a152885bae',
        'https://www.semanticscholar.org/paper/Fair-Allocation-of-Indivisible-Goods%3A-Improvement-Ghodsi-Hajiaghayi/03d557598397d14727803987982c749fbfe1704b',
        'https://www.semanticscholar.org/paper/Restoring-highly-corrupted-images-by-impulse-noise-Taherkhani-Jamzad/637cf5540c0fb1492d94292bf965b2c404e42fb4',
        'https://www.semanticscholar.org/paper/Domino-Temporal-Data-Prefetcher-Bakhshalipour-Lotfi-Kamran/665c0dde22c2f8598869d690d59c9b6d84b07c01',
        'https://www.semanticscholar.org/paper/Deep-Private-Feature-Extraction-Ossia-Taheri/3355aff37b5e4ba40fc689119fb48d403be288be',
    ]

    def __init__(self):
        super(PaperSpider, self).__init__()
        self._crawled_ids = set()
        self.limit = 2000
        self._expand_details = False

    def parse(self, response):
        selector = self.get_selector(response)
        if self._url_to_id(response.url) in self._crawled_ids:
            return
        if len(self._crawled_ids) == self.limit:
            return

        references = self._extract_references(selector)
        result = {
            'type': 'paper',
            'id': self._url_to_id(response.url),
            'title': self._extract_title(selector),
            'authors': self._extract_authors(selector),
            'date': self._extract_year(selector),
            'abstract': self._extract_abstract(selector),
            'references': [self._extract_reference_name(ref) for ref in references],
        }
        self._crawled_ids.add(self._url_to_id(response.url))
        yield result
        for ref in references[:5]:
            self.logger.info(ref)
            yield response.follow(ref, callback=self.parse)

    def _extract_title(self, selector: Selector):
        return selector.css('[data-selenium-selector="paper-detail-title"]::text').extract_first()

    def _extract_abstract(self, selector: Selector):
        return selector.css('.abstract__text::text').extract_first()

    def _extract_authors(self, selector: Selector):
        return selector.css(
            '#paper-header .subhead .author-list__author-name span span::text'
        ).extract()

    def _extract_year(self, selector: Selector):
        return selector.css(
            '[data-selenium-selector="paper-year"] span span::text'
        ).extract_first()

    def _extract_references(self, selector: Selector):
        return selector.css(
            '#references .citation .result-meta [data-selenium-selector="title-link"]::attr(href)'
        ).extract()

    def _extract_reference_name(self, ref_url):
        after_paper = ref_url.split('/paper/')[1]
        return after_paper.split('/')[0]

    def _url_to_id(self, url: str) -> str:
        return url.split('/paper/')[1]

    def get_selector(self, response: Response) -> Selector:
        if not self._expand_details:
            return Selector(text=response.text)
        with Firefox() as driver:
            driver.get(response.url)
            self._click(driver, '.abstract__text .text-truncator__toggle')
            self._click(driver, '.more-authors-label')
            return Selector(text=driver.page_source)

    def _click(self, driver, selector: str):
        try:
            driver.find_element_by_css_selector(selector).click()
        except Exception:
            self.logger.info('Failed to find {}'.format(selector))
