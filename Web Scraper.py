#import and download the necessary tools
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import csv
import pandas as pd
import nltk
nltk.download('stopwords')
from nltk.tokenize import word_tokenize

#input csv file with company names to be searched for contracts
GovtCon = open('file.csv', 'r', encoding='utf8')
reportList = []
#reads csv and converts to pandas dataframe
with open('file.csv', newline='') as termReport:
    reportReader=csv.reader(termReport)
    for termReport in reportReader:
        reportList.append(termReport)
#locate vendor names column and clean dataframe
dfReport = pd.DataFrame(reportList)
dfVendor = dfReport.loc[:,[6]]
dfVendor.drop(index=dfVendor.index[0], axis=0, inplace=True)
dfVendor[6].replace('', "NULL", inplace=True)
vendorList = list(dfVendor[6])

#use chromedriver to access web page
browser = webdriver.Chrome('chromedriver.exe')
browser.get('https://facts.fldfs.com/Search/ContractSearch.aspx')

#this list contains all vendors with contracts with the state of florida
matchesList = []

#define stopwords you wants cleaned as they may differ from the legal vendor name, and you don't need them to find vendor
newSw = [',','llc','.','inc','(',')','pllc','l.l.c','co']

#start loop for each vendor on the vendorsList
for i in vendorList:
    #lowercase vendor name, separate and tokenize each word, eliminate stopwords
    client = i.lower()
    clientNLP= word_tokenize(client)
    filteredClient = [w for w in clientNLP if not w in newSw]

    #if useless text after a particular word (like dba or / in my case), input particular word
    if 'dba' in filteredClient:
        index = filteredClient.index('dba')
        del filteredClient[index:]
    if '/' in filteredClient:
        index = filteredClient.index('/')
        del filteredClient[index:]

    #join tokenized and filtered vendor names
    client = ' '.join([str(word) for word in filteredClient])

    #get each new page source after each loop run
    source = browser.page_source
    #soup the page source
    soup = BeautifulSoup(source, 'lxml')

    #use selenium to find the text bar and send tokenized client name
    searchBar = browser.find_element_by_id('PC_txtVendorName')
    searchBar.send_keys(client)
    #find search button id and send a click
    searchBttn = browser.find_element_by_id('PC_btnSearch')
    searchBttn.click()

    #change waiting time depending on internet speed
    time.sleep(4)
    #go down the page to look for results
    browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')

    #get new page source with results
    source = browser.page_source
    soup = BeautifulSoup(source, 'lxml')

    #if no results, does not append, else, appends to matchesList
    if soup.find('div', {'class': 'grid'}).get_text().strip() == 'No results found for the selected criteria. Please refine your search.':
        print(client)
        print('no\n')
    else:
        matchesList.append(client)
        print(client)
        print('yes\n')

    #clear searchbar for next client
    searchBar = browser.find_element_by_id('PC_txtVendorName')
    searchBar.clear()

#print all matches, or add to a file
print(matchesList)

#done!!

