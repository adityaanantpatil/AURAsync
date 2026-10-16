
import colorsys
import hid
import re

VID = 0x36AE
PID = 0xFEAB

def rgb_to_hsv_bytes(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return (
        round(h * 255) % 256,
        round(s * 255),
        round(v * 255),
    )

def set_color(hex_color):
    hex_color = hex_color.strip().lstrip("#")

    if not re.fullmatch(r"[0-9a-fA-F]{6}", hex_color):
        raise ValueError("Enter a six-digit hex colour, e.g. #00FF00")

    r, g, b = (
        int(hex_color[i:i + 2], 16)
        for i in (0, 2, 4)
    )
    h, s, v = rgb_to_hsv_bytes(r, g, b)

    devices = [
        d for d in hid.enumerate(VID, PID)
        if d.get("usage_page") == 0xFF00
        and d.get("usage") == 0x02
    ]

    if not devices:
        raise RuntimeError("SDCX configuration interface not found.")

    dev = hid.device()

    try:
        dev.open_path(devices[0]["path"])

        # Confirmed working layout from the successful red test.
        payload = bytes([
            0x06, 0x0B, 0x0B,
            0x00, 0x00,
            0x01, 0x00,
            0x01,       # Static lighting mode
            0x04,       # Maximum brightness
            0x02,       # Speed
            0x01,       # Direction
            0xFF,       # Observed colour flag
            0x00,       # Reserved
            h, s, v,
        ])

        report = bytes([0x00]) + payload.ljust(64, b"\x00")
        written = dev.write(report)

        print(f"Colour: #{hex_color.upper()}")
        print(f"RGB:    ({r}, {g}, {b})")
        print(f"HSV:    ({h}, {s}, {v})")
        print(f"Bytes written: {written}")

        # Display the device's acknowledgement.
        response = dev.read(65, 1000)
        if response:
            print("Response:", bytes(response).hex(" "))
        else:
            print("No acknowledgement received; check the lighting.")

    finally:
        dev.close()

if __name__ == "__main__":
    while True:
        color = input("\nEnter hex colour (or q to quit): ").strip()

        if color.lower() == "q":
            break

        try:
            set_color(color)
        except (ValueError, RuntimeError, OSError) as e:
            print("Error:", e)
