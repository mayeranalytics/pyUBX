# pyUBX

This is a small but functional Python3 wrapper for the u-blox M8 UBX protocol, as
defined in [UBX-13003221 - R13, §31](https://www.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_(UBX-13003221)_Public.pdf). The focus is on getting the basics right, which first of all means  correctly creating and parsing UBX messages with usable error messages on failure. The key features are:

- parse, generate and manipulate UBX messages
- make it easy to add new message definitions
- decorators keep the boilerplate code at a minimum
- allow to interact with a device using a REPL
- use as a parser generator for other languages or definition files for other parser generators

**Only a small subset is currently implemented!** 

#### UBX

`UBX` is a "*u-blox proprietary protocol to communicate with a host computer*". There are

- 9 message classes `UPD ` `MON ` `AID` `TIM` `ESF` `MGA` `LOG` `SEC` `HNR` , and
- 155 individual messages, many of which have multiple versions
- `Command` `Get` `Set` `Input` `Output` `Periodic` `Poll Request` `Polled` 

#### Message definitions

For example, the `ACK-ACK` and `ACK-NAK` message format is defined in Python like this.

```python
@initMessageClass
class ACK:
    """Message class ACK."""
    _class = 0x05
    
    class ACK:		# this is message ACK-ACK
        _id = 0x01
        class Fields:
            clsID = U1(1)
            msgID = U1(2)

    class NAK:		# this is message ACK-NAK
        _id = 0x00
        class Fields:
            clsID = U1(1)
            msgID = U1(2)
```

The syntax is quite intuitive. UBX message class and message ID are defined by using member variables `_class` and `_id`. 

This design introduces some syntactic noise such as the frequent `class` keyword and the occasional decorator. It's an acceptable tradeoff: As it is correct Python it can therefore be used parse and manipulate messages. 

It is also possible to use these UBX message definitions to generate parsers and generators for other languages, such as C/C++, etc, by using introspection.

Note that the `Fields` class variables have to be numbered, otherwise the exact order of the variables cannot be recovered (Python stores the various `things' belonging to a class in a dict). So the first argument of a type is always an ordering number. The actual numbers don't matter as long as the resulting ordering is correct.

### Repeated blocks

*UBX* often uses repeated blocks. An example is the `MON-VER` message:

```python
@initMessageClass
class MON:
    """Message class MON."""
    _class = 0x0A

    @addGet
    class VER:
        _id = 0x04

        class Fields:
            swVersion = CH(1, 30, nullTerminatedString=True)
            hwVersion = CH(2, 10, nullTerminatedString=True)
            class Repeated:
                extension = CH(1, 10, nullTerminatedString=True)

```

Here, `swVersion` and `hwVersion` are fixed-length bytestrings that contain a null-terminated ASCII string. The repeated `extension` fields carry additional information.

When `UBXManager` receives a message from the GNSS receiver it tries to parse it. UBX messages are handled by the `onUBX` and `onUBXError` member functions. Here are the signatures of these two functions:

```python
def onUBX(self, obj)						 # handle good UBX message
def onUBXError(self, msgClass, msgId, errMsg)  # handle faulty UBX message
```

The argument `obj` contains a `UBXMessage` object with populated fields. A `UBXMessage` can be pretty-printed with the `__str__` function. A repeated block is unrolled by appending `_n` to the variable names of the fields inside the repeated block. For example, the pretty-printed answer to `UBX.MON.VER.Get` is:

```bash
MON-VER
  swVersion="ROM CORE 3.01 (107888)"
  hwVersion="00080000"
  extension_1="FWVER=SPG 3.01"
  extension_2="PROTVER=18.00"
  extension_3="GPS;GLO;GAL;BDS"
  extension_4="SBAS;IMES;QZSS"
```

(This is from a CAM-M8Q module.)

## What's implemented

- class **`ACK`**:
  - `ACK` `NAK` 
- class **`CFG`**:
  - `GNSS` `PM2` `PSM` `RATE` `RXM`
- class **`MON`**:
  - `VER`

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

The manager can be instantiated with any serial object that has a `read(n)` function that reads `n` bytes from the stream. Nothing more is required (in fact all it needs is `read(1)`).

The manager thread is then started like this:

```python
manager.start()	
```

By default `UBXManager` dumps all `NMEA` and `UBX` messages to stdout. By deriving and overriding the member functions `onNMEA`, `onNMEAError`, `onUBX`, `onUBXError` this behaviour can be changed.

### `UBXMessage`

`UBXMessage` parses and generates UBX messages. The `UBXMessage` classes are organized in a hierarchy so that they can be accessed with a syntax that resembles u-blox' convention. For example, message `CFG-PSM` corresponds to Python class `UBX.CFG.PSM` and its subclasses.

The subclasses capture the message format variations that are used for requesting and receiving. So, the `Get` message of `CFG-GNSS` is

```python
> UBX.CFG.PMS.Get().serialize()
b'\xb5b\n\x04\x00\x00\x0e4'
```

### Get-modify-set

A typical usage pattern is get-modify-set:

```python
rxm = UBX.CFG.RXM(b'\x48\x00') # create a message
rxm.lpMode = 1                 # power save mode (see §31.11.27)
msg = rxm.serialize()          # make new message
# send(msg)
```

### Types

Types are defined in `Types.h`. Currently there are the following:

`U1`, `I1`, `X1`, `U2`, `I2`, `X2`, `U4`, `I4`, `X4`, `R4`, `R8`, `CH`, `U`

and they correspond exactly to the ones defined by u-blox in §31.3.5.

Simple types are defined like this:

```python
@_InitType
class I4:
    """UBX Signed Int."""
    fmt = "i"		# used by the decorator _InitType
    def ctype(): return "int32_t"	# for future use
```

The decorator `@_InitType` does most of the work: It implements the `__init__`, `__parse__`and `toString` functions and adds the `_size` variable. The `_InitType` decorator needs the `fmt` class variable to be defined, the letter corresponds to the code used in the Python `struct` module.

`CH` and `U` are variable-length types and they are hand-coded. `U` is used for the many *reserved* fields.

### `UBX.py`

`UBX.py` is a utlilty that allows to send UBX commands to the device. For example, to switch into power save mode and then start umping NMEA messages, run

```bash
./UBX.py --RXM 1 --NMEA
```

The content of the `CFG-RATE` register can queried like so:

```bash
> ./UBX.py --RATE-GET
CFG-RATE:
  measRate=0x03E8
  navRate=0x0001
  timeRef=0x0001
ACK-ACK:
  clsID=0x06
  msgID=0x08
```

Not that always all UBX messages are printed, including the `ACK-ACK`.

##### Usage

```bash
usage: UBX.py [-h] [--VER-GET] [--GNSS-GET] [--PMS-GET] [--PM2-GET]
              [--RATE-GET] [--RXM RXM] [--NMEA] [-d]

Send UBX commands to u-blox M8 device.

optional arguments:
  -h, --help   show this help message and exit
  --VER-GET    Get the version string
  --GNSS-GET   Get CFG-GNSS
  --PMS-GET    Get CFG-PMS
  --PM2-GET    Get CFG-PM2
  --RATE-GET   Get CFG-RATE
  --RXM RXM    Set the power mode (0=cont, 1=save)
  --NMEA       Dump NMEA messages.
  -d, --debug  Turn on debug mode
```

`UBX.py` uses finite state machines defined in `FSM.py`. The `Manager` class derives from `UBXManager` and overrides the `onUBX`, etc., callbacks.

## Protoyping with Python

It is unusual to interface with a chip using Python. Usually this is done in C/C++ using a microcontroller, maybe an Arduino. 

However, it is desirable to use a high-level language in the early stages of a project where it is key to quickly

- learn the interface/protocol,
- test new products (chips, modules, antenna configurations),
- cobble together prototypes or some mobile test-kit

#### Interfacing

The standard serial interfaces, such as UART, I<sup>2</sup>C, SPI, are easy to use with the appropriate USB-to-XYZ adapters.

#### REPL

The Python shell (or even better: [IPython](https://ipython.org/)) provides a [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) that allows to interactively explore the protocol and the behaviour of the chip.

#### SBCs

For field tests single board computers (SBCs) can be used. Some draw less than 200mA, so a 5Ah USB power bank is more than enough for a day's work. A default choice is the ubiquitous Rasperry Pi. The community is huge and libraries are plentiful. But with only one each of UART, SPI, I<sup>2</sup>C it's not necessarliy the best choice for prototyping. Some alternatives are

- **[C.H.I.P](http://getchip.com)**: Very cheap, with on-board flash, and with slightly more I/O than the Raspberry
- **[Beaglebone Black](https://beagleboard.org/black)**: Well equipped with on-board flash, 2 x SPI, 2 x I<sup>2</sup>C, 4 x UART, etc., but not so cheap (around 50$).
- **[Pine64](https://www.pine64.org)**: Rather large and power hungry (300-800mA current draw), but cheap yet powerful with a quad-core A64 processor and [generous I/O](https://drive.google.com/file/d/0B0cEs0lxTtL3YU1CNmJ2bEIzTlE/view).
- [**UDOO Neo**](https://www.udoo.org/docs-neo/Introduction/Introduction.html): i.MX 6SoloX-based with 3 x UART, 3 x I<sup>2</sup>C, but only 1 x SPI. The basic version is about 50$.

#### Migration to C/C++, etc.

@Todo

#### Typical setup

Here's what we used for testing:

- SBC: Raspberry Pi
- GNSS: CAM-M8Q module on carrier board (80x40mm ground plane), connected via UART
- Power consumption measurement: [INA219](http://www.ti.com/product/INA219) module, connected via I<sup>2</sup>C

## Outlook

### Todo

- Manipulators/accessors

Also have a look at the logged [enhancement requests](https://github.com/mayeranalytics/pyUBX/issues?q=is:open+is:issue+label:enhancement) on github.

## Alternatives

The UBX protocol takes up about 220 pages of the *Receiver Description*, so is rather extensive and it would have been nice to rely on prior work. Almost all libraries we could find are hand-crafted C libraries. It's hard to imagine that this manual approach resulted in bug-free code.

### Kaitai

[Kaitai](http://kaitai.io) is a parser generator for binary structures. It looks very promising and would have been a great fit. Unfortunately, Kaitai can only create parsers but not writers (serializers). We'll look again at Kaitai when this limitation is lifted. Since the `pyUBX` message definition is written in Python it shouldn't be difficult to generate the necessay `.ksy` yaml files automatically.

### arobenko/ublox

This quite comprehensive C++11 library is available on [github](https://github.com/arobenko/ublox). It relies on the Qt framework - not an option for most microcontrollers.

### libMGA

U-blox own library called *libMGA* can be obtained, according to the [forum](https://forum.u-blox.com/index.php?qa=748&qa_1=source-code-libmga-where-can-this-be-acquired), by contacting u-blox.

## Legal stuff

### pyUBX

The `pyUBX` software is GPL 3.0 licensed. The software is provided "as-is". Use it carefully. If you brick your device it's your, and *only* your fault!!!

### u-blox

U-blox' documentation has a very peculiar copyright note that **strictly prohibits the *use* of the documents without the express permission of u-blox**. U-blox reacted quickly when confronted with it on the [forum](https://forum.u-blox.com/index.php?qa=13486&qa_1=weird-copyright-notice-of-u-blox-documentation). It's probably safe to dismiss parts of this disclaimer as unreasonably broad.

This is the full text of the disclaimer:

> u-blox reserves all rights to this document and the information contained herein. Products, names, logos and designs described herein mayin whole or in part be subject to intellectual property rights. Reproduction, use, modification or disclosure to third parties of this document or any part thereof without the express permission of u-blox is strictly prohibited.
>
> The information contained herein is provided “as is” and u-blox assumes no liability for the use of the information. No warranty, either express or implied, is given, including but not limited, with respect to the accuracy, correctness, reliability and fitness for a particularpurpose of the information. This document may be revised by u-blox at any time. For most recent documents, please visit www.u-blox.com.
>
> Copyright © 2017, u-blox AG.
>
> u-blox® is a registered trademark of u-blox Holding AG in the EU and other countries. ARM® is the registered trademark of ARM Limitedin the EU and other countries.