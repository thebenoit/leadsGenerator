import requests
from bs4 import BeautifulSoup
import re
import json
import time
import os
import random
from pymongo import MongoClient
from seleniumwire import webdriver
import seleniumwire.undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv

load_dotenv()


chrome_driver_path = os.getenv("CHROME_DRIVER_PATH")

class Bd:
    
        def __init__(self, uri, database_name, collection):
        
            # connection to the database
            self.client = MongoClient(uri)
            # initialisation of the database
            self.db = self.client[database_name]
            
            # initialisation of the collection 
            self.collection = self.db[collection]
            
            # delete all documents in the collection
            self.collection.delete_many({})
        
        def add_data(self,data):
            try:
                self.collection.insert_one(data)
            except Exception as e:
                print(f"Error adding data: {e}")
                
                
                
class Scraper:
    
    def __init__(self,mongo_uri=None, database_name=None, collection_name=None):
        print("INIT...")
        self.mongo_uri = os.getenv("MONGO_URI")
        self.database_name = os.getenv("DATABASE_NAME")
        self.collection_name = os.getenv("COLLECTION_NAME")
        
        self.bd = Bd(self.mongo_uri, self.database_name, self.collection_name)
        
        proxies = {
            "http": os.getenv("PROXY_URL"),
            "https": os.getenv("PROXY_URL")
        }
        
        proxy_options = {
            
        }
        
        chrome_options = uc.ChromeOptions()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--ignore-ssl-errors=yes')
        self.chrome_options.add_argument('--ignore-certificate-errors')
        
        # Initialiser le service Chrome
        self.service = Service(chromedriver_path)
        
        # Nombre maximum de tentatives et délai entre les tentatives
        self.max_retries = 3
        self.retry_delay = 10
        
    def initialize_driver(self):
        print("Initialisation du navigateur Chrome")
        
        """Initialise et retourne une nouvelle instance du navigateur Chrome"""
        try:
            return uc.Chrome(
                service=self.service,
                options=self.chrome_options,
                
            )
        except Exception as e:
            print(f"Erreur lors de l'initialisation du navigateur Chrome: {e}")
            return None
        
        
    def get_realtorca_url(self, page_number):
        try:
            return f"https://www.realtor.ca/realtor-search-results#province=4&page={page_number}&sort=11-A"
        except Exception as e:
            return None
        
        
    def extract_data_from_html(self, html_content, item_id):
        """Extrait les données pertinentes du HTML de la page Facebook Marketplace"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extraction des données
            data = {
                "id": item_id,
                "name": "",
                "speciality": "",
                "Company": "",
                "phone": "",
                "email": "",
                "address": "",
                "city": "",
                "province": "",
                "postal_code": "",
                "website": "",            
            }
            
            cards = soup.find_all(id="realtorCard")
            for agent in cards:
                
                name = agent.find("div",class_="realtorCardName")
                if name:
                    nom = name.get_text(strip=True)
                    print("inserer nom: ", nom)
                    data["name"] = nom
                    
                    
                    
                speciality = agent.find("div", class_="realtorCardTitle")
                if speciality:
                    titre = speciality.get_text(strip=True)
                    print("inserer titre: ", titre)
                    data["speciality"] = titre
                    
            return data
        except Exception as e:
            print(f"Erreur lors de l'extraction des données HTML: {e}")
            return None

    def insert_data(self,data):
        try:
            print("inserer les données dans la base de données")
            self.bd.collection_name.insert_one(data)
        except Exception as e:
            print(f"Erreur lors de l'insertion des données dans la base de données: {e}")
            
def main():
    print("Début du scraping...")
    scraper = Scraper()
    driver = scraper.initialize_driver()
    
    # boucle sur les pages
    for page_number in range(1, 20):
        
        url = f"https://www.realtor.ca/realtor-search-results#province=4&page={page_number}&sort=11-A"
        driver.get(url)
        time.sleep(3)
        html_content = driver.page_source
        data = scraper.extract_data_from_html(html_content, page_number)
        scraper.insert_data(data)
        
  
    
if __name__ == "__main__":
    main()
        
    

        
        
        
        
        
        
        
        
        
        
        