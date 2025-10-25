import serial
import sys
import time
import argparse

def open_serial(path, baud, timeout=0.1, retry_delay=1.0, max_retries=10):
    attempts = 0
    while attempts < max_retries:
        try:
            return serial.Serial(path, baud, timeout=timeout)
        except Exception:
            attempts += 1
            if attempts >= max_retries:
                raise
            time.sleep(retry_delay)
            continue

def sanitize_text(bytes_payload):
    try:
        text = bytes_payload.decode("utf-8", errors="replace")
    except:
        text = "".join(chr(b) if 32 <= b < 127 else "?" for b in bytes_payload)
    return "".join(ch if 32 <= ord(ch) < 127 else "?" for ch in text)

def parse_and_print(buf):
    while True:
        i = buf.find(b"\xAA\x55")
        if i == -1:
            if len(buf) > 2:
                buf = buf[-2:]
            return [], buf
        if len(buf) - i < 3:
            return [], buf
        length = buf[i + 2]
        total = 4 + length
        if len(buf) - i < total:
            return [], buf
        payload = buf[i + 3 : i + 3 + length]
        checksum = buf[i + 3 + length]
        if (sum(payload) & 0xFF) == checksum:
            msg = sanitize_text(payload)
            del buf[: i + total]
            return [msg], buf
        else:
            del buf[i : i + 1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port")
    args = parser.parse_args()
    PORT = f"/dev/tty{args.port}"
    BAUD = 115200
    ser = None
    try:
        while True:
            try:
                ser = open_serial(
                    PORT, BAUD, timeout=0.1, retry_delay=1.0, max_retries=10
                )
            except Exception:
                print(
                    f"Could not connect to {PORT} after 10 seconds, exiting."
                )
                sys.stdout.flush()
                break
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
                        msgs, buf = parse_and_print(buf)
                        for m in msgs:
                            print(m)
                            sys.stdout.flush()
                    else:
                        time.sleep(0.01)
            finally:
                try:
                    ser.close()
                except:
                    pass
                ser = None
    except KeyboardInterrupt:
        print("\nStopping...")
        sys.stdout.flush()

if __name__ == "__main__":
    main()

