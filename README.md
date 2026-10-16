#AURAsync process
# SDCX SDMulti Keyboard RGB Control

Reverse-engineering notes and Python tools for controlling the RGB lighting on an **SDCX SDMulti** keyboard on Windows.

- **Device:** SDCX SDMulti
- **USB VID:PID:** `36AE:FEAB`
- **Configuration HID interface:** `MI_02`
- **Usage page / usage:** `0xFF00` / `0x02`

> **Project status:** Direct static-colour control has been tested successfully on this keyboard. Screen-reactive ambient lighting and game-aware effects are planned, not implemented yet.

## What this project does

- Identifies the keyboard's vendor-specific HID configuration interface.
- Reads the current global lighting configuration.
- Sets a static lighting colour using a hex RGB input converted to the device's HSV byte format.
- Documents the USB capture and protocol investigation behind the working command.

## Requirements

- Windows and Python 3.10 or compatible
- SDCX SDMulti keyboard connected over USB
- Wireshark if reproducing the USB capture/reverse-engineering process

Install dependencies:

```powershell
python -m pip install hidapi mss numpy
```

`hidapi` is used by the current scripts. `mss` and `numpy` are for the planned screen-reactive stage and are not required by the static-colour scripts.

## Quick start

```powershell
python .\find_keyboard.py
python .\read_lighting.py
python .\set_color_test.py
```

- `find_keyboard.py` lists the HID interfaces exposed by the keyboard.
- `read_lighting.py` requests the current lighting configuration.
- `set_color_test.py` prompts for a six-digit hex colour such as `#FF0000`, `#00FF00`, or `#8000FF`.

Close the manufacturer's keyboard software before running a script that writes lighting settings.

## Documentation

- [Reverse engineering and protocol notes](docs/REVERSE_ENGINEERING.md) — Wireshark setup, captures, known report bytes, and command format.
- [Python scripts and how they work](docs/PYTHON_SCRIPTS.md) — purpose, usage, and limitations of each script.

## Current limitations

- Static global colour control is confirmed; the current controller uses Static mode and maximum brightness.
- Per-key RGB is not verified on this device.
- Built-in effects, screen sampling, smooth transitions, game telemetry, and game-event recognition are not implemented yet.
- DRM-protected video is not intentionally bypassed. Screen capture may show black regions in protected video apps.

## Safety

- Use the vendor-specific configuration interface, not the ordinary keyboard input interface.
- Do not send firmware-update or factory-reset commands while experimenting.
- Keep copies of capture files and notes.
