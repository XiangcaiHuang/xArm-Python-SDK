#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2019, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET
import re
import sys
import json
import time


class BlocklyTool(object):
    def __init__(self, path):
        self.tree = ET.parse(path)
        self.root = self.tree.getroot()
        self.namespace = self.get_namespace()
        self._ops = {
            'EQ': '==',
            'NEQ': '!=',
            'LT': '<',
            'LTE': '<=',
            'GT': '>',
            'GTE': '>='
        }
        self._ops2 = {
            '===': '==',
            '!==': '!=',
            '>=': '>=',
            '>': '>',
            '<=': '<=',
            '<': '<',
        }
        self._code_list = []
        self._hasEvent = False
        self._events = {}
        self._funcs = {}
        self._func_index = 0
        self._index = -1
        self._first_index = 0
        self._is_insert = False
        self.codes = ''
        self._succeed = True
        self._show_comment = False

    @property
    def index(self):
        self._index += 1
        return self._index

    @property
    def func_index(self):
        self._func_index += 1
        return self._func_index

    @property
    def first_index(self):
        self._first_index += 1
        self._index += 1
        return self._first_index

    def _append_to_file(self, data):
        if not self._is_insert:
            self._code_list.append(data)
        else:
            self._code_list.insert(self.first_index, data)

    def _insert_to_file(self, i, data):
        self._code_list.insert(i, data)

    def get_namespace(self):
        try:
            r = re.compile('({.+})')
            if r.search(self.root.tag) is not None:
                ns = r.search(self.root.tag).group(1)
            else:
                ns = ''
        except Exception as e:
            # print(e)
            ns = ''
        return ns

    def get_node(self, tag, root=None):
        if root is None:
            root = self.root
        return root.find(self.namespace + tag)

    def get_nodes(self, tag, root=None, descendant=False, **kwargs):
        if root is None:
            root = self.root
        nodes = []
        if descendant:
            func = root.iter
        else:
            func = root.findall
        for node in func(self.namespace + tag):
            flag = True
            for k, v in kwargs.items():
                if node.attrib[k] != v:
                    flag = False
            if flag:
                nodes.append(node)
        return nodes

    def _init_py3(self, arm=None, init=True, wait_seconds=1, mode=0, state=0, error_exit=True, stop_exit=True):
        self._insert_to_file(self.index, '#!/usr/bin/env python3')
        self._insert_to_file(self.index, '# Software License Agreement (BSD License)\n#')
        self._insert_to_file(self.index, '# Copyright (c) {}, UFACTORY, Inc.'.format(time.localtime(time.time()).tm_year))
        self._insert_to_file(self.index, '# All rights reserved.\n#')
        self._insert_to_file(self.index, '# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>\n')
        self._insert_to_file(self.index, '"""')
        self._insert_to_file(self.index, '# Notice')
        self._insert_to_file(self.index, '#   1. Changes to this file on Studio will not be preserved')
        self._insert_to_file(self.index, '#   2. The next conversion will overwrite the file with the same name')
        self._insert_to_file(self.index, '"""')
        self._insert_to_file(self.index, 'import sys')
        self._insert_to_file(self.index, 'import time')
        self._insert_to_file(self.index, 'import datetime')
        self._insert_to_file(self.index, 'import threading\n')
        self._insert_to_file(self.index, '"""')
        self._insert_to_file(self.index, '# xArm-Python-SDK: https://github.com/xArm-Developer/xArm-Python-SDK')
        self._insert_to_file(self.index, '# git clone git@github.com:xArm-Developer/xArm-Python-SDK.git')
        self._insert_to_file(self.index, '# cd xArm-Python-SDK')
        self._insert_to_file(self.index, '# python setup.py install')
        self._insert_to_file(self.index, '"""')
        self._insert_to_file(self.index, 'from xarm import version')
        self._insert_to_file(self.index, 'from xarm.wrapper import XArmAPI\n')
        self._insert_to_file(self.index, 'print(\'xArm-Python-SDK Version:{}\'.format(version.__version__))\n')
        if arm is None:
            self._insert_to_file(self.index, 'arm = XArmAPI(sys.argv[1])')
        elif isinstance(arm, str):
            self._insert_to_file(self.index, 'arm = XArmAPI(\'{}\')'.format(arm))
        if init:
            self._insert_to_file(self.index, 'arm.clean_warn()')
            self._insert_to_file(self.index, 'arm.clean_error()')
            self._insert_to_file(self.index, 'arm.motion_enable(True)')

            self._insert_to_file(self.index, 'arm.set_mode({})'.format(mode))
            self._insert_to_file(self.index, 'arm.set_state({})'.format(state))
        if wait_seconds > 0:
            self._insert_to_file(self.index, 'time.sleep({})\n'.format(wait_seconds))
        self._insert_to_file(self.index, 'params = {\'speed\': 100, \'acc\': 2000, '
                                         '\'angle_speed\': 20, \'angle_acc\': 500, '
                                         '\'events\': {}, \'variables\': {}, \'quit\': False}')
        if error_exit:
            self._insert_to_file(self.index, '\n\n# Register error/warn changed callback')
            self._insert_to_file(self.index, 'def error_warn_change_callback(data):')
            self._insert_to_file(self.index, '    if data and data[\'error_code\'] != 0:')
            self._insert_to_file(self.index, '        arm.set_state(4)')
            self._insert_to_file(self.index, '        params[\'quit\'] = True')
            self._insert_to_file(self.index, '        print(\'err={}, quit\'.format(data[\'error_code\']))')
            # self._insert_to_file(self.index, '        sys.exit(1)')
            self._insert_to_file(self.index, 'arm.register_error_warn_changed_callback(error_warn_change_callback)')
        if stop_exit:
            self._insert_to_file(self.index, '\n\n# Register state changed callback')
            self._insert_to_file(self.index, 'def state_changed_callback(data):')
            self._insert_to_file(self.index, '    if data and data[\'state\'] == 4:')
            self._insert_to_file(self.index, '        if arm.version_number[0] >= 1 and arm.version_number[1] >= 1 and arm.version_number[2] > 0:')
            self._insert_to_file(self.index, '            params[\'quit\'] = True')
            self._insert_to_file(self.index, '            print(\'state=4, quit\')')
            # self._insert_to_file(self.index, '        sys.exit(1)')
            self._insert_to_file(self.index, 'arm.register_state_changed_callback(state_changed_callback)')

        self._first_index = self._index

    def _finish_py3(self):
        if self._hasEvent:
            self._append_to_file('\n# Main loop')
            self._append_to_file('while arm.connected and arm.error_code == 0 and not params[\'quit\']:')
            self._append_to_file('    time.sleep(1)')

    def to_python(self, path=None, arm=None, init=True, wait_seconds=1, mode=0, state=0,
                  error_exit=True, stop_exit=True, show_comment=False, **kwargs):
        self._show_comment = show_comment
        self._succeed = True
        self._init_py3(arm=arm, init=init, wait_seconds=wait_seconds, mode=mode, state=state, error_exit=error_exit, stop_exit=stop_exit)
        self.parse()
        self._finish_py3()
        self.codes = '\n'.join(self._code_list)
        if path is not None:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('{}\n'.format(self.codes))
        return self._succeed

    def parse(self, root=None, prefix=''):
        blocks = self.get_nodes('block', root=root)
        if blocks:
            for block in blocks:
                is_statement = root is None
                if root is not None:
                    if root.tag == self.namespace + 'statement':
                        is_statement = True
                while block is not None:
                    if not is_statement:
                        block = self.get_node('next', root=block)
                        if not block:
                            break
                        block = self.get_node('block', root=block)
                    else:
                        is_statement = False
                    if block.attrib.get('disabled', False):
                        continue
                    func = getattr(self, '_handle_{}'.format(block.attrib['type']), None)
                    if func:
                        func(block, prefix)
                    else:
                        self._succeed = False
                        print('block {} can\'t convert to python code'.format(block.attrib['type']))
        # block = self.get_node('block', root=root)
        # while block is not None:
        #     if not is_statement:
        #         block = self.get_node('next', root=block)
        #         if not block:
        #             break
        #         block = self.get_node('block', root=block)
        #     else:
        #         is_statement = False
        #     if block.attrib.get('disabled', False):
        #         continue
        #     func = getattr(self, '_handle_{}'.format(block.attrib['type']), None)
        #     if func:
        #         func(block, prefix)
        #     else:
        #         print('block {} can\'t convert to python code'.format(block.attrib['type']))

    def _handle_set_speed(self, block, prefix=''):
        field = self.get_node('field', root=block)
        if field is not None:
            value = field.text
        else:
            value = self.get_node('value', root=block)
            value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}params[\'speed\'] = {}'.format(prefix, value))

    def _handle_set_acceleration(self, block, prefix=''):
        field = self.get_node('field', root=block)
        if field is not None:
            value = field.text
        else:
            value = self.get_node('value', root=block)
            value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}params[\'acc\'] = {}'.format(prefix, value))

    def _handle_set_angle_speed(self, block, prefix=''):
        field = self.get_node('field', root=block)
        if field is not None:
            value = field.text
        else:
            value = self.get_node('value', root=block)
            value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}params[\'angle_speed\'] = {}'.format(prefix, value))

    def _handle_set_angle_acceleration(self, block, prefix=''):
        field = self.get_node('field', root=block)
        if field is not None:
            value = field.text
        else:
            value = self.get_node('value', root=block)
            value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}params[\'angle_acc\'] = {}'.format(prefix, value))

    def _handle_reset(self, block, prefix=''):
        self._append_to_file('{}if arm.error_code == 0 and not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.reset()'.format(prefix))

    def _handle_sleep(self, block, prefix=''):
        value = self.get_node('value', root=block)
        value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}# set pause time'.format(prefix))
        self._append_to_file('{}if arm.error_code == 0 and not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.set_pause_time({})'.format(prefix, value))

    def _handle_move(self, block, prefix=''):
        fields = self.get_nodes('field', root=block)
        orientation = fields[0].text
        wait = fields[1].text == 'TRUE'
        value = fields[2].text
        if orientation == 'forward':
            param = 'x'
        elif orientation == 'backward':
            param = 'x'
            value = '-{}'.format(value)
        elif orientation == 'left':
            param = 'y'
        elif orientation == 'right':
            param = 'y'
            value = '-{}'.format(value)
        elif orientation == 'up':
            param = 'z'
        elif orientation == 'down':
            param = 'z'
            value = '-{}'.format(value)
        else:
            return

        if self._show_comment:
            self._append_to_file('{}# relative move'.format(prefix))
        self._append_to_file('{}if arm.error_code == 0 and not params[\'quit\']:'.format(prefix))
        self._append_to_file(
            '{}    if arm.set_position({}={}, speed=params[\'speed\'], mvacc=params[\'acc\'], '
            'relative=True, wait={}) < 0:'.format(prefix, param, value, wait))
        self._append_to_file(
            '{}        params[\'quit\'] = True'.format(prefix))

    def _handle_move_arc_to(self, block, prefix=''):
        value = self.get_node('value', root=block)
        p_block = self.get_node('block', root=value)
        fields = self.get_nodes('field', root=p_block)
        values = []
        for field in fields[:-2]:
            values.append(float(field.text))
        radius = float(fields[-2].text)
        wait = fields[-1].text == 'TRUE'
        if self._show_comment:
            self._append_to_file('{}# move{}line and {}'.format(
                prefix, ' arc ' if float(radius) >= 0 else ' ', 'wait' if wait else 'no wait'))
        self._append_to_file('{}if arm.error_code == 0 and not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    if arm.set_position(*{}, speed=params[\'speed\'], mvacc=params[\'acc\'], '
                             'radius={}, wait={}) < 0:'.format(prefix, values, radius, wait))
        self._append_to_file('{}        params[\'quit\'] = True'.format(prefix))

    def _handle_move_circle(self, block, prefix=''):
        values = self.get_nodes('value', root=block)
        percent = self.get_nodes('field', root=values[2], descendant=True)[0].text
        percent = round(float(percent) / 360 * 100, 2)
        wait = self.get_nodes('field', root=values[3], descendant=True)[0].text == 'TRUE'

        p1_block = self.get_node('block', root=values[0])
        fields = self.get_nodes('field', root=p1_block)
        pose1 = []
        for field in fields:
            pose1.append(float(field.text))

        p2_block = self.get_node('block', root=values[1])
        fields = self.get_nodes('field', root=p2_block)
        pose2 = []
        for field in fields:
            pose2.append(float(field.text))
        if self._show_comment:
            self._append_to_file('{}# move circle and {}'.format(
                prefix, 'wait' if wait else 'no wait'))
        self._append_to_file('{}if arm.error_code == 0 and not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    if arm.move_circle({}, {}, {}, speed=params[\'speed\'], mvacc=params[\'acc\'], '
                             'wait={}) < 0:'.format(prefix, pose1, pose2, percent, wait))
        self._append_to_file('{}        params[\'quit\'] = True'.format(prefix))

    def _handle_move_7(self, block, prefix=''):
        value = self.get_node('value', root=block)
        p_block = self.get_node('block', root=value)
        fields = self.get_nodes('field', root=p_block)
        values = []
        for field in fields[:-1]:
            values.append(float(field.text))
        wait = fields[-1].text == 'TRUE'
        if self._show_comment:
            self._append_to_file('{}# move joint and {}'.format(prefix, 'wait' if wait else 'no wait'))
        self._append_to_file('{}if arm.error_code == 0 and not params[\'quit\']:'.format(prefix))
        self._append_to_file(
            '{}    arm.set_servo_angle(angle={}, speed=params[\'angle_speed\'], '
            'mvacc=params[\'angle_acc\'], wait={})'.format(prefix, values, wait))

    def _handle_move_joints(self, block, prefix=''):
        fields = self.get_nodes('field', root=block)
        values = []
        for field in fields[:-1]:
            values.append(float(field.text))
        wait = fields[-1].text == 'TRUE'
        if self._show_comment:
            self._append_to_file('{}# move joint and {}'.format(prefix, 'wait' if wait else 'no wait'))
        self._append_to_file('{}if arm.error_code == 0 and not params[\'quit\']:'.format(prefix))
        self._append_to_file(
            '{}    if arm.set_servo_angle(angle={}, speed=params[\'angle_speed\'], '
            'mvacc=params[\'angle_acc\'], wait={}) < 0:'.format(prefix, values, wait))
        self._append_to_file(
            '{}        params[\'quit\'] = True'.format(prefix))

    def _handle_move_cartesian(self, block, prefix=''):
        fields = self.get_nodes('field', root=block)
        values = []
        for field in fields[:-2]:
            values.append(float(field.text))
        radius = float(fields[-2].text)
        wait = fields[-1].text == 'TRUE'
        if self._show_comment:
            self._append_to_file('{}# move{}line and {}'.format(
                prefix, ' arc ' if float(radius) >= 0 else ' ', 'wait' if wait else 'no wait'))
        self._append_to_file('{}if arm.error_code == 0 and not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    if arm.set_position(*{}, speed=params[\'speed\'], mvacc=params[\'acc\'], '
                             'radius={}, wait={}) < 0:'.format(prefix, values, radius, wait))
        self._append_to_file('{}        params[\'quit\'] = True'.format(prefix))

    def _handle_motion_stop(self, block, prefix=''):
        if self._show_comment:
            self._append_to_file('{}# emergency stop'.format(prefix))
        self._append_to_file('{}arm.emergency_stop()'.format(prefix))

    def _handle_studio_run_traj(self, block, prefix=''):
        filename = self.get_node('field', root=block).text
        value = self.get_node('value', root=block)
        times = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    if arm.playback_trajectory(times={}, filename=\'{}\', wait=True) != 0:'.format(prefix, times, filename))
        self._append_to_file('{}        params[\'quit\'] = True'.format(prefix))

    def _handle_tool_message(self, block, prefix=''):
        fields = self.get_nodes('field', block)
        msg = json.dumps(fields[-1].text, ensure_ascii=False)
        self._append_to_file('{}print({})'.format(prefix, msg))
        # msg = fields[-1].text
        # self._append_to_file('{}print(\'{}\')'.format(prefix, message))
        # self._append_to_file('{}print(\'{{}}\'.format(\'{}\'))'.format(prefix, message))

    def _handle_tool_console(self, block, prefix=''):
        fields = self.get_nodes('field', block)
        msg = json.dumps(fields[1].text, ensure_ascii=False)
        self._append_to_file('{}print({})'.format(prefix, msg))
        # msg = fields[1].text
        # self._append_to_file('{}print(\'{}\')'.format(prefix, msg))

    def _handle_tool_console_with_variable(self, block, prefix=''):
        fields = self.get_nodes('field', block)
        msg = fields[1].text
        # msg = json.dumps(fields[1].text, ensure_ascii=False)
        value = self.get_node('value', block)
        expression = self.__get_condition_expression(value)
        # self._append_to_file('{}value = {}'.format(prefix, expression))
        if msg:
            self._append_to_file('{}print({}.format({}))'.format(prefix, json.dumps(msg+'{}', ensure_ascii=False), expression))
            # self._append_to_file('{}print(\'{}{{}}\'.format({}))'.format(prefix, msg, expression))
        else:
            self._append_to_file('{}print(\'{{}}\'.format({}))'.format(prefix, expression))

    def _handle_wait(self, block, prefix=''):
        value = self.get_node('value', root=block)
        value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    time.sleep({})'.format(prefix, value))

    def _handle_gpio_get_digital(self, block, prefix=''):
        io = self.get_node('field', block).text
        if self._show_comment:
            self._append_to_file('{}# get tgpio-{} digital'.format(prefix, io))
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.get_tgpio_digital({})'.format(prefix, io))

    def _handle_gpio_get_analog(self, block, prefix=''):
        io = self.get_node('field', block).text
        if self._show_comment:
            self._append_to_file('{}# get tgpio-{} analog'.format(prefix, io))
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.get_tgpio_analog({})'.format(prefix, io))

    def _handle_gpio_set_digital(self, block, prefix=''):
        fields = self.get_nodes('field', root=block)
        io = fields[0].text
        value = 0 if fields[1].text == 'LOW' else 1
        # io = self.get_node('field', block).text
        # value = self.get_node('value', root=block)
        # value = self.get_nodes('field', root=value, descendant=True)[0].text
        if self._show_comment:
            self._append_to_file('{}# set tgpio-{} digital'.format(prefix, io))
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.set_tgpio_digital({}, {})'.format(prefix, io, value))

    def _handle_set_suction_cup(self, block, prefix=''):
        field = self.get_node('field', root=block)
        on = True if field.text == 'ON' else False
        # io = self.get_node('field', block).text
        # value = self.get_node('value', root=block)
        # value = self.get_nodes('field', root=value, descendant=True)[0].text
        if self._show_comment:
            self._append_to_file('{}# set_suction_cup({})'.format(prefix, on))
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.set_suction_cup({})'.format(prefix, on))

    def _handle_gpio_get_controller_digital(self, block, prefix=''):
        io = self.get_node('field', block).text
        if self._show_comment:
            self._append_to_file('{}# get cgpio-{} digital'.format(prefix, io))
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.get_cgpio_digital({})'.format(prefix, io))

    def _handle_gpio_get_controller_analog(self, block, prefix=''):
        io = self.get_node('field', block).text
        if self._show_comment:
            self._append_to_file('{}# get cgpio-{} analog'.format(prefix, io))
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.get_cgpio_analog({})'.format(prefix, io))

    def _handle_gpio_set_controller_digital(self, block, prefix=''):
        fields = self.get_nodes('field', root=block)
        io = fields[0].text
        value = 0 if fields[1].text == 'LOW' else 1
        # io = self.get_node('field', block).text
        # value = self.get_node('value', root=block)
        # value = self.get_nodes('field', root=value, descendant=True)[0].text
        if self._show_comment:
            self._append_to_file('{}# set cgpio-{} digital'.format(prefix, io))
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.set_cgpio_digital({}, {})'.format(prefix, io, value))

    def _handle_gpio_set_controller_analog(self, block, prefix=''):
        io = self.get_node('field', block).text
        value = self.get_node('value', root=block)
        value = self.get_nodes('field', root=value, descendant=True)[0].text
        if self._show_comment:
            self._append_to_file('{}# set cgpio-{} digital'.format(prefix, io))
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.set_cgpio_analog({}, {})'.format(prefix, io, value))

    def _handle_set_collision_sensitivity(self, block, prefix=''):
        value = self.get_node('value', root=block)
        value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.set_collision_sensitivity({})'.format(prefix, value))

    def _handle_set_teach_sensitivity(self, block, prefix=''):
        value = self.get_node('value', root=block)
        value = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.set_teach_sensitivity({})'.format(prefix, value))

    def _handle_set_tcp_load(self, block, prefix=''):
        fields = self.get_nodes('field', root=block)
        weight = fields[1].text
        x = fields[2].text
        y = fields[3].text
        z = fields[4].text
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.set_tcp_load({}, [{}, {}, {}])'.format(prefix, weight, x, y, z))
        self._append_to_file('{}    arm.set_state(0)'.format(prefix))

        # values = self.get_nodes('value', root=block)
        # weight = self.get_nodes('field', root=values[0], descendant=True)[0].text
        # x = self.get_nodes('field', root=values[1], descendant=True)[0].text
        # y = self.get_nodes('field', root=values[2], descendant=True)[0].text
        # z = self.get_nodes('field', root=values[3], descendant=True)[0].text
        # self._append_to_file('{}arm.set_tcp_load({}, [{}, {}, {}])'.format(prefix, weight, x, y, z))
        # self._append_to_file('{}arm.set_state(0)'.format(prefix))

    def _handle_set_gravity_direction(self, block, prefix=''):
        values = self.get_nodes('value', root=block)
        x = self.get_nodes('field', root=values[0], descendant=True)[0].text
        y = self.get_nodes('field', root=values[1], descendant=True)[0].text
        z = self.get_nodes('field', root=values[2], descendant=True)[0].text
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.set_gravity_direction([{}, {}, {}])'.format(prefix, x, y, z))

    def _handle_set_tcp_offset(self, block, prefix=''):
        fields = self.get_nodes('field', root=block)
        x = fields[1].text
        y = fields[2].text
        z = fields[3].text
        roll = fields[4].text
        pitch = fields[5].text
        yaw = fields[6].text
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.set_tcp_offset([{}, {}, {}, {}, {}, {}])'.format(prefix, x, y, z, roll, pitch, yaw))
        self._append_to_file('{}    arm.set_state(0)'.format(prefix))

        # values = self.get_nodes('value', root=block)
        # x = self.get_nodes('field', root=values[0], descendant=True)[0].text
        # y = self.get_nodes('field', root=values[1], descendant=True)[0].text
        # z = self.get_nodes('field', root=values[2], descendant=True)[0].text
        # roll = self.get_nodes('field', root=values[3], descendant=True)[0].text
        # pitch = self.get_nodes('field', root=values[4], descendant=True)[0].text
        # yaw = self.get_nodes('field', root=values[5], descendant=True)[0].text
        # self._append_to_file('{}arm.set_tcp_offset([{}, {}, {}, {}, {}, {}])'.format(prefix, x, y, z, roll, pitch, yaw))
        # self._append_to_file('{}arm.set_state(0)'.format(prefix))

    def _handle_gripper_set(self, block, prefix=''):
        fields = self.get_nodes('field', root=block)
        if fields is not None and len(fields) >= 3:
            pos = fields[0].text
            speed = fields[1].text
            wait = fields[2].text == 'TRUE'
        else:
            values = self.get_nodes('value', root=block)
            pos = self.get_nodes('field', root=values[0], descendant=True)[0].text
            speed = self.get_nodes('field', root=values[1], descendant=True)[0].text
            wait = self.get_nodes('field', root=values[2], descendant=True)[0].text == 'TRUE'
        if self._show_comment:
            self._append_to_file('{}# set gripper position and '.format(prefix, 'wait' if wait else 'no wait'))
        self._append_to_file('{}if not params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    arm.set_gripper_position({}, wait={}, speed={}, auto_enable=True)'.format(prefix, pos, wait, speed))

    def __handle_gpio_event(self, gpio_type, block, prefix=''):
        fields = self.get_nodes('field', root=block)
        io = fields[0].text
        trigger = fields[1].text

        if 'gpio' not in self._events:
            num = 1
        else:
            if gpio_type not in self._events['gpio']:
                num = 1
            else:
                num = self._events['gpio'][gpio_type] + 1

        if gpio_type == 'tgpio_digital':
            name = 'tool_gpio_{}_digital_is_changed_callback_{}'.format(io, num)
            self._append_to_file('\n\n{}# Define Tool GPIO-{} DIGITAL is changed callback'.format(prefix, io))
        elif gpio_type == 'tgpio_analog':
            name = 'tool_gpio_{}_analog_is_changed_callback_{}'.format(io, num)
            self._append_to_file('\n\n{}# Define Tool GPIO-{} ANALOG is changed callback'.format(prefix, io))
        elif gpio_type == 'cgpio_digital':
            name = 'controller_gpio_{}_digital_is_changed_callback_{}'.format(io, num)
            self._append_to_file('\n\n{}# Define Contoller GPIO-{} DIGITAL is {} callback'.format(prefix, io, trigger))
        elif gpio_type == 'cgpio_analog':
            name = 'controller_gpio_{}_digital_is_changed_callback_{}'.format(io, num)
            self._append_to_file('\n\n{}# Define Contoller GPIO-{} ANALOG is changed callback'.format(prefix, io))
        else:
            return
        self._append_to_file('{}def {}():'.format(prefix, name))
        old_prefix = prefix
        prefix = '    ' + prefix
        statement = self.get_node('statement', root=block)
        if statement:
            self.parse(statement, prefix)
        else:
            self._append_to_file('{}pass'.format(prefix))

        if gpio_type == 'tgpio_digital':
            self._append_to_file(
                '\n{}params[\'events\'][\'gpio\'].tgpio_digital_callbacks.append({{'
                '\'io\': {}, \'trigger\': {}, \'op\': \'==\', \'callback\': {}}})'.format(
                    old_prefix, io, 1 if trigger == 'HIGH' else 0, name))
        elif gpio_type == 'tgpio_analog':
            op = self._ops2.get(trigger)
            trigger = fields[2].text
            self._append_to_file(
                '\n{}params[\'events\'][\'gpio\'].tgpio_analog_callbacks.append({{'
                '\'io\': {}, \'trigger\': {}, \'op\': \'{}\', \'callback\': {}}})'.format(
                    old_prefix, io, trigger, op, name))
        elif gpio_type == 'cgpio_digital':
            self._append_to_file(
                '\n{}params[\'events\'][\'gpio\'].cgpio_callbacks.append({{'
                '\'type\': \'digital\', \'io\': {}, \'trigger\': {}, \'op\': \'{}\', \'callback\': {}}})'.format(
                    old_prefix, io, 1 if trigger == 'HIGH' else 0, '==', name))
        elif gpio_type == 'cgpio_analog':
            op = self._ops2.get(trigger)
            trigger = fields[2].text
            self._append_to_file(
                '\n{}params[\'events\'][\'gpio\'].cgpio_callbacks.append({{'
                '\'type\': \'analog\', \'io\': {}, \'trigger\': {}, \'op\': \'{}\', \'callback\': {}}})'.format(
                    old_prefix, io, trigger, op, name))
        else:
            return
        self._append_to_file('{}if not params[\'events\'][\'gpio\'].alive:'.format(old_prefix))
        self._append_to_file('{}    params[\'events\'][\'gpio\'].start()'.format(old_prefix))

        if 'gpio' not in self._events:
            name2 = 'EventGPIOThread'
            self._insert_to_file(self.index, '\n\n# Define GPIO callback handle thread')
            self._insert_to_file(self.index, 'class {}(threading.Thread):'.format(name2))
            self._insert_to_file(self.index, '    def __init__(self, *args, **kwargs):'
                                             '\n        threading.Thread.__init__(self, *args, **kwargs)')
            self._insert_to_file(self.index, '        self.daemon = True')
            self._insert_to_file(self.index, '        self.alive = False')

            self._insert_to_file(self.index, '        self.values = {'
                                             '\'tgpio\': {\'digital\': [-1] * 2, \'analog\': [-1] * 2},'
                                             '\'cgpio\': {\'digital\': [-1] * 8, \'analog\': [-1] * 2}}')

            self._insert_to_file(self.index, '        self.tgpio_digital_callbacks = []')
            self._insert_to_file(self.index, '        self.tgpio_analog_callbacks = []')
            self._insert_to_file(self.index, '        self.cgpio_callbacks = []')

            self._insert_to_file(self.index, '\n    def run(self):')
            self._insert_to_file(self.index, '        self.alive = True')
            self._insert_to_file(self.index, '        while arm.connected and arm.error_code == 0 and not params[\'quit\']:')

            self._insert_to_file(self.index, '            if len(self.tgpio_digital_callbacks) > 0:')
            self._insert_to_file(self.index, '                _, values = arm.get_tgpio_digital()')
            self._insert_to_file(self.index, '                if _ == 0:')
            self._insert_to_file(self.index, '                    for item in self.tgpio_digital_callbacks:')
            self._insert_to_file(self.index, '                        for io in range(2):')
            self._insert_to_file(self.index, '                            if item[\'io\'] == io and eval(\'{} {} {}\'.format(values[io], item[\'op\'], item[\'trigger\'])) and not eval(\'{} {} {}\'.format(self.values[\'tgpio\'][\'digital\'][io], item[\'op\'], item[\'trigger\'])):')
            # self._insert_to_file(self.index, '                            if item[\'io\'] == io and values[io] {op} item[\'trigger\'] and not (values[io] {op} self.values[\'tgpio\'][\'digital\'][io]):'.format(op='item[\'op\']'))
            self._insert_to_file(self.index, '                                item[\'callback\']()')
            self._insert_to_file(self.index, '                    self.values[\'tgpio\'][\'digital\'] = values')

            self._insert_to_file(self.index, '            if len(self.tgpio_analog_callbacks) > 0:')
            self._insert_to_file(self.index, '                _, values = arm.get_tgpio_analog()')
            self._insert_to_file(self.index, '                if _ == 0:')
            self._insert_to_file(self.index, '                    for item in self.tgpio_analog_callbacks:')
            self._insert_to_file(self.index, '                        for io in range(2):')
            self._insert_to_file(self.index, '                            if item[\'io\'] == io and eval(\'{} {} {}\'.format(values[io], item[\'op\'], item[\'trigger\'])) and not eval(\'{} {} {}\'.format(self.values[\'tgpio\'][\'analog\'][io], item[\'op\'], item[\'trigger\'])):')
            # self._insert_to_file(self.index, '                            if item[\'io\'] == io and values[io] {op} item[\'trigger\'] and not (values[io] {op} self.values[\'tgpio\'][\'analog\'][io]):'.format(op='item[\'op\']'))
            self._insert_to_file(self.index, '                                item[\'callback\']()')
            self._insert_to_file(self.index, '                    self.values[\'tgpio\'][\'analog\'] = values')

            self._insert_to_file(self.index, '            if len(self.cgpio_callbacks) > 0:')
            self._insert_to_file(self.index, '                _, values = arm.get_cgpio_state()')
            self._insert_to_file(self.index, '                if _ == 0:')
            self._insert_to_file(self.index, '                    digitals = [values[3] >> i & 0x01 if values[10][i] in [0, 255] else 1 for i in range(8)]')
            self._insert_to_file(self.index, '                    analogs = [values[6], values[7]]')
            self._insert_to_file(self.index, '                    for item in self.cgpio_callbacks:')
            self._insert_to_file(self.index, '                        if item[\'type\'] == \'digital\':')
            self._insert_to_file(self.index, '                            for io in range(8):')
            self._insert_to_file(self.index, '                                if item[\'io\'] == io and eval(\'{} {} {}\'.format(digitals[io], item[\'op\'], item[\'trigger\'])) and not eval(\'{} {} {}\'.format(self.values[\'cgpio\'][\'digital\'][io], item[\'op\'], item[\'trigger\'])):')
            # self._insert_to_file(self.index, '                                if item[\'io\'] == io and values[io] {op} item[\'trigger\'] and not (values[io] {op} self.values[\'cgpio\'][\'digital\'][io]):'.format(op='item[\'op\']'))
            self._insert_to_file(self.index, '                                    item[\'callback\']()')
            self._insert_to_file(self.index, '                        elif item[\'type\'] == \'analog\':')
            self._insert_to_file(self.index, '                            for io in range(2):')
            self._insert_to_file(self.index, '                                if item[\'io\'] == io and eval(\'{} {} {}\'.format(analogs[io], item[\'op\'], item[\'trigger\'])) and not eval(\'{} {} {}\'.format(self.values[\'cgpio\'][\'analog\'][io], item[\'op\'], item[\'trigger\'])):')
            # self._insert_to_file(self.index, '                                if item[\'io\'] == io and values[io] {op} item[\'trigger\'] and not (values[io] {op} self.values[\'cgpio\'][\'analog\'][io]):'.format(op='item[\'op\']'))
            self._insert_to_file(self.index, '                                    item[\'callback\']()')
            self._insert_to_file(self.index, '                    self.values[\'cgpio\'][\'digital\'] = digitals')
            self._insert_to_file(self.index, '                    self.values[\'cgpio\'][\'analog\'] = analogs')

            self._insert_to_file(self.index, '            time.sleep(0.1)')
            self._insert_to_file(self.index, '\nparams[\'events\'][\'gpio\'] = {}()'.format(name2))
            self._events['gpio'] = {}

        if gpio_type not in self._events['gpio']:
            self._events['gpio'][gpio_type] = 2
        else:
            self._events['gpio'][gpio_type] += 1

        self._hasEvent = True

    def _handle_event_gpio_digital(self, block, prefix=''):
        self.__handle_gpio_event('tgpio_digital', block, prefix)

    def _handle_event_gpio_analog(self, block, prefix=''):
        self.__handle_gpio_event('tgpio_analog', block, prefix)

    def _handle_event_gpio_controller_digital(self, block, prefix):
        self.__handle_gpio_event('cgpio_digital', block, prefix)

    def _handle_event_gpio_controller_analog(self, block, prefix):
        self.__handle_gpio_event('cgpio_analog', block, prefix)

    # def _handle_event_gpio_digital(self, block, prefix=''):
    #     fields = self.get_nodes('field', root=block)
    #     io = fields[0].text
    #     trigger = fields[1].text
    #
    #     if 'gpio' not in self._events:
    #         num = 1
    #     else:
    #         num = self._events['gpio'] + 1
    #     name = '{}_io{}_is_{}_{}'.format(block.attrib['type'], io, trigger.lower(), num)
    #     self._append_to_file('\n\n{}# Define TGPIO-{} is {} callback'.format(prefix, io, trigger))
    #     self._append_to_file('{}def {}():'.format(prefix, name))
    #     old_prefix = prefix
    #     prefix = '    ' + prefix
    #     statement = self.get_node('statement', root=block)
    #     if statement:
    #         self.parse(statement, prefix)
    #     else:
    #         self._append_to_file('{}pass'.format(prefix))
    #     self._append_to_file('\n{}params[\'events\'][\'gpio\'].callbacks[\'IO{}\'][{}].append({})'.format(
    #         old_prefix, io, 1 if trigger == 'HIGH' else 0, name))
    #     self._append_to_file('{}if not params[\'events\'][\'gpio\'].alive:'.format(old_prefix))
    #     self._append_to_file('{}    params[\'events\'][\'gpio\'].start()'.format(old_prefix))
    #
    #     if 'gpio' not in self._events:
    #         name2 = 'EventGPIOThread'.format(io, trigger.capitalize())
    #         self._insert_to_file(self.index, '\n\n# Define GPIO callback handle thread')
    #         self._insert_to_file(self.index, 'class {}(threading.Thread):'.format(name2))
    #         self._insert_to_file(self.index, '    def __init__(self, *args, **kwargs):'
    #                                          '\n        threading.Thread.__init__(self, *args, **kwargs)')
    #         self._insert_to_file(self.index, '        self.daemon = True')
    #         self._insert_to_file(self.index, '        self.alive = False')
    #         self._insert_to_file(self.index, '        self.digital = [-1, -1]')
    #         self._insert_to_file(self.index, '        self.callbacks = {\'IO0\': {0: [], 1: []}, '
    #                                          '\'IO1\': {0: [], 1: []}}')
    #         self._insert_to_file(self.index, '\n    def run(self):')
    #         self._insert_to_file(self.index, '        self.alive = True')
    #         self._insert_to_file(self.index, '        while arm.connected and arm.error_code == 0:')
    #         self._insert_to_file(self.index, '            _, digital = arm.get_tgpio_digital()')
    #         self._insert_to_file(self.index, '            if _ == 0:')
    #         self._insert_to_file(self.index, '                if digital[0] != self.digital[0]:')
    #         self._insert_to_file(self.index, '                    for callback in self.callbacks[\'IO0\'][digital[0]]:')
    #         self._insert_to_file(self.index, '                        callback()')
    #         self._insert_to_file(self.index, '                if digital[1] != self.digital[1]:')
    #         self._insert_to_file(self.index, '                    for callback in self.callbacks[\'IO1\'][digital[1]]:')
    #         self._insert_to_file(self.index, '                        callback()')
    #         self._insert_to_file(self.index, '            if _ == 0:')
    #         self._insert_to_file(self.index, '                self.digital = digital')
    #         self._insert_to_file(self.index, '            time.sleep(0.1)')
    #         self._insert_to_file(self.index, '\nparams[\'events\'][\'gpio\'] = {}()'.format(name2))
    #
    #     if 'gpio' not in self._events:
    #         self._events['gpio'] = 2
    #     else:
    #         self._events['gpio'] += 1
    #
    #     self._hasEvent = True

    def _handle_procedures_defnoreturn(self, block, prefix=''):
        if not self._funcs:
            name = 'MyDef'
            self._insert_to_file(self.first_index, '\n\n# Define Mydef class')
            self._insert_to_file(self.first_index, 'class {}(object):'.format(name))
            self._insert_to_file(self.first_index,
                                 '    def __init__(self, *args, **kwargs):\n        pass')
        field = self.get_node('field', block).text
        if not field:
            field = '1'
        if field not in self._funcs:
            name = 'function_{}'.format(self.func_index)
        else:
            name = self._funcs[field]
        self._is_insert = True
        try:
            self._append_to_file('\n    @classmethod')
            self._append_to_file('    def {}(cls):'.format(name))
            prefix = '        '
            comment = self.get_node('comment', block).text
            self._append_to_file('{}"""'.format(prefix))
            self._append_to_file('{}{}'.format(prefix, comment))
            self._append_to_file('{}"""'.format(prefix))
            statement = self.get_node('statement', root=block)
            if statement:
                self.parse(statement, prefix)
            else:
                self._append_to_file('{}pass'.format(prefix))
            self._funcs[field] = name
        except:
            self._succeed = False
        self._is_insert = False

    def _handle_procedures_defreturn(self, block, prefix=''):
        self._handle_procedures_defnoreturn(block, prefix)
        value = self.get_node('value', root=block)
        expression = self.__get_condition_expression(value)
        self._is_insert = True
        prefix = '        '
        self._append_to_file('{}return {}'.format(prefix, expression))
        self._is_insert = False

    def _handle_procedures_callnoreturn(self, block, prefix=''):
        mutation = self.get_node('mutation', block).attrib['name']
        if not mutation:
            mutation = '1'
        if mutation in self._funcs:
            name = self._funcs[mutation]
        else:
            name = 'function_{}'.format(self.func_index)
        self._append_to_file('{}MyDef.{}()'.format(prefix, name))
        self._funcs[mutation] = name

    def _handle_procedures_ifreturn(self, block, prefix=''):
        self._is_insert = True
        values = self.get_nodes('value', block)
        expression = self.__get_condition_expression(values[0])
        self._append_to_file('{}if {}:'.format(prefix, expression))
        expression = self.__get_condition_expression(values[1])
        self._append_to_file('{}    return {}'.format(prefix, expression))
        self._is_insert = False

    def _handle_procedures_callreturn(self, block, prefix=''):
        self._handle_procedures_callnoreturn(block, prefix)

    def _handle_variables_set(self, block, prefix=''):
        field = self.get_node('field', block).text
        value = self.get_node('value', root=block)
        expression = self.__get_condition_expression(value)
        self._append_to_file('{}params[\'variables\'][\'{}\'] = {}'.format(prefix, field, expression))

    def _handle_math_change(self, block, prefix=''):
        field = self.get_node('field', block).text
        value = self.get_node('value', root=block)
        shadow = self.get_node('shadow', root=value)
        val = self.get_node('field', root=shadow).text
        self._append_to_file('{}params[\'variables\'][\'{}\'] += {}'.format(prefix, field, val))

    def _handle_controls_repeat_ext(self, block, prefix=''):
        value = self.get_node('value', root=block)
        times = self.get_nodes('field', root=value, descendant=True)[0].text
        self._append_to_file('{}for i in range({}):'.format(prefix, times))
        prefix = '    ' + prefix
        self._append_to_file('{}if params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    break'.format(prefix))
        statement = self.get_node('statement', root=block)
        if statement:
            self.parse(statement, prefix)
        else:
            self._append_to_file('{}pass'.format(prefix))

    # def handle_controls_for(self, block, prefix=''):
    #     print(block.attrib.get('disabled', False))

    def _handle_controls_whileUntil(self, block, prefix=''):
        field = self.get_node('field', root=block)
        if field.text == 'WHILE':
            value = self.get_node('value', root=block)
            expression = self.__get_condition_expression(value)
            self._append_to_file('{}while {} and not params[\'quit\']:'.format(prefix, expression))
        elif field.text == 'UNTIL':
            value = self.get_node('value', root=block)
            expression = self.__get_condition_expression(value)
            self._append_to_file('{}while not {} and not params[\'quit\']:'.format(prefix, expression))
        prefix = '    ' + prefix
        statement = self.get_node('statement', root=block)
        if statement:
            self.parse(statement, prefix)
        else:
            self._append_to_file('{}pass'.format(prefix))

    def _handle_loop_run_forever(self, block, prefix=''):
        self._append_to_file('{}while True:'.format(prefix))
        prefix = '    ' + prefix
        self._append_to_file('{}if params[\'quit\']:'.format(prefix))
        self._append_to_file('{}    break'.format(prefix))
        statement = self.get_node('statement', root=block)
        if statement:
            self.parse(statement, prefix)
        else:
            self._append_to_file('{}pass'.format(prefix))

    def _handle_loop_break(self, block, prefix=''):
        self._append_to_file('{}break'.format(prefix))

    def _handle_tool_comment(self, block, prefix=''):
        field = self.get_node('field', block)
        self._append_to_file('{}# {}'.format(prefix, field.text))
        statement = self.get_node('statement', block)
        if statement:
            self.parse(statement, prefix)

    def _handle_tool_remark(self, block, prefix=''):
        field = self.get_node('field', block)
        self._append_to_file('{}# {}'.format(prefix, field.text))

    def _handle_controls_if(self, block, prefix=''):
        value = self.get_node('value', root=block)
        expression = self.__get_condition_expression(value)
        self._append_to_file('{}if {}:'.format(prefix, expression))
        prefix = '    ' + prefix
        statement = self.get_node('statement', root=block)
        if statement:
            self.parse(statement, prefix)
        else:
            self._append_to_file('{}pass'.format(prefix))

    def __get_condition_expression(self, value_block):
        block = self.get_node('block', value_block)
        if block.attrib['type'] == 'logic_boolean':
            return str(self.get_node('field', block).text == 'TRUE')
        elif block.attrib['type'] == 'logic_compare':
            op = self._ops.get(self.get_node('field', block).text)
            cond_a = 0
            cond_b = 0
            values = self.get_nodes('value', block)
            if len(values) > 0:
                cond_a = self.__get_condition_expression(values[0])
                if len(values) > 1:
                    cond_b = self.__get_condition_expression(values[1])
            return '{} {} {}'.format(cond_a, op, cond_b)
        elif block.attrib['type'] == 'logic_operation':
            op = self.get_node('field', block).text.lower()
            cond_a = False
            cond_b = False
            values = self.get_nodes('value', block)
            if len(values) > 0:
                cond_a = self.__get_condition_expression(values[0])
                if len(values) > 1:
                    cond_b = self.__get_condition_expression(values[1])
            return '{} {} {}'.format(cond_a, op, cond_b)
        elif block.attrib['type'] == 'logic_negate':
            value = self.get_node('value', root=block)
            return 'not ({})'.format(self.__get_condition_expression(value))
        elif block.attrib['type'] == 'gpio_get_digital':
            io = self.get_node('field', block).text
            return 'arm.get_tgpio_digital({})[{}]'.format(io, 1)
        elif block.attrib['type'] == 'gpio_get_analog':
            io = self.get_node('field', block).text
            return 'arm.get_tgpio_analog({})[{}]'.format(io, 1)
        elif block.attrib['type'] == 'gpio_get_controller_digital':
            io = self.get_node('field', block).text
            return 'arm.get_cgpio_digital({})[{}]'.format(io, 1)
        elif block.attrib['type'] == 'gpio_get_controller_analog':
            io = self.get_node('field', block).text
            return 'arm.get_cgpio_analog({})[{}]'.format(io, 1)
        elif block.attrib['type'] == 'math_number':
            val = self.get_node('field', block).text
            return val
        elif block.attrib['type'] == 'math_arithmetic':
            field = self.get_node('field', block).text
            values = self.get_nodes('value', block)
            if len(values) > 1:
                block_a = self.get_node('block', root=values[0])
                block_b = self.get_node('block', root=values[1])
                if block_a is not None:
                    val_a = self.__get_condition_expression(values[0])
                else:
                    shadow = self.get_node('shadow', root=values[0])
                    val_a = self.get_node('field', root=shadow).text
                if block_b is not None:
                    val_b = self.__get_condition_expression(values[1])
                else:
                    shadow = self.get_node('shadow', root=values[1])
                    val_b = self.get_node('field', root=shadow).text
                if field == 'ADD':
                    return '{} + {}'.format(val_a, val_b)
                elif field == 'MINUS':
                    return '{} - {}'.format(val_a, val_b)
                elif field == 'MULTIPLY':
                    return '{} * {}'.format(val_a, val_b)
                elif field == 'DIVIDE':
                    return '{} / {}'.format(val_a, val_b)
                elif field == 'POWER':
                    return 'pow({}, {})'.format(val_a, val_b)
        elif block.attrib['type'] == 'variables_get':
            field = self.get_node('field', block).text
            return 'params[\'variables\'].get(\'{}\', 0)'.format(field)
        elif block.attrib['type'] == 'tool_get_date':
            return 'datetime.datetime.now()'
        elif block.attrib['type'] == 'tool_combination':
            field = self.get_node('field', block).text
            values = self.get_nodes('value', block)
            var1 = self.__get_condition_expression(values[0])
            var2 = self.__get_condition_expression(values[1])
            return '\'{{}}{{}}{{}}\'.format({}, \'{}\', {})'.format(var1, field, var2)
        elif block.attrib['type'] == 'procedures_callreturn':
            mutation = self.get_node('mutation', block).attrib['name']
            if not mutation:
                mutation = '1'
            if mutation in self._funcs:
                name = self._funcs[mutation]
            else:
                name = 'function_{}'.format(self.func_index)
            return 'MyDef.{}()'.format(name)


if __name__ == '__main__':
    blockly = BlocklyTool('C:\\Users\\ufactory\\.UFACTORY\projects\\test\\xarm6\\app\\myapp\local_test_1\\app.xml')
    # blockly = BlocklyTool('C:\\Users\\ufactory\\.UFACTORY\projects\\test\\xarm6\\app\\myapp\\app_template\\app.xml')
    # blockly = BlocklyTool('C:\\Users\\ufactory\\.UFACTORY\projects\\test\\xarm6\\app\\myapp\\test_gpio\\app.xml')
    # blockly = BlocklyTool('C:\\Users\\ufactory\\.UFACTORY\projects\\test\\xarm7\\app\\myapp\\pour_water\\app.xml')
    # blockly = BlocklyTool('C:\\Users\\ufactory\\.UFACTORY\projects\\test\\xarm7\\app\\myapp\\233\\app.xml')
    import os
    target_path = os.path.join(os.path.expanduser('~'), '.UFACTORY', 'app', 'tmp')
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    target_file = os.path.join(target_path, 'blockly_app.py')
    blockly.to_python(target_file, arm='192.168.1.145')
