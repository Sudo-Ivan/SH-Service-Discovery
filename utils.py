import re
from bs4 import BeautifulSoup
import csv

def get_wordlist():
    with open("data/wordlist.txt", "r") as file:
        return file.read().splitlines()
    
def parse_ports(ports):
    parsed = []
    for port in ports:
        if isinstance(port, int):
            parsed.append(port)
            continue
        if "-" in str(port):
            start, end = map(int, port.split('-'))
            parsed.extend(range(start, end + 1))
        else:
            parsed.append(int(port))
    return parsed

def match_service_name(html_content, wordlist):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True).lower()
    return next((word for word in wordlist if word.lower() in text), "Unknown")

def load_service_data():
    service_data = {}
    with open("data/service_data.csv", mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            service_name = row["serviceName"]
            service_data[service_name] = row
    return service_data

def get_service_name_with_data(response_content, wordlist, service_data):
    service_name = match_service_name(response_content, wordlist)
    return service_data.get(service_name, {"description": "No description", "metadataTags": "", "previewImage": "/static/images/unknown_service.jpg"})