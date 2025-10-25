import serial
import sys
import time
import argparse

def main():
    parser = argparse.ArgumentParser(description='Serial port listener')
    parser.add_argument('port', help='Serial port suffix (e.g., USB0 or ACM0)')
    args = parser.parse_args()
    
    PORT = f'/dev/tty{args.port}'
    BAUD = 115200

    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.1)
    except Exception as e:
        print(f"Cannot open port: {e}")
        return
        
    print(f"Listening on {PORT}...")
    sys.stdout.flush()
    buf = bytearray()
    try:
        while True:
            data = ser.read(64)
            if data:
                buf += data
            else:
                time.sleep(0.01)
                continue
            while True:
                i = buf.find(b'\xAA\x55')
                if i == -1:
                    if len(buf) > 2:
                        buf = buf[-2:]
                    break
                if len(buf) - i < 4:
                    break
                payload_start = i + 2
                found = False
                for payload_len in range(1, min(254, len(buf) - payload_start)):
                    checksum_pos = payload_start + payload_len
                    if checksum_pos >= len(buf):
                        break
                    payload = buf[payload_start:checksum_pos]
                    expected_checksum = sum(payload) & 0xFF
                    if buf[checksum_pos] == expected_checksum:
                        try:
                            message = payload.decode('utf-8')
                            print(message)
                        except:
                            print(f"[Binary data: {payload.hex()}]")
                        sys.stdout.flush()
                        del buf[:checksum_pos + 1]
                        found = True
                        break
                if not found:
                    del buf[i:i+1]
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        ser.close()

if __name__ == '__main__':
    main()

