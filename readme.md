# pyUBX

This is a small but functional python wrapper for the u-blox M8 UBX protocol, as
defined in [UBX-13003221 - R13](https://www.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_(UBX-13003221)_Public.pdf). Only a small subset is implemented. However, this python was designed so that it is very easy to add messages.

For example, the `ACK-ACK` and `ACK-NAK` message format is defined in Python like this.

```python
@initMessageClass
class ACK:
    """Message class ACK."""
    _class = 0x05
    class ACK:
        _id = 0x01
        class Fields:
            clsID = U1(1)
            msgID = U1(2)

    class NAK:
        _id = 0x00
        class Fields:
            clsID = U1(1)
            msgID = U1(2)
```

The syntax is quite intuitive. UBX message class and message ID are defined by using member variables `_class` and `_id`. 

Python introduces some syntactic noise such as the frequent `class` keyword, but we feel it's acceptable, in particular since it is correct Python and can therefore be used to generate parsers and writers via introspection. It is also possible to use these UBX message definitions to generate parsers and generators for other languages, such as C, C++, etc.

## What's implemented

- `MON-VER`
- `ACK-ACK`  `ACK-NAK` 
- `CFG-PSM`  `CFG-GNSS` 

## Usage

The two main classes are `UBXManager` and `UBXMessage`. They are defined in files with the same name.

### `UBXManager`

 `UBXManager` runs a thread that reads and writes to/from a `pyserial` device. It is assumed that a *u-blox* M8 GNSS module is connected to the serial port. 

```python
import serial
from UBXManager import UBXManager
ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=None)
manager = UBXManager(ser, debug=True)
```

The manager thread is then started like this:

```python
manager.start()	
```

By default `UBXManager` dumps all `NMEA` and `UBX` messages to stdout. By deriving and overriding the member functions `onNMEA`, `onNMEAERR`, `onUBX`, `onUBXErr` this behaviour can be changed.

### `UBXMessage`

`UBXMessage` parses and generates UBX messages. The `UBXMessage` classes are organized in a hierarchy so that they can be accessed with a syntax that resembles u-blox' convention. For example, message `CFG-PSM` corresponds to Python class `UBX.CFG.PSM` and its subclasses.

The subclasses capture the message format variations that are used for requesting and receiving. So, the `Get` message of `CFG-GNSS` is

```python
> UBX.CFG.PMS.Get().serialize()
b'\xb5b\n\x04\x00\x00\x0e4'
```

## Protoyping with Python

It is unusual to want to interface with a chip using Python. But we've found that it is desirable to use a high-level language for getting acquanted, learning the interface, and cobbling together prototypes or some mobile test-kit using Rasperry Pis or other single board computers (SBCs) running Linux. (The [C.H.I.P](http://getchip.com) is quite attractive in this regard. It's cheap and it has more IO pins than the Raspberry.)

The Python shell (or even better: [IPython](https://ipython.org/)) provides a [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) that allows to interactively explore the protocol and the behaviour of the chip.

## Outlook



## Alternatives

The UBX protocol is rather extensive, so it would have been nice to rely on prior work.

### Kaitai

We briefly looked at [kaitai](http://kaitai.io, which looks very promising and would have been a good fit. Unfortunately, Kaitai can create parsers (readers)  but it does not allow to create writers. We'll look again at Kaitai when this limitation is lifted. Since the `pyUBX` message definition is written in Python it shouldn't be difficult to generate the necessay `.ksy` yaml files automatically.

### arobenko/ublox

This is a C++11 library available on [github](https://github.com/arobenko/ublox). It is quite comprehensive. It quite heavily relies on the Qt framework which may not be an option on microcontrollers so for us this is not a feasible path.