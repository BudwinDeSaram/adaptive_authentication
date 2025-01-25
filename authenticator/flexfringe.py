import os
import subprocess
from flask import jsonify

MODEL_FOLDER = "/home/flexfringe/model"
os.makedirs(MODEL_FOLDER, exist_ok=True)

app.config["MODEL_FOLDER"] = MODEL_FOLDER

MODEL_DAT_PATH = os.path.join(MODEL_FOLDER, "model.dat")
PREDICT_DAT_PATH = os.path.join(MODEL_FOLDER, "predict.dat")
RESULT_FILE_PATH = os.path.join(MODEL_FOLDER, "model.dat.ff.final.json.result")

def predict(data):
    if not data:
        print ("No data provided")
        return

    try:
        with open(PREDICT_DAT_PATH, "w") as dat_file:
            dat_file.write("1 100" + "\n")
            dat_file.write("1 6 " + data + "\n") 

        with open(PREDICT_DAT_PATH, "r") as dat_file:
            lines = dat_file.readlines()

        if lines:  
            first_line = lines[0].split()  
            if first_line:
                first_line[0] = str(len(lines) - 1)  
                lines[0] = " ".join(first_line) + "\n"  
        
        with open(PREDICT_DAT_PATH, "w") as dat_file:
            dat_file.writelines(lines)
        
        print ("Data file created")

        command = "cd /home/flexfringe && ./flexfringe --ini /home/flexfringe/ini/aic.ini /home/flexfringe/model/predict.dat --mode=predict --aptafile=/home/flexfringe/model/model.dat.ff.final.json"

        result = subprocess.run(
            [command],
            shell = True,
            capture_output=True,
            text=True
        )

        error_count = 0
        try:
            with open(RESULT_FILE_PATH, "r") as result_file:
                result_content = result_file.readlines()
            
            for line in result_content:
                if '-inf' in line:
                    error_count += 1

        except FileNotFoundError:
            print ("Result file not found.")

        return error_count 

    except Exception as e:
        print (e)
        return


def updatelsm(data):
    if not data:
        print ("No data provided")
        return       

    if not os.path.exists(MODEL_DAT_PATH):
        with open(MODEL_DAT_PATH, "w") as dat_file:
            dat_file.write("1 100" + "\n") 

    try:
        with open(MODEL_DAT_PATH, "a") as dat_file:
            dat_file.write("1 6 " + data + "\n")  
        
        print ("Data file appended")

        with open(MODEL_DAT_PATH, "r") as dat_file:
            lines = dat_file.readlines()

        if lines:  
            first_line = lines[0].split()
            if first_line:  
                first_line[0] = str(len(lines) - 1)  
                lines[0] = " ".join(first_line) + "\n"  
 
        with open(MODEL_DAT_PATH, "w") as dat_file:
            dat_file.writelines(lines)

        command = "cd /home/flexfringe && ./flexfringe --ini /home/flexfringe/ini/aic.ini " + MODEL_DAT_PATH

        result = subprocess.run(
            [command],
            shell = True,
            capture_output=True,
            text=True
        )

        print ("subprocess")

        if result.returncode == 0:
            return jsonify({
                "message": f"Data appended to '{MODEL_DAT_PATH}' and processed successfully"
            }), 200
        else:
            return jsonify({
                "error": "Error processing model.dat with flexfringe"
            }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500