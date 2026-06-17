import time
from pymavlink import mavutil
from math import cos, radians

#Connect to SITL
connection_string = 'udp:127.0.0.1:14550'
print(f"connecting to vehicle on {connection_string}")
vehicle = mavutil.mavlink_connection(connection_string)

print("Waiting for heartbeat...")
vehicle.wait_heartbeat()
print(f'Heartbeat received from system: {vehicle.target_system}')


def  meters_to_lat(meters):
    degrees = meters/111000
    return degrees

def meters_to_lon(meters, current_lat):
    degrees = meters/(111000*cos(radians(current_lat)))
    return degrees


#Get Current GPS Position
msg = None
while msg is None:
    msg = vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=False, timeout = 5)
    time.sleep(1)
    if msg:
        lat = msg.lat / 1e7
        lon = msg.lon / 1e7
        alt = msg.relative_alt / 1000.0
        print(f"GPS Position: Lat {lat:.6f}, Lon {lon:.6f}, Alt {alt:.2f} m")
    else:
        print("Waiting for GPS Data")
        time.sleep(1)

search_height = 50
strip_width = 20
strip_length = 35



#Generate Waypoints for search
def  waypoint_generator(strip_length, search_height, strip_width, lat, lon):
    rows = search_height//strip_width + 1
    waypoints = []
    for row in range(rows):
        current_lat = lat + (row*meters_to_lat(strip_width))
        if row%2 == 0:
            waypoints.append((current_lat, lon))
            waypoints.append((current_lat, lon+meters_to_lon(strip_length, current_lat)))
        else:
            waypoints.append((current_lat, lon+meters_to_lon(strip_length, current_lat)))
            waypoints.append((current_lat, lon))
    return waypoints



#Testing Script
test_waypoints = waypoint_generator(strip_length, search_height, strip_width, lat, lon)

for i, wp in enumerate(test_waypoints):
    print(f"Waypoint {i}: lat={wp[0]:.6f}, lon={wp[1]:.6f}")

    


