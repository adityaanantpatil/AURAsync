
from scapy.all import rdpcap, Raw

capture = rdpcap("red_blue_white.pcapng")

for packet in capture:
    if Raw in packet:
        data = bytes(packet[Raw].load)
        if data:
            print(data.hex(" "))
