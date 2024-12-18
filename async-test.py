from hub import light_matrix
from hub import port
# from threading import Thread
# import thread
import color_sensor 
import distance_sensor
import runloop
import motor
import asyncio 

speed = 200
angle = 90

async def lookaround(count: int):
    for i in range(count):
        await motor.run_to_absolute_position(port.E, angle, speed, direction = motor.CLOCKWISE)
        await motor.run_to_absolute_position(port.E, -angle, speed, direction = motor.COUNTERCLOCKWISE)

async def scan_distance():
    while (True):
        print('Distance: ', distance_sensor.distance(port.F))
        await runloop.sleep_ms(100)

async def fa():
    print("fa() started")
    # do something 
    await motor.run_for_time(port.C, 1000, 1000)
    # do something else after motor stops 

async def fb():
    print("fb() started")
    # do something
    await motor.run_for_time(port.D, 1000, 1000)
    # do something else after motor stops

async def main():

    a = fa()
    b = fb()

    print("Awaiting...")

    await a
    print("a completed")
    await b
    print("b completed")

    await light_matrix.write("Hi!", 100, 200)
    print("Hey!")

    print('Distance: ', distance_sensor.distance(port.F))

    # a = asyncio.create_task(lookaround(1))
    # s = asyncio.create_task(scan_distance())

    # Thread(target = lookaround(1)).start()

    print("Task created")

    # await uasyncio.gather(a, s)

    # while (True):
    #     print('Distance: ', distance_sensor.distance(port.F))
    #     await runloop.sleep_ms(100)

    # print("Started")
    # await runloop.sleep_ms(3000)
    # print("go")
    await a

    # await lookaround(3)
 
    await light_matrix.write("Bye!", 100, 200)
 
runloop.run(main())
