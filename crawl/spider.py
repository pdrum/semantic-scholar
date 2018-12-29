from scrapy import Spider, Selector
from scrapy.http import Response


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

    def parse(self, response):
        if self._url_to_id(response.url) in self._crawled_ids:
            return
        if len(self._crawled_ids) == self.limit:
            return
        try:
            data = self._extract_paper_data(response)
            self._crawled_ids.add(self._url_to_id(response.url))
            yield data
        except Exception:
            self.logger.error('Failed to extract info for {}'.format(response.url))
        try:
            ref_links = self._extract_reference_links(self.get_selector(response))
            for ref in ref_links[:5]:
                if len(self._crawled_ids) == self.limit:
                    return
                self.logger.info(ref)
                yield response.follow(ref, callback=self.parse)
        except Exception:
            self.logger.error('Failed to extract ref links for {}'.format(response.url))

    def _extract_paper_data(self, response: Response):
        selector = self.get_selector(response)
        return {
            'type': 'paper',
            'id': self._url_to_id(response.url),
            'title': self._extract_title(selector),
            'authors': self._extract_authors(selector),
            'date': self._extract_year(selector),
            'abstract': self._extract_abstract(selector),
            'references': self._references_to_ids(self._extract_reference_links(selector)),
        }

    def _extract_title(self, selector: Selector):
        return selector.xpath("//meta[@name='citation_title']/@content")[0].extract()

    def _extract_abstract(self, selector: Selector):
        return selector.xpath("//meta[@name='description']/@content")[0].extract()

    def _extract_authors(self, selector: Selector):
        return selector.xpath("//meta[@name='citation_author']/@content").extract()

    def _extract_year(self, selector: Selector):
        return selector.xpath("//meta[@name='citation_publication_date']/@content")[0].extract()

    def _extract_reference_links(self, selector: Selector):
        return selector.css(
            '#references .citation .result-meta [data-selenium-selector="title-link"]::attr(href)'
        ).extract()

    def _references_to_ids(self, references):
        result = []
        for ref in references:
            try:
                ref_id = self._url_to_id(ref)
                result.append(ref_id)
            except Exception:
                self.logger.info('Failed to extract id for {}'.format(ref))
        return result

    def _extract_reference_name(self, ref_url):
        after_paper = ref_url.split('/paper/')[1]
        return after_paper.split('/')[0]

    def _url_to_id(self, url: str) -> str:
        return url.split('/paper/')[1]

    def get_selector(self, response: Response) -> Selector:
        return Selector(text=response.text)
