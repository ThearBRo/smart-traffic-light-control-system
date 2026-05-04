from flask import Flask, render_template, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

import serial
import serial.tools.list_ports
import time
import atexit

import csv
import io

# Create Flask app
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///traffic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db = SQLAlchemy(app)

migrate = Migrate(app, db)  

class TrafficLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    road = db.Column(db.String(10), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)


with app.app_context():
    db.create_all()
# Global variable for Arduino connection
arduino = None

# Find and connect to Arduino
def connect_arduino():
    global arduino
    
    # Close any existing connection to avoid permission errors
    if arduino is not None:
        try:
            arduino.close()
            print("Closed existing connection")
        except:
            pass
            
    # List all available ports
    print("Looking for Arduino...")
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(f"Found port: {p.device}")
        
    # Try to find Arduino port
    arduino_port = None
    for p in ports:
        if "Arduino" in p.description or "CH340" in p.description:
            arduino_port = p.device
            print(f"Arduino found at {arduino_port}")
            break
            
    # If not found, try COM3 or COM4 (common Arduino ports)
    if not arduino_port:
        if any(p.device == "COM4" for p in ports):
            arduino_port = "COM4"
            print("Using COM4 for Arduino")
        elif any(p.device == "COM3" for p in ports):
            arduino_port = "COM3"
            print("Using COM3 for Arduino")
        else:
            print("Arduino not found automatically.")
            return False
            
    # Connect to the port
    try:
        arduino = serial.Serial(arduino_port, 9600, timeout=0.05)
        time.sleep(2)  # Wait for Arduino to reset
        print("Connected to Arduino!")
        return True
    except Exception as e:
        print(f"Error connecting: {e}")
        return False

# Close Arduino connection when the app exits
def close_arduino():
    global arduino
    if arduino:
        try:
            arduino.close()
            print("Arduino connection closed")
        except:
            pass

# Register the function to be called on exit
atexit.register(close_arduino)

# Send command to Arduino using a context manager to avoid port conflicts
def send_to_arduino(command):
    global arduino
    
    try:
        # If we don't have a connection or it's closed, try to reconnect
        if not arduino or not arduino.is_open:
            if not connect_arduino():
                return "Not connected to Arduino"
                
        # Send the command
        arduino.write(f"{command}\n".encode())
        print(f"Sent: {command}")
        
        # Wait for response
        time.sleep(0.1)
        response = ""
        while arduino.in_waiting:
            response += arduino.readline().decode().strip()
            
        if response:
            print(f"Arduino says: {response}")
            return response
            
        return f"Command {command} sent"
        
    except Exception as e:
        print(f"Error: {e}")
        # Try to close and reset connection for next attempt
        try:
            if arduino:
                arduino.close()
        except:
            pass
        arduino = None
        return f"Error sending command: {e}"


# Web page route
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


##== OPEN ROAD (A, B, C, D) ==##
@app.route("/open_road/<road>", methods=["POST"])
def open_road(road):

    command = f"OPEN:{road}"
    response = send_to_arduino(command)

    if response:
        new_log = TrafficLog(road=road, action="OPEN")
        db.session.add(new_log)
        db.session.commit()

    return {"status": "Success", "arduino_msg": response}


##== Auto Double ==##
@app.route("/double", methods=["POST"])
def open_double_road():

    command = f"DOUBLE"
    response = send_to_arduino(command)
    return {"status": "Success", "arduino_msg": response}


##== Auto Traffic ==##
@app.route("/auto", methods=["POST"])
def auto_traff():
    command = f"SET_AUTO"
    response = send_to_arduino(command)
    return {"status": "Success", "arduino_msg" : response}


##== Set Timer ==##
@app.route("/set_timer/<road>/<int:ms>", methods=["POST"])
def set_timer(road, ms):

    command = f"TIME:{road}{ms}"
    response = send_to_arduino(command)
    
    # print(response)
    # if response:
    #     new_log = TrafficLog(road=road, action=f"TIMER {ms}S")
    #     db.session.add(new_log)
    #     db.session.commit()

    return {"status": "Success", "arduino_msg": response}


@app.route("/get_stats", methods=["GET"])
def view():
    data = {
        "A": TrafficLog.query.filter_by(road='A', action='OPEN').count(),
        "B": TrafficLog.query.filter_by(road='B', action='OPEN').count(),
        "C": TrafficLog.query.filter_by(road='C', action='OPEN').count(),
        "D": TrafficLog.query.filter_by(road='D', action='OPEN').count()
    }

    return jsonify({"stats": data})


@app.route("/export_traffic")
def export_traffic():

    traffic_data = TrafficLog.query.all()

    si = io.StringIO()
    cw = csv.writer(si)

    cw.writerow(['ID', 'Road', 'Action', 'Timestamp'])

    for traffic in traffic_data:
        cw.writerow([traffic.id, traffic.road, traffic.action, traffic.timestamp])

    response = make_response(si.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=traffic.csv"
    response.headers["Content-type"] = "text/csv"

    return response


if __name__ == "__main__":
    # Connect to Arduino when starting

    connect_arduino()
    # Start the web server
    print("Starting web server...")
    print("Open your browser and go to: http://127.0.0.1:5000")

    app.run(debug=False, host="0.0.0.0", port=5000)