#
# Notes:
#
#   LLCC68 wants 5V
#

import time
import sys

sys.path.append("hwlib/e220")

from machine import UART, Pin

from lora_e220 import (
    LoRaE220,
    Configuration,
    print_configuration,
)

from lora_e220_constants import (
    UARTParity,
    UARTBaudRate,
    TransmissionPower,
    FixedTransmission,
    AirDataRate,
    OperatingFrequency,
    LbtEnableByte,
    WorPeriod,
    RssiEnableByte,
    RssiAmbientNoiseEnable,
    SubPacketSetting,
)

from lora_e220_operation_constant import ResponseStatusCode

#
# TTGO available pins: 2, 12, 13, 15, 27, 32, 33
# 25, 26 are DAC pins that can be programmed to a voltage
#

LORA_AUX = 15  # 4.7k pulldown
LORA_M0 = 12
LORA_M1 = 13
LORA_RX = 32  # on esp32 and 4.7k pulldown
LORA_TX = 33  # on esp32 and 4.7k pulldown

UART_ID = 2

CHAN = 65  # Frequency: Base Freq 850.125 + 65 = 915.125

#
# Many of the config settings are optional,
# but are included here as examples.
#
cfg_900t22d = Configuration("900T22D")
cfg_900t22d.ADDL = 0x02
cfg_900t22d.ADDH = 0x01
cfg_900t22d.CHAN = 65

cfg_900t22d.SPEED.airDataRate = AirDataRate.AIR_DATA_RATE_000_24
cfg_900t22d.SPEED.uartParity = UARTParity.MODE_00_8N1
cfg_900t22d.SPEED.uartBaudRate = UARTBaudRate.BPS_9600

cfg_900t22d.OPTION.transmissionPower = (
    TransmissionPower("900T22D").get_transmission_power().POWER_10
)
# alternately:
# cfg_900t22d.OPTION.transmissionPower = TransmissionPower22.POWER_10

cfg_900t22d.OPTION.RSSIAmbientNoise = RssiAmbientNoiseEnable.RSSI_AMBIENT_NOISE_ENABLED
cfg_900t22d.OPTION.subPacketSetting = SubPacketSetting.SPS_064_10

cfg_900t22d.TRANSMISSION_MODE.fixedTransmission = FixedTransmission.FIXED_TRANSMISSION
cfg_900t22d.TRANSMISSION_MODE.WORPeriod = WorPeriod.WOR_1500_010
cfg_900t22d.TRANSMISSION_MODE.enableLBT = LbtEnableByte.LBT_DISABLED

# cfg_900t22d.TRANSMISSION_MODE.enableRSSI = RssiEnableByte.RSSI_ENABLED
#
# code, value, rssi = lora.receive_message(True)
# code, value, rssi = lora.receive_dict(True)

cfg_900t22d.CRYPT.CRYPT_H = 1
cfg_900t22d.CRYPT.CRYPT_L = 1
## END OF CONFIG


def print_config(lora):
    code, conf = lora.get_configuration()
    print(f"LORA conf: {ResponseStatusCode.get_description(code)}")
    print_configuration(conf)


uart2 = UART(UART_ID, baudrate=9600, tx=LORA_TX, rx=LORA_RX)


try:
    lora = LoRaE220(
        uart2,
        "900T22D",
        LORA_TX,
        LORA_RX,
        aux_pin=LORA_AUX,
        m0_pin=LORA_M0,
        m1_pin=LORA_M1,
        uart_baudrate=9600,
    )
    print_config(lora)
    code, conf_new = lora.set_configuration(cfg_900t22d)
    print_config(lora)
    code = lora.begin()
except Exception as e:
    sys.print_exception(e)
    sys.exit(1)
