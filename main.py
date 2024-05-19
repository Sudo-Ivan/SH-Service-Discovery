import requests
import yaml
import sqlite3
import logging
import secrets
from fastapi import FastAPI
from bs4 import BeautifulSoup

app = FastAPI()

TOKEN = secrets.token_urlsafe(16)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect('services.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS services (host TEXT, port INTEGER, service TEXT, status TEXT)''')
    conn.commit()
    conn.close()

def reset_db():
    conn = sqlite3.connect('services.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS services")
    conn.commit()
    conn.close()
    init_db()

def add_service_to_db(host, port, service, status):
    conn = sqlite3.connect('services.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO services VALUES (?, ?, ?, ?)", (host, port, service, status))
    conn.commit()
    conn.close()

def get_services_from_db():
    conn = sqlite3.connect('services.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services")
    services = cursor.fetchall()
    conn.close()
    return services

@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info(f"Reset Token: {TOKEN}")

@app.get("/reset/{token}")
def reset(token: str):
    if token == TOKEN:
        reset_db()
        return {"status": "Database reset successfully"}
    else:
        return {"error": "Invalid token"}

def load_config():
    with open("config.yaml", "r") as ymlfile:
        config = yaml.safe_load(ymlfile)
    return config

def parse_ports(ports_conf):
    ports = []
    for port in ports_conf:
        if "-" in str(port):
            start_port, end_port = map(int, port.split('-'))
            ports.extend(range(start_port, end_port + 1))
        else:
            ports.append(int(port))
    return ports

def get_wordlist():
    with open("wordlist.txt", "r") as file:
        wordlist = file.read().splitlines()
    return wordlist

def match_service_name(html_content, wordlist):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    for word in wordlist:
        if word.lower() in text.lower():
            return word
    return "Unknown"

def get_service_name(response):
    wordlist = get_wordlist()
    return match_service_name(response.content, wordlist)

def scan_service(host, port, services):
    url = f"http://{host}:{port}"
    try:
        response = requests.get(url, timeout=1)
        if response.status_code == 200:
            service_name = get_service_name(response)
            add_service_to_db(host, port, service_name, "open")
            services.append({"host": host, "port": port, "service": service_name, "status": "open"})
            logger.info(f"Service detected and added: {url} - {service_name}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to access {url}: {e}")

@app.get("/detect")
def detect_services():
    config = load_config()
    ip_ranges = config["ip_ranges"]
    ports_conf = config["ports"]
    domains = config["domains"]
    services = []
    ports = parse_ports(ports_conf)
    for ip in ip_ranges:
        for port in ports:
            scan_service(ip, port, services)
    for domain in domains:
        for port in ports:
            scan_service(domain, port, services)
    logger.info(f"Detection complete. Total services found: {len(services)}.")
    return {"services": services}

@app.get("/services")
def fetch_services():
    services = get_services_from_db()
    return {"services": services}