# Reverse Engineering the SDCX SDMulti Keyboard

This document records the steps used to identify and understand the keyboard's RGB control protocol.

## 1. Identify the hardware

The keyboard enumerates as:

- Product: `SDMulti`
- Manufacturer: `SDCX`
- USB VID:PID: `36AE:FEAB`

The HID enumeration output showed ordinary keyboard/consumer interfaces and one vendor-specific configuration interface:

| Property | Observed value |
|---|---|
| Interface path component | `MI_02` |
| Usage page | `0xFF00` |
| Usage | `0x02` |

The vendor-specific interface was selected for configuration commands rather than the normal keyboard input interface.

## 2. Capture USB traffic with Wireshark

Wireshark was used to observe USB traffic while changing the keyboard colour in the manufacturer's software.

A useful display filter for the observed device address and outgoing endpoint was:

```text
usb.device_address == 2 && usb.endpoint_address == 0x03
```

The USB device address can change between sessions, so check the current capture before reusing the filter.

Capture procedure:

1. Set a known colour in the manufacturer's software.
2. Start capturing USB traffic.
3. Change the colour to another known colour.
4. Stop capture and inspect outgoing interrupt transfers.
5. Compare report bytes between captures.

The captures included blue, green, white, and red tests. Interpret the HID report payload, not USBPcap framing bytes.

## 3. Consult the protocol reference

The investigation also examined the `sdcx-keypad` protocol documentation. It describes a family of SDCX/SDINNOVATION devices with a vendor-defined HID configuration interface and 64-byte output reports. Its documented reference model is not the same physical keyboard, so its protocol was treated as a hypothesis and verified against this SDMulti.

Reference repository: https://github.com/parsaj-dev/sdcx-keypad

The reference describes configuration group `0x06`, lighting read command `0x0A`, and lighting write command `0x0B`.

## 4. Confirm the interface with Python

Install `hidapi`:

```powershell
python -m pip install hidapi
```

Running `find_keyboard.py` identified:

```text
Product:       SDMulti
Manufacturer:  SDCX
Interface:     2
Usage page:    0xff00
Usage:         0x2
Path:          ...VID_36AE&PID_FEAB&MI_02...
```

## 5. Read the lighting configuration

`read_lighting.py` sent the read request and received a report beginning:

```text
AA 0A 0A 00 00 01 00 01 04 02 01 FF ...
```

Known colours selected in the manufacturer's software produced these observed response bytes:

| Software colour | RGB hex | Observed HSV bytes |
|---|---|---|
| Red | `#FE2408` | `04 F6 FE` |
| Pure green | `#00FF00` | `55 FF FF` |

The bytes are consistent with HSV encoded in the range 0–255. Pure green has hue byte `0x55` (85), close to one third of the hue range.

The keyboard returned `FF` in the colour-flag position, unlike the reference device's documented 0/1 values. The successful write preserved `FF`.

## 6. Confirm the write command

The first successful test wrote a 64-byte HID report with the lighting configuration command and red HSV values. The keyboard changed colour, and a subsequent read returned the expected red values.

The working report structure was:

```text
00 06 0B 0B 00 00 01 00 01 04 02 01 FF 00 04 F6 FE ...
```

The leading `00` is the HIDAPI report-ID byte used by the Windows script. The command payload begins with `06 0B`; the rest contains the length/configuration fields and zero padding.

The device returned an acknowledgement beginning `AA 0B 01 ...`, followed by a read response beginning `AA 0A 0A ...`.

## 7. Validate multiple colours

| Input | RGB | Generated HSV bytes |
|---|---|---|
| `#0000FF` | `(0, 0, 255)` | `(170, 255, 255)` |
| `#00FF00` | `(0, 255, 0)` | `(85, 255, 255)` |
| `#FF0000` | `(255, 0, 0)` | `(0, 255, 255)` |
| `#8000FF` | `(128, 0, 255)` | `(191, 255, 255)` |
| `#FFFFFF` | `(255, 255, 255)` | `(0, 0, 255)` |

The keyboard changed to each requested colour and returned an acknowledgement for each write.

## Confirmed vs. unverified

**Confirmed on SDMulti `36AE:FEAB`:**
- `MI_02` can be opened using `hidapi`.
- The lighting read request returns a configuration report.
- The lighting write command changes the global static colour.
- RGB hex values convert to HSV bytes and apply successfully.

**Not yet confirmed:**
- Per-key RGB on this keyboard.
- All lighting effects and parameter ranges.
- Screen-reactive ambient lighting.
- Game-specific event detection or telemetry integration.

Avoid firmware-update and factory-reset commands during RGB testing.
