import hashlib
from flask import request
from user_agents import parse

def get_details():
    
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)

    user_agent = request.headers.get('User-Agent', '')
    parsed_ua = parse(user_agent)

    device = parsed_ua.device.family
    browser = parsed_ua.browser.family
    os = parsed_ua.os.family

    request_data = request.get_json()
    dwell_time = request_data.get('dwell_time', 0) 
    keystroke = request_data.get('keystroke', 0)  

    return {
        "ip": ip_address,
        "browser": browser,
        "device": device,
        "os": os,
        "dwell_time": dwell_time,
        "keystroke": keystroke,
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
        "dwell_time": deterministic_scale(request_data.get("dwell_time")),
        "keystroke": deterministic_scale(request_data.get("keystroke"))
    }

    return " ".join(map(str, processed_data.values()))