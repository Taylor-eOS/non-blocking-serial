#include "NonBlockingSerial.h"
#include <string.h>

NonBlockingSerial::NonBlockingSerial(Stream& serial, uint32_t timeout_ms)
    : _serial(serial), _timeout_ms(timeout_ms) {}

void NonBlockingSerial::setTimeoutMs(uint32_t timeout_ms) {
    _timeout_ms = timeout_ms;
}

bool NonBlockingSerial::send(const char* s) {
    size_t len = strlen(s);
    if (len > MAX_PAYLOAD) len = MAX_PAYLOAD;
    uint8_t buf[MAX_PAYLOAD];
    for (size_t i = 0; i < len; ++i) {
        unsigned char c = (unsigned char)s[i];
        if (c < 32 || c >= 127) buf[i] = '?';
        else buf[i] = (uint8_t)c;
    }
    return sendMessage(buf, len);
}

bool NonBlockingSerial::sendMessage(const uint8_t* payload, size_t payload_len) {
    if (payload_len > MAX_PAYLOAD) return false;
    uint8_t header0 = 0xAA;
    uint8_t header1 = 0x55;
    uint8_t lenb = (uint8_t)payload_len;
    uint8_t checksum = 0;
    for (size_t i = 0; i < payload_len; ++i) checksum += payload[i];
    checksum &= 0xFF;
    size_t total = 4 + payload_len;
    unsigned long start = millis();
    while (_serial.availableForWrite() < (int)total) {
        if (millis() - start > _timeout_ms) return false;
        yield();
    }
    _serial.write(header0);
    _serial.write(header1);
    _serial.write(lenb);
    if (payload_len) _serial.write(payload, payload_len);
    _serial.write(checksum);
    return true;
}

