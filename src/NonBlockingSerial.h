#ifndef NON_BLOCKING_SERIAL_H
#define NON_BLOCKING_SERIAL_H

#include <Arduino.h>

class NonBlockingSerial {
public:
    NonBlockingSerial(Stream& serial, uint32_t timeout_ms = 50);
    bool send(const char* s);
    void setTimeoutMs(uint32_t timeout_ms);
private:
    Stream& _serial;
    uint32_t _timeout_ms;
    static constexpr size_t MAX_PAYLOAD = 250;
    bool sendMessage(const uint8_t* payload, size_t payload_len);
};
#endif

