#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

from PIL import Image
import io

import cv2

import websocket

import base64
import codecs

import time

try:
	import thread
except ImportError:
	import _thread as thread



capture = None

def en64(byte):
	return base64.b64encode(byte)

def de64(byte):
	return base64.b64decode(byte)

def on_message(ws, message):
###	print(message)
	pass

def on_error(ws, error):
	print(error)

def on_close(ws):
	print("### closed ###")

def on_open(ws):
	def run(*args):
		time.sleep(1)
		ws.send("im6")	#hub.pyにimgstreamと認めてもらうコマンド
		time.sleep(1)
		try:
			while True:
				rc,img = capture.read()
				if not rc:
					continue
				imgRGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
				jpg = Image.fromarray(imgRGB)
				tmpFile = io.BytesIO()#インスタンスを生成しているのね...
				jpg.save(tmpFile,'JPEG')
				tmpFile.seek(0)#ディスクプリタの先頭に
				img = tmpFile.read()
				b64 = en64(img)
				#print(type(b64))
				ws.send(b64)
				time.sleep(1)
		except KeyboardInterrupt:
			pass
		finally:
			ws.close()
			print("thread terminating...")
	thread.start_new_thread(run, ())

def main():
	global capture
	global img

	capture = cv2.VideoCapture(0)
#	capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320); 
#	capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240);
#	capture.set(cv2.cv.CV_CAP_PROP_SATURATION,0.2);

	#websocket.enableTrace(True)
	websocket.enableTrace(False)
	ws = websocket.WebSocketApp("ws://garameki.com:8801/",
	on_message = on_message,
	on_error = on_error,
	on_close = on_close)
	ws.on_open = on_open
	try:
		ws.run_forever()
	except KeyboardInterrupt:
		capture.release()

if __name__ == "__main__":
	main()
