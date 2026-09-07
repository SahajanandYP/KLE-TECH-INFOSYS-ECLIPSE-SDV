import socket
import struct
import time

def sniff():
    print("🚗 Starting Virya APM CAN Sniffer for 0x1291...")
    try:
        s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        s.bind(('can0',))
    except Exception as e:
        print(f"Failed to bind to can0: {e}")
        return

    last_print = 0
    while True:
        try:
            cf, addr = s.recvfrom(16)
            can_id, can_dlc, data = struct.unpack("<IB3x8s", cf)
            
            is_extended = bool(can_id & 0x80000000)
            clean_id = can_id & 0x1FFFFFFF if is_extended else can_id & 0x7FF
            pgn = (clean_id >> 8) & 0x3FFFF
            
            if clean_id == 0x1291 or clean_id == 0x12910109 or pgn == 0x1291:
                now = time.time()
                if now - last_print > 0.1: # Max 10 prints per second
                    hex_data = " ".join([f"{b:02X}" for b in data])
                    speed_le = data[6] | (data[7] << 8)
                    speed_be = (data[6] << 8) | data[7]
                    print(f"RAW 0x1291: [ {hex_data} ] | B6-B7 Little-E: {speed_le} | B6-B7 Big-E: {speed_be}")
                    last_print = now
        except Exception as e:
            pass

if __name__ == "__main__":
    sniff()
