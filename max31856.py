#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

import sys
import time
import spidev


class Max31856:

	spi = None
	DUMMY = 0

	def __init__(self):
		#ここで
		#dev0.0 dev0.1 dev1.0の選択
		#B,T,R,K,...の選択
		#verboseの選択
		#などをするべきだろう
		pass


	def open(self):
		if self.spi is None:
			self.spi = spidev.SpiDev()
			self.spi.open(0,0)			#/sys/bus/spi/devices/dev0.0を使う
			self.spi.mode = 0x03			#モード3 CPOL:1 CPHA:1 ,Especially CPHA must be 1
			self.spi.max_speed_hz = 1000000	#最大クロック周波数

	def close(self):
		if self.spi is not None:
			self.spi.close()
			self.spi = None

	def reset(self):
		#FAULTピンのリセット
		resp = self.spi.xfer2([0x80,0x17])

	def read(self):
		dummy = self.DUMMY

		#通常計測
		#xfer2はcsを下げたまま
		#xferは1バイトごとにcsを下げ上げする
		resp = self.spi.xfer2([0x80,0x55,0x35,0x00,0x3C,0xF6,0x57,0x80,0xFE,0xC0,0x00])	#設定と同時に計測するのでCR0の第6ビットを立てる
		time.sleep(1)			#計測を待つ


		#Faultの検知
		resp = self.spi.xfer([0x0f,dummy])
		if (resp[1] & 0xFF) != 0:
			valueFlt = resp[1]
			valueHJ = ""
			valueCJ = ""
		else:

			valueFlt = resp[1]

			#熱電対の温度を読み込み
			resp = self.spi.xfer2([0x0C,0x0D,0x0E,dummy])
			valueHJ = resp[1] * 256 + resp[2]
			if (resp[1] & 0x80) != 0:
				valueHJ = -1 * (~(valueHJ - 1) & 0x7FFF)	#2の補数の10進数化

			#冷接点の温度を読み込み
			resp = self.spi.xfer2([0x0A,0x0B,dummy])
			valueCJ = (resp[1] << 6)  + (resp[2] >> 2)
			if (resp[1] & 0x80) != 0:
				valueCJ = -1 * (~(valueCJ - 1) & 0x7FFF)	#2の補数の10進数化

		return self._format(valueFlt,valueHJ,valueCJ)

	def _format(self,valueFlt,valueHJ,valueCJ):
		aa = { }
		aa["FAULT"] = valueFlt
		aa["HJ"] = valueHJ
		aa["CJ"] = valueCJ
		return aa

	def write_file(filepath,jsonFormat):
		file = codecs.open(filepath,"w","utf-8")
		file.write(jsonFormat)
		file.close()

if __name__ == '__main__':


	spi0_0 = Max31856()
	if "reset" in sys.argv:
		spi0_0.open()
		spi0_0.reset()
		spi0_0.close()
	else:
		spi0_0.open()
		print(spi0_0.read())
		spi0_0.close()


