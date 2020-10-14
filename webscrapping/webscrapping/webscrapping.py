import requests
import urllib3
from bs4 import BeautifulSoup
import pandas as pd
def scrapping(url):
   # url = 'https://www.sportaus.gov.au/grants_and_funding/grant_funding_report?sq_content_src=%2BdXJsPWh0dHBzJTNBJTJGJTJGbWF0cml4c3NpZnJlcG9ydC5hdXNwb3J0Lmdvdi5hdSUyRmdyYW50cyUzRnBhZ2UlM0QxJTI2c29ydE9yZGVyJTNEbmFtZV9hc2MlMjZyZWNpcGllbnRZZWFyJTNEMjAyMCUyNnBhZ2VTaXplJTNEMjAmYWxsPTE%3D'
    response = requests.get(url)
    soup = BeautifulSoup(response.text,'lxml')
    mytable = soup.find('table',{'class':'table'})

    links = mytable.findAll('a',text=True)
    link_data = mytable.findAll('td',text=True)
    titles = []
    datas = []
    filter_data = []
    for link in links:
        titles.append("".join(link))
    for linky in link_data:
        datas.append("".join(linky))
    datas = "".join(datas)
    for dat in datas.split('\r\n'):
        if dat.strip() != "":
            filter_data.append(dat.lstrip())
    df = pd.DataFrame(columns=titles)
    total_data = []
    i = 0
    j = 6
    dat = []
    while(i<len(filter_data)):
        if i<j:
            dat.append(filter_data[i])
        else:
            total_data.append(dat)
            j+=6
            i-=1
            dat = []
        i+=1
    df = pd.DataFrame(total_data,columns=titles)
    df.to_csv("sport_grant.csv")
    return df

