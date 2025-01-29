from flask import jsonify
from sendemail import send_code_email, generate_code, send_notification_block, send_notification_login

code = 0
email_address = ""

def mfa(error_count, email):
    global email_address
    email_address = email
    if error_count == 0:
        return jsonify({
            "status": "success"
        })
    elif error_count <= 3:
        global code 
        code = generate_code()
        send_code_email(email_address, code)
        return jsonify({
            "status": "OTP sent"
        })
    else:        
        send_notification_block(email_address)
        return jsonify({
            "status": "User blocked"
        })
    
def verify_otp_code(otp):    
    if otp == code:
        send_notification_login(email_address)
        return jsonify({"status": "success"})
    return jsonify({"status": "failure"})
     