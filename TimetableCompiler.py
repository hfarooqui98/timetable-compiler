from collections import defaultdict as dd

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def fetchinfo(sub, sem):
    TIMETABLE = "https://sws.unimelb.edu.au/2017/"
    delay = 5

    # Opening the web page
    driver = webdriver.Chrome()
    driver.get(TIMETABLE)

    # Assigning window handle to assist with switching later
    window_before = driver.window_handles[0]

    # Selecting "find subject" option on web page
    subject_elem = driver.find_element_by_xpath('//*[@id="LinkBtn_modules"]')
    subject_elem.click()

    # Selecting which subject to search for and searching
    sbox = WebDriverWait(
        driver,
        delay).until(EC.presence_of_element_located((By.ID, 'tWildcard')))
    sbox.send_keys(sub)
    submit_box = WebDriverWait(
        driver,
        delay).until(EC.presence_of_element_located((By.ID, 'bWildcard')))
    submit_box.click()

    # Possible elements in subject box being assigned
    ss1 = 1
    ss2 = 1
    sss = 1
    try:
        subject_sem1 = driver.find_element_by_xpath(
            '//*[@id="dlObject"]/option[1]')
    except:
        ss1 = 0
    try:
        subject_sem2 = driver.find_element_by_xpath(
            '//*[@id="dlObject"]/option[2]')
    except:
        ss2 = 0
    try:
        subject_sum = driver.find_element_by_xpath(
            '//*[@id="dlObject"]/option[3]')
    except:
        sss = 0
    # Selecting time period
    if sem == 1:
        subject_sem1.click()
    # Subject offered in all three semesters
    if ss1 and ss2 and sss:
        if sem == 1:
            subject_sem1.click()
        elif sem == 2:
            subject_sem2.click()
        elif sem == 'S':
            subject_sum.click()
        else:
            print("ERROR! Incorrect semester type given.")
    # Subject offered in only one semester
    elif (not (sss)) and (not (ss2)):
        subject_sem1.click()
    # Subject offered in 2 semesters: SM1 and SM2
    elif ss1 and ss2:
        if (sem == 1):
            subject_sem1.click()
        elif (sem == 2):
            subject_sem2.click()
    # Subject offered in 2 semesters: SM1 and SUM
    elif ss1 and ss2:
        if (sem == 1):
            subject_sem1.click()
        elif (sem == 'S'):
            subject_sem2.click()
    # Subject offered in 2 semesters: SM2 and SUM
    elif ss1 and ss2:
        if (sem == 2):
            subject_sem1.click()
        elif (sem == 'S'):
            subject_sem2.click()
    # Selecting period and view type
    semester_1 = WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((By.XPATH,
                                        '//*[@id="lbWeeks"]/option[3]')))
    semester_2 = WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((By.XPATH,
                                        '//*[@id="lbWeeks"]/option[4]')))
    semester_sum = WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((By.XPATH,
                                        '//*[@id="lbWeeks"]/option[21]')))
    if sem == 1:
        semester_1.click()
    elif sem == 2:
        semester_2.click()
    elif sem == 'S':
        semester_sum.click()
    else:
        print("ERROR! Incorrect semester type given.")
    list_view = WebDriverWait(driver, delay).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="RadioType_1"]')))
    list_view.click()

    # Clicking view timetable
    view_tt = driver.find_element_by_xpath('//*[@id="bGetTimetable"]')
    view_tt.click()
    # switching tabs
    driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND +
                                                      Keys.NUMPAD2)
    window_after = driver.window_handles[1]
    driver.switch_to_window(window_after)

    # Extracting the HTMl source of the subject page
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    # Locating all elements with tag 'td' holding required subject info
    soup = soup.find_all('td')
    # compiling a list of all text to itterate through
    raw_data = []
    data = dd(list)
    for mem in soup:
        text = mem.get_text()
        raw_data.append(text)

    # Extracting into dictionary for use
    i = False
    current_pos = 0
    for mem in raw_data:
        if sub in mem:
            i = True
        if i:
            add = [
                raw_data[(current_pos + 2)], raw_data[(current_pos + 3)],
                raw_data[(current_pos + 4)]
            ]
            data[raw_data[(current_pos + 1)]].append(add)
            i = False
        current_pos += 1

    # Cleaning data
    # Code bellow creates a final dictionary with format:
    # {class_type: {'Day': [],...}, class_type: {'Day': [],...}}
    final_data = {}
    for mem in data.items():
        class_type = mem[0]
        days_lst = []
        for list_times in data[class_type]:
            day = list_times[0]
            if not (day in days_lst):
                days_lst.append(day)
        final_data[class_type] = {}
        for day in days_lst:
            final_data[class_type][day] = []
    # itterate through times to to add to final_data
    for mem in data.items():
        class_type = mem[0]
        for list_times in data[class_type]:
            day = list_times[0]
            start_time = list_times[1]
            end_time = list_times[2]
            add = (start_time, end_time)
            if not (add in final_data[class_type][day]):
                final_data[class_type][day].append(add)

    return final_data


def ttcompiler(subject_list):
    working_dict = {}
    len_sub = len(subject_list)
    print("Compiling Timetable(s) for ", len_sub, "subject(s)")
    for subject, sem in subject_list:
        working_dict[subject] = fetchinfo(subject, sem)
    print(working_dict)


sublist = [('INFO20003', 2), ('SWEN20003', 2), ('MAST20005', 2), ('HPSC20001',
                                                                  2)]
ttcompiler(sublist)
