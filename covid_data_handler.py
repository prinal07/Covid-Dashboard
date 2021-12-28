from uk_covid19 import Cov19API, exceptions
import sched
import time
from datetime import date, datetime, timedelta
import json
import logging

cov_logger = logging.getLogger(__name__)
cov_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
file_handler = logging.FileHandler("logfile.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
cov_logger.addHandler(file_handler)

with open("config.json", "r") as f:
    config = json.load(f)
    covid_request_data = config["covid_request_data"]
    news_data = config["news_data"]
    interface_settings = config["interface_settings"]


def parse_csv_data(csv_filename: str) -> list[str]:
    """
    Description: Returns a List with each line of the file as an individual element.

        Arguments:
            csv_filename (str): File name as String.

        Returns:
            lines (list[str]): Covid Data as a List of Strings, where each String is the data of one day.
    """
    with open(csv_filename) as f:
        lines = f.readlines()
    return lines


def process_covid_csv_data(covid_csv_data: list) -> tuple[int, str, str]:
    """
    Description: Returns caclulated values of the Covid Cases in the past week, Total Deaths and Hospital Cases.

        Arguments:
            covid_csv_data (list[str]): Covid Data as a List of Strings, where each String is the data of one day.

        Returns:
            week_cases (int): Integer value of the Covid Cases in the last 7 days.
            total_deaths (str): String value of the Total Deaths.
            hopsital_cases (str): String value of the Hospital Cases.
    """
    cases_list = []
    x = 3
    y = 1
    while len(cases_list) != 7:
        split_data = (covid_csv_data[x].strip()).split(",")
        if split_data[6] != "":
            cases_list.append(int(split_data[6]))
            x = x + 1
        else:
            x = x + 1
    week_cases = sum(cases_list)
    hospital_cases = int((covid_csv_data[1].strip()).split(",")[5])

    total_deaths = (covid_csv_data[y].strip()).split(",")[4]
    while not total_deaths:
        y = y + 1
        total_deaths = (covid_csv_data[y].strip()).split(",")[4]

    total_deaths = int((covid_csv_data[y].strip()).split(",")[4])

    return week_cases, hospital_cases, total_deaths


def covid_API_request(
    location: str = "Exeter", location_type: str = "ltla"
) -> list[dict]:
    """
    Description: Returns up-to-date COVID-19 Data from the Public Health England API as a list of dictionaries.

        Arguments:
            location (str): String value of Location for which COVID-19 data needs to requested.
            location_type (str): String value of Location Type, used to differentiate requests for national and local data.

        Returns:
            covid_data (list[dict]): List of dictionaries, each dictionary holds COVID-19 data of 1 day.
    """
    try:
        filters = ["areaType=" + location_type, "areaName=" + location]
        data_required = {
            "areaCode": "areaCode",
            "areaName": "areaName",
            "areaType": "areaType",
            "date": "date",
            "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
            "hospitalCases": "hospitalCases",
            "newCasesBySpecimenDate": "newCasesBySpecimenDate",
            "newCasesByPublishDate": "newCasesByPublishDate",
        }
        api = Cov19API(filters=filters, structure=data_required)
        covid_data = api.get_json()["data"]
    except exceptions.FailedRequestError:
        cov_logger.exception(
            " Unable to request data from COVID-19 API; Re-check entered arguments"
        )
    else:
        return covid_data


def process_covid_data(covid_data: list[dict]) -> list:
    """
    Description: Returns a list of processed and calculated data from the COVID-19 data.

        Arguments:
            covid_data (list[dict]): List of dictionaries, each dictionary holds COVID-19 data of 1 day.

        Returns:
            processed_data (list): List of calculated values of Total Covid Cases in the last week, Location, Location Type, Hospital Cases and Total Deaths.
    """
    try:
        weekly_cases = []
        processed_data = []
        for x in range(0, 7):
            y = x + 1
            if type(covid_data[x]["newCasesBySpecimenDate"]):
                x = y
                covid_cases = covid_data[x]["newCasesBySpecimenDate"]
                weekly_cases.append(covid_cases)

        weekly_cases_sum = sum(weekly_cases)
        location = covid_data[0]["areaName"]
        location_type = covid_data[0]["areaType"]

        processed_data.append(weekly_cases_sum)
        processed_data.append(location)
        processed_data.append(location_type)

        if location_type == "nation":
            x = 1
            hospital_cases = covid_data[0]["hospitalCases"]
            while type(hospital_cases) != int:
                hospital_cases = covid_data[x]["hospitalCases"]
                x = x + 1
            x = 1
            total_deaths = covid_data[0]["cumDailyNsoDeathsByDeathDate"]
            while type(total_deaths) != int:
                total_deaths = covid_data[x]["cumDailyNsoDeathsByDeathDate"]
                x = x + 1

        else:
            hospital_cases = ""
            total_deaths = ""

        processed_data.append(hospital_cases)
        processed_data.append(total_deaths)
    except TypeError:
        cov_logger.exception(
            "Unable to process COVID-data; Check whether covid_API_request() arguments are valid."
        )
    else:
        return processed_data


def update_covid_data() -> None:
    """
    Description: Updates global lists of Local and National COVID-19 data.

        Arguments:
            None

        Returns:
            None
    """
    global local_covid_data
    global nation_covid_data
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

    with open("manual_check_cov_data.txt", "a") as f:
        f.write("\n Covid-data updated at: " + str(datetime.now().time()))

    cov_logger.info(" Covid-data updated successfully")


def schedule_covid_updates(update_interval: str, update_name: str) -> None:
    """
    Description: Creates an event for the covid-data update

        Arguments:
            update_interval (str): String value of the time for the Scheduled Update, in 24 hour format.
            update_name (str): String value of the name of the Scheduled Update.

        Returns:
            None
    """
    s = sched.scheduler(time.time, time.sleep)
    event = s.enter(float(update_interval), 10, update_covid_data)
    s.run(event)


def time_difference(update_interval: str) -> float:
    """
    Description: Returns time difference between the Scheduled time from the argument and the current time in seconds.

        Arguments:
            update_interval (str): String value of the time for the scheduled update, in 24 hour format.

        Returns:
            time_diff_in_secs (float): Time difference in seconds.
    """
    update_time = datetime.strptime(update_interval, "%H:%M").time()
    dateTimeTarget = datetime.combine(date.today(), update_time)
    dateTimeNow = datetime.combine(date.today(), datetime.now().time())
    dateTimeDifference = dateTimeTarget - dateTimeNow

    if dateTimeTarget < dateTimeNow or dateTimeTarget == dateTimeNow:
        dateTimeDifference += timedelta(days=2)

    time_diff_in_secs = dateTimeDifference.total_seconds()

    return time_diff_in_secs


def plus_24_hours(update_interval: str) -> float:
    """
    Description: Calculates time difference for scheduling updates, and adds 24 hours to it; for repeats.

        Arguments:
            update_interval (str): String value of the time for the scheduled update, in 24 hour format.

        Returns:
            repeat_update_time (float): Time difference in seconds
    """
    time_in_seconds = time_difference(update_interval)
    repeat_update_time = time_in_seconds + 86400
    return repeat_update_time
