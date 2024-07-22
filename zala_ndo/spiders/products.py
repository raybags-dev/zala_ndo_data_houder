import scrapy
import json
import uuid
import re
from ..items import ZalaNdoItem


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["zalando.co.uk"]
    start_urls = ["https://zalando.co.uk"]

    def start_requests(self):
        # Extract URLs for men, women, and kids categories
        nav_urls = ["/women-home/", "/men-home/", "/kids-home/"]

        base_url = "https://www.zalando.co.uk"

        for url in nav_urls:
            modified_url = url.replace("-home", "/?p=1")
            yield scrapy.Request(
                url=base_url + modified_url, callback=self.parse_category
            )

    def parse_category(self, response):
        total_pages = None
        total_pages_text = response.css("a.DJxzzA.DDVsUa.v8v6pv::text").get()
        if total_pages_text:
            try:
                total_pages = int(total_pages_text.strip())
                self.logger.info(f"Total pages from text: {total_pages}")
            except ValueError:
                self.logger.warning(
                    f"Failed to parse total pages from text: {total_pages_text}"
                )
                total_pages = None

        if total_pages is None:
            total_pages_span = response.css(
                "span[aria-atomic='true'][aria-live='polite']::text"
            ).get()
            if total_pages_span:
                match = re.search(r"Page \d+ of (\d+)", total_pages_span)
                if match:
                    try:
                        total_pages = int(match.group(1))
                        self.logger.info(f"Total pages from span: {total_pages}")
                    except ValueError:
                        self.logger.warning(
                            f"Failed to parse total pages from span: {total_pages_span}"
                        )
                        total_pages = None

        if total_pages is None:
            script_content = response.css("script::text").re_first(
                r'"numberOfPages":(\d+)'
            )
            if script_content:
                try:
                    total_pages = int(script_content)
                    self.logger.info(f"Total pages from script: {total_pages}")
                except ValueError:
                    self.logger.warning(
                        f"Failed to parse total pages from script: {script_content}"
                    )
                    total_pages = None

        if total_pages is None:
            total_pages = 10  # default page total
            self.logger.info(f"Defaulting to total pages: {total_pages}")

        self.logger.info(
            f"\n==============\nProcessing [{total_pages}] pages...\n==============\n"
        )

        category = response.url.split("/")[-2].replace("-home", "")
        base_url = "https://www.zalando.co.uk"

        start_urls = [
            f"{base_url}/{category}/?p={p}" for p in range(1, total_pages + 1)
        ]

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_search_page)

    def parse_search_page(self, response):
        links = response.css("article[role=link] > a::attr(href)").getall()
        for link in links:
            if "https" in link:
                yield scrapy.Request(url=link, callback=self.parse_item)

    def generate_uuid(self):
        return str(uuid.uuid4())

    def parse_item(self, response):
        item = ZalaNdoItem()
        product = json.loads(
            response.css("script[type='application/ld+json']::text").get()
        )
        for p in product["offers"]:
            url = product["url"]
            match = re.search(r"([^/]+)\.html$", url)

            if match:
                product_id = match.group(1).lower().replace("-", "").strip()
            else:
                product_id = None

            item["uuid"] = self.generate_uuid()
            item["product_id"] = product_id
            item["name"] = product["name"]
            item["colour"] = product["color"]
            item["image"] = json.dumps(product["image"])
            item["manufacturer"] = product["manufacturer"]
            item["description"] = product["description"]
            item["sku"] = product["sku"]
            item["variant_sku"] = p["sku"]
            item["availability"] = p["availability"].replace("http://schema.org/", "")
            item["price"] = p["price"]
            item["url"] = f"https://www.zalando.co.uk{product['url']}"

            yield item
