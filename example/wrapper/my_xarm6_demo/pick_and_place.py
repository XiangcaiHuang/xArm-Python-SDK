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

def xarm_init():
    arm = XArmAPI("192.168.31.100")
    time.sleep(0.5)

    if arm.warn_code != 0:
        arm.clean_warn()
    if arm.error_code != 0:
        arm.clean_error()

    arm.motion_enable(enable=True)
    arm.set_mode(0)
    arm.set_state(state=0)

    return arm

def xarm_deinit(arm):
    arm.disconnect()

def gripper_init(arm, gripper_speed):
    code = arm.set_gripper_mode(0)
    print('set gripper mode: location mode, code={}'.format(code))

    code = arm.set_gripper_enable(True)
    print('set gripper enable, code={}'.format(code))

    code = arm.set_gripper_speed(gripper_speed)
    print('set gripper speed, code={}'.format(code))

def go_home(arm, speed):
    # HOME
    arm.set_servo_angle(angle=[0.036784, -33.186798, -27.734135, -0.612721, 61.077812, -0.122728], speed=speed, wait=True, is_radian=False)

def go_for_catching(arm, speed):
    # CATCH
    arm.set_servo_angle(angle=[-0.1, 79.9, -109.2, -0.8, 29.4, 0.3], speed=speed, wait=True, is_radian=False)
    
def gripper_open(arm):
    arm.set_gripper_position(850, wait=True)

def gripper_close(arm):
    arm.set_gripper_position(786, wait=True)

###########################################
###########################################
def xarm_gripper_init():
    xarm = xarm_init()
    gripper_speed = 1000
    gripper_init(xarm, gripper_speed)

    return xarm

def xarm_gripper_deinit(arm):
    xarm_deinit(arm)

def read_for_pick_and_place(arm, arm_speed):
    go_home(arm, arm_speed)
    gripper_open(arm)

def xarm_gripper_pick(arm, arm_speed):
    go_for_catching(arm, arm_speed)
    gripper_close(arm)
    time.sleep(1.5)
    go_home(arm, arm_speed)

def xarm_gripper_place(arm, arm_speed):
    go_for_catching(arm, arm_speed)
    gripper_open(arm)
    time.sleep(1)
    go_home(arm, arm_speed)

###########################################
###########################################
# Main entry
###########################################
if __name__ == "__main__":
    xarm = xarm_gripper_init()

    xarm_speed = 10
    read_for_pick_and_place(xarm, xarm_speed)
    xarm_gripper_pick(xarm, xarm_speed)
    xarm_gripper_place(xarm, xarm_speed)

    xarm_gripper_deinit(xarm)
