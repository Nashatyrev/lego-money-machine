from hub import light_matrix, sound
from hub import button
from hub import port
import motor
import color_sensor
import runloop

from math import sqrt

COLOR_SENSOR_PORT = port.C
MOTOR_BONE_PORT = port.A
MOTOR_ROTATE_PORT = port.E

BONE_VISIBLE_THRESHOLD = 2
COLOR_DETECTION_REF_THRESHOLD = 20

class Bone:
    def __init__(self, nominal, color_hue, position, color_saturation = 0.0):
        self.nominal = nominal
        self.color_hue = color_hue
        self.color_saturation = color_saturation
        self.position = position

    def __str__(self):
        return "Bone {}".format(self.nominal)

BONES_ALL = [
    Bone(1, 212, 50, color_saturation= 0.19),
    Bone(5, 345, 100),
    Bone(10, 199, 150, color_saturation= 0.37),
    Bone(20, 153, 200),
    Bone(50, 240, 250, color_saturation= 0.19),
    Bone(100, 22, 300, color_saturation= 0.2),
    Bone(500, 16, 350, color_saturation= 0.44)
]

def sqr(a): 
    return a * a

def color_distance(bone: Bone, h: float, s: float) -> float:
    if (bone.color_saturation == 0): return abs(bone.color_hue - h)
    else: return sqrt(sqr(bone.color_hue - h) + sqr(360 * (bone.color_saturation - s)))

def find_best_bone_match(h: float, s: float, v: float) -> Bone:
    return sorted(BONES_ALL, key = lambda b: color_distance(b, h, s))[0]


def rgb_to_hsv(r, g, b, o):
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    delta = max_c - min_c
    h = 0
    if delta != 0:
        if max_c == r:
            h = (60 * ((g - b) / delta)) % 360
        elif max_c == g:
            h = (60 * ((b - r) / delta)) + 120
        else:
            h = (60 * ((r - g) / delta)) + 240
    s = 0 if max_c == 0 else (delta / max_c)
    v = max_c
    return h, s, v

APPEAR_OK = 0
APPEAR_TIMEOUT = 1
async def waitAppear(maxIterationCount = 1000): 
    while (color_sensor.reflection(COLOR_SENSOR_PORT) < BONE_VISIBLE_THRESHOLD and maxIterationCount > 0):
        await runloop.sleep_ms(5)
        maxIterationCount -= 1
    return APPEAR_OK if maxIterationCount > 0 else APPEAR_TIMEOUT

async def waitDisappear():
    while (color_sensor.reflection(COLOR_SENSOR_PORT) >= BONE_VISIBLE_THRESHOLD):
        await runloop.sleep_ms(5)

async def detectHsv(): 
    # simple approach 
    # more advanced way would be to accumulate several measurements and aggreagte them (e.g. mean value)
    while(True):
        ref = color_sensor.reflection(COLOR_SENSOR_PORT)
        if (ref >= COLOR_DETECTION_REF_THRESHOLD):
            col = color_sensor.rgbi(COLOR_SENSOR_PORT)
            return rgb_to_hsv(*col)
        else:
            await runloop.sleep_ms(5)

async def loop_iteration(): 
    print("Start")
    motor.run(MOTOR_BONE_PORT, 100)
    rc = await waitAppear()
    if (rc == APPEAR_TIMEOUT):
        print("Appear timeout")
        motor.stop(MOTOR_BONE_PORT)
        return None
    print("Appeared")
    sound.beep(400, 100)
    motor.run(MOTOR_BONE_PORT, 60)
    hsv = await detectHsv()
    motor.stop(MOTOR_BONE_PORT)
    bone = find_best_bone_match(*hsv)
    print("Detected {} with hue {}".format(bone, hsv))
    sound.beep(800, 100)
    await motor.run_to_absolute_position(MOTOR_ROTATE_PORT, bone.position, 100, direction = motor.SHORTEST_PATH, stop = motor.SMART_BRAKE)
    motor.run(MOTOR_BONE_PORT, 60)
    print("Waiting for drop")
    await waitDisappear()
    print("Dropped")
    sound.beep(1600, 100)
    motor.stop(MOTOR_BONE_PORT)
    return bone

async def main():
    while(True):
        light_matrix.write("Hi!")
        while not button.pressed(button.LEFT):
            pass
        sum = 0
        while(True):
            bone = await loop_iteration()
            if (bone == None): break
            # while not button.pressed(button.LEFT):
            #     pass
            sum += bone.nominal
        sound.beep()
        for _ in range(5555):
            await light_matrix.write("${} ".format(sum), 100, 1000)
 

runloop.run(main())
