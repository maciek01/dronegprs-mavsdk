#!/usr/bin/env python


import dbmanager



dbmanager.open("/home/pi/uavonboard.db")

wps = dbmanager.getWaypoints();

dbmanager.close()


for wp in wps:
	print wp[0], wp[1], wp[2]



