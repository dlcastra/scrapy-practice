import scrapy


class WorkUaSpider(scrapy.Spider):
    name = "parse_wua"
    custom_settings = {"CLOSESPIDER_PAGECOUNT": 100}
    start_urls = ["https://www.work.ua/jobs-python/"]

    def parse_vacancy(self, response):
        title = response.xpath('//h1[@id="h1-name"]/text()').get()

        currency = response.css(".glyphicon-hryvnia")
        salary = None
        if currency:
            salary = (
                currency.xpath("./following-sibling::span/text()")
                .get()
                .replace("\u202f", "")
                .replace("\xa0", "")
                .replace("\u2009", "")
            )

        description = response.css("div#job-description::text").getall()
        description_text = " ".join(description).strip().replace("\r\n", "")
        employer = (
            response.css(".glyphicon-company")
            .xpath("./following-sibling::a/span/text()")
            .get()
        )

        workplace = None
        company_address_or_city = response.css(".glyphicon-map-marker")
        other_place = response.css(".glyphicon-remote")
        if company_address_or_city:
            workplace = (
                company_address_or_city.xpath("./following-sibling::text()")
                .get()
                .replace("\n", "")
                .strip()
            )

        elif other_place:
            workplace = (
                other_place.xpath("./following-sibling::text()")
                .get()
                .replace("\n", "")
                .strip()
            )

        yield {
            "url": response.url,
            "workplace": workplace,
            "title": title,
            "salary": salary,
            "description": description_text,
            "employer": employer,
        }

    def parse(self, response, **kwargs):
        for card in response.css(".card"):
            vacancy_url = card.css(".add-bottom").xpath("./h2/a/@href").get()
            if vacancy_url is None:
                continue
            yield response.follow(vacancy_url, callback=self.parse_vacancy)
        next_page = (
            response.css(".pagination").xpath("./li")[-1].xpath("./a/@href").get()
        )
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
