##################################
# fuelish.py — NDTV Fuel Price Scraper
# -------------------------------------
# Saves:
#   - State-level data -> State.csv
#   - District-level data -> root/assets/<State>.csv
##################################

import csv
import os
import re
import json
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

###################################
# Utility Functions
###################################

def clean_state_name(name: str) -> str:
    """Return a clean, URL-friendly state name."""
    return re.sub(r'[\s&]+', '-', name.strip().lower())

def get_driver():
    """Initialize and return a headless Chrome driver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/140.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

###################################
# Scraping Functions
###################################

def wait_for_table(driver, timeout=10):
    """Wait for a table to appear on the page."""
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "table")))    

def scrape_state_level(driver):
    """Scrape state-level petrol and diesel prices."""
    URL_PETROL = "https://www.ndtv.com/fuel-prices/petrol-price-in-all-state"
    URL_DIESEL = "https://www.ndtv.com/fuel-prices/diesel-price-in-all-state"  
    driver.get(URL_PETROL)
    wait_for_table(driver)
    soup1 = BeautifulSoup(driver.page_source, "html.parser")
    table_p = soup1.find("table")

    driver.get(URL_DIESEL)
    wait_for_table(driver)
    soup2 = BeautifulSoup(driver.page_source, "html.parser")
    table_d = soup2.find("table")  

    if not table_p or not table_d:
        print("❌ Could not find one of the state-level tables.")
        return []

    state, price_p, change_p, price_d, change_d = [], [], [], [], []

    for row in table_p.find_all("tr")[1:]:
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

    for row in table_d.find_all("tr")[1:]:
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

    out = [["State", "Price(P)", "Change(P)", "Price(D)", "Change(D)"]]
    for (i, j, k, l, m) in zip(state, price_p, change_p, price_d, change_d):
        out.append([i, j, k, l, m])

    with open("State.csv", "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(out)

    print("✅ State-level data saved successfully as State.csv")
    return state                                       

def scrape_all_districts(driver):
    """Scrape all districts from the NDTV city-level page."""
    URL_PETROL = "https://www.ndtv.com/fuel-prices/petrol-price-in-all-city"
    URL_DIESEL = "https://www.ndtv.com/fuel-prices/diesel-price-in-all-city"
    driver.get(URL_PETROL)
    wait_for_table(driver)
    soup1 = BeautifulSoup(driver.page_source, "html.parser")
    table_p = soup1.find("table")

    driver.get(URL_DIESEL)
    wait_for_table(driver)
    soup2 = BeautifulSoup(driver.page_source, "html.parser")
    table_d = soup2.find("table")

    if not table_p or not table_d:
        print("❌ Could not find district table.")
        return []
    
    data = []
    district, price_p, change_p, price_d, change_d = [], [], [], [], []

    for row in table_p.find_all("tr")[1:]:
        tds = row.find_all("td")
        if len(tds) < 3:
            continue
        district.append(tds[0].text.strip())
        price_p.append(tds[1].text.strip())
        ch = tds[2]
        if ch.find(class_="chngBx up"):
            change_p.append("+ " + ch.text.strip())
        elif ch.find(class_="chngBx down"):
            change_p.append("- " + ch.text.strip())
        else:
            change_p.append("  " + ch.text.strip())
    
    for row in table_d.find_all("tr")[1:]:
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

    # out = [["District", "Price(P)", "Change(P)", "Price(D)", "Change(D)"]]
    out = []
    for (i, j, k, l, m) in zip(district, price_p, change_p, price_d, change_d):
        out.append([i, j, k, l, m])
    return out

###################################
# Main Execution
###################################

def save_state_districts(state_name, districts):
    """Save districts belonging to a single state."""
    assets_path = "assets"
    os.makedirs(assets_path, exist_ok=True)
    file_path = os.path.join(assets_path, f"{state_name}.csv")
    print(file_path)
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["District", "Price(P)", "Change(P)", "Price(D)", "Change(D)"])
        writer.writerows(districts)
    print(f"✅ Saved district-level data for {state_name} ({len(districts)} entries)")


def main():

    driver = get_driver()
    states = scrape_state_level(driver)
    print("\n📍 Starting district-level scraping...")
    districts = scrape_all_districts(driver)
    driver.quit()

    if not districts:
        print("⚠️ No district data scraped.")
        return

    with open(file=os.path.join("src","district_state_map.json"), mode="r", encoding="utf-8") as f:
        district_to_state = json.load(f)
        print(f"Loaded map json")

    # Group districts by state
    state_groups = {}
    for district, price_p, change_p, price_d, change_d in districts:
        state_name = district_to_state.get(district)
        if not state_name:
            print(f"⚠️ State not found for district: {district}")
            continue
        state_groups.setdefault(state_name, []).append([district, price_p, change_p, price_d, change_d])
        # print(f"{state_name} : {district}")

    # Save state CSVs in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        for state_name, data in state_groups.items():
            executor.submit(save_state_districts, state_name, data)

    print("\n🎉 All district-level data saved successfully!")

###################################
if __name__ == '__main__':
    main()
    print("Updated Data!")
