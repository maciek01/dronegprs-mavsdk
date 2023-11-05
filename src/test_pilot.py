#!/usr/bin/env python


import time

import pilot

pilot.pilotinit("udp:localhost:14550", 115200)

while True:
	time.sleep(1)
	if pilot.vehicle != None:
		print "Global lat: %s" % pilot.vehicle.location.global_frame.lat
		print "Global lon: %s" % pilot.vehicle.location.global_frame.lon
		print "Global alt: %s" % pilot.vehicle.location.global_frame.alt
		print "Global relative lat: %s" % pilot.vehicle.location.global_relative_frame.lat
		print "Global relative lon: %s" % pilot.vehicle.location.global_relative_frame.lon
		print "Global relative alt: %s" % pilot.vehicle.location.global_relative_frame.alt
		print "Local north: %s" % pilot.vehicle.location.local_frame.north
		print "Local east: %s" % pilot.vehicle.location.local_frame.east
		print "Local down: %s" % pilot.vehicle.location.local_frame.down
		if pilot.vehicle.home_location != None:
			print "Home location lat: %s" % pilot.vehicle.home_location.lat
			print "Home location lon: %s" % pilot.vehicle.home_location.lon
			print "Home location alt: %s" % pilot.vehicle.home_location.alt
		print "GPS visisble sats: %s" % pilot.vehicle.gps_0.satellites_visible
		print "GPS fix type: %s" % pilot.vehicle.gps_0.fix_type
		print "GPS eph: %s cm" % pilot.vehicle.gps_0.eph
		print "GPS epv: %s cm" % pilot.vehicle.gps_0.epv
		print "Last heart beast secs ago %s" % pilot.vehicle.last_heartbeat
		print "Attitude pitch: %s" % pilot.vehicle.attitude.pitch
		print "Attitude roll: %s" % pilot.vehicle.attitude.roll
		print "Attitude yaw: %s" % pilot.vehicle.attitude.yaw
		print "Velocity vx: %s" % pilot.vehicle.velocity[0]
		print "Velocity vy: %s" % pilot.vehicle.velocity[1]
		print "Velocity vz: %s" % pilot.vehicle.velocity[2]
		print "Groundspeed: %s" % pilot.vehicle.groundspeed
		print "Airspeed: %s" % pilot.vehicle.airspeed
		print "Heading: %s" % pilot.vehicle.heading
		print "STATUS state: %s" % pilot.vehicle.system_status.state
		print "Battery: %s V" % (pilot.vehicle.battery.voltage / 1000)
		print "Battery: %s percent" % pilot.vehicle.battery.level
		print "Mode: %s" % pilot.vehicle.mode.name    # settable
		print "Armed: %s" % pilot.vehicle.armed    # settable
		print "Mount status: %s" % pilot.vehicle.mount_status
		print "Rangefinder: %s" % pilot.vehicle.rangefinder
		print "Rangefinder distance: %s" % pilot.vehicle.rangefinder.distance
		print "Rangefinder voltage: %s" % pilot.vehicle.rangefinder.voltage
		print "-------------------------------------"




