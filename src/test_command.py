#!/usr/bin/env python

import time, json
import command_processor
import pilot
import asyncio
import logger



async def run():
	log = logger.setup_custom_logger('main')

	await command_processor.processorinit(log)
	await pilot.pilotinit(log)

	await command_processor.commandQueue.put(json.loads('{"command":{"name" : "RTL"}}'))
	await command_processor.commandQueue.put(json.loads('{"command":{"name" : "LAND"}}'))
	await command_processor.commandQueue.put(json.loads('{"command":{"name" : "TAKEOFF"}}'))
	await command_processor.commandQueue.put(json.loads('[{"command":{"name" : "TAKEOFF"}}]')[0])

	time.sleep(1)

#main
if __name__ == '__main__':
        asyncio.run(run())

