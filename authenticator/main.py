import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from processdata import get_details, process_data
from flexfringe import predict, updatelsm
from mfa import mfa, verify_otp_code

app = Flask(__name__)
CORS(app)

MODEL_FOLDER = "/home/flexfringe/model"
os.makedirs(MODEL_FOLDER, exist_ok=True)

app.config["MODEL_FOLDER"] = MODEL_FOLDER

client = MongoClient("mongodb+srv://dbadmin:qwe123@cluster0.dkfxt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  
db = client['lsmauth']
users_collection = db['users']

login_attempts = {}
abagingo_data = {}

# Create an account
# @app.route('/create-account', methods=['POST'])
# def create_account():
#     data = request.json
#     useremail = data.get("useremail")
#     password = data.get("password")
#     securityQuestion = data.get("securityQuestion")
#     securityAnswer = data.get("securityAnswer")

#     if not useremail or not password:
#         return jsonify({"message": "Useremail and password are required"})

#     if users_collection.find_one({"useremail": useremail}):
#         return jsonify({"message": "Useremail already exists"})

#     users_collection.insert_one({
#         "useremail": useremail,
#         "password": password,
#         "securityQuestion": securityQuestion,
#         "securityAnswer": securityAnswer,
#         "blocked": False
#     })
#     return jsonify({"message": "Account created successfully"})

# # Route for login
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     useremail = data.get("useremail")
#     password = data.get("password")

#     user = users_collection.find_one({"useremail": useremail})

#     if not user:
#         return jsonify({"status": "Invalid Useremail"})

#     if user["blocked"]:
#         print(f"Access denied for {useremail}")
#         return jsonify({
#                 "status": "User blocked"
#             })

#     if user["password"] == password:
#         if useremail in login_attempts and 1 < login_attempts[useremail] <= 3:
#             login_attempts[useremail] = 0
#             return jsonify({
#                 "status": "Security question",
#                 "securityQuestion": user["securityQuestion"]
#             }), 200
#         login_attempts[useremail] = 0
#         return jsonify({"status": "success"})
#     else:
#         if useremail not in login_attempts:
#             login_attempts[useremail] = 0
#         login_attempts[useremail] += 1

#         if login_attempts[useremail] >= 3:
#             users_collection.update_one({"useremail": useremail}, {"$set": {"blocked": True}})
#             return jsonify({"status": "User blocked"})

#         return jsonify({"status": "Invalid credentials"})

# Predict with flexfringe
@app.route('/predict', methods=['POST'])
def process_file():
    useremail = request.get_json().get('useremail')

    request_data = get_details()
    global abagingo_data
    abagingo_data = process_data(request_data)
    error_count = predict(abagingo_data, useremail)
    result = mfa(error_count, useremail)
    if result.status == "User blocked":
        users_collection.update_one({"useremail": useremail}, {"$set": {"blocked": True}})
    return result

# Replace or create LSM model
@app.route('/update-lsm', methods=['POST'])
def update_dat_file():
    useremail = request.get_json().get('useremail')
    request_data = get_details()
    data = process_data(request_data)
    results = updatelsm(data, useremail)
    return results

# Route to verify OTP
# @app.route('/verify-otp', methods=['POST'])
# def verify_otp():
#     data = request.json
#     otp = data.get("otp")
#     result = verify_otp_code(otp)
#     if result.status == "success":
#         global abagingo_data
#         updatelsm(abagingo_data)
#     return result    

# @app.route("/verify-securityquestion", methods=["POST"])
# def verify_security():
#     data = request.json
#     useremail = data.get("useremail")
#     answer = data.get("answer")

#     user = users_collection.find_one({"useremail": useremail})
#     if not user:
#         return jsonify({"status": "failure"})

#     if user["securityAnswer"].lower() == answer.lower():
#         updatelsm(abagingo_data)
#         return jsonify({"status": "success"})
#     return jsonify({"status": "failure"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
