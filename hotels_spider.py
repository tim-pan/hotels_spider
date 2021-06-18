#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue June 15 11:28:05 2021

@author: pao
"""
import csv
import time
import datetime
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.action_chains import ActionChains  
from selenium.webdriver.chrome.options import Options
import re
# the webpage we want
URL = "https://tw.hotels.com/"
# seraching conditions
KEY = "基隆"
CHECKIN = "2021-7-1"
CHECKOUT = "2021-7-3"
PEOPLE ={"1":[2, 0], "2":[1, 3], "3":[2, 2]} 
NUMBER_OUTCOME = 50
#means room1 has two adults and two children
#room2 has four adults

driver = None

def start_driver():
    global driver

    print("open webdriver...")
    driver = webdriver.Chrome("./chromedriver")
    driver.implicitly_wait(10)

def close_driver():
    global driver

    driver.quit()
    print("close webdriver...")

def get_page(url):
    global driver

    print("get webpage")
    driver.get(url)
    driver.implicitly_wait(10)

def get_diff_of_month(search_year, search_month):
    #take the number of months between the day you want and today
    now_y = datetime.date.today().year
    now_m = datetime.date.today().month

    return abs(search_year - now_y) * 12 + (search_month - now_m) + 1

def get_week_of_month(year, month, day):
    ############################################################
    # take the week of a date of in a month
    #
    # DEFAULT:--------------------------------------------------
    # the start of a week is monday
    # but here, in hotels.com, the start of a week is "sunday"
    #
    # IDEA:-----------------------------------------------------
    # calculate the week of a date in this year，and same , and 
    # do the same steps on the first of this month. Finally,
    # we just get the diff between this two numbers
    # but the DEFAULT will inflence the correctness of answer
    # so, if the day of a date is sunday, then we should add one 
    # on the week of the year.thus, we have "if" blocks below.
    # more detail please refer to the "pic_A" of the README.md
    ############################################################

    begin = int(datetime.date(year, month, 1).strftime("%W"))
    flag_begin = int(datetime.datetime(year, month, 1).strftime("%w"))
    
    end = int(datetime.date(year, month, day).strftime("%W"))
    flag_end = int(datetime.datetime(year, month, day).strftime("%w"))
    
    if (flag_begin == 0):
        begin += 1

    if (flag_end == 0):
        end += 1
    
    return end - begin + 1

def get_day(year, month, day):#find day of a date
    anyday = int(datetime.datetime(year, month, day).strftime("%w"))

    return anyday

def get_td(anyday):# same idea as get_week_of_month() above
    if anyday == 0:#if the day is sunday
        return 1
    else:# if the day is not sunday
        return int(anyday) + 1

def split_date(date):#split a date into year, month, and date
    ens = datetime.datetime.strptime(date, "%Y-%m-%d")

    return ens.year, ens.month, ens.day

def key_in_people(people):
    global driver

    guestInfButton = driver.find_element_by_css_selector('#main > div._3a4h66 > div._3-V-HY > div > form > div.bLAr9b._1cDU8I > div:nth-child(2) > button')
    driver.execute_script("arguments[0].click();", guestInfButton)

    num_room = len(list(people.keys()))
    addRoomButton = driver.find_element_by_xpath('//*[@id="modal-panel-oc-0"]/section/div/div[2]/button')

    while (num_room != 1):
        addRoomButton.click()
        num_room -= 1

    for room_i, room_guest in zip(people.keys(), people.values()):
        driver.implicitly_wait(10)
        #click adult then we can choose number of adult
        try:#//*[@id="modal-panel-oc-0"]/section/div[2]/div[1]/div[2]/div[2]/div/div/select
            adult = driver.find_element_by_xpath(f'//*[@id="modal-panel-oc-0"]/section/div/div[1]/div[{room_i}]/div[2]/div/div/select')
        except:
            print('12344')
            adult = driver.find_element_by_xpath(f'//*[@id="modal-panel-oc-0"]/section/div[2]/div[1]/div[{room_i}]/div[2]/div/div/select')
        #it would show a vertical list from 1 to ?? after adult.click()
        adult.click() 
        
        driver.implicitly_wait(3)
        #locate the number we want to choose
        try:
            option_adult = driver.find_element_by_xpath(f'//*[@id="modal-panel-oc-0"]/section/div/div[1]/div[{room_i}]/div[2]/div/div/select/option[{room_guest[0]}]')
        except:
            option_adult = driver.find_element_by_xpath(f'//*[@id="modal-panel-oc-0"]/section/div[2]/div[1]/div[{room_i}]/div[2]/div/div/select/option[{room_guest[0]}]')
        #choose an option in this vertical list
        option_adult.click()

        driver.implicitly_wait(3)
        # children is the same as adult
        try:
            children = driver.find_element_by_xpath(f'//*[@id="modal-panel-oc-0"]/section/div/div[1]/div[{room_i}]/div[3]/div[2]/div/select')
        except:
            children = driver.find_element_by_xpath(f'//*[@id="modal-panel-oc-0"]/section/div[2]/div[1]/div[{room_i}]/div[3]/div[2]/div/select')
        children.click()

        driver.implicitly_wait(3)

        try:
            option_children = driver.find_element_by_xpath(f'//*[@id="modal-panel-oc-0"]/section/div/div[1]/div[{room_i}]/div[3]/div[2]/div/select/option[{room_guest[1]+1}]')
        except:
            option_children = driver.find_element_by_xpath(f'//*[@id="modal-panel-oc-0"]/section/div[2]/div[1]/div[{room_i}]/div[3]/div[2]/div/select/option[{room_guest[1]+1}]')

        option_children.click()

        driver.implicitly_wait(3)
        #then we press "apply"
    applyButton = driver.find_element_by_xpath('//*[@id="modal-panel-oc-0"]/footer/button')
    applyButton.click()

    time.sleep(5)

def search_hotels(searchKey, checkInDate, checkOutDate, people):
    global driver
    ######################################################################
    # notice that: if a user want to key in the city he/she want to search
    #then he/she must CLICK the column which be filled by "e.g. Taipei" initially(<button> tag).
    #the page will generate an <input> tag after clicking the column
    #and this "colmun" is named "cityButton" in this file
    #and this "<input> tag" is named "cityEle" in this file
    ######################################################################
    #################################key in city##############################
    cityButton = driver.find_element_by_xpath('//*[@id="main"]/div[1]/div[2]/div/form/div[1]/button')

    cityButton.click()
    #cityEle is the object that generated 
    cityEle = driver.find_element_by_xpath('//*[@id="modal-panel-srs-0"]/header/div/form/fieldset/div/div/input')

    cityEle.send_keys(searchKey)
    cityEle.send_keys(Keys.ENTER)
    ################################key in datecheckin############################
    time.sleep(5)
    dateButton = driver.find_element_by_css_selector('#main > div._3a4h66 > div._3-V-HY > div > form > div.bLAr9b._1cDU8I > div:nth-child(1) > button')
    driver.execute_script("arguments[0].click();", dateButton)#i.e. dateButton.click()

    yearIn, monthIn, dayIn = split_date(checkInDate)
    yearOut, monthOut, dayOut = split_date(checkOutDate)

    in_li = get_diff_of_month(yearIn, monthIn)
    in_tr = get_week_of_month(yearIn, monthIn, dayIn)
    in_td = get_td(get_day(yearIn, monthIn, dayIn)) #cause hotels.com starts from sunday other tan monday

    driver.implicitly_wait(10)

    dateCheckIn = driver.find_element_by_css_selector(f'#modal-panel-dp-0 > section > div > div > ul > li:nth-child({in_li}) > div > table > tbody > tr:nth-child({in_tr}) > td:nth-child({in_td}) > button')
    driver.execute_script("arguments[0].click();", dateCheckIn)
    ################################key in datecheckout############################
    time.sleep(5)
    out_li = get_diff_of_month(yearOut, monthOut)
    out_tr = get_week_of_month(yearOut, monthOut, dayOut)
    out_td = get_td(get_day(yearOut, monthOut, dayOut)) #cause hotels.com starts from sunday other tan monday

    driver.implicitly_wait(10)

    dateCheckOut = driver.find_element_by_css_selector(f'#modal-panel-dp-0 > section > div > div > ul > li:nth-child({out_li}) > div > table > tbody > tr:nth-child({out_tr}) > td:nth-child({out_td}) > button')
    driver.execute_script("arguments[0].click();", dateCheckOut)
    #apply the dates you chose
    applyDateButton = driver.find_element_by_xpath('//*[@id="modal-panel-dp-0"]/footer/div/button')
    driver.execute_script("arguments[0].click();", applyDateButton)

    time.sleep(5)
    # fill in room information
    key_in_people(people)
    #search
    searchButton = driver.find_element_by_xpath('//*[@id="main"]/div[1]/div[2]/div/form/div[2]/div[3]/button')
    searchButton.click()

def get_hotels():
    i = 1
    inf = [['name', 'address', 'eva', 'star', 'price']]
    global driver
    #get the information we want
    while (i!=0):# use while to get all hotels in the "ul" tag
        li = []

        try:
            #get "name" information
            name = driver.find_element_by_css_selector(f'[id="{i}"]  > div > div._3NQzWW > div._15s9kr > section._2sPUhr > div > h2').text
            #get "address" information
            address = driver.find_element_by_xpath(f'//*[@id="{i}"]/div/div[2]/div[1]/section[1]/p').text
            #get "evaluation" from every hotel
            try:
                eva = driver.find_element_by_xpath(f'//*[@id="{i}"]/div/div[2]/div[1]/section[3]/span[1]').text
                forma = re.compile("[0-9]+[.][0-9]")# use simple to make strings in the same format
                eva = forma.search(eva)
                eva = eva.group()
            except:
                #some hotels have no evaluation
                eva = 'no evaluation'
            #get star of hotels 
            try:
                star = driver.find_element_by_xpath(f'//*[@id="{i}"]/div/div[2]/div[1]/section[1]/div/span').text
            except:#while some hotel may have no star
                star = 'no star'
            #get price
            price = driver.find_element_by_css_selector(f'[id="{i}"] > div > div._3NQzWW > div._2FhWhh > div._3cxHmh > div._3XSqn6 > span._2R4dw5').text
            price = re.sub("[^0-9]", "", price)#use regular exp to make price more beautiful

            li = [name, address, eva, star, price]

            inf.append(li)
            i += 1
        except:
            i = 0

    return inf

def get_search_outcome():#this ft is to scroll page down make page generate new hotels information staticly.
    #IDEA:
    #the number of "li" in "ul" tag will change after every "scroll"
    # since each li corresponds to a hotel, we set a conditional exp
    #to check if there are new hotels information after every scrol-
    #ling
    global driver

    while (True):
        ul = driver.find_element_by_xpath('//*[@id="main"]/div[2]/div/div/div[2]/section[2]/ul')
        lis = ul.find_elements_by_xpath('li')
        flag = len(lis)

        target = driver.find_element_by_xpath('//*[@id="main"]/div[2]/div/ul')
        driver.execute_script("arguments[0].scrollIntoView(false);", target)
        driver.implicitly_wait(10)
        time.sleep(10)

        ul = driver.find_element_by_xpath('//*[@id="main"]/div[2]/div/div/div[2]/section[2]/ul')
        lis = ul.find_elements_by_xpath('li')
        
        if (len(lis) == flag) or (len(lis) > 50):
            break

def save_to_csv(name, data):
    print(f"save data to file: {name}")
    with open(name, 'w', encoding = 'utf') as fp:
        csv.writer(fp).writerows(data)

if __name__ == "__main__":
    start_driver()
    get_page(URL)

    search_hotels(KEY, CHECKIN, CHECKOUT, PEOPLE)
    get_search_outcome()

    data = get_hotels()
    save_to_csv("hotels_information.csv", data)
    close_driver()




















