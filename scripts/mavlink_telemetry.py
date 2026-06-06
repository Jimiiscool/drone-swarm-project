import time
from pymavlink import mavutil

#Connect to vehicle
#When using SITL, this will be: udp:127.0.0.1:14550
# When using real hardware this will be: /dev/ttyAMA0 (RPi UART)
def connect_to_vehicle(connection_string):
    print(f"Connecting to vehicle on: {connection_string}")
    vehicle = mavutil.mavlink_connection(connection_string)
    
    #Wait for heartbeat
    print("Waiting for heartbeat...")
    vehicle.wait_heartbeat()
    print(f"Heartbeat received from system {vehicle.target_system} ")
    return vehicle

#Read basic telemetry data
def read_telemetry(vehicle):
    print('\n ---- Telemetry Data ----')

    #Get GPS Position
    msg = vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=False, timeout = 5)
    if msg:
        lat = msg.lat / 1e7
        lon = msg.lon / 1e7
        alt = msg.relative_alt / 1000.0
        print(f"GPS Position: Lat {lat:.6f}, Lon {lon:.6f}, Alt {alt:.2f} m")
    else:
        print("No GPS data received")

    #Get Battery Status
    msg = vehicle.recv_match(type = 'SYS_STATUS', blocking = False, timeout = 5)
    if msg:
        voltage = msg.voltage_battery / 1000.0
        current = msg.current_battery / 100.0
        remaining = msg.battery_remaining
        print(f"Battery: {voltage:.2f} V, {current:.2f} A, {remaining}% remaining")
    else:
        print("No battery data received")
    
#Main Loop
def main():
    #SITL connection for now
    #Change to actual connection when hardware is available
    connection_string = 'udp:127.0.0.1:14550'
    vehicle = connect_to_vehicle(connection_string)

    print("\nReading telemetry every 2 seconds. Press Ctrl+C to exit.\n")
    try:
        while True:
            read_telemetry(vehicle)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nExiting telemetry reader.")
        vehicle.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()