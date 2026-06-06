import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class DroneSubscriber(Node):
    def __init__(self):
        super().__init__('drone_subscriber')
        self.sub = self.create_subscription(
            String,
            'drone_status',
            self.listener_callback,
            10)
        self.get_logger().info('Drone Subscriber Node Started')

    def listener_callback(self, msg):
        self.get_logger().info(f'Ground Station received: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = DroneSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
