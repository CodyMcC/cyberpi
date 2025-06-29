import asyncio
import tesla_fleet_api
from tesla_fleet_api import TeslaBluetooth
from tesla_fleet_api.const import BluetoothVehicleData
from time import sleep
from typing import Optional, Union
import json
from pathlib import Path
try:
    from gpiozero import LED
except ImportError:
    print("gpiozero not found, running in simulation mode.")
    from mock_gpiozero import LED  # Fallback for simulation
    

import signal
import sys
import logging


DRIVER_LIGHT_PIN = 21  # GPIO pin for the driver light (Bottom left corner)
PASSENGER_LIGHT_PIN = 20  # GPIO pin for the passenger light (Second from the bottom left corner)


def signal_handler(sig, frame):
    print('\nYou pressed Ctrl+C!')
    sys.exit(0)


def setup_logging():
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
    return logger


def get_config(path="~/.cyber_pi.config") -> dict:
    with open(Path(path).expanduser(), 'r') as f:
        return json.load(f)

async def main():
    signal.signal(signal.SIGINT, signal_handler)
    # Create a logger
    logger = setup_logging()
    logger.info("Starting CyberPi application...")

    
    driver_light = LED(DRIVER_LIGHT_PIN) 
    passenger_light = LED(PASSENGER_LIGHT_PIN) 


    config = get_config()
    key_path: str = str(Path(config.get("key_path", '')).expanduser())
    vin: str = config.get("vin", '')
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
    
    while True:
        data = await vehicle.vehicle_data([BluetoothVehicleData.CLOSURES_STATE])
        logger.info(f"Driver open: {data.closures_state.door_open_driver_front or data.closures_state.door_open_driver_rear} - Passenger open: {data.closures_state.door_open_passenger_front or data.closures_state.door_open_passenger_rear}")
        
        if data.closures_state.door_open_passenger_front or data.closures_state.door_open_passenger_rear:
            passenger_light.on()
            logger.info(f"Passenger door is open, turning on passenger light. ")
        else:
            passenger_light.off()
            logger.info(f"Passenger door is closed, turning off passenger light. ")
        
        if data.closures_state.door_open_driver_front or data.closures_state.door_open_driver_rear:
            driver_light.on()
        else:
            driver_light.off()

asyncio.run(main())


