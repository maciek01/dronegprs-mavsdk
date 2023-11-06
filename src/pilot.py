#!/usr/bin/env python3


import sys, traceback
import threading
import time, datetime, json
import asyncio
from mavsdk import System
import pyproj

geodesic = pyproj.Geod(ellps='WGS84')

current_milli_time = lambda: int(time.time() * 1000)

task = None

operatingAlt = 100
operatingSpeed = 15
requestedLat = None
requestedLon = None
savedLat = None
savedLon = None

vehicle = None
vehicleLock = threading.RLock()
URL = None
BAUD = None

#MAVLINK status
curr_tot = 0
voltages = None
bat_percent = 0
heading = 0
statusMessage = ""
statusSev = -1 #https://mavlink.io/en/messages/common.html#MAV_SEVERITY
gps_info = None
pos = None
gps_data = None
home = None
mode = None
armed = None



########################### STATE AND MESSAGE OBSERVERS ########################


async def onPX4_mode(drone):
	global mode
	async for my_mode in drone.telemetry.flight_mode():
		mode = str(my_mode)

async def onPX4_battery(drone):
	global curr_tot
	global voltages
	global bat_percent
	async for battery in drone.telemetry.battery():
		bat_percent = battery.remaining_percent
		voltages = battery.voltage_v

async def onPX4_heading(drone):
	global heading
	async for head in drone.telemetry.heading():
		heading = head.heading_deg

async def onPX4_statusText(drone):
	global statusMessage
	global statusSev
	async for status_text in drone.telemetry.status_text():
		statusMessage = status_text.text
		statusSev = status_text.type

async def onPX4_gps_info(drone):
	global gps_info
	async for my_gps_info in drone.telemetry.gps_info():
		gps_info = my_gps_info

async def print_in_air(drone):
	async for in_air in drone.telemetry.in_air():
		print(f"In air: {in_air}")

async def onPX4_position(drone):
	global pos
	async for my_position in drone.telemetry.position():
		pos = my_position

async def onPX4_raw_gps(drone):
        global gps_data
        async for my_gps in drone.telemetry.raw_gps():
                gps_data = my_gps

async def onPX4_home(drone):
        global home
        async for my_home in drone.telemetry.home():
                home = my_home

async def onPX4_is_armed(drone):
	global armed
	async for is_armed in drone.telemetry.armed():
		armed = is_armed


########################### THREAD HELPERS #####################################

def lockV():
	vehicleLock.acquire()

def unlockV():
	vehicleLock.release()

async def initVehicle():
	global URL
	global BAUD
	global vehicle

	lockV()
	try:
		if vehicle != None:

			#close vehicle
			try:
				vehicle.close()
				vehicle = None
			except Exception as inst:
				vehicle = None

		#open vehicle

		while vehicle == None:
			try:
				# Init the drone

				#PX4
				_vehicle = System()
				#await _vehicle.connect(system_address="udp://:14540")
				print("calling connect " + URL)
				await _vehicle.connect(system_address=URL)
				print("connect accepted " + URL)

				print("Waiting for drone to connect...")
				async for state in _vehicle.core.connection_state():
					if state.is_connected:
						print(f"Connected to vehicle")
						break
				print("Connected via " + URL)
				vehicle = _vehicle


			except Exception as inst:
				vehicle = None
				traceback.print_exc()
				await asyncio.sleep(5)


		#register listeners

		await vehicle.telemetry.set_rate_position(2)
		await vehicle.telemetry.set_rate_camera_attitude(1)
		await vehicle.telemetry.set_rate_in_air(1)
		await vehicle.telemetry.set_rate_landed_state(1)
		await vehicle.telemetry.set_rate_landed_state(1)

		if False:
			asyncio.ensure_future(onPX4_battery(vehicle))
			asyncio.ensure_future(onPX4_mode(vehicle))
			asyncio.ensure_future(onPX4_heading(vehicle))
			asyncio.ensure_future(onPX4_statusText(vehicle))
			asyncio.ensure_future(onPX4_gps_info(vehicle))
			#asyncio.ensure_future(print_in_air(vehicle))
			asyncio.ensure_future(onPX4_position(vehicle))
			asyncio.ensure_future(onPX4_raw_gps(vehicle))
			asyncio.ensure_future(onPX4_home(vehicle))
			asyncio.ensure_future(onPX4_is_armed(vehicle))
		else:
			asyncio.create_task(onPX4_battery(vehicle))
			asyncio.create_task(onPX4_mode(vehicle))
			asyncio.create_task(onPX4_heading(vehicle))
			asyncio.create_task(onPX4_statusText(vehicle))
			asyncio.create_task(onPX4_gps_info(vehicle))
			#asyncio.create_task(print_in_air(vehicle))
			asyncio.create_task(onPX4_position(vehicle))
			asyncio.create_task(onPX4_raw_gps(vehicle))
			asyncio.create_task(onPX4_home(vehicle))
			asyncio.create_task(onPX4_is_armed(vehicle))



	finally:
		unlockV()


async def initPosUpdate():
	asyncio.ensure_future(onPX4_position(vehicle))



####################### MAIN THREAD ############################################

async def pilotMonitor():

	#wait to initialize the pilot

	print("ABOUT to call INIT VEH")

	await initVehicle()

	#task = asyncio.create_task(coro=initPosUpdate(), name="pos")

	#read loop

	while True:
		try:
			await asyncio.sleep(1)
			#if vehicle.last_heartbeat > 5:
			if False:
				print("REINIT VEHICLE CONNECTION")
				await initVehicle()

		except Exception as inst:
			#traceback.print_exc()
			await initVehicle()



###################### INIT HANDLER ############################################
	
async def pilotinit(url, baud):
	global URL
	global BAUD
	global task

	URL = url
	BAUD = baud

	task = asyncio.create_task(coro=pilotMonitor(), name="pilot")

############################ COMMAND HANDLERS ##################################

async def arm(data):

	global vehicle

	lockV()
	try:
		print("ARM")

		await vehicle.action.arm()
		await releaseSticks()
		
		#cancel resume
		savedLat = None
		savedLon = None		
		
		return "OK"	
		
	finally:
		unlockV()

async def disarm(data):

	global vehicle

	lockV()
	try:
		print("DISARM")
			
		await vehicle.action.arm()
		await releaseSticks()
		
		#cancel resume
		savedLat = None
		savedLon = None		
	
		print(" disarming")
		return "OK"	
		
	finally:
		unlockV()


async def takeoff(data):

	global vehicle

	lockV()
	try:
	
		aTargetAltitude = operatingAlt

		#request and wait for the arm thread to be armed	
		await arm(data)

		print("TAKEOFF")

		i = 0
		while not armed and i < 10:
			i = i + 1
			await asyncio.sleep(1)

		if not armed:
			print(" NOT ARMED")
			return "ERROR: NOT ARMED IN 10 secs"
			
		await vehicle.action.set_takeoff_altitude(float(aTargetAltitude))
		await vehicle.action.takeoff()
		await releaseSticks()

		#cancel resume
		savedLat = None
		savedLon = None		
		
		print(" took off")
			

		return "OK"
	finally:
		unlockV()

async def land(data):

	global vehicle
	global requestedLat
	global requestedLon
	global savedLat
	global savedLon
	
	lockV()
	try:
		print("LAND")
		#if not armed:
			#print " NOT ARMED"
			#return "ERROR: NOT ARMED"
			
		await vehicle.action.land()
		await releaseSticks()

		#cancel last goto		
		savedLat = None
		savedLon = None		
		requestedLat = None
		requestedLon = None
		
		print(" landing")
	
		return "OK"

	finally:
		unlockV()

async def position(data):

	global vehicle
	global requestedLat
	global requestedLon
	global savedLat
	global savedLon 
	
	lockV()
	try:
		print("POSITION")
			
		await centerSticks()
		await vehicle.action.hold()
		
		#save last goto
		savedLat = requestedLat
		savedLon = requestedLon
		requestedLat = None
		requestedLon = None
		
			
		return "OK"

	finally:
		unlockV()
		

async def loiter(data):

	global vehicle
	global requestedLat
	global requestedLon
	global savedLat
	global savedLon 
	
	lockV()
	try:
		print("LOITER")
			
		await centerSticks()
		await vehicle.action.hold()
		
		#save last goto
		savedLat = requestedLat
		savedLon = requestedLon
		requestedLat = None
		requestedLon = None
		
			
		return "OK"

	finally:
		unlockV()		

async def auto(data):

	global vehicle
	global requestedLat
	global requestedLon
	global savedLat
	global savedLon 
	
	lockV()
	try:
		print("AUTO")
			
		await releaseSticks()
		await vehicle.mission.start_mission()
		
		#save last goto
		savedLat = None
		savedLon = None
		requestedLat = None
		requestedLon = None
		
			
		return "OK"

	finally:
		unlockV()
		
async def pause(data):

	global vehicle
	global operatingAlt
	global operatingSpeed
	global requestedLat
	global requestedLon
	global savedLat
	global savedLon 
	
	lockV()
	try:
		print("PAUSE")
			
		
		if True:
			#just loiter
			await vehicle.action.hold()

		
			
		return "OK"

	finally:
		unlockV()

async def resume(data):

	global vehicle
	global requestedLat
	global requestedLon
	global savedLat
	global savedLon 
	global geodesic
	
	lockV()
	try:
		print("RESUME")

		if savedLat != None and savedLon != None:
			requestedLat = savedLat
			requestedLon = savedLon
			#vehicle.mode = VehicleMode("GUIDED")

			fwd_azimuth,back_azimuth,distance = geodesic.inv(pos.longitude_deg, pos.latitude_deg, float(requestedLon), float(requestedLat))

			if fwd_azimuth <0:
				fwd_azimuth = 360.0 + fwd_azimuth

			await vehicle.action.goto_location(float(requestedLat), float(requestedLon), float(home.absolute_altitude_m) + float(operatingAlt), float(fwd_azimuth))
			await vehicle.action.set_current_speed(float(operatingSpeed))

			savedLat = None
			savedLon = None
			await releaseSticks()
		
			
		return "OK"

	finally:
		unlockV()

#release channel overrides
async def manual(data):

	global vehicle
	
	lockV()
	try:
		print("MANUAL")
		await vehicle.action.hold()
		await releaseSticks()
		return "OK"

	finally:
		unlockV()

async def reHome(data):
	global vehicle
	
	lockV()
	try:
		print("REHOME - not supported")

		#vehicle.home_location=vehicle.location.global_frame

		return "OK"

	finally:
		unlockV()
		
async def rtl(data):

	global vehicle
	global requestedLat
	global requestedLon
	global savedLat
	global savedLon	   
	
	lockV()
	try:
		print("RTL")
		#if not armed:
			#print " NOT ARMED"
			#return "ERROR: NOT ARMED"

		await vehicle.action.return_to_launch()
		await releaseSticks()

		#cancel last goto
		savedLat = None
		savedLon = None		
		requestedLat = None
		requestedLon = None
		
		print(" returning home")


		return "OK"

	finally:
		unlockV()
		
		
async def goto(data):

	global vehicle
	global operatingAlt
	global requestedLat
	global requestedLon
	global geodesic
	
	lockV()
	try:
		print("GOTO")
		if not armed:
			print(" NOT ARMED")
			return "ERROR: NOT ARMED"
		
		parameters = data['command']['parameters']
		
		for i in parameters:
			if i['name'] == "lat":
				lat = i['value']
				requestedLat = lat
			if i['name'] == "lon":
				lon = i['value']
				requestedLon = lon

		fwd_azimuth,back_azimuth,distance = geodesic.inv(pos.longitude_deg, pos.latitude_deg, float(requestedLon), float(requestedLat))

		if fwd_azimuth <0:
			fwd_azimuth = 360.0 + fwd_azimuth
		
		await vehicle.action.goto_location(float(requestedLat), float(requestedLon), float(home.absolute_altitude_m) + float(operatingAlt), float(fwd_azimuth))
		await vehicle.action.set_current_speed(float(operatingSpeed))

		await releaseSticks()

		#cancel resume
		savedLat = None
		savedLon = None

		print(" going to ")
		return "OK"

	finally:
		unlockV()

async def setHome(data):
	global vehicle
	lockV()
	try:
		print("SETHOME - not supported")
		
		parameters = data['command']['parameters']
		
		for i in parameters:
			if i['name'] == "lat":
				lat = i['value']
			if i['name'] == "lon":
				lon = i['value']
		
		#point1 = LocationGlobal(float(lat), float(lon), vehicle.home_location.alt)
		#if vehicle.home_location != None:
		#	vehicle.home_location=point1

		return "OK"

	finally:
		unlockV()

		
async def alt(data):

	global vehicle
	global operatingAlt
	global requestedLat
	global requestedLon
	global operatingSpeed
	
	lockV()
	try:
		print("ALT")
		
		parameters = data['command']['parameters']
		
		for i in parameters:
			if i['name'] == "alt":
				operatingAlt = i['value']
				if requestedLat != None and requestedLon != None:
					#wont work in LOITER mode
					#vehicle.mode = VehicleMode("GUIDED")
					#point1 = LocationGlobalRelative(float(requestedLat), float(requestedLon), int(operatingAlt))
					#vehicle.simple_goto(point1, int(operatingSpeed))
					fwd_azimuth,back_azimuth,distance = geodesic.inv(pos.longitude_deg, pos.latitude_deg, float(requestedLon), float(requestedLat))

					if fwd_azimuth <0:
						fwd_azimuth = 360.0 + fwd_azimuth

					await vehicle.action.goto_location(float(requestedLat), float(requestedLon), float(home.absolute_altitude_m) + float(operatingAlt), float(fwd_azimuth))
					await vehicle.action.set_current_speed(float(operatingSpeed))
		
		print(" operating alt is now " + operatingAlt)
		return "OK"

	finally:
		unlockV()
		
async def altAdjust(delta):

	global vehicle
	global operatingAlt
	global requestedLat
	global requestedLon
	global operatingSpeed
	global geodesic
	
	lockV()
	try:
		operatingAlt = str(max(int(operatingAlt) + delta, 0))
		
		
		if requestedLat != None and requestedLon != None:
			#wont work in LOITER mode

			fwd_azimuth,back_azimuth,distance = geodesic.inv(pos.longitude_deg, pos.latitude_deg, float(requestedLon), float(requestedLat))

			if fwd_azimuth <0:
				fwd_azimuth = 360.0 + fwd_azimuth

			await vehicle.action.goto_location(float(requestedLat), float(requestedLon), float(home.absolute_altitude_m) + float(operatingAlt), float(fwd_azimuth))
			await vehicle.action.set_current_speed(float(operatingSpeed))

		
		print(" operating alt is now " + operatingAlt)

		return "OK"

	finally:
		unlockV()		
		
async def speed(data):

	global vehicle
	global operatingSpeed
	
	lockV()
	try:
		print("SPEED")
		
		parameters = data['command']['parameters']
		
		for i in parameters:
			if i['name'] == "speed":
				operatingSpeed = i['value']
				await vehicle.action.set_current_speed(float(operatingSpeed))
		
		print(" operating speed is now " + operatingSpeed)
		return "OK"

	finally:
		unlockV()
		
async def speedAdjust(delta):
	global vehicle
	global operatingSpeed
	
	lockV()
	try:
		operatingSpeed = str(max(min(int(operatingSpeed) + delta, 15), 1))
		await vehicle.action.set_current_speed(float(operatingSpeed))
		
		print(" operating speed is now " + operatingSpeed)
		
		return "OK"

	finally:
		unlockV()

async def decAlt1(data):
	print("DECALT1")
	return altAdjust(-1)
	
async def decAlt10(data):
	print("DECALT10")
	return altAdjust(-10)
	
async def incAlt10(data):
	print("INCALT10")
	return altAdjust(10)
	
async def incAlt1(data):
	print("INCALT1")
	return altAdjust(1)
	
async def decSpeed1(data):
	print("DECSPEED1")
	return speedAdjust(-1)
	
async def decSpeed10(data):
	print("DECSPEED10")
	return speedAdjust(-10)
	
async def incSpeed10(data):
	print("INCSPEED10")
	return speedAdjust(10)
	
async def incSpeed1(data):
	print("INCSPEED1")
	return speedAdjust(1)


#override channels - center 
async def centerSticks():
	global vehicle

	#await vehicle.manual_control.set_manual_control_input(
	#	float(0), float(0), float(0.5), float(0)
	#)

	#await vehicle.manual_control.start_position_control()
	
#remove channel overrides
async def releaseSticks():
	global vehicle
	#await vehicle.manual_control.set_manual_control_input(
	#	float(0), float(0), float(0.5), float(0)
	#)
	#await vehicle.action.hold()

	#vehicle.channels.overrides = {}
	


