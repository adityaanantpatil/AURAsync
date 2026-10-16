
import hid
import time

VID = 0x36AE
PID = 0xFEAB

# Find the vendor-specific configuration interface.
matches = [
    d for d in hid.enumerate(VID, PID)
    if d.get("usage_page") == 0xFF00
    and d.get("usage") == 0x02
]

if not matches:
    raise RuntimeError("Vendor HID interface not found.")

dev = hid.device()
dev.open_path(matches[0]["path"])
dev.set_nonblocking(True)

try:
    # Read-only command: get global lighting configuration.
    # 64-byte payload, preceded by report ID 0 for Windows HIDAPI.
    report = bytes([0x00, 0x06, 0x0A] + [0x00] * 62)

    written = dev.write(report)
    print(f"Bytes written: {written}")

    # Look for the response; skip unsolicited lighting events.
    deadline = time.time() + 3
    while time.time() < deadline:
        data = dev.read(65)

        if not data:
            time.sleep(0.05)
            continue

        print("Received:", bytes(data).hex(" "))

        if len(data) >= 2 and data[0] == 0xAA and data[1] == 0xFA:
            continue

        print("Inspect this report for the lighting configuration.")
        break
    else:
        print("No response received within 3 seconds.")

finally:
    dev.close()
