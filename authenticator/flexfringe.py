import os
import subprocess
from flask import jsonify

MODEL_FOLDER = "/home/flexfringe/model"
os.makedirs(MODEL_FOLDER, exist_ok=True)

def predict(data, useremail):
    if not data:
        print ("No data provided")
        error_count = 2
        return error_count
    
    username = useremail.split("@")[0].replace(".", "_")

    try:
        PREDICT_DAT_PATH = os.path.join(MODEL_FOLDER, f"{username}_predict.dat")
        APTAFILE_FILE_PATH = os.path.join(MODEL_FOLDER, f"{username}_model.dat.ff.final.json")
        RESULT_FILE_PATH = os.path.join(MODEL_FOLDER, f"{username}_model.dat.ff.final.json.result")

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

        command = "cd /home/flexfringe && ./flexfringe --ini /home/flexfringe/ini/aic.ini " + PREDICT_DAT_PATH + " --mode=predict --aptafile=" + APTAFILE_FILE_PATH

        result = subprocess.run(
            [command],
            shell = True,
            capture_output=True,
            text=True
        )

        error_count = 0
        try:
            if result.returncode == 0:
                with open(RESULT_FILE_PATH, "r") as result_file:
                    result_content = result_file.readlines()
                
                for line in result_content:
                    if '-inf' in line:
                        error_count += 1
                
                return error_count
            else:
                print ("Error processing predict.dat with flexfringe")
                error_count = 2
                return error_count

        except FileNotFoundError:
            print ("Result file not found.")
            error_count = 2
            return error_count        

    except Exception as e:
        print (e)
        error_count = 2
        return error_count


def updatelsm(data, useremail):
    if not data:
        print ("No data provided")
        return None 
    username = useremail.split("@")[0].replace(".", "_")
    MODEL_DAT_PATH = os.path.join(MODEL_FOLDER, f"{username}_model.dat")

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
            })
        else:
            return jsonify({
                "error": "Error processing model.dat with flexfringe"
            })
    except Exception as e:
        return jsonify({"error": str(e)})