import asyncio
import tesla_fleet_api
from tesla_fleet_api import TeslaBluetooth
from tesla_fleet_api.const import BluetoothVehicleData
from time import sleep
import json
from pathlib import Path

def get_config() -> dict:
    with open(Path("~/.cyber_pi.config").expanduser(), 'r') as f:
        return json.load(f)

async def main():
    config = get_config()
    key_path: str = config.get("key_path", '')
    vin: str = config.get("vin", '')
    tesla_bluetooth = TeslaBluetooth()
    await tesla_bluetooth.get_private_key(key_path)
    vehicle = tesla_bluetooth.vehicles.create(vin)
    await vehicle.find_vehicle()
    print(f"Created VehicleBluetooth instance for VIN: {vehicle.vin}")

    data = await vehicle.vehicle_data([BluetoothVehicleData.CLOSURES_STATE])
    print(f"Data: {data}")

    # while True:
    #     data = await vehicle.vehicle_data([BluetoothVehicleData.CLOSURES_STATE])
    #     print(f"Open: {data.closures_state.door_open_passenger_front}")
        # sleep(.25)

asyncio.run(main())

