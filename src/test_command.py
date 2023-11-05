#!/usr/bin/env python

import time, json
import command_processor


command_processor.processorinit()

await command_processor.commandQueue.put(json.loads('{"command":{"name" : "RTL"}}'))
await command_processor.commandQueue.put(json.loads('{"command":{"name" : "LAND"}}'))
await command_processor.commandQueue.put(json.loads('{"command":{"name" : "TAKEOFF"}}'))
await command_processor.commandQueue.put(json.loads('[{"command":{"name" : "TAKEOFF"}}]')[0])

time.sleep(1)


