import RPi.GPIO as GPIO #RPi.GPIO 라이브러리를 GPIO로 사용
from time import sleep  #time 라이브러리의 sleep함수 사용
import socket 
from _thread import *
import select
import constant

servoPin          = 7   # 서보 핀
SERVO_MAX_DUTY    = 12   # 서보의 최대(180도) 위치의 주기
SERVO_MIN_DUTY    = 3    # 서보의 최소(0도) 위치의 주기

LED_Pin           = 11  #LED핀

GPIO.setmode(GPIO.BOARD)        # GPIO 설정
GPIO.setup(servoPin, GPIO.OUT)  # 서보핀 출력으로 설정
GPIO.setup(LED_Pin, GPIO.OUT, initial=GPIO.LOW)

'''
서보 위치 제어 함수
degree에 각도를 입력하면 duty로 변환후 서보 제어(ChangeDutyCycle)
'''
def setServoPos(degree):
  servo = GPIO.PWM(servoPin, 50)  # 서보핀을 PWM 모드 50Hz로 사용하기 (50Hz > 20ms)
  servo.start(0)  # 서보 PWM 시작 duty = 0, duty가 0이면 서보는 동작하지 않는다. 
  # 각도는 180도를 넘을 수 없다.
  if degree > 180:
    degree = 180

  # 각도(degree)를 duty로 변경한다.
  duty = SERVO_MIN_DUTY+(degree*(SERVO_MAX_DUTY-SERVO_MIN_DUTY)/180.0)
  # duty 값 출력
  print("Degree: {} to {}(Duty)".format(degree, duty))

  # 변경된 duty값을 서보 pwm에 적용
  servo.ChangeDutyCycle(duty)
  sleep(1)
  servo.stop() # 서보 PWM 정지


HOST = "192.168.1.100"
NAME = "taehwan"
PORT = 3000
SIZE = 1024
constant.LOCK='0';
constant.UNLOCK='1';

if __name__ == "__main__": 
  
  # 서보 0도에 위치
  setServoPos(0)
  sleep(1) # 1초 대기
  # 90도에 위치
  setServoPos(180)
  sleep(1)
  
  client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
  client_socket.connect((HOST, PORT))

  client_socket.send(NAME.encode())
  data = client_socket.recv(SIZE)
  if not data:
    print('서버(%s:%s)와의 연결이 끊어졌습니다.' %HOST %PORT)
    client_socket.close()
    sys.exit()
    
  print("run")
  while True:
    try:
      #connection_list = [sys.stdin, client_socket]
      connection_list = [client_socket]

      read_socket, write_socket, error_socket = select.select(connection_list, [], [], 3)

      for sock in read_socket:
          if sock == client_socket:
              data = sock.recv(SIZE)
              if not data:
                print('서버(%s:%s)와의 연결이 끊어졌습니다.' %HOST %PORT)
                client_socket.close()
                sys.exit()
              else:
                data = data.decode()
                print('전달 받음 %s' % data)
                if data == constant.LOCK :
                      setServoPos(0)
                      GPIO.output(LED_Pin,GPIO.LOW)
                      client_socket.send(constant.LOCK.encode())
                elif data == constant.UNLOCK :
                      setServoPos(90)
                      GPIO.output(LED_Pin,GPIO.HIGH)
                      client_socket.send(constant.UNLOCK.encode())


    except KeyboardInterrupt:

      servo.stop() # 서보 PWM 정지
      GPIO.cleanup() # GPIO 모드 초기화

      client_socket.close()
      sys.exit()


