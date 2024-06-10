import threading
import logging
from pymycobot.myagv import MyAgv
import socket

# 로그 설정
logging.basicConfig(level=logging.INFO)

# MyAgv 객체 생성
agv = MyAgv("/dev/ttyAMA2", 115200)
run_flag = True

# 소켓 설정
HOST = '172.30.1.63'
PORT = 12345
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
logging.info('Socket created')

try:
    s.bind((HOST, PORT))
except socket.error as e:
    logging.error(f'Bind failed: {e}')

s.listen()
logging.info('Socket awaiting messages')
(conn, addr) = s.accept()
logging.info('Connected')

def turn_left():
    agv.counterclockwise_rotation(3)  # CCW
    
def turn_right():
    agv.clockwise_rotation(3)  # CC

def forward():  
    agv.go_ahead(3)

def camera_thread():
    global run_flag
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            data_dec = data.decode().strip()                
            logging.info(f'Received data: {data_dec}')
            
            if data_dec == "STOP":
                run_flag = False
            else:
                run_flag = True

            if run_flag:
                if data_dec == "LEFT":
                    logging.info('Turning left')
                    turn_left()
                elif data_dec == "RIGHT":
                    logging.info('Turning right')
                    turn_right()
                elif data_dec == "FORWARD":
                    logging.info('Moving forward')
                    forward()

    except Exception as e:
        logging.error(f"Error occurred: {e}")

    finally:
        conn.close()

# 카메라 스레드 시작
camera_thread = threading.Thread(target=camera_thread)
camera_thread.start()

'''
import numpy as np
import threading
import time
import logging
from pymycobot.myagv import MyAgv
import socket

agv = MyAgv("/dev/ttyAMA2", 115200 )
run_flag = True

################### 소켓통신 config ##########################
HOST = '172.30.1.63' 
PORT = 12345 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

try:
    s.bind((HOST, PORT))
except socket.error:
    print('Bind failed')
    
s.listen()
print('Socket awaiting messages')
(conn, addr) = s.accept()
print('Connected')
#############################################################


def turn_left():
    # agv.go_ahead(1)
    agv.counterclockwise_rotation(3) # CCW
    
def turn_right():
    # agv.go_ahead(1)
    agv.clockwise_rotation(3) # CC

def forward():  
    # agv.restore()
    agv.go_ahead(3)

def stop_agv():
    # agv.restore()
    agv.stop()


def camera_thread():
    try:
        while True:
            
            data = conn.recv(1024)
            data_dec= data.decode()                
            print('data : ')
            print(data_dec)
            if data_dec == "STOP":
                run_flag = False
            else:
                run_flag = True

            if data_dec and run_flag:
                if data_dec == "LEFT":
                    print('call left')
                    turn_left()
                elif data_dec == "RIGHT":
                    print('call right')
                    turn_right()
                elif data_dec == "FORWARD":
                    print('call foward')
                    forward()

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")

camera_thread = threading.Thread(target=camera_thread)
camera_thread.start()
'''