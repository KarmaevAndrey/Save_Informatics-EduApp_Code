import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

delay = 3


def get_urls_to_lessons_of_day(driver, url="https://my.informatics.ru/pupil/calendar/"):
    """
    Получаем информацию о занятиях на недели
    :param driver: драйвер
    :param url: ссылка на calendar с нужной датой (https://my.informatics.ru/pupil/calendar/?date=2023-10-01)
    :return:
    """
    global delay
    driver.get(url)
    time.sleep(delay)
    urls = {}
    count_lessons = len(driver.find_elements(By.CLASS_NAME, "panel-row-md"))
    for i in range(1, count_lessons + 1):
        xpath_href = f"/html/body/div/div/div[3]/div/div[2]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div/div[2]/div[{i}]/div/div/div[2]/div[2]/div[3]/div[2]/a"
        href_item = driver.find_element(By.XPATH, xpath_href)

        xpath_main_name = f"/html/body/div[1]/div/div[3]/div/div[2]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div/div[2]/div[{i}]/div/div/div[1]/div/div[1]"
        main_name_item = driver.find_element(By.XPATH, xpath_main_name).text

        xpath_topic = f"/html/body/div/div/div[3]/div/div[2]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div/div[2]/div[{i}]/div/div/div[2]/div[1]/div[2]/div"
        topic_item = driver.find_element(By.XPATH, xpath_topic).text

        xpath_date = f"/html/body/div/div/div[3]/div/div[2]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div/div[1]/div"
        date_item = driver.find_element(By.XPATH, xpath_date).text

        urls[get_folder_name(main_name_item, topic_item, date_item)] = href_item.get_attribute("href")
    return urls


def get_urls_from_task_lessons(driver, lesson_url):
    """
    Получаем ссылки на занятия для копирования кода
    :param driver: драйвер
    :param lesson_url: ссылка на занятие (https://my.informatics.ru/pupil/calendar/612772/)
    :return:
    """
    global delay

    driver.get(lesson_url)
    urls = []
    time.sleep(delay)
    all_urls = driver.find_elements(By.CLASS_NAME, "classes-navigation-step-element")
    for item in all_urls:
        if "/" in item.text:
            urls.append(item.get_attribute("href"))
    return urls


def some_str_to_code(input_str) -> str:
    """
    Возвращает код с занятия
    :param input_str: Код с синими символами
    :return:
    """
    lines = input_str.split('\n')
    filtered_lines = [line for line in lines if not (line.strip() == '' or line.strip().isdigit())]
    result_text = '\n'.join(filtered_lines)
    return result_text


def get_folder_name(main_name, topic, date):
    """
    Получаем имя для папки
    :param main_name: имя курса (Пром. прогр-е: теоретический курс)
    :param topic: тема (Знакомство с git. Понятие коммита)
    :param date: дата (воскресенье, 08 октября)
    :return: 0_08_10_Знакомство_с_git_Понятие_коммита
    """
    folder_name = ''
    if main_name == "Пром. прогр-е: теоретический курс":
        folder_name += '0'
    elif main_name == "Пром. прогр-е: практ. курс":
        folder_name += '1'
    topic = topic.replace(".", "")
    topic = topic.replace(",", "")
    topic = topic.replace("!", "")
    topic = topic.replace("\n", "")
    date = date.split(",")[1]
    date = date.replace("января", "01")
    date = date.replace("февраля", "02")
    date = date.replace("марта", "03")
    date = date.replace("апреля", "04")
    date = date.replace("мая", "05")
    date = date.replace("июня", "06")
    date = date.replace("июля", "07")
    date = date.replace("августа", "08")
    date = date.replace("сентября", "09")
    date = date.replace("октября", "10")
    date = date.replace("ноября", "11")
    date = date.replace("декабря", "12")
    folder_name += date
    folder_name += "_"
    folder_name += topic
    folder_name = folder_name.replace(" ", "_")
    return folder_name


def get_all_code_from_lessons(driver, urls_from_lesson):
    """
    Получаем имя и код задания
    :param driver: драйвер
    :param urls_from_lesson: ссылки на занятия
    :return:
    """
    global delay

    task_code = {}
    for url in urls_from_lesson:
        try:
            driver.get(url + "/detail/online/show/")
            time.sleep(delay)
            name_task = driver.find_element(By.CLASS_NAME, "classes_navigation_title").text
            some_str = driver.find_element(By.CLASS_NAME, "CodeMirror-lines").text
            code = some_str_to_code(some_str)
            task_code[name_task] = code
        except Exception:
            # Это может быть тест без кода
            print(f"Couldn't save the code from the page: {url}/detail/online/show/")
    return task_code


def registration_account(driver):
    global delay
    if "session" in os.listdir():
        driver.get("https://my.informatics.ru/accounts/login/#/")
        for cookie in pickle.load(open('session', 'rb')):
            driver.add_cookie(cookie)
        driver.refresh()
        print("Вы используйте cookies для регестрации")
    else:
        print(
            "Давайте зарегистрируемся, у вас есть 60 секунд, чтобы ввести свой пароль и логин и нажить на кнопку войти...")
        time.sleep(7)
        driver.get("https://my.informatics.ru/accounts/login/#/")
        time.sleep(60)
        pickle.dump(driver.get_cookies(), open('session', 'wb'))
        print("Cookie сохранились, регистрироваться больше не нужно.")
    return driver


def main(main_url):
    global delay
    main_url = "https://my.informatics.ru/pupil/calendar/?date=2023-10-01" if main_url == "" else main_url
    base_directory = os.getcwd()
    browser = "Chrome"
    if browser == "Firefox":
        driver = webdriver.Firefox()
    elif browser == "Chrome":
        driver = webdriver.Chrome()
    else:
        raise "Укажите браузер"


    driver = registration_account(driver)
    all_code = {}
    lessons = get_urls_to_lessons_of_day(driver, main_url)
    delay = 3
    print(f"Куда буду сохранять файлы: {base_directory}")
    print(f"Задержка при загрузке страниц: {delay} секунды")
    print("Какие занятия буду сохранять: ")
    for item in lessons.keys():
        print(item, end=' ')
    for folder in lessons:
        urls_from_lesson = get_urls_from_task_lessons(driver, lessons[folder])
        c = get_all_code_from_lessons(driver, urls_from_lesson)
        all_code[folder] = c
    for folder, code_data in all_code.items():
        folder_path = os.path.join(base_directory, folder)
        os.makedirs(folder_path, exist_ok=True)
        for filename, code in code_data.items():
            file_path = os.path.join(folder_path, f"{filename}.py")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(code)
    driver.close()


if __name__ == '__main__':
    main_url = input(
        "Напишите ссылку из календаря для парсинга занятий или нажмие enter, последнего (https://my.informatics.ru/pupil/calendar):\n")
    main(main_url)
