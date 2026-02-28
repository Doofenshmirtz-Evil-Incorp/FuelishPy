##################################

import requests
import csv
from bs4 import BeautifulSoup
import concurrent.futures
###################################
headers = {
    'Host': 'www.ndtv.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/147.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'DNT': '1',
    'Sec-GPC': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'TE': 'trailers'
}
def get_page(st,url):
    resp = requests.get(url=url, headers = headers)
    print(st)
    return {st:resp.content,}

def asyncget(urls):
    with concurrent.futures.ThreadPoolExecutor() as executor:

        futures = []
        result={}
        for i,j in zip(list(urls.keys()),list(urls.values())):
            futures.append(executor.submit(get_page, st=i,url=j))

        for future in concurrent.futures.as_completed(futures):
            result.update(future.result())
    return result

def main():
    
    URL1 = "https://www.ndtv.com/fuel-prices/petrol-price-in-all-state"
    page1 = requests.get(URL1, headers = headers)
    URL2 = "https://www.ndtv.com/fuel-prices/diesel-price-in-all-state"
    page2 = requests.get(URL2, headers = headers)

    #print(page.text)
    soup1 = BeautifulSoup(page1.content, "html.parser")
    results1=soup1.find(id="myID")

    soup2 = BeautifulSoup(page2.content, "html.parser")
    results2=soup2.find(id="myID")

    #create lists for each parameters
    state = []
    city =[]
    price_p = []
    change_p = []
    price_d = []
    change_d = []
    cprice_p = []
    cchange_p = []
    cprice_d = []
    cchange_d = []

    x = 1

#####################################

#extracting all elements under td tag
    for SData_P in results1.find_all("td"):
        match (x%3):
            case 1:
                state.append(SData_P.text)
            case 2:
                price_p.append(SData_P.text)
            case 0:
                if(SData_P.find(class_="chngBx up")):
                    change_p.append("- "+SData_P.text)
                elif(SData_P.find(class_="chngBx down")):
                    change_p.append("+ "+SData_P.text)
                else:
                    change_p.append("  "+SData_P.text)
        x+=1
    x=1
    for SData_D in results2.find_all("td"):
        match (x%3):
            case 2:
                price_d.append(SData_D.text)
            case 0:
                if(SData_D.find(class_="chngBx up")):
                    change_d.append("- "+SData_D.text)
                elif(SData_D.find(class_="chngBx down")):
                    change_d.append("+ "+SData_D.text)
                else:
                    change_d.append("  "+SData_D.text)
        x+=1
    x=1
    ses = requests.Session()
    lstp={}
    lstd={}
    for s in state:
        lstp[s]=("https://www.ndtv.com/fuel-prices/petrol-price-in-"+s.replace(" ","-")+"-state")
        lstd[s]=("https://www.ndtv.com/fuel-prices/diesel-price-in-"+s.replace(" ","-")+"-state")
    lstp=asyncget(lstp)
    lstd=asyncget(lstd)
    keyp=list(lstp.keys())
    keyp.sort()
    keyd=list(lstd.keys())
    keyd.sort()
    lstp = {i: lstp[i] for i in keyp}
    lstd = {i: lstd[i] for i in keyd}
    try:
        for i,j,s in zip(list(lstp.values()),list(lstd.values()),state):
            print("csv-",s)
            city=[]
            cprice_p = []
            cchange_p = []
            cprice_d = []
            cchange_d = []
            soup3 = BeautifulSoup(i, "html.parser")
            results3=soup3.find(id="myID")
            soup4 = BeautifulSoup(j, "html.parser")
            results4=soup4.find(id="myID") 
            for CData_P in results3.find_all("td"):
                match (x%3):
                    case 1:
                        city.append(CData_P.text)
                    case 2:
                        cprice_p.append(CData_P.text)
                    case 0:
                        if(CData_P.find(class_="chngBx up")):
                            cchange_p.append("- "+CData_P.text)
                        elif(CData_P.find(class_="chngBx down")):
                            cchange_p.append("+ "+CData_P.text)
                        else:
                            cchange_p.append("  "+CData_P.text)
                x+=1
            x=1
            for CData_D in results4.find_all("td"):
                match (x%3):
                    case 2:
                        cprice_d.append(CData_D.text)
                    case 0:
                        if(CData_D.find(class_="chngBx up")):
                            cchange_d.append("- "+CData_D.text)
                        elif(CData_D.find(class_="chngBx down")):
                            cchange_d.append("+ "+CData_D.text)
                        else:
                            cchange_d.append("  "+CData_D.text)
                x+=1
            out2=[]
            out2.append(["City","Price(P)","Change(P)","Price(D)","Change(D)"])
            for (i,j,k,l,m) in zip(city,cprice_p,cchange_p,cprice_d,cchange_d):
                list2=[i,j,k,l,m]
                out2.append(list2)
            f=open("./assets/"+s+".csv","w",encoding="utf-8")
            cswrite=csv.writer(f)
            cswrite.writerows(out2)
            f.close()
    except:
        print("Re-run")
        main()
        
#####################################

    out1=[]
    out1.append(["State","Price(P)","Change(P)","Price(D)","Change(D)"])
    for (i,j,k,l,m) in zip(state,price_p,change_p,price_d,change_d):
        list1=[i,j,k,l,m]
        out1.append(list1)
    #tablemaker(out)

    # out2=[]
    # out2.append(["City","Price(P)","Change(P)","Price(D)","Change(D)"])
    # for (i,j,k,l,m) in zip(city,cprice_p,cchange_p,cprice_d,cchange_d):
    #     list2=[i,j,k,l,m]
    #     out2.append(list2)
    #tablemaker(out)

######################################

    f=open("State.csv","w",encoding="utf-8")

    cswrite=csv.writer(f)
    cswrite.writerows(out1)
    f.close()

    # f=open("City.csv","w",encoding="utf-8")

    # cswrite=csv.writer(f)
    # cswrite.writerows(out2)
    # f.close()

#######################################
if __name__ == '__main__':
    main()
    print("Updated Data!")
