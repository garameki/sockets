#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
'''
MIT License

Copyright (c) 2018 USAKU Takahashi

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
-------------------------------------------------------------------------
Copyright 2018 Hiroki Ohtani.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''
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
