from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect
import MySQLdb       
import math
import time
import configparser as ConfigParser
import random
import json
import serial

async_mode = None

app = Flask(__name__)


config = ConfigParser.ConfigParser()
config.read('config.cfg')
myhost = config.get('mysqlDB', 'host')
myuser = config.get('mysqlDB', 'user')
mypasswd = config.get('mysqlDB', 'passwd')
mydb = config.get('mysqlDB', 'db')
print(myhost)


app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 

ser = serial.Serial(port='/dev/ttyACM0',baudrate=9600)
# ser = serial.Serial(port='/dev/ttyACM0',baudrate=9600, timeout=.1)
# print(ser.readline().decode().strip('\r\n'))

def background_thread(args):
    count = 0  
    dataCounter = 0 
    dataList = []  
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)          
    while True:
        senzorData = ser.readline().decode().removesuffix("\r\n").split(",")

        light = senzorData[0]
        distance = senzorData[1]
        
        # print(senzorData[0])
        # print(senzorData[1])
        if args:
          A = dict(args).get('A')
          dbV = dict(args).get('db_value')
        else:
          A = 1
          dbV = 'nieco'  
        #print A
        print(dbV) 
        print(args)  
        socketio.sleep(2)
        count += 1
        dataCounter +=1
        prem = random.random()
        x=time.time()
        # sinX=float(A)*math.sin(time.time())
        # cosX=float(A)*math.cos(time.time())
        if dbV == 'start':
          dataDict = {
            #"t": time.time(),
            "light": light,
            "distance": distance}
          dataList.append(dataDict)
          socketio.emit('my_response',
                      {'data': json.dumps({"light":light, "distance":distance}), 'count': count},
                      namespace='/test')  
        else:
          if len(dataList)>0:
            fuj = str(dataList).replace("'", "\"")
            cursor = db.cursor()
            cursor.execute("SELECT MAX(id) FROM graph")
            maxIdFromDB = cursor.fetchone()

            maxid=0
            if(maxIdFromDB[0]):
              maxid=maxIdFromDB[0]

            cursor.execute("INSERT INTO graph (id, hodnoty) VALUES (%s, %s)", (maxid + 1, fuj))
            db.commit()
          dataList = []
          dataCounter = 0
          
    db.close()

@app.route('/') 
def index(): 
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route('/graph', methods=['GET', 'POST'])
def graph():
    return render_template('graph.html', async_mode=socketio.async_mode)
    
@app.route('/db')
def db():
  db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
  cursor = db.cursor()
  cursor.execute('''SELECT  hodnoty FROM  graph WHERE id=1''')
  rv = cursor.fetchall()
  return str(rv)    

@app.route('/dbdata/<string:num>', methods=['GET', 'POST'])
def dbdata(num):
  db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
  cursor = db.cursor()
  print(num)
  cursor.execute("SELECT hodnoty FROM  graph WHERE id=%s", num)
  rv = cursor.fetchone()
  return str(rv[0])
    
@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['value']    
    emit('my_response',
         {'data': message['value'], 'count': session['receive_count']})



@socketio.on('db_event', namespace='/test')
def db_message(message):   
    session['db_value'] = message['value']  
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)          
    cursor = db.cursor()
    cursor.execute("SELECT * FROM graph")
    data = cursor.fetchall()
    if ( message["value"]=="stop"):
       
       emit('refresh_db_response',
         {'data': data})





@socketio.on('get_graph_values_by_id', namespace='/test')
def db_message(message):   
    session['db_value'] = message['value']  
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)          
    cursor = db.cursor()

    try:
      cursor.execute("SELECT hodnoty FROM  graph WHERE id=%s", [message["value"]])
      oneVal = cursor.fetchone()

      print("DB FETCH SUCCESS")

      emit('fetch-one', {'data': oneVal})
      
    except (MySQLdb.Error, MySQLdb.Warning) as e:
      print(e)
      return None
      #emit('fetch-one',{'data': "ERROR"})

     

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
    
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)          
    cursor = db.cursor()
    cursor.execute("SELECT * FROM graph")
    data = cursor.fetchall()       
    emit('refresh_db_response',
      {'data': data})
    
   # emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True) 
