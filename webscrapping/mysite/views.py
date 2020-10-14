from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
# Create your views here.
def index(request):
    if(request.method == 'GET'):
        tables =[]
        context_dic = {"tables":tables}
        return render(request,"mysite.html",context_dic)
    elif(request.method == 'POST'):
        countTable,header,datass,pdf,docx = scrapping(request.POST['url'])
        li = []
        for i in range(countTable):
            li.append('Table_'+str(i+1))
        tables = []
        for i in range(len(li)):
            table = []
            table.append(li[i])
            table.append(header[i])
            table.append(datass[i])
            tables.append(table)
        pdfs,docxs = [],[]
        for pd in pdf:
            indexEnd = pd.find('.pdf')
            indexStart = pd.rfind('/')
            pdfs.append([pd[indexStart+1:indexEnd],pd])
        for do in docx:
            indexEnd = do.find('.docx')
            indexStart = do.rfind('/')
            docxs.append([do[indexStart+1:indexEnd],do])
        context_dic = {"tables":tables,"pdf":pdfs,"docx":docxs}
    return render(request,"mysite.html",context_dic)

def scrapping(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text,'lxml')
    body = soup.find('body')
    links = [url]
    try:
        links.extend(find_links_from_body(body))
    except:
        print("No href found")
    tables = find_all_tables(body)
    count = 1
    headers,datass = [],[]
    for table in tables:
        header,datas = convert_header_data(url,table,count)
        headers.append(header)
        datass.append(datas)
        count+=1
    downloadable_file_Links = []
    for link in links:
        li = []
        if link.startswith('https') or link.startswith('http'):
            if(('mailto' not in link) and ('Email' not in link) and ('titan' not in link)):
                li = findFileLinks(link)
            downloadable_file_Links.extend(li)
    pdf,docx = download_pdf(downloadable_file_Links)
    return count-1,headers,datass,pdf,docx
def find_links_from_body(body):
    links = []
    aTag = body.findAll('a')
    for i in aTag:
        href = i['href']
        links.append(href)
    return links

def find_all_tables(body):
    tables = body.findAll('table')
    return tables

def filter_data(li):
    for i in range(len(li)):
        st = li[i]
        for j in st.split('\r\n'):
             if j.lstrip() != "":
                 li[i] = j

        st = li[i]
        for j in st.split('\r'):
             if j.strip() != "":
                 li[i] = j

        st = li[i]
        for j in st.split('\n'):
             if j.strip() != "":
                 li[i] = j

        st = li[i]
        li[i] = st.strip()
    return li
def convert_header_data(url,table,count):
    first_tr = table.find('tr')
    childNode = first_tr.findChildren()
    topic,tagged = [],[]
    if(str(childNode[0])[1:3]=='td'):
        tagged = first_tr.findAll('td')
    else:
        tagged = first_tr.findAll('th')
    for tag in tagged:
        topic.append(tag.text)
    other_tr = table.findAll('tr')
    pagination_url = paginationUrl(url)
    if(pagination_url):
        for url in pagination_url:
            response = requests.get(url)
            soup = BeautifulSoup(response.text,'lxml')
            body = soup.find('body')
            tabless = body.find('table')
            if(tabless):
                trs = tabless.findAll('tr')
                del trs[0]
                other_tr.extend(trs)

    del other_tr[0]
    data_set =[]
    for other in other_tr:
        dat = []
        datas = other.findAll('td')
        for data in datas:
            if(data.text):
                dat.append(data.text)
            else:
                img = data.find('img')
                dat.append(img['src'])
        data_set.append(dat)
    filter_topic = filter_data(topic)
    filter_datas = []
    # for dat in data_set:
    #     filter_datas.append(filter_data(dat))
    return filter_topic,data_set


def findFileLinks(link):
    response = requests.get(link)
    soupplus = BeautifulSoup(response.text,'lxml')
    bodies = soupplus.find('body')
    aTag=[]
    try:
        aTag = bodies.findAll('a')
    except:
        print("no link")
    linky = []
    for at in aTag:
        try:
            href = ''
            try:
                href = at['href']
            except:
                break
            end = len(href)
            start = end - 3
            if(href[start:end]=='pdf'):
                linky.append(href)
            elif(href[start-1:end]=='docx'):
                linky.append(href)
        except:
            continue
    return linky

def download_pdf(links):
    pdf,docx = [],[]
    for link in links:
        end = len(link)
        start = end - 3
        if(link[start:end]=='pdf'):
            pdf.append(link)
        elif(link[start-1:end]=='docx'):
            docx.append(link)
    return pdf,docx

def paginationUrl(url):
    urlLinks = []
    status = False
    count = 1
    while(not status and count<=20):
        count+=1
        try:
            link = page_next_link(url)
            if(link):
                urlLinks.append(link)
                url = link
            else:
                status = True
        except:
            break
    return urlLinks

def page_next_link(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text,'lxml')
    mytable = soup.find('table')
    mypages = soup.find('ul',{'class':'pagination'})
    next = mypages.find('a',{'rel':'next'})
    return next['href']
