# Face-recognition-door-lock-pi
라즈베리파이를 이용한 얼굴인식 잠금장치 예시입니다.

## Features
- TCP통신 기반, Select로 구현
- 서버는 카메라를 통해 사용자를 식별하는 스레드와 네트워크통신을 위한 스레드로 구분
- 클라이언트는 방의 이름과 현재 문의 개방상태를 서버에게 전달
- 서버는 카메라를 통해 사용자를 식별한 결과값과 방의 이름과 대조하여 일치하는 클라이언트로 결과 전달
- 서버는 문의 개방상태를 디스플레이에 표시
- 동일한 객체에 접근을 차단하기 위해 Semaphore 사용
- 클라이언트는 전달받은 결과값으로 전구 점등 및 문을 개방 또는 잠금

## Installation
- Main Raspberry Pi (얼굴인식용)
```
pip3 install face_recognition
pip3 install cv2
```

## What do you need?
- GPU가 내장된 라즈베리파이 1개, 
- 점퍼선
- 카메라 (BCM2835)
- 서보모터 2개
- 터치센서 (없을 경우 face_recog_server_no_touch.py 를 실행)
- LED (문 개방 확인용으로 없어도 됩니다.)

![image](https://user-images.githubusercontent.com/90737528/158806382-812aefea-dbbb-4c3a-87c7-36837be837c2.png)

## How to work
![image](https://user-images.githubusercontent.com/90737528/158808765-1ced7603-8d95-4976-a6ba-80eaee2fd372.png)
![image](https://user-images.githubusercontent.com/90737528/158808785-0448c185-8647-4561-81d2-a4c8d71b2a2a.png)
![image](https://user-images.githubusercontent.com/90737528/158808793-fcd10153-ab06-4e9e-88de-ff2a317574e0.png)
![image](https://user-images.githubusercontent.com/90737528/158808807-b17f2603-8abc-4aae-95e7-1b693bd50659.png)

얼굴 인식에 성공하면 해당 클라이언트의 LED가 점등하며, 서보모터가 수직으로 돌아갑니다. 만약 수직인 상태일 경우 수평으로 돌아갑니다. (문고리가 틀에서 빠지지 못하도록 잠겼다 열렸다 하는 방식입니다.)

## How to use
- Main Raspberry Pi (얼굴인식용)
1. 얼굴인식용 라즈베리파이의 IP주소를 공유기의 DHCP 고정할당을 통해 192.168.1.100으로 설정합니다.
2. 네트워크망에 연결 후 IP주소와 3000번 포트의 방화벽 개방여부를 확인해주세요.
3. 라즈베리파이에 BCM2835 카메라를 연결한 후 raspi-config를 통해 카메라 활성화가 되었는지 확인해 주세요.
4. GPIO 7번에 터치센서핀을 연결합니다.
5. `face_recog_server.py`코드를 실행합니다.

- Sub Raspberry Pi (서보모터)
1. 서버와 동일한 네트워크에 연결해주세요.
2. 3000번 포트의 개방여부를 확인해주세요.
3. GPIO 7번 핀에 서보모터를 연결해주세요.
4. GPIO 11번 핀에 LED를 연결해주세요.
5. 각 클라이언트마다 `door_jongmin_client.py`, `door_taehwan_client.py`를 실행합니다.

두 작업 완료 후 얼굴인식용 라즈베리파이에 연결된 터치센서를 누른 상태로 `for_client\knowns` 폴더에 있는 얼굴을 비추면 해당하는 서보모터가 움직입니다.

## Demo
~~None~~

## Snapshots
~~None~~

## Thanks
https://github.com/ageitgey/face_recognition

## License
```
MIT License

Copyright (c) 2022 harusiku

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```


