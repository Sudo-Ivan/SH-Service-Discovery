from fastapi import APIRouter
import requests
from db.database import add_service_to_db
from utils import parse_ports, get_service_name_with_data, get_wordlist, load_service_data
from config import load_config

router = APIRouter()

def scan_service(host: str, port: int, wordlist, service_data):
    url = f"http://{host}:{port}"
    try:
        response = requests.get(url, timeout=1)
        if response.status_code == 200:
            data = get_service_name_with_data(response.content, wordlist, service_data)
            service_name = data.get("serviceName", "Unknown")
            previewImage = data.get("previewImage", "/static/images/unknown_service.jpg")
            add_service_to_db(host, port, service_name, "open", previewImage)
            return {"host": host, "port": port, "service": service_name, "previewImage": previewImage}
    except requests.exceptions.RequestException:
        return None

@router.get("/detect")
def detect_services():
    config = load_config()
    services_detected = []
    wordlist = get_wordlist()
    service_data = load_service_data()

    if "ip_ranges" in config and "ports" in config:
        for ip_range in config["ip_ranges"]:
            if '-' in ip_range:
                # Assuming IPv4, split into components for start and end of range
                start_ip_str, end_ip_str = ip_range.split('-', 1)
                start_ip_int = int(ipaddress.IPv4Address(start_ip_str))
                end_ip_int = int(ipaddress.IPv4Address(end_ip_str))
                for ip_int in range(start_ip_int, end_ip_int + 1):
                    ip_str = str(ipaddress.IPv4Address(ip_int))
                    for port in parse_ports(config["ports"]):
                        result = scan_service(ip_str, port, wordlist, service_data)
                        if result:
                            services_detected.append(result)
            else:
                for port in parse_ports(config["ports"]):
                    result = scan_service(ip_range, port, wordlist, service_data)
                    if result:
                        services_detected.append(result)

    if "domains" in config and "ports" in config:
        for domain in config["domains"]:
            for port in parse_ports(config["ports"]):
                result = scan_service(domain, port, wordlist, service_data)
                if result:
                    services_detected.append(result)

    return {"detected_services": services_detected}