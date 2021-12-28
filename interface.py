import json
import logging
from typing import Callable
from flask import Flask
from flask import app
from flask import request
from flask.templating import render_template
from covid_data_handler import (
    covid_API_request,
    plus_24_hours,
    process_covid_data,
    time_difference,
    schedule_covid_updates,
)
from covid_news_handling import (
    live_news_adding,
    news_API_request,
    schedule_news_update, 
    news_logger,
)
from multiprocessing import Process

logger = logging.getLogger("interface")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
file_handler = logging.FileHandler("logfile.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app = Flask(__name__, template_folder="templates")

with open("config.json", "r") as f:
    config = json.load(f)
    covid_request_data = config["covid_request_data"]
    news_data = config["news_data"]
    interface_settings = config["interface_settings"]

local_req = covid_API_request(
    covid_request_data["local_request_location"],
    covid_request_data["local_req_location_type"],
)
nation_req = covid_API_request(
    covid_request_data["nation_request_location"],
    covid_request_data["nation_req_location_type"],
)

local_covid_data = process_covid_data(local_req)
nation_covid_data = process_covid_data(nation_req)

news_list = news_API_request(news_data["covid_terms"], 1)

current_page_number = 1
sched_updates_list = []
deleted_articles = []
processes_list = []
all_processes = []

processes = {"name": "", "process": ""}

with open("manual_check_cov_data.txt", "w") as f:
    f.close()
with open("manual_check_news_data.txt", "w") as f:
    f.close


@app.route("/", methods=["GET"])
def interface():
    """
    Description: Returns specific values to be displayed on the HTML page through flask.

        Paramaters:
            GET:/

        Returns:
            It renders the home page of index.html

    """
    global local_covid_data
    global nation_covid_data
    global sched_updates_list
    global news_list

    try:
        return render_template(
            "index.html",
            location=local_covid_data[1],
            local_7day_infections=local_covid_data[0],
            nation_location=nation_covid_data[1],
            national_7day_infections=nation_covid_data[0],
            hospital_cases=nation_covid_data[3],
            deaths_total=nation_covid_data[4],
            news_articles=news_list[0 : interface_settings["max_articles_displayed"]],
            updates=sched_updates_list[0 : interface_settings["max_updates_displayed"]],
            image=interface_settings["logo"],
        )
    except TypeError:
        logger.critical("Value/Values in render_template() are None.")


@app.route("/index", methods=["GET"])
def submit_updates() -> Callable:
    """
    Description: Retrieves any data input from the html for processing and then renders it.

        Parameters:
            GET:/index

        Returns:
            It returns the interface() function, which will render the page with the processed and updated data.
    """
    global sched_updates_list
    global news_list
    global deleted_articles
    global current_page_number
    global local_covid_data
    global nation_covid_data
    global update_check
    x = 0
    y = 0
    counter = 0

    if request.method == "GET":
        scheduled_time = request.args.get("update")
        scheduled_name = request.args.get("two")
        covid_checkbox = request.args.get("covid-data")
        repeat_checkbox = request.args.get("repeat")
        news_checkbox = request.args.get("news")
        news_title_clicked = request.args.get("notif")
        close_updates = request.args.get("update_item")

        update_dictionary = {
            "title": scheduled_name,
            "content": "",
            "process": "",
            "update_check": "",
        }

        processes_list = []

        print(repeat_checkbox)

        if news_checkbox and covid_checkbox:
            if repeat_checkbox:

                update_dictionary["content"] = (
                    "Covid-Data and News will be updated at "
                    + scheduled_time
                    + "\n"
                    + "Repeated Update (after 24 hours)"
                )

                covid_update_process = Process(
                    target=schedule_covid_updates,
                    args=(time_difference(scheduled_time), scheduled_name),
                )
                news_update_process = Process(
                    target=schedule_news_update,
                    args=(time_difference(scheduled_time), scheduled_name),
                )

                covid_24hr_update_process = Process(
                    target=schedule_covid_updates,
                    args=(plus_24_hours(scheduled_time), scheduled_name),
                )
                news_24hr_update_process = Process(
                    target=schedule_news_update,
                    args=(plus_24_hours(scheduled_time), scheduled_name),
                )
                # Created individual processes for the scheduled updates using the multiprocessing module

                processes_list.append(covid_update_process)
                processes_list.append(news_update_process)
                processes_list.append(covid_24hr_update_process)
                processes_list.append(news_24hr_update_process)

                covid_update_process.start()
                news_update_process.start()
                covid_24hr_update_process.start()
                news_24hr_update_process.start()

                update_dictionary["process"] = processes_list
                sched_updates_list.append(update_dictionary.copy())

                logger.info(
                    "News and Covid-data update successfully added (repeated update)"
                )

            else:
                update_dictionary["content"] = (
                    "Covid-Data and News will be updated at " + scheduled_time
                )

                covid_update_process = Process(
                    target=schedule_covid_updates,
                    args=(time_difference(scheduled_time), scheduled_name),
                )
                news_update_process = Process(
                    target=schedule_news_update,
                    args=(time_difference(scheduled_time), scheduled_name),
                )
                # Created individual processes for the scheduled updates using the multiprocessing module

                processes_list.append(covid_update_process)
                processes_list.append(news_update_process)

                covid_update_process.start()
                news_update_process.start()

                update_dictionary["process"] = processes_list
                sched_updates_list.append(update_dictionary.copy())

                logger.info("News and Covid-data update successfully added")

        else:
            if covid_checkbox:
                if repeat_checkbox:
                    update_dictionary["content"] = (
                        "Covid-Data will be updated at "
                        + scheduled_time
                        + "\n"
                        + "Repeated Update (after 24 hours)"
                    )

                    covid_update_process = Process(
                        target=schedule_covid_updates,
                        args=(time_difference(scheduled_time), scheduled_name),
                    )
                    covid_24hr_update_process = Process(
                        target=schedule_covid_updates,
                        args=(plus_24_hours(scheduled_time), scheduled_name),
                    )
                    # Created individual processes for the scheduled updates using the multiprocessing module

                    processes_list.append(covid_update_process)
                    processes_list.append(covid_24hr_update_process)

                    covid_update_process.start()
                    covid_24hr_update_process.start()

                    update_dictionary["process"] = processes_list
                    sched_updates_list.append(update_dictionary.copy())

                    logger.info(
                        "Covid-data update successfully added (repeated update)"
                    )

                else:
                    update_dictionary["content"] = (
                        "Covid-Data will be updated at " + scheduled_time
                    )

                    covid_update_process = Process(
                        target=schedule_covid_updates,
                        args=(time_difference(scheduled_time), scheduled_name),
                    )
                    # Created individual processes for the scheduled updates using the multiprocessing module

                    processes_list.append(covid_update_process)
                    covid_update_process.start()

                    update_dictionary["process"] = processes_list
                    sched_updates_list.append(update_dictionary.copy())

                    logger.info("Covid-data update successfully added")

            if news_checkbox:
                if repeat_checkbox:

                    update_dictionary["content"] = (
                        "News will be updated at " + scheduled_time
                    )

                    news_update_process = Process(
                        target=schedule_news_update,
                        args=(time_difference(scheduled_time), scheduled_name),
                    )
                    news_24hr_update_process = Process(
                        target=schedule_news_update,
                        args=(plus_24_hours(scheduled_time), scheduled_name),
                    )
                    # Created individual processes for the scheduled updates using the multiprocessing module

                    processes_list.append(news_update_process)
                    processes_list.append(news_24hr_update_process)

                    news_update_process.start()
                    news_24hr_update_process.start()

                    update_dictionary["process"] = processes_list
                    sched_updates_list.append(update_dictionary.copy())

                    logger.info("News update successfully added (repeated update)")

                else:
                    update_dictionary["content"] = (
                        "News will be updated at " + scheduled_time
                    )

                    news_update_process = Process(
                        target=schedule_news_update,
                        args=(time_difference(scheduled_time), scheduled_name),
                    )
                    # Created individual processes for the scheduled updates using the multiprocessing module

                    processes_list.append(news_update_process)
                    news_update_process.start()

                    update_dictionary["process"] = processes_list
                    sched_updates_list.append(update_dictionary.copy())

                    logger.info("News update successfully added")

        if news_title_clicked:
            for article in news_list:
                title = article["title"]

                if news_title_clicked == title:
                    deleted_articles.append(news_list[x])
                    news_list.pop(x)
                    news_logger.info(" News article closed -> " + title),
                    break
                else:
                    x = x + 1

        if close_updates:
            for update in sched_updates_list:
                update_title = update["title"]

                if close_updates == update_title:
                    sched_updates_list.pop(y)
                    logger.info(
                        " Scheduled Update cancelled/closed -> "
                        + "Update Name: "
                        + update_title
                    )
                    process = update["process"]
                    for ctr in process:
                        ctr.terminate()
                    logger.info(" Update/Updates terminated successfully")
                    break
                else:
                    y = y + 1

        if len(news_list) == 5:
            news_logger.info(" New articles required for displayed list.")
            remaining_articles = news_list
            local_list, local_page_number = live_news_adding(
                news_list, current_page_number, remaining_articles
            )
            current_page_number = local_page_number
            news_list = local_list
            news_logger.info(" New articles successfully added.")

    return interface()


if __name__ == "__main__":
    app.run(debug=True)
