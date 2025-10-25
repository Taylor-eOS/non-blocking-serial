#ifndef NON_BLOCKING_SERIAL_H
#define NON_BLOCKING_SERIAL_H
#include <Arduino.h>

class NonBlockingSerial {
public:
    NonBlockingSerial(Stream& serial, uint32_t timeout_ms = 50);
    bool sendU8(uint8_t value);
    bool sendU16(uint16_t value);
    bool sendU32(uint32_t value);
    bool sendBytes(const uint8_t* data, size_t len);
    void setTimeoutMs(uint32_t timeout_ms);
private:
    Stream& _serial;
    uint32_t _timeout_ms;
    bool sendMessage(const uint8_t* payload, size_t payload_len);
};

#endif

