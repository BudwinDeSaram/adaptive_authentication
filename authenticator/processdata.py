import hashlib
from flask import request
from user_agents import parse

def get_details():   
    request_data = request.get_json()

    useremail = request_data.get('useremail')   
    ip_address = request_data.get('ip')
    user_agent = request_data.get('userAgent')
    dwellTime = request_data.get('dwellTime', 0)

    parsed_ua = parse(user_agent)

    device = parsed_ua.device.family
    browser = parsed_ua.browser.family
    os = parsed_ua.os.family    

    return {
        "ip": ip_address,
        "browser": browser,
        "device": device,
        "os": os,
        "dwellTime": dwellTime,
        "useremail": useremail,
    }

# Function to process and scale data
def process_data(request_data):
    def deterministic_scale(value, max_value=99):
        if not value:
            return 0
        hash_object = hashlib.sha256(str(value).encode())
        return int(hash_object.hexdigest(), 16) % (max_value + 1)

    processed_data = {
        "ip": deterministic_scale(request_data.get("ip")),
        "browser": deterministic_scale(request_data.get("browser")),
        "device": deterministic_scale(request_data.get("device")),
        "os": deterministic_scale(request_data.get("os")),
        "dwellTime": deterministic_scale(request_data.get("dwellTime")),
        "useremail": deterministic_scale(request_data.get("useremail"))
    }

    return " ".join(map(str, processed_data.values()))