# face_recog.py

import face_recognition
import cv2
import camera
import os
import numpy as np
from threading import Thread
import threading
import socket
from select import select
from _thread import *
from time import ctime
import constant
import RPi.GPIO as GPIO #RPi.GPIO 라이브러리를 GPIO로 사용

class FaceRecog():
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.camera = camera.VideoCamera()

        self.known_face_encodings = []
        self.known_face_names = []

        # Load sample pictures and learn how to recognize it.
        dirname = 'knowns'
        files = os.listdir(dirname)
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext == '.jpg':
                self.known_face_names.append(name)
                pathname = os.path.join(dirname, filename)
                img = face_recognition.load_image_file(pathname)
                face_encoding = face_recognition.face_encodings(img)[0]
                self.known_face_encodings.append(face_encoding)

        # Initialize some variables
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True
        self.previous_facename="";

    def __del__(self):
        del self.camera

    def reset(self):
        self.previous_facename=""

    def get_frame(self):
        # Grab a single frame of video
        frame = self.camera.get_frame()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25) #계산량 줄임

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if self.process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            self.face_locations = face_recognition.face_locations(rgb_small_frame)
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

            self.face_names = []
            for face_encoding in self.face_encodings:
                # See if the face is a match for the known face(s)
                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                min_value = min(distances)

                # tolerance: How much distance between faces to consider it a match. Lower is more strict.
                # 0.6 is typical best performance.
                name = "unknown" #if none user
                if min_value < 0.6:
                    index = np.argmin(distances)
                    name = self.known_face_names[index]

                self.face_names.append(name)

                print(name)
                
        self.process_this_frame = not self.process_this_frame
        #print(f'find : {self.face_names}')
        if self.face_names:
            if self.previous_facename in self.face_names:
                pass #이전에 확인한 얼굴이면 문을 조작하는 함수를 호출 금지
            else:
                door_lock(self.face_names[0])
                self.previous_facename=self.face_names[0]
        else:
            self.previous_facename=""
        
        # Display the results
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            semaphore.acquire() #세마포어 잠금
            if name in is_open.keys():
                is_open_exp = ('Door Close' if is_open[name]==constant.LOCK else 'Door Open') 
                cv2.putText(frame,is_open_exp,(50,50),font,1.0,(255, 255, 255), 1)
            semaphore.release() #세마포어 해제

        return frame 
        

    def get_jpg_bytes(self):
        frame = self.get_frame()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes()

HOST = ''
PORT = 3000
SIZE = 1024
constant.LOCK='0';
constant.UNLOCK='1';

thread_flag=0;
client_name={}
is_open={}
connection_list=[]

semaphore = threading.Semaphore(1) #세마포어 생성 

#클라이언트에게 전송
def door_lock(facename):
    print("send to client")
    try:
        semaphore.acquire() #세마포어 잠금
        if facename in client_name.keys():
            socket = client_name[facename]
        else:
            print("Client not connected")
            return

        print(is_open)
        if is_open[facename]==constant.LOCK:
            socket.send(constant.UNLOCK.encode())
            print("open",socket)
            #is_open[facename]=constant.UNLOCK
        else :
            socket.send(constant.LOCK.encode())
            print("close",socket)
            #is_open[facename]=constant.LOCK
    finally:
        semaphore.release() #세마포어 해제
    
def socket_server():
    while not thread_flag.is_set():
        read_socket, write_socket, error_socket = select(connection_list,[],[],3)
        for sock in read_socket: #new connection
            semaphore.acquire() #세마포어 잠금
            print("read socket Object : ", sock);
            if sock == connection_list[0]:
                client_socket, addr_info = connection_list[0].accept();
                connection_list.append(client_socket); #클라이언트 소켓 리스트 추가
                data = client_socket.recv(SIZE).decode()
                client_name[data]=client_socket #방이름과 소켓번호를 dict에 기록
                is_open[data]=constant.LOCK;
                print('[INFO][%s] (%s)방 클라이언트(%s)가 연결 되었습니다. 현재상태 : %s' % (ctime(), data, addr_info[0], is_open[data]))
                client_socket.send("OK".encode())
            else:
                temp_name = [name for name, sock_num in client_name.items() if sock_num == sock][0]
                data = sock.recv(SIZE)
                if data:
                    data = data.decode();
                    print(f'data receive : {data}')
                    is_open[temp_name]=data; #전달받은 값으로 문 열림상태 전환
                else:
                    connection_list.remove(sock)
                    sock.close()
                    print(f'[INFO][{ctime()}] {temp_name}게이트와 연결이 끊어졌습니다.')
            semaphore.release() #세마포어 해제
            
    print("스레드 종료")

face_recog = 0

if __name__ == '__main__':

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT)) 
    server_socket.listen()
    connection_list = [server_socket]
    thread_flag = threading.Event()

    print("Listen start");
    socket_thread = Thread(target=socket_server, args=())
    socket_thread.start()

    face_recog = FaceRecog()
    print(face_recog.known_face_names)

    frame = face_recog.get_frame() #화면 표시
    cv2.imshow("Frame", frame)

    print("Loop start");
    while True:
        # show the frame
        frame = face_recog.get_frame() #화면 표시
        cv2.imshow("Frame", frame)
            
        # if the `q` key was pressed, break from the loop
        key = cv2.waitKey(50) & 0xFF
        if key == ord("q"):
            thread_flag.set()
            break

    socket_thread.join()
    # do a bit of cleanup
    cv2.destroyAllWindows()
    print('finish')
