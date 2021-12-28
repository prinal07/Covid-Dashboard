import time
from covid_data_handler import (
    parse_csv_data,
    plus_24_hours,
    process_covid_csv_data,
    covid_API_request,
    schedule_covid_updates,
    time_difference,
    update_covid_data,
)
from covid_news_handling import (
    live_news_adding,
    news_API_request,
    next_news_page,
    schedule_news_update,
    update_news,
)


def test_parse_csv_data():
    data = parse_csv_data("nation_2021-10-28.csv")
    assert len(data) == 639


def test_process_covid_csv_data():
    last7days_cases, current_hospital_cases, total_deaths = process_covid_csv_data(
        parse_csv_data("nation_2021-10-28.csv")
    )
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544


def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, list)


def test_update_covid_data():
    update_covid_data()


def test_schedule_covid_updates():
    schedule_covid_updates(update_interval=10, update_name="update test")


def test_time_difference():
    first_time = time_difference("12:00")
    time.sleep(1)
    second_time = time_difference("12:00")
    assert first_time != second_time
    assert (first_time - second_time) < 2


def test_plus_24_hours():
    time1 = plus_24_hours("12:00")
    time.sleep(0.5)
    time2 = plus_24_hours("12:00")
    assert time1 != time2
    assert (time1 - time2) < 1


def test_news_API_request():
    news_API_request()
    assert news_API_request("Covid COVID-19 coronavirus") == news_API_request()


def test_next_news_page():
    news_list = news_API_request()
    next_news_page(news_list, 1)
    next_list, next_page_number = next_news_page(news_list, 1)
    assert (news_list, 1) != (next_list, next_page_number)


def test_live_news_adding():
    news_list = news_API_request()
    remaining_list = ["1", "2", "3", "4", "5"]
    assert live_news_adding(news_list, 1, remaining_list)


def test_schedule_news_update():
    schedule_news_update(update_interval=5, update_name="news update test")


def test_update_news():
    update_news()


if __name__ == "__main__":
    test_parse_csv_data()
    test_process_covid_csv_data()
    test_covid_API_request()
    test_update_covid_data()
    test_schedule_covid_updates()
    test_time_difference()
    test_plus_24_hours()

    test_news_API_request()
    test_next_news_page()
    test_live_news_adding()
    test_schedule_news_update()
    test_update_news()

    print("Passed all of them!")
