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
from selenium.webdriver.chrome.options import Options
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
        try:
            print("INIT...")
            self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
            self.database_name = os.getenv("DATABASE_NAME")
            self.collection_name = os.getenv("COLLECTION")
            

            
            self.bd = Bd(self.mongo_uri, self.database_name, self.collection_name)
            
            proxies = {
                "http": os.getenv("PROXY_URL"),
                "https": os.getenv("PROXY_URL")
            }
            
            proxy_options = {
                
            }
            
            self.chrome_options = Options()
            self.chrome_options.add_argument('--headless')
            self.chrome_options.add_argument('--ignore-ssl-errors=yes')
            self.chrome_options.add_argument('--ignore-certificate-errors')
            self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            
            # Initialiser le service Chrome
            self.service = Service(chrome_driver_path)
            
            # Nombre maximum de tentatives et délai entre les tentatives
            self.max_retries = 3
            self.retry_delay = 10
        except Exception as e:
            print(f"Erreur lors de l'initialisation du Scraper: {e}")
            raise
        
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
        print("Extraction des données du HTML")
        """Extrait les données pertinentes du HTML de la page Facebook Marketplace"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
                                                
           
            extracted_data = []
            cards = soup.find_all(id="realtorCard")
            for agent in cards:
                data = {
                    "name": "",
                    "speciality": "",
                    "Company": "",
                    "phone": "",
                    "email": "",
                    "address": "",
                    "city": "",
                    "website": "",            
                      }                 
                
                                         
                name = agent.find("span",class_="realtorCardName")
                if name:
                    nom = name.get_text(strip=True)
                    
                    # Vérifier si le nom existe déjà dans la base de données
                    existing_record = self.bd.collection.find_one({"name": nom})
                    if existing_record:
                        print(f"Le nom '{nom}' existe déjà dans la base de données, passage au suivant")
                        continue
                    
                    print("inserer nom: ", nom, "dans la liste")
                    data["name"] = nom
                #si il n'y a pas de nom fuck a ca next    
                else:
                    print("pas de nom")
                    continue
                    
                phone = agent.find("span",class_="realtorCardContactNumber TelephoneNumber")
                if phone:
                    numero = phone.get_text(strip=True)
                    #print("inserer numero: ", numero)
                    data["phone"] = numero
                    
                website = agent.find("a",class_="realtorCardWebsite")
                if website:
                    site_web = website.get('href')
                    #print("inserer site web: ", site_web)
                    data["website"] = site_web
                    
                email = agent.find("span",class_="realtorCardFooterLinkText")
                if email:
                    mail = email.get_text(strip=True)
                    #print("inserer mail: ", mail)
                    data["email"] = mail
                                   
                officeAddress = agent.find("div",class_="realtorCardOfficeAddress")
                if officeAddress:
                    adresse = officeAddress.get_text(strip=True)
                    #print("inserer adresse: ", adresse)
                    data["address"] = adresse
                                                           
                    
                speciality = agent.find("div", class_="realtorCardTitle")
                if speciality:
                    titre = speciality.get_text(strip=True)
                    #print("inserer speciality: ", titre)
                    data["speciality"] = titre

                extracted_data.append(data)
                    
            return extracted_data
        except Exception as e:
            print(f"Erreur lors de l'extraction des données HTML: {e}")
            return None

    def insert_data(self,data):
        try:
            print("inserer les données dans la base de données")
            for item in data:
                print(f"inserer {item['name']}la base de données: ")
                self.bd.add_data(item)
        except Exception as e:
            print(f"Erreur lors de l'insertion des données dans la base de données: {e}")
            
def main():
    scraper = Scraper()
    driver = scraper.initialize_driver()
    
    # boucle sur les pages
    for page_number in range(1, 40):
        print(f"Traitement de la page {page_number}")
        url = f"https://www.realtor.ca/realtor-search-results#province=4&page={page_number}&sort=11-A"
        driver.get(url)
        time.sleep(5)
        html_content = driver.page_source
        data = scraper.extract_data_from_html(html_content, page_number)
        scraper.insert_data(data)
        
  
    
if __name__ == "__main__":
    main()
        
    

        
        
        
        
        
        
        
        
        
        
        