import network
import time
from machine import Pin, I2C
import dht
import ujson
from umqtt.simple import MQTTClient
from i2c_lcd import I2cLcd  # Import the custom I2C_LCD class
import ussl as ssl

# MQTT Server Parameters
MQTT_CLIENT_ID = "ESP32-001"
MQTT_BROKER    = "a23sutvtpz6muq-ats.iot.ap-southeast-1.amazonaws.com"
MQTT_TOPIC     = "test"

# DHT22 sensor setup
sensor = dht.DHT22(Pin(15))

# I2C and LCD setup (adjust the I2C address if necessary)
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)  # SDA to pin 27, SCL to pin 26
I2C_ADDR = 0x27  # Default I2C address for the LCD
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)  # Assuming a 16x2 LCD

# Private key and certificate (paste the contents here as strings)
key_data = """
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA40vgDoDotAi9FyayvIlOMP0id6mzmDFRA0xHoRh1pNdgpnLY
/dSbhdCE40AiHo1qxqEs4JnWuPPzPrho4CwbnpxMaWtCpaLBODqagLGOfOoNJ7ua
IR5dVck6cIb0kESA/4N8pqBioroCflIZeYiSkHEJDvjqpw0D4IU5Ovz6DZrrJ1Ln
o/U67VevzKQ2Pz6ufBh76Qb3whCb+OQ9oKzK1eGdqKkyuO88Raag0BXhZ+Nymd6y
ZSmleSwDMM8NCQg6Lx5V3k4CcBkvATOYNoQ7MGCPsItE/NIsCItnn7Iq5UDfQDr3
587wi205oRS8/7ynCurkltafFB7jdfyF5rXeOQIDAQABAoIBAET9XsCIOBmNHXfN
cyrusiEEdFXF2JE1RtWtbYBkIDEsflWHPn2s7perNuqTKMgFPIeVnD1/9ECnKwm6
h3qjaK632imVOOF1iRg8EXFGc21OzTdmJd4vjTzgmzBUhh7T7COiEU+yFr41n1Qg
L0NIRNQ6uvkkbHTP6oFXbouNBYjjDlSF3kjaS7tjJCLjF3gKKelmp0F4riTzAd0z
7In0gaaIrUn5ptc5mXk5ZPIK/2+8oj2NTHw0tubCwrkWfHAcdfs6lF8jBZLoolvz
AtC6xXl1G+leQBefmcFvceSVyZWtW58D5/AKrII1oMOTSJysDhsYnC++tubkLrdO
CwN0IgECgYEA8zGFncxnxW4GNR4FKGu+lCW8coAZg1fPo7qQyc+RsyKYWiF5Y2Qa
Vr2V+ADgiEqRG/y0T1vR6u5c3XItGWZ+IBzPJbCtfirH7qRApBVHXiznMljNZ9kY
5mgQ6GPO5RVX24MZzq8fqkKMd+c5xAeV2YtJ56v4Dxco02aZBGWKxBECgYEA70QL
vyAT3Eb24lUpmjfCLO0ux3cIiYADn4tQZI4emSDaVL0zZyDvp/qeP1aYoU2OO7bb
6H/hi/YejxIQGE4nza6kB2/jEY2QZgmWq2UQt+UezBdq9ynNVKUlxdyA0aIbwVPP
ya3QoA0IdaBFK1C8kWIY1oKj/3gBXgEemTd2f6kCgYAE0BkV22K+XIQQ7wwpFaDK
68hD99cJa2Z3lgyhgdMfWXLsbbcqSWPgDZZ3NwU6jUc7549l9qo73QXHeCf+VbHv
TsKmu01jrtMQHP4OgUFNUtQsgedmw7wjazHSd48zp216saiEF6EnzHNdOB1DjObh
TEllJVkea1XqgSBMHvpVEQKBgQC8epPuSSyb92MARCnzjDzv+x9Ajaox9p/kDHCV
5caAxfp3ilt1v+JKJwiFyIePeXKz44Y0Dpj0EjtcZNQ88UQ1qH8aRK9Q4n1/g8om
1gRneJvcFg5zCYDwTvAEf4ESomrOzmD+9GdFzT5+unQCfSUuOWJriJn74uLg1Gzw
MVqtkQKBgG2DuPf1NazRqwTx6Rh5pMiochp+aEWp9mQAiftndhTQMcz5bMsYZiZ2
tAsP0fipjEWXXD7ohH7PbaORSyvUjUn2NrA0k6lIEZlNTOIv6gUFwyynggJfpDog
TMLWw0xRa7Umd5261FuZO6cFskqxUT0rVqYcJwPq/9z4Y/OWXRgE
-----END RSA PRIVATE KEY-----
"""

cert_data = """
-----BEGIN CERTIFICATE-----
MIIDWjCCAkKgAwIBAgIVAMLFyQVxqWVsqu7pI/s1cf9Vi7GHMA0GCSqGSIb3DQEB
CwUAME0xSzBJBgNVBAsMQkFtYXpvbiBXZWIgU2VydmljZXMgTz1BbWF6b24uY29t
IEluYy4gTD1TZWF0dGxlIFNUPVdhc2hpbmd0b24gQz1VUzAeFw0yNDEwMDgwMjE5
MjFaFw00OTEyMzEyMzU5NTlaMB4xHDAaBgNVBAMME0FXUyBJb1QgQ2VydGlmaWNh
dGUwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDjS+AOgOi0CL0XJrK8
iU4w/SJ3qbOYMVEDTEehGHWk12Cmctj91JuF0ITjQCIejWrGoSzgmda48/M+uGjg
LBuenExpa0KlosE4OpqAsY586g0nu5ohHl1VyTpwhvSQRID/g3ymoGKiugJ+Uhl5
iJKQcQkO+OqnDQPghTk6/PoNmusnUuej9TrtV6/MpDY/Pq58GHvpBvfCEJv45D2g
rMrV4Z2oqTK47zxFpqDQFeFn43KZ3rJlKaV5LAMwzw0JCDovHlXeTgJwGS8BM5g2
hDswYI+wi0T80iwIi2efsirlQN9AOvfnzvCLbTmhFLz/vKcK6uSW1p8UHuN1/IXm
td45AgMBAAGjYDBeMB8GA1UdIwQYMBaAFDjd7jUnk8YcAzqEZS+3WV9WzQajMB0G
A1UdDgQWBBQqSBkX74xeYNhC1J87oOrgF/1gCDAMBgNVHRMBAf8EAjAAMA4GA1Ud
DwEB/wQEAwIHgDANBgkqhkiG9w0BAQsFAAOCAQEAnwrjVIbK1Z0XqfWoJRf7Fozw
GfmORlMI90kQR1QPJ5UveeVxdgmmKbT1YXBpDMoOV4H14XOP3CciFvaCaF42+csj
5YVsMIqFXVWrsYzwYWBBCtDw2MM6h875njG6GHf2fPoH/ruQSl99H+ZSQCU3ec22
7YVS/Lm8F4MPTdYeX0mdce1wsCaYNzHBylZnp35/XC3FnCDktUgmI2f9BJ/jr3vS
vwaCKDFTVEn0SAmR1S+V08KoLSMY9RYYjdVQXGgnGOZEgTEOs9vyGwMgiSE4pNon
VRGT+Xm3OKQTWudRL3bBHZNrllAVUQlkoKkle0X/Xnt2lS6X09GqxwPNq9vy4w==
-----END CERTIFICATE-----
"""

ca_data = """
-----BEGIN CERTIFICATE-----
MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6
b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv
b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj
ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM
9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw
IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6
VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L
93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm
jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC
AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA
A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI
U5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJeHZERxhlbI1Bjjt/msv0tadQ1wUs
N+gDS63pYaACbvXy8MWy7Vu33PqUXHeeE6V/Uq2V8viTO96LXFvKWlJbYK8U90vv
o/ufQJVtMVT8QtPHRh8jrdkPSHCa2XV4cdFyQzR1bldZwgJcJmApzyMZFo6IQ6XU
5MsI+yMRQ+hDKXJioaldXgjUkK642M4UwtBV8ob2xJNDd2ZhwLnoQdeXeGADbkpy
rqXRfboQnoZsG4q5WTP468SQvvG5
-----END CERTIFICATE-----
"""

# WiFi connection
print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
    print(".", end="")
    time.sleep(0.1)
print(" Connected!")

# MQTT setup
print("Connecting to MQTT server... ", end="")

ssl_params = {
    'key': key_data,
    'cert': cert_data,
    'cadata':ca_data
}
client = MQTTClient(
    MQTT_CLIENT_ID, 
    MQTT_BROKER, 
    ssl=True,
    ssl_params=ssl_params,
    port=8883
)

client.connect()

print("Connected!")

# Display welcome message on LCD
lcd.clear()
lcd.putstr("Weather Station")
time.sleep(2)

prev_weather = ""
while True:
    print("Measuring weather conditions... ", end="")
    sensor.measure() 
    temp = sensor.temperature()
    humidity = sensor.humidity()
    
    # Format the message for MQTT
    message = ujson.dumps({
        "temp": temp,
        "humidity": humidity,
    })
    
    # Display temperature and humidity on the LCD
    lcd.clear()
    lcd.putstr("Temp: {:.1f} C".format(temp))
    lcd.move_to(0, 1)
    lcd.putstr("Humidity: {:.1f}%".format(humidity))
    
    # Publish to MQTT if there is a change in the readings
    if message != prev_weather:
        print("Updated!")
        print("Reporting to MQTT topic {}: {}".format(MQTT_TOPIC, message))
        client.publish(MQTT_TOPIC, message)
        prev_weather = message
    else:
        print("No change")
        
    time.sleep(2)