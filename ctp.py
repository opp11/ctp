#!/usr/bin/env python3
"""
Script for compiling a protocol file to a binary file which can be uploaded to
the component tester's SD card.

usage: ctp2.py [-h | --help] [-o FILE] [-t | --test] [INFILE | -c | --code]

-h --help       show this
-o FILE         specify output file [default: ./out.tst]
-t --test       show if compilation was succesfull but make no output file
-c --code       read code from stdin, instead of a file

"""
import sys
import struct
import warnings
from docopt import docopt

__all__ = ['CtpSyntaxError', 'make_file', 'parse_code']
__version__ = '0.9.0'
__author__ = 'Patrick M. Jensen'

class CtpSyntaxError(Exception):
    def __init__(self, message, *args):
        self.message = message.format(*args)
    def __str__(self):
        return self.message

_cmd_codes = {
    'check': 1,
    'set': 2,
    'vin': 3,
    'gnd': 4,
    'delay': 5
}

def _pins_to_arg(pins):
    if type(pins) is not type(dict()):
        raise TypeError("pins must be a dictionary")
    out = 0
    for pin in pins:
        if pins[pin]:
            out |= 1<<(pin - 1)
    return out

def _is_pin(arg):
    try:
        return 1 <= int(arg) <= 16
    except ValueError:
        return False

def _is_keyword(arg):
    return arg in ['check', 'set', 'vin', 'delay', 'rest']

def _get_pin_vals(args):
    pins = dict()
    check_val = None
    for i, arg in enumerate(args):
        if arg == 'on':
            check_val = True
        elif arg == 'off':
            check_val = False
        elif arg == 'rest':
            if i < len(args) - 1:
                raise CtpSyntaxError('REST keyword must be the last argument')
            elif check_val is None:
                raise CtpSyntaxError(
                    'pins must be preceded by either ON or OFF')
            for pin in range(1, 17):
                if pin not in pins:
                    pins[pin] = check_val
        elif _is_pin(arg):
            if int(arg) in pins:
                raise CtpSyntaxError('pin {} has already been given a value', 
                    arg)
            elif check_val is None:
                raise CtpSyntaxError(
                    'pins must be preceded by either ON or OFF')
            pins[int(arg)] = check_val
        else:
            raise CtpSyntaxError("'{}' is not a valid pin or value", arg)
    return pins

def _cmd_check(args, where):
    global _cmd_codes
    try:
        pins = _get_pin_vals(args)
    except CtpSyntaxError as err:
        raise CtpSyntaxError("check: {}: {}", where, err)
    for pin in range(1, 17):
        if pin not in pins:
            raise CtpSyntaxError("check: {}: all pins must be given a value", 
                where)
    return struct.pack('<BH', _cmd_codes['check'], _pins_to_arg(pins))

def _cmd_set(args, where):
    global _cmd_codes
    try:
        pins = _get_pin_vals(args)
    except CtpSyntaxError as err:
        raise CtpSyntaxError("set: {}: {}", where, err)
    for pin, val in pins.items():
        _cmd_set.pin_state[pin] = val
    return struct.pack('<BH', _cmd_codes['set'], 
        _pins_to_arg(_cmd_set.pin_state))
_cmd_set.pin_state = {
    1: False,
    2: False,
    3: False,
    4: False,
    5: False,
    6: False,
    7: False,
    8: False,
    9: False,
    10: False,
    11: False,
    12: False,
    13: False,
    14: False,
    15: False,
    16: False,
}

def _cmd_vin(args, where):
    global _cmd_codes
    _cmd_vin.is_called = True
    valid_vins = ['5', '14', '15', '16']
    pins = dict()
    for arg in args:
        if arg in valid_vins:
            pins[int(arg)] = True
        else:
            raise CtpSyntaxError("vin: {}: invalid vin pin", where)

    return struct.pack('<BH', _cmd_codes['vin'], _pins_to_arg(pins))
_cmd_vin.is_called = False

def _cmd_gnd(args, where):
    global _cmd_codes
    _cmd_gnd.is_called = True
    valid_gnds = ['8', '12']
    pins = dict()
    for arg in args:
        if arg in valid_gnds:
            pins[int(arg)] = True
        else:
            raise CtpSyntaxError("gnd: {}: invalid ground pin", where)

    return struct.pack('<BH', _cmd_codes['gnd'], _pins_to_arg(pins))
_cmd_gnd.is_called = False

def _cmd_delay(args, where):
    global _cmd_codes
    if len(args) > 1:
        raise CtpSyntaxError('delay: {}: only 1 delay value can be specified',
            where)
    try:
        time = int(args[0])
        if time > (2**16 - 1):
            raise CtpSyntaxError(
                'delay: {}: delay time must be less than {}', where, 65535)
        if time < 0:
            raise CtpSyntaxError(
                'delay: {}: delay time must be greater than 0', where)
        return struct.pack('<BH', _cmd_codes['delay'], time)
    except ValueError:
        raise CtpSyntaxError('delay: {}: delay time must be a number', where)

def parse_line(args, line_num, commands):
    parsers = {
        'check': _cmd_check,
        'set': _cmd_set,
        'vin': _cmd_vin,
        'gnd': _cmd_gnd,
        'delay': _cmd_delay,
    }
    if args[0] not in parsers:
        raise CtpSyntaxError('error: {}: {} is not a command', 
                    line_num + 1, args[0])

    if args[0] not in ('gnd', 'vin', 'delay'):
        if not _cmd_gnd.is_called:
            warnings.warn(
                "warning: {}: {}: manipulating pins without specifying gnd".
                format(args[0], line_num))
        if not _cmd_vin.is_called:
            warnings.warn(
                "warning: {}: {}: manipulating pins without specifying vin".
                format(args[0], line_num))
    commands.append(parsers[args[0]](args[1:], line_num))

def parse_code(code):
    """
    Parses an enumerable containing a protocol and returns a list where each
    element is a string conatining the 3 bytes of tester command.
    """
    commands = []
    # parse alle lines
    for line_num, line in enumerate(code):
        args = line.lower().split()
        if len(args) > 1 and not line[0] == '#':
            # attempt to parse the line
            parse_line(args, line_num + 1, commands)
                
    return commands

def make_file(fname, commands):
    """
    Makes a binary file with the name 'fname' containing the commands in the
    'commands' parameter.
    """
    with open(fname, 'wb') as file:
        file.write(b'PM1')
        for cmd in commands:
            file.write(cmd)
        file.write(b'END')

def _ctp_formatwarning(msg, *a):
    return str(msg) + '\n'

def main():
    opts = docopt(__doc__)

    # monkeypatch the warnings module to make warnings pretty
    warnings.formatwarning = _ctp_formatwarning

    code = None
    if not opts['--code']:
        with open(opts['INFILE'], 'r') as file:
            code = file.readlines()
    else:
        code = sys.stdin.readlines()

    try:
        commands = parse_code(code)
        if not opts['--test']:
            make_file(opts['-o'], commands)
        else:
            print('compilation succesfull')
    except CtpSyntaxError as err:
        print(err.message)
        if opts['--test']:
            print('compilation failed')

if __name__ == '__main__':
    main()