import os
from flask import Flask, request
from flask_cors import CORS
from processdata import get_details, process_data
from flexfringe import predict, updatelsm

app = Flask(__name__)
CORS(app)

MODEL_FOLDER = "/home/flexfringe/model"
os.makedirs(MODEL_FOLDER, exist_ok=True)

app.config["MODEL_FOLDER"] = MODEL_FOLDER

# Predict with flexfringe
@app.route('/predict', methods=['POST'])
def process_file():
    useremail = request.get_json().get('useremail')

    request_data = get_details()
    abagingo_data = process_data(request_data)
    error_count = predict(abagingo_data, useremail)   
    return error_count

# Replace or create LSM model
@app.route('/update-lsm', methods=['POST'])
def update_dat_file():
    useremail = request.get_json().get('useremail')
    request_data = get_details()
    data = process_data(request_data)
    results = updatelsm(data, useremail)
    return results

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
