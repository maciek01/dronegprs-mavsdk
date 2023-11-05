#!/usr/bin/env python3

import asyncio
from mavsdk import System


async def run():
    """
    This is the "main" function.
    It first creates the drone object and initializes it.

    Then it registers tasks to be run in parallel (one can think of them as threads):
        - print_altitude: print the altitude
        - print_flight_mode: print the flight mode
        - observe_is_in_air: this monitors the flight mode and returns when the
                             drone has been in air and is back on the ground.

    Finally, it goes to the actual works: arm the drone, initiate a takeoff
    and finally land.

    Note that "observe_is_in_air" is not necessary, but it ensures that the
    script waits until the drone is actually landed, so that we receive feedback
    during the landing as well.
    """

    # Init the drone
    drone = System()
    await drone.connect(system_address="udp://:14540")

    # Start parallel tasks

    asyncio.ensure_future(print_altitude(drone))
    asyncio.ensure_future(print_flight_mode(drone))
    asyncio.ensure_future(print_heading(drone))

    termination_task = asyncio.ensure_future(observe_is_in_air(drone))

    # Execute the maneuvers
    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")

    await drone.action.set_takeoff_altitude(50)
    await drone.action.set_maximum_speed(20)

    await drone.action.takeoff()

    await asyncio.sleep(60)



    print("-- Landing")
    await drone.action.land()

    # Wait until the drone is landed (instead of returning after 'land' is sent)
    await termination_task


async def print_altitude(drone):
    """ Prints the altitude when it changes """

    previous_altitude = None

    targetAltReached = False

    async for position in drone.telemetry.position():
        altitude = round(position.relative_altitude_m)
        #await asyncio.sleep(1)
        if altitude != previous_altitude:
            previous_altitude = altitude
            print(f"Altitude: {altitude}")
            if altitude > 40 and not targetAltReached:
                targetAltReached = True
                print("Going to the mooon!")
                await drone.action.goto_location(0, 0, round(position.absolute_altitude_m), 0)

async def print_heading(drone):
    """ Prints the heading when it changes """

    previous_heading = None

    async for heading in drone.telemetry.heading():
        await asyncio.sleep(1)
        if heading.heading_deg != previous_heading:
            previous_heading = heading.heading_deg
            print(f"Heading: {previous_heading}")



async def print_flight_mode(drone):
    """ Prints the flight mode when it changes """

    previous_flight_mode = None

    async for flight_mode in drone.telemetry.flight_mode():
        #print("modeloop")
        if flight_mode is not previous_flight_mode:
            previous_flight_mode = flight_mode
            print(f"Flight mode: {flight_mode}")


async def observe_is_in_air(drone):
    """ Monitors whether the drone is flying or not and
    returns after landing """

    was_in_air = False

    async for is_in_air in drone.telemetry.in_air():
        if is_in_air:
            was_in_air = is_in_air

        if was_in_air and not is_in_air:
            await asyncio.get_event_loop().shutdown_asyncgens()
            return


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())


