#!/usr/local/bin/python3
"""
Script for compiling a protocol file to a binary file which can be uploaded to
the component tester's SD card.

usage: ctp2.py [-h | --help] [-o FILE] [-v | --verify] [INFILE | -c | --code]

-h --help       show this
-o FILE         specify output file [default: ./out.tst]
-v --verify     show if compilation was succesfull but make no output file
-c --code       read code from stdin, instead of a file

"""
"""
PROTOCOL SYNTAX
==============================================================================
A protocol should be described as a series of commands with arguments.
Each command must be on a seperate. Lines beginning with a '#' and lines only
consisting of whitespace are skipped. Case (even mixed case liKe tHiS) 
does not matter.

Protocols will be run untill a CHECK command finds that the pin state does not
match what was specified. If this happens the component has failed the test.
If the protocol is run through without an error then the component has passed
the test.

COMMANDS
------------------------------------------------------------------------------
    VIN <PINS...>
Specifies that PINS... should be used as positive voltage supply.
Valid pin values are: 5, 14, 15, 16. 


    GND <PINS...>
Specifies that PINS.. should be used as ground.
Valid pin values are: 8, 12.


    DELAY <TIME>
Delays further execution by TIME milliseconds (ms).
NOTE: If a delay larger than 65535 ms is needed, it must be split into
multiple DELAY calls.


    SET (<VALUE> <PINS...>)...
Sets the PINS... to the value specified by VALUE. 
VALUE is either 'ON' or 'OFF' (without the qoutation marks). 
PINS... is a list of pin numbers (between 1 and 16) seperated by a space. 
Any pins which have not been given a value will remain in their current state 
(either ON or OFF). Furthermore the REST keyword may be used to specify any 
pins, which have not yet been given a value. Note however that no pins may be 
specified after the REST keyword, but it is *not* necessary to have pins 
*before* REST.

### Some examples:

    SET ON 1 2
This will set pins 1 and 2 to ON. The rest of the pins will stay in their
current state (ON or OFF).

    SET ON 1 2 OFF 3
This will set pins 1 and 2 to ON and pin 3 to OFF. The rest of the pins will 
stay in their current state (ON or OFF).

    SET ON 1 2 OFF REST
This will set pins 1 and 2 to ON and every other pin to OFF.

    SET ON REST
This will set every pin to ON since no pin was specified before REST.


    CHECK (<VALUE> <PINS...>)...
Checks whether PINS... have the value specified by VALUE.
VALUE is either 'ON' or 'OFF' (without the qoutation marks).
PINS... is a list of pin numbers (between 1 and 16) seperated by a space.
The way CHECK is called is similar to SET except that a value must be 
specified for all pins. However, it is still possible to use the REST keyword 
to represent every pin which have not been given a value.

** NOTE **: If a pin has previously been set to ON with a call to VIN or SET,
then CHECK will assume it should be ON, regardless of what is specified by the
arguments.

### Some examples:

    CHECK ON 1 OFF REST
This will check whether pin 1 is ON and the rest of the pins are OFF.

    CHECK ON 1 2 3 OFF REST
This will check whether pin 1, 2 and 3 are ON and the rest of the pins are OFF.

    CHECK OFF 1 2 OFF REST
This will check whether pin 1 and 2 are ON and the rest of the pins are OFF.


EXAMPLES
------------------------------------------------------------------------------
The following program will use pin 16 as VIN and pin 8 as ground. It will
then set pins 1 and 2 to ON and check if pin 3 is ON and everything else
(except for pin 16 since that is VIN and pins 1 and 2 since we set these 
to ON previously) is OFF.

    GND 8
    VIN 16
    SET ON 1 2
    CHECK ON 3 OFF REST


The following program will use pin 16 as VIN and pins 8 and 12 as ground.
It will then set pin 2 to ON, wait 2 seconds, then set it to OFF again. It
then checks if all pins (except for pin 16 since that is VIN) are OFF:

    GND 8 12
    VIN 16
    SET ON 2
    DELAY 2000
    SET OFF 2
    CHECK OFF REST
"""
import sys
import struct
from docopt import docopt

__all__ = ['CtpSyntaxError', 'make_file', 'parse_code']
__version__ = '0.8.0'
__author__ = 'Patrick M. Jensen'

class CtpSyntaxError(Exception):
    def __init__(self, message, *args):
        self.message = message.format(*args)

_ctp_cmd_codes = {
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
            raise CtpSyntaxError("'{}'' is not a valid pin or value", arg)
    return pins

def _cmd_check(args):
    global _ctp_cmd_codes
    pins = _get_pin_vals(args)
    for pin in range(1, 17):
        if pin not in pins:
            raise CtpSyntaxError("pin {} has not been given a value", pin)
    return struct.pack('<BH', _ctp_cmd_codes['check'], _pins_to_arg(pins))

def _cmd_set(args):
    global _ctp_cmd_codes
    pins = _get_pin_vals(args)
    for pin, val in pins.items():
        _cmd_set.pin_state[pin] = val
    return struct.pack('<BH', _ctp_cmd_codes['set'], 
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

def _cmd_vin(args):
    global _ctp_cmd_codes
    valid_vins = ['5', '14', '15', '16']
    pins = dict()
    for arg in args:
        if arg in valid_vins:
            pins[int(arg)] = True
        else:
            raise CtpSyntaxError("Invalid vin pin")

    return struct.pack('<BH', _ctp_cmd_codes['vin'], _pins_to_arg(pins))

def _cmd_gnd(args):
    global _ctp_cmd_codes
    valid_gnds = ['8', '12']
    pins = dict()
    for arg in args:
        if arg in valid_gnds:
            pins[int(arg)] = True
        else:
            raise CtpSyntaxError("Invalid ground pin")

    return struct.pack('<BH', _ctp_cmd_codes['gnd'], _pins_to_arg(pins))

def _cmd_delay(args):
    global _ctp_cmd_codes
    if len(args) > 1:
        raise CtpSyntaxError('only 1 delay value can be specified')
    try:
        time = int(args[0])
        if time > (2**16 - 1):
            raise CtpSyntaxError('delay time must be less than {}', 2**16 - 1)
        if time < 0:
            raise CtpSyntaxError('delay time must be greater than 0')
        return struct.pack('<BH', _ctp_cmd_codes['delay'], time)
    except ValueError:
        raise CtpSyntaxError('delay time must be a number')

def parse_code(code):
    """
    Parses an enumerable containing a protocol and returns a list where each
    element is a string conatining the 3 bytes of tester command.
    """
    commands = []
    parsers = {
        'check': _cmd_check,
        'set': _cmd_set,
        'vin': _cmd_vin,
        'gnd': _cmd_gnd,
        'delay': _cmd_delay,
    }
    # parse alle lines
    for line_num, line in enumerate(code):
        if len(line) > 1 and not line[0] == '#':
            args = line.lower().split()
            # attempt to parse the line, and if any errors occur
            # then add information as to where it happened and reraise
            if args[0] in parsers:
                try:
                    commands.append(parsers[args[0]](args[1:]))
                except CtpSyntaxError as err:
                    raise CtpSyntaxError('error: {}: {}: {}',
                        line_num + 1, args[0], err)
            else:
                raise CtpSyntaxError('error: {}: {} is not a command', 
                    line_num + 1, args[0])
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

if __name__ == '__main__':
    opts = docopt(__doc__)

    code = None
    if not opts['--code']:
        with open(opts['INFILE'], 'r') as file:
            code = file.readlines()
    else:
        code = sys.stdin.readlines()

    try:
        commands = parse_code(code)
        if not opts['--verify']:
            make_file(opts['-o'], commands)
        else:
            print('compilation succesfull')
    except CtpSyntaxError as err:
        print(err.message)
        if opts['--verify']:
            print('compilation failed')
