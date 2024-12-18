import serial
from flask import Flask, render_template, url_for, redirect, request
import pymysql

device = '/dev/ttyS0'
arduino = serial.Serial(device, 9600, timeout = 1)
arduino.flush()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stop')
def stop():
    arduino.write(b"stop")
    return redirect(url_for('index'))

@app.route('/save')
def save_data():
    dbConn = pymysql.connect("localhost","kratos","","smoke_db") or die("Could not connect to database")
    data = arduino.readline()
    data = data.decode('ascii')
    
    while(data):
        with dbConn:
            cursor = dbConn.cursor()
            cursor.execute("INSERT INTO smokeLog (smokeAmount) VALUES (%s)"% (data))
            dbConn.commit
            cursor.close()
    return redirect(url_for('index'))
    
@app.route('/stored')
def stored():
    dbConn = pymysql.connect("localhost","kratos","","smoke_db") or die("Could not connect to database")
    data = []
    with dbConn:
        cursor = dbConn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM smokeLog")
        
        for row in cursor:
            data.append(row);
        cursor.close()
    return render_template('smokeData.html', data = data)

@app.route('/change', methods=['POST'])
def change():
    submitValue = request.form['changeThreshold']
    submitValue = int(submitValue)
    arduino.write(b"%i" %(submitValue))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
    