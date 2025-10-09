##################################
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv, requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
###################################
headers = {
    'Host': 'www.ndtv.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
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
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/140.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)

    URL1 = "https://www.ndtv.com/fuel-prices/petrol-price-in-all-state"
    URL2 = "https://www.ndtv.com/fuel-prices/diesel-price-in-all-state"

    driver.get(URL1)
    time.sleep(2)
    soup1 = BeautifulSoup(driver.page_source, "html.parser")
    results1 = soup1.find("table")
    if not results1:
        print("❌ Could not find Petrol table.")
        print(soup1.prettify()[:1000])
        return

    driver.get(URL2)
    time.sleep(2)
    soup2 = BeautifulSoup(driver.page_source, "html.parser")
    results2 = soup2.find("table")
    if not results2:
        print("❌ Could not find Diesel table.")
        print(soup2.prettify()[:1000])
        return

    state = []
    price_p = []
    change_p = []
    price_d = []
    change_d = []

    # Parse petrol
    for row in results1.find_all("tr")[1:]:
        tds = row.find_all("td")
        if len(tds) < 3:
            continue
        state.append(tds[0].text.strip())
        price_p.append(tds[1].text.strip())
        ch = tds[2]
        if ch.find(class_="chngBx up"):
            change_p.append("+ " + ch.text.strip())
        elif ch.find(class_="chngBx down"):
            change_p.append("- " + ch.text.strip())
        else:
            change_p.append("  " + ch.text.strip())

    # Parse diesel
    for row in results2.find_all("tr")[1:]:
        tds = row.find_all("td")
        if len(tds) < 3:
            continue
        price_d.append(tds[1].text.strip())
        ch = tds[2]
        if ch.find(class_="chngBx up"):
            change_d.append("+ " + ch.text.strip())
        elif ch.find(class_="chngBx down"):
            change_d.append("- " + ch.text.strip())
        else:
            change_d.append("  " + ch.text.strip())

    driver.quit()

    out1 = []
    out1.append(["State", "Price(P)", "Change(P)", "Price(D)", "Change(D)"])
    for (i, j, k, l, m) in zip(state, price_p, change_p, price_d, change_d):
        out1.append([i, j, k, l, m])

    with open("State.csv", "w", encoding="utf-8", newline="") as f:
        cswrite = csv.writer(f)
        cswrite.writerows(out1)

    print("✅ State-level data saved successfully.")

#######################################
if __name__ == '__main__':
    main()
    print("Updated Data!")
