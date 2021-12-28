import json
import logging
import requests
import sched
import time
from datetime import datetime

news_logger = logging.getLogger(__name__)
news_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
file_handler = logging.FileHandler("logfile.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
news_logger.addHandler(file_handler)

with open("config.json", "r") as f:
    config = json.load(f)
    covid_request_data = config["covid_request_data"]
    news_data = config["news_data"]
    interface_settings = config["interface_settings"]

def news_API_request(
    covid_terms: str = news_data["covid_terms"], current_page_number: int = 1
) -> list:
    """
    Description: Requests and returns latest COVID-19 related news from the NEWS API

        Arguments:
            current_page_number (int): Integer value of page number; used to import next set/page of news articles
            covid_terms (str): String data of terms to filter articles that mention them.

        Returns:
        news_list (list): Returns list of dictionaries; each dictionary holds one news article and it's related data.
    """
    try:
        url = (
            "https://newsapi.org/v2/everything?"
            "q=" + covid_terms + "&"
            "q=COVID-19&"
            "q=coronavirus&"
            "q=COVID&"
            "pageSize=10&"
            "page=" + str(current_page_number) + "&"
            "apiKey=" + news_data["apiKey"]
        )
        response = requests.get(url)
        news_list = response.json()["articles"]
    except KeyError:
        news_logger.exception(
            " Unable to request news from NEWS API; INCORRECT API KEY"
        )
    else:
        return news_list


def next_news_page(news_list: list, current_page_number: int) -> tuple[list, int]:
    """
    Description: Requests and Returns the next immediate page of COVID related articles.

        Arguments:
            news_list (list): List of current page of COVID related articles
            current_page_number (int): Current page number of the articles; page number of news_list

        Returns:
            next_news_list (list): List of next page of COVID related articles
            next_page_number (int): Integer value of the next page of articles; page number of next_news_list
    """
    next_page_number = current_page_number + 1
    next_news_list = news_API_request(news_data["covid_terms"], next_page_number)

    return next_news_list, next_page_number


def live_news_adding(
    news_list: list, current_page_number: int, remaining_list: list
) -> tuple[list, int]:
    """
    Description: Continuously updates the news list with new articles, ensuring there are 4 articles rendered at all times.
                 (This is required as all articles cannot be imported at once; due to the maximum limit)

        Arguments:
            news_list (list): List of new articles
            current_page_number (int): Page number of the articles; page number of news_list
            remaining_list (list): Temporary list holding remaining articles once 5 have been closed; which is then inserted into the next list of articles.

        Returns:
            news_list (list): List of news with the remaining articles and articles from the next page.
            current_page_number (int): Current page number of the imported articles.
    """
    next_news_list, new_page_number = next_news_page(news_list, current_page_number)
    current_page_number = new_page_number

    for x in range(5):
        next_news_list.insert(0, remaining_list[4 - x])
    news_list = next_news_list

    return news_list, current_page_number


def update_news() -> None:
    """
    Description: Updates the global News list.

        Arguments:
            None

        Returns:
            None
    """
    global news_list
    news_list = news_API_request(news_data["covid_terms"], 1)

    with open("manual_check_news_data.txt", "a") as f:
        f.write("\n News data updated at: " + str(datetime.now().time()))

    news_logger.info(" News data updated successfully")


def schedule_news_update(update_interval: str, update_name: str) -> None:
    """
    Description: Creates an event for the news update

        Arguments:
            update_interval (str): String value of the time for the Scheduled Update, in 24 hour format.
            update_name (str): String value of the name of the Scheduled Update.

        Returns:
            None
    """
    s = sched.scheduler(time.time, time.sleep)
    event = s.enter(float(update_interval), 10, update_news)
    s.run(event)
