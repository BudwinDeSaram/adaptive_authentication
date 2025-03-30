import os
import logging
import bcrypt
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from processdata import get_details, process_data
from flexfringe import predict, updatelsm
from mfa import mfa, verify_otp_code

app = Flask(__name__)
CORS(app)   # allow cross-origin requests from any domain

MODEL_FOLDER = os.getenv("MODEL_FOLDER")
os.makedirs(MODEL_FOLDER, exist_ok=True)  # create the model folder if it doesn't exist

app.config["MODEL_FOLDER"] = MODEL_FOLDER

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
DB_CLIENT = os.getenv("DB_CLIENT")
DB_COLLECTION = os.getenv("DB_COLLECTION")

client = MongoClient(DB_CONNECTION_STRING)  
db = client[DB_CLIENT]
users_collection = db[DB_COLLECTION]

login_attempts = {}
abagingo_data = {}

logging.basicConfig(filename="logfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create an account
@app.route('/create-account', methods=['POST'])
def create_account():
    data = request.json
    useremail = data.get("useremail")
    password = data.get("password")
    securityQuestion = data.get("securityQuestion")
    securityAnswer = data.get("securityAnswer")

    if not useremail or not password:
        return jsonify({"message": "Useremail and password are required"})

    if users_collection.find_one({"useremail": useremail}):
        return jsonify({"message": "Useremail already exists"})

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    password = hashed_password.decode('utf-8')
    users_collection.insert_one({
        "useremail": useremail,
        "password": password,
        "securityQuestion": securityQuestion,
        "securityAnswer": securityAnswer,
        "blocked": False
    })
    logger.info("User account created: " + useremail)
    return jsonify({"message": "Account created successfully"})

# Route for login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    useremail = data.get("useremail")
    password = data.get("password")

    user = users_collection.find_one({"useremail": useremail})

    if not user:
        return jsonify({"status": "Invalid Useremail"})

    if user["blocked"]:
        print(f"Access denied for {useremail}")
        logger.info("Access denied for " + useremail)
        return jsonify({
                "status": "User blocked"
            })

    if bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        if useremail in login_attempts and 1 < login_attempts[useremail] <= 3:
            login_attempts[useremail] = 0
            logger.info("Security question given to " + useremail)
            return jsonify({
                "status": "Security question",
                "securityQuestion": user["securityQuestion"]
            }), 200
        login_attempts[useremail] = 0
        return jsonify({"status": "success"})
    else:
        if useremail not in login_attempts:
            login_attempts[useremail] = 0
        login_attempts[useremail] += 1

        if login_attempts[useremail] >= 3:
            users_collection.update_one({"useremail": useremail}, {"$set": {"blocked": True}})
            return jsonify({"status": "User blocked"})

        return jsonify({"status": "Invalid credentials"})

# Predict with flexfringe
@app.route('/predict', methods=['POST'])
def process_file():
    useremail = request.get_json().get('useremail')

    request_data = get_details()
    global abagingo_data
    abagingo_data = process_data(request_data)
    error_count = predict(abagingo_data, useremail)
    result = mfa(error_count, useremail)
    logger.info("Prediction done: " + useremail)
    if result.status == "User blocked":
        users_collection.update_one({"useremail": useremail}, {"$set": {"blocked": True}})
        logger.info("User blocked " + useremail)
    return result

# Replace or create LSM model
@app.route('/update-lsm', methods=['POST'])
def update_dat_file():
    useremail = request.get_json().get('useremail')
    request_data = get_details()
    data = process_data(request_data)
    results = updatelsm(data, useremail)
    logger.info("LSM model updated: " + useremail)
    return results

# Route to verify OTP
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    otp = data.get("otp")
    result = verify_otp_code(otp)
    if result.status == "success":
        global abagingo_data
        updatelsm(abagingo_data)
        logger.info("OTP verified")
    return result    

@app.route("/verify-securityquestion", methods=["POST"])
def verify_security():
    data = request.json
    useremail = data.get("useremail")
    answer = data.get("answer")

    user = users_collection.find_one({"useremail": useremail})
    if not user:
        return jsonify({"status": "failure"})

    if user["securityAnswer"].lower() == answer.lower():
        updatelsm(abagingo_data, useremail)
        logger.info("Security question verified: " + useremail)
        return jsonify({"status": "success"})
    return jsonify({"status": "failure"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)  #allow all external connections without restrictions
