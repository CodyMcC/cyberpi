
from time import perf_counter
print(1, perf_counter())
import asyncio
print(2, perf_counter())
# import tesla_fleet_api
from tesla_fleet_api import TeslaBluetooth
print(3, perf_counter())
from tesla_fleet_api.tesla import VehicleBluetooth
print(4, perf_counter())
from tesla_fleet_api.const import BluetoothVehicleData
print(5, perf_counter())
from time import sleep
print(6, perf_counter())
from typing import Optional, Union
print(7, perf_counter())
import json
print(8, perf_counter())
from pathlib import Path
print(9, perf_counter())
try:
    from gpiozero import LED
except ImportError:
    print("gpiozero not found, running in simulation mode.")
    from mock_gpiozero import LED  # Fallback for simulation
    
print(10, perf_counter())
import signal
print(11, perf_counter())
import sys
print(12, perf_counter())
import logging
print(13, perf_counter())

from cryptography.exceptions import InvalidSignature, InvalidTag
print(14, perf_counter())


DRIVER_LIGHT_PIN = 21  # GPIO pin for the driver light (Bottom left corner)
PASSENGER_LIGHT_PIN = 20  # GPIO pin for the passenger light (Second from the bottom left corner)


def signal_handler(sig, frame):
    print('\nYou pressed Ctrl+C!')
    sys.exit(0)


def setup_logging():
    logging_start = perf_counter()
    logger = logging.getLogger('cyber-pi')
    logger.setLevel(logging.DEBUG)  # Set the logger's minimum level

    # Create file handler (logs DEBUG and above to file)
    file_handler = logging.FileHandler('cyber_pi.log')
    file_handler.setLevel(logging.DEBUG)

    # Create console handler (logs INFO and above to stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')

    # Assign formatters to handlers
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.info(f"Logging setup complete in {perf_counter() - logging_start:.2f} seconds")
    return logger



class Relay:
    def __init__(self, pin: int, description: str, logger: Optional[logging.Logger] = None):
        self.pin = pin
        self.state = False
        self.switch = LED(pin)  
        self.description = description
        self.logger = logger

    def on(self):
        if self.state:
            return
        self.state = True
        self.switch.on()  
        message = f"Relay on pin {self.pin} turned ON ({self.description})"
        self.logger.info(message) if self.logger else print(message)
        
    def off(self):
        if not self.state:
            return
        self.state = False
        self.switch.off()
        message = f"Relay on pin {self.pin} turned OFF ({self.description})"
        self.logger.info(message) if self.logger else print(message)


def get_config(path="~/.cyber_pi.config") -> dict:
    with open(Path(path).expanduser(), 'r') as f:
        return json.load(f)


async def establish_connection(key_path: str, vin: str, logger: logging.Logger) -> VehicleBluetooth:
    logger.info("Establishing connection to Tesla vehicle...")
    tesla_bluetooth = TeslaBluetooth()
    await tesla_bluetooth.get_private_key(key_path)
    vehicle = tesla_bluetooth.vehicles.create(vin)

    try:
        await vehicle.find_vehicle()
    except ValueError as e:
        logger.error(f"Error finding vehicle: {e}")
        logger.info("Please check your VIN and key path in the configuration file.")
        sys.exit(1)

    logger.info(f"Created VehicleBluetooth instance for VIN: {vehicle.vin}")
    return vehicle

async def main():
    signal.signal(signal.SIGINT, signal_handler)

    logger = setup_logging()
    logger.info("Starting CyberPi application...")

    driver_side_relay = Relay(DRIVER_LIGHT_PIN, "driver", logger)  # Relay for driver side light
    passenger_side_relay = Relay(PASSENGER_LIGHT_PIN, "passenger", logger)  # Relay for passenger
    lock_relay = Relay(16, "lock", logger)  # Relay for lock (not used in this example) 


    config = get_config()
    key_path: str = str(Path(config.get("key_path", '')).expanduser())
    vin: str = config.get("vin", '')
    
    
    
    while True:
        vehicle = await establish_connection(key_path, vin, logger)

        while True:

            try:
                data = await vehicle.vehicle_data([BluetoothVehicleData.CLOSURES_STATE])
                # print(data)
            except TimeoutError as e:
                logger.error(f"Timeout error while fetching vehicle data (break): {e}")
                # await asyncio.sleep(5)
                break  # Exit the inner loop to re-establish connection
            except InvalidTag as e:
                logger.error(f"Invalid tag error while fetching vehicle data (break): {e}")
                # await asyncio.sleep(5)
                break

            # logger.info(f"Driver open: {data.closures_state.door_open_driver_front or data.closures_state.door_open_driver_rear} - Passenger open: {data.closures_state.door_open_passenger_front or data.closures_state.door_open_passenger_rear}")
            
            if data.closures_state.door_open_passenger_front or data.closures_state.door_open_passenger_rear:
                passenger_side_relay.on()
            else:
                passenger_side_relay.off()
            
            if data.closures_state.door_open_driver_front or data.closures_state.door_open_driver_rear:
                driver_side_relay.on()
            else:
                driver_side_relay.off()

            if data.closures_state.locked:
                lock_relay.off()
            else:
                lock_relay.on()


asyncio.run(main())


