#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

from max31856 import Max31856

a = Max31856()
a.close()

import websocket
import sys
try:
	import thread
except ImportError:
	import _thread as thread
import time

def on_message(ws, message):
	print(message)

def on_error(ws, error):
	print(error)

def on_close(ws):
	print("### closed ###")

def on_open(ws):
	def run(*args):
		time.sleep(1)
		ws.send("ma6")	#hub.pyにmax31856と認めてもらうコマンド
		time.sleep(1)
		spi00 = Max31856()
		spi00.open()
		try:
			while True:
				status = spi00.read()
				print(status)
				ws.send("toC "+str(status["HJ"]*0.0625))
				time.sleep(1)
		except KeyboardInterrupt:
			pass
		finally:
			spi00.close()
			ws.close()
			print("thread terminating...")
	thread.start_new_thread(run, ())


if __name__ == "__main__":
	args = sys.argv
	if len(args) == 2:
		port = args[1].strip()
	else:
		port = "9801"
	print("port={}".format(port))
	websocket.enableTrace(True)
	ws = websocket.WebSocketApp("ws://garameki.com:"+port+"/",
	on_message = on_message,
	on_error = on_error,
	on_close = on_close)
	ws.on_open = on_open
	ws.run_forever()
