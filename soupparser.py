from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, Comment
import bs4
import ssl
import operator
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os
import json
from EditDistance import Trie
from selenium.webdriver.common.keys import Keys
import re

classnames = {}
def visit(node):
    if isinstance(node, bs4.element.Tag):
        if(node.get('class')):
            #print(type(node), 'tag:', node.get('class'))
            classname_list = node.get('class')
            strval = ','.join(classname_list)
            if(strval in classnames):
                classnames[strval] += 1
            else:
                classnames[strval] = 1

    elif isinstance(node, bs4.element.NavigableString):
        #print("string", repr(node.string))
        c = 1
    else:
        #print("uknown", 'UNKNOWN')
        c = 2

def dfs(bs):
    visit(bs)
    for child in bs.recursiveChildGenerator():
        visit(child)
#






context = ssl._create_unverified_context()
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}

city_path = 'city_coding.json'
airlines_path = 'data_airlines.json'
status_path = 'iata_status.json'

city_names = []
airline_names = []
status_names = []

with open (os.path.join(os.getcwd(), city_path)) as f:
    city_names = json.load(f)
with open(os.path.join(os.getcwd(), airlines_path)) as f:
    airline_names = json.load(f)
with open(os.path.join(os.getcwd(), status_path)) as f:
    status_names = json.load(f)

city_trie = Trie(city_names)
airline_trie = Trie(airline_names)
status_trie = Trie(status_names)

# req = Request('https://www.bud.hu/en/arrivals', headers=headers)

driver = webdriver.Chrome(ChromeDriverManager().install())
#https://www.bud.hu/en/arrivals
#https://www.heathrow.com/arrivals
#https://www.amman-airport.com/queen-alia-arrivals?tp=6
#https://www.sharjahairport.ae/en/traveller/flight-information/passenger-arrivals/
website_url = 'https://www.amman-airport.com/queen-alia-arrivals?tp=6'
driver.get(website_url)
html = driver.find_element_by_tag_name('html')

#creating a scroll like event for websites which load data on scroll
count = 50
while(count >0):
    html.send_keys(Keys.DOWN)
    count = count-1
soup = BeautifulSoup(driver.page_source, 'html.parser')
comments = soup.findAll(text=lambda text:isinstance(text, Comment))
[comment.extract() for comment in comments]
#print(driver.page_source)
driver.quit()
htmlcontents = soup.body
dfs(htmlcontents)

#no logic for selecting 30. Picked top 30
sorted_x = sorted(classnames.items(), key=operator.itemgetter(1), reverse=True)
print(sorted_x)
i = 0
finalclname = []
maxpercentage = 0



def getTextFromElement(child):
    text = child.find(text=True, recursive=False)
    if(text):
        text = text.strip()
    if(not text):
        children = child.findChildren(recursive=False)
        if(children):
            text = getTextFromElement(children[0])
        # text = getFirstChildText(child).strip()
    return text

def getAllTextFromElement(child, resArray):
    text = child.find(text=True, recursive=False)
    if(text):
        text = text.strip()
    if(not text):
        children = child.findChildren(recursive=False)
        for child in children:
            text = getTextFromElement(child)
            if(text):
                resArray.append(text)
    else:
        resArray.append(text)




print("Started scanning the html tags from source code to find points of interest. This might take a while. Sit back!!")
#Loop through most repeated css classes and get the elements
for index,(clname,num) in enumerate(sorted_x):
    print("Scanning number {} from top repeating elements".format(index))
    i = i+1
    clslist = clname.split(",")
    elements = soup.findAll(lambda tag:tag.get('class') == clslist)

    if(i == 21):
        print("catch")
    percentage = 0
    #Get text within these elements and store them in alist
    for element in elements:
        texts = []
        children = element.findChildren(recursive=False)
        for child in children:
            text = getTextFromElement(child)
            texts.append(text)
        #print(texts)
        elementHasCity = False
        elementHasAirLine = False
        elementHasStatus = False

        for text in texts:

            if (text and len(text) > 2):
                try:
                    text = re.sub('[^0-9a-zA-Z:, ,-]+', '', text)
                except:
                    print(text)
                #the text inside these elements should have atleast one city name, one airline name and one status value
                res1 = city_trie.search(text.lower(), 0.4)
                res2 = airline_trie.search(text.lower(), 0.4)

                res3 = status_trie.search(text.lower(), 0.4)

                if (len(res1) > 0):
                    elementHasCity = True
                    res4 = res1
                if (len(res2) > 0):
                    elementHasAirLine = True
                    res5 = res2
                if (len(res3) > 0):
                    elementHasStatus = True
                    res6 = res3
        if (elementHasCity):
            percentage += 1/3
        if (elementHasAirLine):
            percentage += 1/3
        if (elementHasStatus):
            percentage += 1/3
    #Percentage of elements having the  highest flight information will obviously be the flight card.It can be div or table doesn't matter. Store that class name or any other necessary attribute for further use

    if (len(elements) > 0):
        percentage = (percentage / len(elements)) * 100
    if(percentage > maxpercentage):
        maxpercentage = percentage
        finalclname = clslist
        print("Number {} element's confidence percentage is {}".format(index, maxpercentage))
        print("Number {} element's class name is {}".format(index,finalclname))
    #if percentage is 100 then we have found the class name no point in traversing further
    if(maxpercentage == 100):
        break
print(" The class names of interest for this url is {} ".format(finalclname))
print("This is a one time procedure . Use above value for continuous scraping unless any change in page source")
print("<--- Extracted flight detail values are as follows associate them yourself --->")
elements = soup.findAll(lambda tag:tag.get('class') == finalclname)
for element in elements:
    texts = []
    children = element.findChildren(recursive=False)
    for child in children:
        getAllTextFromElement(child, texts)
    print(texts)





