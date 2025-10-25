#include "NonBlockingSerial.h"

NonBlockingSerial::NonBlockingSerial(Stream& serial, uint32_t timeout_ms)
    : _serial(serial), _timeout_ms(timeout_ms) {}

void NonBlockingSerial::setTimeoutMs(uint32_t timeout_ms) {
    _timeout_ms = timeout_ms;
}

bool NonBlockingSerial::sendMessage(const uint8_t* payload, size_t payload_len) {
    if (payload_len > 253) return false;
    size_t frame_len = payload_len + 2;
    uint8_t checksum = 0;
    for (size_t i = 0; i < payload_len; i++) {
        checksum += payload[i];
    }
    checksum &= 0xFF;
    unsigned long start = millis();
    while (_serial.availableForWrite() < (int)(frame_len + 1)) {
        if (millis() - start > _timeout_ms) return false;
        yield();
    }
    _serial.write(0xAA);
    _serial.write(0x55);
    _serial.write(payload, payload_len);
    _serial.write(checksum);
    return true;
}

bool NonBlockingSerial::sendU8(uint8_t value) {
    return sendMessage(&value, 1);
}

bool NonBlockingSerial::sendU16(uint16_t value) {
    uint8_t payload[2];
    payload[0] = (value >> 8) & 0xFF;
    payload[1] = value & 0xFF;
    return sendMessage(payload, 2);
}

bool NonBlockingSerial::sendU32(uint32_t value) {
    uint8_t payload[4];
    payload[0] = (value >> 24) & 0xFF;
    payload[1] = (value >> 16) & 0xFF;
    payload[2] = (value >> 8) & 0xFF;
    payload[3] = value & 0xFF;
    return sendMessage(payload, 4);
}

bool NonBlockingSerial::sendBytes(const uint8_t* data, size_t len) {
    return sendMessage(data, len);
}

