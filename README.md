ctp
==============================================================================
Script for compiling a protocol file to a binary file which can be uploaded to
the component tester's SD card. This was made since hand compiling every
protocol quickly gets tedious, and escpecially for longer protocols it is very
easy to make errors. Therefore i made a python script to automate the process.

    usage: 
        ctp2.py [-h | --help] [-o FILE] [-v | --verify] [INFILE | -c | --code]

    -h --help       show this
    -o FILE         specify output file [default: ./out.tst]
    -v --verify     show if compilation was succesfull but make no output file
    -c --code       read code from stdin, instead of a file

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
Specifies that `PINS...` should be used as positive voltage supply.
Valid pin values are: 5, 14, 15, 16. 


    GND <PINS...>
Specifies that `PINS..` should be used as ground.
Valid pin values are: 8, 12.


    DELAY <TIME>
Delays further execution by `TIME` milliseconds (ms).
NOTE: If a delay larger than 65535 ms is needed, it must be split into
multiple `DELAY` calls.


    SET (<VALUE> <PINS...>)...
Sets the `PINS...` to the value specified by ``VALUE``. 
`VALUE` is either `ON` or `OFF` (without the qoutation marks). 
`PINS...` is a list of pin numbers (between 1 and 16) seperated by a space. 
Any pins which have not been given a value will remain in their current state 
(either `ON` or `OFF`). Furthermore the `REST` keyword may be used to specify
any pins, which have not yet been given a value. Note however that no pins may
be specified after the `REST` keyword, but it is *not* necessary to have pins 
*before* `REST`.

### Some examples:

    SET ON 1 2
This will set pins 1 and 2 to `ON`. The rest of the pins will stay in their
current state (`ON` or `OFF`).

    SET ON 1 2 OFF 3
This will set pins 1 and 2 to ON and pin 3 to `OFF`. The rest of the pins will 
stay in their current state (`ON` or `OFF`).

    SET ON 1 2 OFF REST
This will set pins 1 and 2 to `ON` and every other pin to `OFF`.

    SET ON REST
This will set every pin to `ON` since no pin was specified before `REST`.


    CHECK (<VALUE> <PINS...>)...
Checks whether `PINS...` have the value specified by `VALUE`.
`VALUE` is either `ON` or `OFF` (without the qoutation marks).
`PINS...` is a list of pin numbers (between 1 and 16) seperated by a space.
The way `CHECK` is called is similar to `SET` except that a value must be 
specified for all pins. However, it is still possible to use the `REST` keyword 
to represent every pin which have not been given a value.

*NOTE*: If a pin has previously been set to `ON` with a call to VIN or SET,
then `CHECK` will assume it should be `ON`, regardless of what is specified by
the arguments.

### Some examples:

    CHECK ON 1 OFF REST
This will check whether pin 1 is `ON` and the rest of the pins are `OFF`.

    CHECK ON 1 2 3 OFF REST
This will check whether pin 1, 2 and 3 are `ON` and the rest of the pins are 
`OFF`.

    CHECK OFF 1 2 OFF REST
This will check whether pin 1 and 2 are `ON` and the rest of the pins are `OFF`.


EXAMPLES
------------------------------------------------------------------------------
The following program will use pin 16 as vin and pin 8 as ground. It will
then set pins 1 and 2 to `ON` and check if pin 3 is `ON` and everything else
(except for pin 16 since that is vin and pins 1 and 2 since we set these 
to `ON` previously) is `OFF`.

    GND 8
    VIN 16
    SET ON 1 2
    CHECK ON 3 OFF REST


The following program will use pin 16 as vin and pins 8 and 12 as ground.
It will then set pin 2 to `ON`, wait 2 seconds, then set it to `OFF` again. It
then checks if all pins (except for pin 16 since that is vin) are `OFF`:

    GND 8 12
    VIN 16
    SET ON 2
    DELAY 2000
    SET OFF 2
    CHECK OFF REST