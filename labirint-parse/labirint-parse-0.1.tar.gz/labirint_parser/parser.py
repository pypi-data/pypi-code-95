import time
import csv
import click
import asyncio
import aiohttp
from bs4 import BeautifulSoup


async def get_page_data(session, link, page, books_data):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0"
    }

    url = f"{link}/page={page}"

    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()
        soup = BeautifulSoup(response_text, "lxml")
        books_items = soup.find("tbody", class_="products-table__body").find_all("tr")

        for bi in books_items:
            book_data = bi.find_all("td")

            try:
                book_title = book_data[0].find("a").text.strip()
            except AttributeError:
                book_title = "Нет названия книги"

            try:
                book_author = book_data[1].text.strip()
            except AttributeError:
                book_author = "Нет автора"

            try:
                book_publishing = book_data[2].find_all("a")
                book_publishing = ":".join([bp.text for bp in book_publishing])
            except AttributeError:
                book_publishing = "Нет издательства"

            try:
                book_new_price = book_data[3].find("div", class_="price").find("span").find("span")
                book_new_price = int(book_new_price.text.strip().replace(" ", ""))
            except AttributeError:
                book_new_price = "Нет новой цены"

            try:
                book_old_price = int(book_data[3].find("span", class_="price-gray").text.strip().replace(" ", ""))
            except AttributeError:
                book_old_price = "Нет старой цены"

            try:
                book_sale = round(((book_old_price - book_new_price) / book_old_price) * 100)
            except (TypeError, AttributeError):
                book_sale = "Нет скидки"

            try:
                book_status = book_data[-1].text.strip()
            except AttributeError:
                book_status = "Нет статуса"

            books_data.append(
                {
                    "book_title": book_title,
                    "book_author": book_author,
                    "book_publishing": book_publishing,
                    "book_new_price": book_new_price,
                    "book_old_price": book_old_price,
                    "book_sale": book_sale,
                    "book_status": book_status
                }
            )

        print(f"Обработана страница {page}")


async def gather_data(url):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"
    }

    books_data = []

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        soup = BeautifulSoup(await response.text(), "lxml")
        pages_count = int(soup.find("div", class_="pagination-numbers").find_all("a")[-1].text)

        tasks = []

        for page in range(1, pages_count + 1):
            task = asyncio.create_task(get_page_data(session, url, page, books_data))
            tasks.append(task)

        await asyncio.gather(*tasks)

    return books_data


@click.command()
@click.option('--save', default="labirint_books.csv", help='The name of the file to be saved')
@click.option('--link', help='Enter the link to the page on the Labirint website you want to download')
def main(save, link):
    start_time = time.time()
    books_data = asyncio.run(gather_data(link))

    csv_file_name = save

    with open(csv_file_name, "w") as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                "Название книги",
                "Автор",
                "Издательство",
                "Цена со скидкой",
                "Цена без скидки",
                "Процент скидки",
                "Наличие на складе"
            )
        )

    for book in books_data:
        with open(csv_file_name, "a") as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    book["book_title"],
                    book["book_author"],
                    book["book_publishing"],
                    book["book_new_price"],
                    book["book_old_price"],
                    book["book_sale"],
                    book["book_status"]
                )
            )

    finish_time = time.time() - start_time
    print(f"Затраченное на работу скрипта время: {finish_time}")


if __name__ == "__main__":
    main()
