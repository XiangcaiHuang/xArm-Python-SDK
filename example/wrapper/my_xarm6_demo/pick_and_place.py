#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2019, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

"""
Description: Move Joint
"""

import os
import sys
import time
import math

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI


#######################################################
"""
Just for test example
"""
if len(sys.argv) >= 2:
    ip = sys.argv[1]
else:
    try:
        from configparser import ConfigParser
        parser = ConfigParser()
        parser.read('../robot.conf')
        ip = parser.get('xArm', 'ip')
    except:
        ip = input('Please input the xArm ip address:')
        if not ip:
            print('input error, exit')
            sys.exit(1)
########################################################


arm = XArmAPI(ip)
time.sleep(0.5)
if arm.warn_code != 0:
    arm.clean_warn()
if arm.error_code != 0:
    arm.clean_error()
arm.motion_enable(enable=True)
arm.set_mode(0)
arm.set_state(state=0)

# Gripper Setting
code = arm.set_gripper_mode(0)
print('set gripper mode: location mode, code={}'.format(code))

code = arm.set_gripper_enable(True)
print('set gripper enable, code={}'.format(code))

code = arm.set_gripper_speed(1000)
print('set gripper speed, code={}'.format(code))

speed = 10

# HOME
arm.set_servo_angle(angle=[0.036784, -33.186798, -27.734135, -0.612721, 61.077812, -0.122728], speed=speed, wait=True, is_radian=False)
arm.set_gripper_position(500, wait=True)

# CATCH
arm.set_servo_angle(angle=[-0.1, 79.9, -109.2, -0.8, 29.4, 0.3], speed=speed, wait=True, is_radian=False)
arm.set_gripper_position(50, wait=True)

# HOME
arm.set_servo_angle(angle=[0.036784, -33.186798, -27.734135, -0.612721, 61.077812, -0.122728], speed=speed, wait=True, is_radian=False)

# CATCH
arm.set_servo_angle(angle=[-0.1, 79.9, -109.2, -0.8, 29.4, 0.3], speed=speed, wait=True, is_radian=False)
arm.set_gripper_position(500, wait=True)

# HOME
arm.set_servo_angle(angle=[0.036784, -33.186798, -27.734135, -0.612721, 61.077812, -0.122728], speed=speed, wait=True, is_radian=False)


arm.disconnect()
