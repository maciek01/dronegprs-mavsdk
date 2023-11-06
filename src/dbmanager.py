#!/usr/bin/env python



import sqlite3 as lite
import sys
import Main


con = None


def open(dbname):
	global con

	try:
		con = lite.connect(dbname)
	except lite.Error as e:
		Main.log.info("Error {}:".format(e.args[0]))

def close():
	global con
	if con != None:
		try:
			con.close()
		except lite.Error as e:
			Main.log.info("Error {}:".format(e.args[0]))

def getWaypoints():

	waypoints = None

	try:
		cur = con.cursor()

		cur.execute("SELECT name, lat, lon from waypoints")
		waypoints = cur.fetchall()
	except lite.Error as e:
		Main.log.info("Error {}:".format(e.args[0]))

	return waypoints




