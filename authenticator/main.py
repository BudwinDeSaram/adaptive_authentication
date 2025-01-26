import os
from flask import Flask
from processdata import get_details, process_data
from flexfringe import predict, updatelsm

app = Flask(__name__)

MODEL_FOLDER = "/home/flexfringe/model"
os.makedirs(MODEL_FOLDER, exist_ok=True)

app.config["MODEL_FOLDER"] = MODEL_FOLDER

# Endpoint 1: Predict with flexfringe
@app.route('/predict', methods=['POST'])
def process_file():
    request_data = get_details()
    data = process_data(request_data)
    error_count = predict(data)
    return error_count

# Endpoint 2: Replace or create LSM model
@app.route('/update-lsm', methods=['POST'])
def update_dat_file():
    request_data = get_details()
    data = process_data(request_data)
    results = updatelsm(data)
    return results

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
