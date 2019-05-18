#!/usr/bin/env python3:
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
----------------------------------------------------------------------------
The MIT License (MIT)

Copyright (c) 2018 Johan Hanssen Seferidis

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

'''
import logging
from websocket_server import WebsocketServer
import re	#regexp

import sys

class MyClient:

	allClients = []	#class variable : all client instans is allocated into 

	def __init__(self,client_websocket_server,server_websocket_server):
		self.pClient = client_websocket_server
		self.pServer = server_websocket_server
		self.pRoll = None
		MyClient.allClients.append(self)

	def speak_to_myself(self,message):
		self.pServer.send_message(self.pClient,message)

	def say_to_roll(self,roll,message):
		allclients = MyClient.allClients
		for ii in range(0,len(allclients)):
			if allclients[ii].pRoll == roll:
				self.pServer.send_message(allclients[ii].pClient,message)

	def say_to_all(self,message):
		self.pServer.send_message_to_all(message)

	def get_roll(self):
		return self.pRoll

	def set_roll(self,roll):
		self.pRoll = roll

	def set_roll_exclusively(self,roll):
		if self.pRoll == roll:
			self.pServer.send_message(self.pClient,"success : you have already been "+roll)
			return True
		elif MyClient.exist_roll(roll):
			self.pServer.send_message(self.pClient,"falure : "+roll+" already exists")
			return False
		else:
			self.set_roll(roll)
			self.pServer.send_message(self.pClient,"success : you became "+roll)
			return True

	@classmethod
	def get_rolls_of_all(cself):
		rolls = []
		for ii in range(0,len(MyClient.allClients)):
			rolls.append(MyClient.allClients[ii].pRoll)
		print('rolls =',rolls)
		return rolls

	@classmethod
	def exist_roll(cself,roll):
		allRolls = MyClient.get_rolls_of_all()
		if roll in allRolls:
			return True
		else:
			return False

	@classmethod
	def remove(cself,client_websocket_server):
		for ii in range(0,len(MyClient.allClients)):
			if MyClient.allClients[ii].pClient == client_websocket_server:
				del MyClient.allClients[ii]

	@classmethod
	def convertFrom(cself,client_websocket_server):
		ii=0
		for ii in range(0,len(MyClient.allClients)):
			if MyClient.allClients[ii].pClient == client_websocket_server:
				break
		return MyClient.allClients[ii]





class HubServer:

	ANONYMOUS = 'anonymous'
	rollnameMAX31856 = 'MAX31856'
	rollnameCONTROLLER = 'CONTROLLER'


	def __init__(self,PORT,HOST,LOGGING):
		server = WebsocketServer(PORT,HOST,LOGGING)
		server.set_fn_new_client(self.new_client)
		server.set_fn_client_left(self.client_left)
		server.set_fn_message_received(self.message_received)
		server.run_forever()

	# Called for every client connecting (after handshake)
	def new_client(self,client_websocket_server, server):
		print("New client connected and was given id %d" % client_websocket_server['id'])
		print(client_websocket_server)
		server.send_message_to_all('new client joined')
		MyClient(client_websocket_server,server)

	# Called for every client disconnecting
	def client_left(self,client, server):
		print("Client(%d) disconnected" % client['id'])
		MyClient.remove(client)


	# Called when a client sends a message
	def message_received(self,client_websocket_server, server, message):
###		#print('messge from ',client_websocket_server)
###		#print("Client({}) said: {}".format(client_websocket_server['id'], message))
		client = MyClient.convertFrom(client_websocket_server)

		client.say_to_all(message)
#		if message.strip() == "co6":
#			client.set_roll_exclusively(HubServer.rollnameCONTROLLER)
#		elif message.strip() == "ma6":
#			client.set_roll_exclusively(HubServer.rollnameMAX31856)
#
#		roll = client.get_roll()
#		if roll == HubServer.rollnameCONTROLLER:
#			if re.search('toM',message):#pass phrase
#				client.say_to_roll(HubServer.rollnameMAX31856,message)
#		elif roll == HubServer.rollnameMAX31856:
#			if re.search('toC',message):#pass phrase
#				client.say_to_roll(HubServer.rollnameCONTROLLER,message)
#		else:
#			client.say_to_all(message)

if __name__ == '__main__':
	args = sys.argv
	if len(args) == 2:
		port = int(args[1])
	else:
		port = 8801
	print("port={}".format(port))
	#HubServer(port,'garameki.com',logging.INFO)
	HubServer(port,'192.168.3.6',logging.INFO)
