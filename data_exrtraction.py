import requests
from bs4 import BeautifulSoup
import json
import time

base_url = "https://support.highrise.game"

main_url = f"{base_url}/en/"

# Headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


def fetch_page(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


main_soup = fetch_page(main_url)

faq_data = {"collections": []}

collections = main_soup.find_all("a", class_="collection-link")

for collection in collections:
    collection_title = collection.find(
        "div", attrs={"data-testid": "collection-name"}
    ).get_text(strip=True)
    collection_url = collection["href"]

    collection_soup = fetch_page(collection_url)

    articles = collection_soup.find_all("a", attrs={"data-testid": "article-link"})

    articles_data = []

    for article in articles:
        # Extract the article title (question) and URL
        question = article.get_text(strip=True)
        article_url = article["href"]
        print("article url", article_url)

        # Fetch the article page
        article_soup = fetch_page(article_url)

        # Extract the answer content
        answer_div = article_soup.find("div", class_="article_body")
        answer = answer_div.get_text(strip=True) if answer_div else "No answer found."

        # Extract images
        images = []
        for img in answer_div.find_all("img"):
            img_url = img.get("src")
            img_alt = img.get("alt", "")
            images.append({"url": img_url, "alt": img_alt})

        # Extract table of contents
        toc = []
        toc_div = article_soup.find("div", class_="table-of-contents")
        if toc_div:
            for li in toc_div.find_all("li"):
                toc_item = li.get_text(strip=True)
                toc.append(toc_item)

        # Extract sections
        sections = []
        subheadings = answer_div.find_all(
            "div", class_="intercom-interblocks-subheading"
        )

        for subheading in subheadings:
            section_title = subheading.get_text(strip=True)

            section_content = []
            for sibling in subheading.find_next_siblings():
                if sibling.get(
                    "class"
                ) and "intercom-interblocks-subheading" in sibling.get("class"):
                    break
                if (
                    sibling.name == "div"
                    and "intercom-interblocks-paragraph" in sibling.get("class", [])
                ):
                    section_content.append(sibling.get_text(strip=True))

            sections.append(
                {"title": section_title, "content": " ".join(section_content)}
            )

        articles_data.append(
            {
                "question": question,
                "answer": answer,
                "url": article_url,
                "images": images,
                "table_of_contents": toc,
                "sections": sections,
            }
        )
        print(articles_data[-1])

        # Small delay to avoid overwhelming the server
        time.sleep(1)

    faq_data["collections"].append(
        {
            "collection_title": collection_title,
            "articles": articles_data,
        }
    )

# Save the data to a JSON file
with open("faq_data.json", "w", encoding="utf-8") as f:
    json.dump(faq_data, f, ensure_ascii=False, indent=4)

print("FAQ data has been saved to faq_data.json")
