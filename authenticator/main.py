from flask import Flask
from authentication import get_details, process_data
from flexfringe import predict, updatelsm

app = Flask(__name__)

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
    updatelsm(data)
    return 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
