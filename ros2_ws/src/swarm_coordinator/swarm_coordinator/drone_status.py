import time
from pymavlink import mavutil
import rclpy
from rclpy.node import Node
import threading
from swarm_msgs.msg import DroneStatus
from std_msgs.msg import String

class DroneStatusNode(Node):
    def  __init__(self):
        super().__init__('drone_status_node')
        self.declare_parameter('drone_id', 1)
        self.drone_id = self.get_parameter('drone_id').value
        self.declare_parameter('connection_link', 'udp:127.0.0.1:14550')
        self.connection_string = self.get_parameter('connection_link').value
        self.vehicle = mavutil.mavlink_connection(self.connection_string)
        self.get_logger().info('Waiting for heartbeat...')
        self.vehicle.wait_heartbeat()
        self.get_logger().info('Heartbeat received!')
        self.lat = 0.0
        self.lon = 0.0
        self.alt = 0.0
        self.battery = 0.0
        self.battery_left = 0.0
        self.volt_battery = 0.0
        self.mission_state = 'idle'
        self.current_waypoint = 0
        self.total_waypoints = 0
        self.lock = threading.Lock()
        status_topic = f"/drone_{self.drone_id}/status"
        command_topic = f"/drone_{self.drone_id}/commands"
        self.status_publisher = self.create_publisher(DroneStatus, status_topic, 10)
        self.command_subscriber = self.create_subscription(String, command_topic, self.command_callback, 10)
        self.create_timer(2.0, self.publish_status)
        self.mavlink_thread = threading.Thread(target=self.mavlink_poll, daemon=True)
        self.mavlink_thread.start()
        
    def  mavlink_poll(self):

        self.get_logger().info('MAVLink polling thread started')
        while True:
            pose = self.vehicle.recv_match(type='GLOBAL_POSITION_INT',  blocking=True, timeout=5)
            if pose is not None:
                with self.lock:
                    self.lat = pose.lat / 1e7
                    self.lon = pose.lon / 1e7
                    self.alt = pose.relative_alt / 1000.0
            status = self.vehicle.recv_match(type='SYS_STATUS', blocking=True, timeout=5)
            if status is not None:
                with self.lock:
                    self.battery = status.current_battery / 100.0
                    self.battery_left = float(status.battery_remaining)
                    self.volt_battery = status.voltage_battery / 1000.0
            time.sleep(0.1)


    def publish_status(self):
        msg = DroneStatus()
        with self.lock:
            msg.drone_id = self.drone_id
            msg.lat = self.lat
            msg.lon = self.lon
            msg.alt = self.alt
            msg.battery_left = self.battery_left
            msg.volt_battery = self.volt_battery
            msg.mission_state = self.mission_state
            msg.current_waypoint = self.current_waypoint
            msg.total_waypoints = self.total_waypoints
            msg.timestamp = time.time()
        self.status_publisher.publish(msg)
        self.get_logger().info(f'Drone {self.drone_id} status published — battery: {self.battery_left}% alt: {self.alt:.2f}m state: {self.mission_state}')

    def command_callback(self, msg):
        command = msg.data
        self.get_logger().info(f"Received command for drone {self.drone_id}: {command}")
        command_parts = command.split(':')
        command_type = command_parts[0]
        if command_type == 'RTH':
            self.mission_state = 'returning'
            self.get_logger().info(f"Drone {self.drone_id} is returning to base.")
        elif command_type == 'LAND':
            self.mission_state = 'landing'
            self.get_logger().info(f"Drone {self.drone_id} is emergency landing.")
        elif command_type == 'WAYPOINTS':
            if len(command_parts) > 1:
                waypoints_info = command_parts[1]
                self.mission_state = 'assigned'
                self.get_logger().info(f"Drone {self.drone_id} received new zone assignment.")


            else:
                self.get_logger().warning('WAYPOINTS command received but no data included')
        else:
            self.get_logger().warning(f"Unknown command type: {command_type}")


def main(args=None):
    rclpy.init(args=args)
    drone_status_node = DroneStatusNode()
    rclpy.spin(drone_status_node)
    drone_status_node.destroy_node()
    rclpy.shutdown()
        