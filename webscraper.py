
import requests
import time
import csv
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

USER_AGENT = "BookScraper/1.0"

def check_robots_permission(url):
    try:
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.read()

        return parser.can_fetch(USER_AGENT, url)

    except Exception as error:
        print("Could not verify robots.txt:", error)
        return False


def scrape_books(url):
    if not check_robots_permission(url):
        print("Scraping not permitted or permission unverified.")
        return

    headers = {"User-Agent": USER_AGENT}

    try:
        time.sleep(2)

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if response.status_code == 429:
            print("Rate limit reached. Stopping.")
            return

        if response.status_code == 403:
            print("Access forbidden. Stopping.")
            return

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.select("article.product_pod")

        count = 0

        with open("books.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Price", "Availability"])

            for book in books:
                title_element = book.select_one("h3 a")
                price_element = book.select_one(".price_color")
                availability_element = book.select_one(".availability")

                if not title_element or not price_element or not availability_element:
                    continue

                title = title_element.get("title", "").strip()
                price = price_element.get_text(strip=True)
                availability = availability_element.get_text(strip=True)

                if not title:
                    continue

                writer.writerow([title, price, availability])
                count += 1

        print(f"Successfully saved {count} books to books.csv")

    except requests.RequestException as error:
        print("Request failed:", error)


if __name__ == "__main__":
    website_url = "https://books.toscrape.com/"
    scrape_books(website_url)
