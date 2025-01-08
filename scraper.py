import requests
from bs4 import BeautifulSoup
import time
import csv
import random
import smtplib

from selenium import webdriver
from selenium.webdriver.firefox.service import Service

# Path to geckodriver
geckodriver_path = '/Users/gio/Desktop/geckodriver'

# Initialize the WebDriver
service = Service(geckodriver_path)
driver = webdriver.Firefox(service=service)


headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
  'Accept-Language': 'en-US,en;q=0.5'
}

# Function to real URLs from a .txt file
def read_txt(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Function to read URLs from a CSV file
def read_csv(file_path):
    urls = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            urls.append(row['url'])
    return urls

# Function to extract product details from url:
def get_details(product_url):
    prices = []
    try:
        #initialize a dictionary of product details
        product_details = {}

        #get product content and create soup
        page = requests.get(product_url,headers=headers)
        soup = BeautifulSoup(page.content, features = 'lxml')

        #find span and assign variables to title and price for amazon:
        if 'amazon.com' in product_url:
            title = soup.find('span', attrs = {'id':'productTitle'}).get_text().strip()
            if title:
                product_details['title'] = title
            else:
                print("Could not retrieve title")
            price_parent = soup.find('span', attrs={'class': 'a-price aok-align-center', 'data-a-size': 'xl', 'data-a-color': 'base'})
            price = price_parent.find('span', attrs={'class': 'a-offscreen'}).get_text().strip()
            if price:
                product_details['price'] = price
                prices.append(price[1:])
            else:
                print("Could not retrieve price")

        #find span and assign variable to title and price for newegg:
        elif 'newegg.com' in product_url:
            title_parent = soup.find('div',attrs = {'class':'product-wrap'})
            title = title_parent.find('h1', attrs = {'class':'product-title'}).get_text().strip()
            if title:
                product_details['title'] = title
            else:
                print("Could not retrieve title")
            price = soup.find('div', attrs = {'class':'price-current'}).get_text().strip()
            if price:
                product_details['price'] = price
            else:
                print("Could not retrieve price")

        #find span and assign variable to title and price for ebay:
        elif 'ebay.com' in product_url:
            title_parent = soup.find('h1',attrs={'class':'x-item-title__mainTitle'})
            title = title_parent.find('span', attrs = {'class':'ux-textspans ux-textspans--BOLD'}).get_text().strip()
            if title:
                product_details['title'] = title
            else:
                print("Could not retrieve title")

            price_parent = soup.find('div', attrs={'class': 'x-price-primary', 'data-testid':'x-price-primary'})
            price = price_parent.find('span', attrs={'class': 'ux-textspans'}).get_text().strip()
            if price:
                product_details['price'] = price
            else:
                print("Could not retrieve price")
            

        
        
        product_details['product_url'] = product_url

        #return a dictionary with the proper values
        return product_details, prices
    
    except Exception as e:
        #if it could not find 
        print('Could not fetch product details')
        print(f'Failed with exception: {e}')

def save_to_csv(product_details, filename='prices.csv'):
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([product_details['title'], product_details['price'], product_details['product_url']])

def track_price(product_urls, delay = 3600):
    previous_prices={} #make a dictionary to keep track of previous prices
    for i in range(10):
        for url in product_urls:
            product_details = get_details(url)
            if product_details:
                title = product_details['title']
                current_price = product_details['price']
                previous_price = previous_prices.get(url)

                if previous_price and current_price != previous_price:
                    print(f"Price changed for '{title}': {previous_price} -> {current_price}")
                elif not previous_price:
                    print(f"Initial price for '{title}': {current_price}")

                previous_prices[url] = current_price  # Update the previous price
                # save_to_csv(product_details)  # Save data to CSV
            else:
                print(f"Failed to fetch details for {url}")

        print(f"Waiting for {delay} seconds before checking again...")
        time.sleep(delay)
    return 


#main logic

rtx4070tis = read_txt('web scraper/4070tis.txt')
rtx4080s = read_txt('web scraper/4080s.txt')


urls = rtx4070tis
for i in range(len(urls)): 
    url = urls[i]
    product_details,prices = get_details(url)
    print(product_details['title'],product_details['price'])
    # track_price(urls,60*10)
    print("\n")