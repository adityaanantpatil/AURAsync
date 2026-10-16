# Python Scripts: Purpose and Operation

This document explains why each Python file exists and how it works.

## 1. `find_keyboard.py` — discover the HID interface

**Purpose:** List the HID interfaces Windows exposes for the SDCX SDMulti.

It filters by VID `0x36AE` and PID `0xFEAB`, then prints product, manufacturer, interface number, usage page, usage, and device path.

**Why it was needed:** A USB keyboard can expose multiple HID interfaces. The normal keyboard interface handles key input, while RGB configuration uses a vendor-defined channel. This script identified `MI_02`, usage page `0xFF00`, usage `0x02`.

Run:

```powershell
python .\find_keyboard.py
```

## 2. `read_lighting.py` — query current lighting settings

**Purpose:** Send a read-only lighting configuration request and print the response.

The script opens the vendor interface and writes a 65-byte HIDAPI buffer: a leading report-ID byte (`0x00`) followed by the 64-byte command report. The command payload begins `06 0A`, requesting the lighting configuration.

It waits for a response and prints the bytes. It can skip unsolicited light-event reports beginning `AA FA`.

**Why it was needed:** Reading settings provided known colour values from the manufacturer's software and let us verify the protocol before attempting writes.

Run:

```powershell
python .\read_lighting.py
```

## 3. `set_color_test.py` — set a static colour

**Purpose:** Convert a six-digit RGB hex value into HSV bytes and send a lighting write command.

Examples:

```text
#FF0000
#00FF00
#0000FF
#FFFFFF
#8000FF
```

The script:
1. Validates the six-digit hex input.
2. Converts RGB values to HSV using Python's `colorsys`.
3. Scales hue, saturation, and value to bytes from 0 to 255.
4. Opens the vendor HID interface.
5. Sends the 64-byte lighting configuration report with the HIDAPI report-ID byte.
6. Prints the device acknowledgement.

The working packet sets Static mode, maximum brightness, preserves the observed `0xFF` colour flag, and sends the calculated HSV bytes. Speed and direction are fixed to values from the successful test.

**Why it was needed:** It replaced manual colour changes in the manufacturer's software with a reusable Python controller.

Run:

```powershell
python .\set_color_test.py
```

Close the manufacturer's software before running the write script so it does not compete for access to the device.

## Dependencies

Install `hidapi` for the current scripts:

```powershell
python -m pip install hidapi
```

The planned screen-reactive version is expected to use `mss` and `numpy`:

```powershell
python -m pip install mss numpy
```

These screen-capture dependencies are not used by the current three scripts.

## Current behaviour and limitations

- The current script sets one global static colour across the keyboard.
- It does not sample the screen or react to games yet.
- It does not control individual keys.
- It does not implement custom effects, colour cycling, or smooth transitions.
- Protocol features documented for another SDCX model should not be assumed to work without testing.

## Planned extension: ambient and game-aware lighting

The next planned layer will sample visible screen colours, smooth the result, convert it to HSV, and send updates to the keyboard. Game-aware effects can be layered on when reliable telemetry or visual detection is available. DRM bypass is out of scope.
