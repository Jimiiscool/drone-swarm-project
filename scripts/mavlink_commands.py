import time
from pymavlink import mavutil
alt_tolerance  = 0.7
offset_100 = 0.0009
from search_pattern import meters_to_lat
from search_pattern import meters_to_lon
from search_pattern import waypoint_generator
waypoint_tolerance = 5 / 111000


#Connect to SITL
connection_string = 'udp:127.0.0.1:14550'
print(f"connecting to vehicle on {connection_string}")
vehicle = mavutil.mavlink_connection(connection_string)

print("Waiting for heartbeat...")
vehicle.wait_heartbeat()
print(f'Heartbeat received from system: {vehicle.target_system}')

vehicle.set_mode(4)

vehicle.mav.command_long_send(1, 0, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
received = vehicle.recv_match(type = 'COMMAND_ACK', blocking = True, timeout=5)

if received:
    result  = received.result
    command = received.command
    target_component = received.target_component
time.sleep(1)

vehicle.mav.command_long_send(1, 0, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,  0, 0, 0, 0, 0, 0, 0, 15)
takeoff = vehicle.recv_match(type = 'COMMAND_ACK', blocking = True, timeout = 5)

if  takeoff:
    print(takeoff)


alt = 0
alt_tolerance  = 0.5


while alt <  (15 - alt_tolerance):
    position  = vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout = 5)

    if position:
        lat = position.lat / 1e7
        lon = position.lon / 1e7
        alt = position.relative_alt / 1000.0
        print(f"GPS Position: Lat {lat:.6f}, Lon {lon:.6f}, Alt {alt:.2f} m")
    else:
        print("No GPS data received")
    time.sleep(2)



waypoints = waypoint_generator(13, 70, 20, lat, lon)


for wp in waypoints:
    vehicle.mav.set_position_target_global_int_send(0, 1, 0, 6, 3576, int(wp[0]*1e7), int(wp[1]*1e7), 15, 0, 0, 0, 0, 0, 0, 0, 0)
    
    lat_diff = float('inf')
    lon_diff = float('inf')
    while lat_diff > waypoint_tolerance or lon_diff > waypoint_tolerance:
        pose = vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout = 5)
        if pose:
            lat = pose.lat/1e7
            lon = pose.lon/1e7
            alt = pose.alt/1000.0
            lat_diff = abs(lat - wp[0])
            lon_diff = abs(lon - wp[1])
        else:
            print("No Position received")
        
        time.sleep(1)
    print('Arrived at point')



time.sleep(1)
vehicle.mav.command_long_send(1, 0, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0, 0, 0)
landed = vehicle.recv_match(type  = 'COMMAND_ACK', blocking = True, timeout= 5)

if landed:
    print(landed)