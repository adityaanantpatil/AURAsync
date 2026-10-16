
import hid

VID = 0x36AE
PID = 0xFEAB

devices = hid.enumerate(VID, PID)

if not devices:
    print("Keyboard not found. Check the USB connection.")
else:
    for d in devices:
        print("-" * 60)
        print("Manufacturer :", d.get("manufacturer_string"))
        print("Product      :", d.get("product_string"))
        print("VID:PID      :", f"{d['vendor_id']:04X}:{d['product_id']:04X}")
        print("Interface    :", d.get("interface_number"))
        print("Usage page   :", hex(d.get("usage_page", 0)))
        print("Usage        :", hex(d.get("usage", 0)))
        print("Path         :", d.get("path"))
