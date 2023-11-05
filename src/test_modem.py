#!/usr/bin/env python


import modem,time



print ("USB0:", modem.isModem("/dev/ttyUSB0", 38400))
print ("USB1:", modem.isModem("/dev/ttyUSB1", 38400))
print ("USB2:", modem.isModem("/dev/ttyUSB2", 38400))
print ("USB3:", modem.isModem("/dev/ttyUSB3", 38400))
print ("USB4:", modem.isModem("/dev/ttyUSB4", 38400))
print ("USB5:", modem.isModem("/dev/ttyUSB5", 38400))
print ("USB6:", modem.isModem("/dev/ttyUSB6", 38400))

firstModem = modem.findModem([
	"/dev/ttyUSB0",
	"/dev/ttyUSB1",
	"/dev/ttyUSB2",
	"/dev/ttyUSB3",
	"/dev/ttyUSB4",
	"/dev/ttyUSB5",
	"/dev/ttyUSB6"], 38400)

print(firstModem)

if firstModem != "":
	modem.modeminit(firstModem, 38400, 5, True)
	while True:
		print "Status: |" + modem.MODEMSTATUS + "|"
		print "Signal: |" + modem.MODEMSIGNAL + "|"
		print ""
		time.sleep(1)


