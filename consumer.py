import serial
import sys
import time
import argparse

def open_serial(port, baud, timeout=0.1, retry_delay=1.0):
    while True:
        try:
            return serial.Serial(port, baud, timeout=timeout)
        except Exception:
            time.sleep(retry_delay)
            continue

def extract_messages(buf):
    messages = []
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
                    messages.append(payload.decode('utf-8'))
                except:
                    messages.append(f"[Binary data: {payload.hex()}]")
                del buf[:checksum_pos + 1]
                found = True
                break
        if not found:
            del buf[i:i+1]
    return messages, buf

def main():
    parser = argparse.ArgumentParser(description='Serial port listener')
    parser.add_argument('port', help='Serial port suffix (e.g., USB0 or ACM0)')
    args = parser.parse_args()
    PORT = f'/dev/tty{args.port}'
    BAUD = 115200
    ser = None
    try:
        while True:
            ser = open_serial(PORT, BAUD, timeout=0.1, retry_delay=1.0)
            print(f"Listening on {PORT}...")
            sys.stdout.flush()
            buf = bytearray()
            try:
                while True:
                    try:
                        data = ser.read(64)
                    except (serial.SerialException, OSError):
                        break
                    if data:
                        buf += data
                    else:
                        time.sleep(0.01)
                        continue
                    messages, buf = extract_messages(buf)
                    for m in messages:
                        print(m)
                        sys.stdout.flush()
            finally:
                try:
                    ser.close()
                except:
                    pass
                ser = None
    except KeyboardInterrupt:
        print("\nStopping...")
        sys.stdout.flush()

if __name__ == '__main__':
    main()

