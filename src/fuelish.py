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
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

###################################
# Utility Functions
###################################

def clean_state_name(name: str) -> str:
    """Return a clean, URL-friendly state name."""
    return re.sub(r'[\s&]+', '-', name.strip().lower())

def get_driver():
    """Initialize and return a headless Chrome driver."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")
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

def scrape_state_and_districts(driver, state_name, fuel_type="petrol"):
    """Return dict: {city_value: city_name} for the given state."""
    state_url = f"https://www.ndtv.com/fuel-prices/{fuel_type}-price-in-{state_name}-state"
    driver.get(state_url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    city_dropdown = soup.find("select", id="cdropdown")
    if not city_dropdown:
        print(f"❌ Could not find city dropdown for {state_name}")
        return {}
    
    cities = {}
    for option in city_dropdown.find_all("option"):
        val = option.get("value")
        name = option.text.strip()
        if val and val != "select":
            cities[val] = name
    return cities

def scrape_city_prices(driver, state, city_val, city_name, fuel_type="petrol"):
    """Scrape petrol prices for a given city."""
    url = f"https://www.ndtv.com/fuel-prices/{fuel_type}-price-in-{city_val}-city"
    driver.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find("table")
    if not table:
        print(f"⚠️ No table found for {city_name} ({state})")
        return []

    data = []
    for row in table.find_all("tr")[1:]:
        tds = row.find_all("td")
        if len(tds) < 3:
            continue
        city = tds[0].text.strip()
        price = tds[1].text.strip()
        ch = tds[2]
        if ch.find(class_="chngBx up"):
            change = "+ " + ch.text.strip()
        elif ch.find(class_="chngBx down"):
            change = "- " + ch.text.strip()
        else:
            change = "  " + ch.text.strip()
        data.append([city, price, change])
    return data

###################################
# Main Execution
###################################

def main():
    driver = get_driver()

    # URLs for state-level data
    URL_PETROL = "https://www.ndtv.com/fuel-prices/petrol-price-in-all-state"
    URL_DIESEL = "https://www.ndtv.com/fuel-prices/diesel-price-in-all-state"

    # Fetch both tables
    driver.get(URL_PETROL)
    time.sleep(2)
    soup1 = BeautifulSoup(driver.page_source, "html.parser")
    table_p = soup1.find("table")

    driver.get(URL_DIESEL)
    time.sleep(2)
    soup2 = BeautifulSoup(driver.page_source, "html.parser")
    table_d = soup2.find("table")

    if not table_p or not table_d:
        print("❌ Could not find one of the state-level tables.")
        driver.quit()
        return

    state, price_p, change_p, price_d, change_d = [], [], [], [], []

    # Parse petrol table
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

    # Parse diesel table
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

    # Save state-level CSV
    out = [["State", "Price(P)", "Change(P)", "Price(D)", "Change(D)"]]
    for (i, j, k, l, m) in zip(state, price_p, change_p, price_d, change_d):
        out.append([i, j, k, l, m])

    with open("State.csv", "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(out)

    print("✅ State-level data saved successfully as State.csv")

    ######################################
    # DISTRICT LEVEL DATA
    ######################################
    print("\n📍 Starting district-level data scraping...")
    assets_path = os.path.join("root", "assets")
    os.makedirs(assets_path, exist_ok=True)

    for st in state:
        clean_name = clean_state_name(st)
        print(f"\n🔍 Fetching districts for {st}...")
        cities = scrape_state_and_districts(driver, clean_name)
        if not cities:
            print(f"⚠️ Skipped {st}: No city dropdown found.")
            continue

        district_data = [["District", "Petrol Price", "Change"]]
        for city_val, city_name in cities.items():
            city_prices = scrape_city_prices(driver, st, city_val, city_name)
            district_data.extend(city_prices)

        file_path = os.path.join(assets_path, f"{st.replace(' ', '_')}.csv")
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(district_data)
        print(f"✅ Saved district-level data for {st}")

    driver.quit()
    print("\n🎉 All district-level data saved successfully!")

###################################
if __name__ == '__main__':
    main()
    print("Updated Data!")
