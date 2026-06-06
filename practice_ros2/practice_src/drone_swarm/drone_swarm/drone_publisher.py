import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class DronePublisher(Node):
	def __init__(self):
		super().__init__('drone_publisher')
		self.publisher_ = self.create_publisher(String, 'drone_status', 10)
		self.timer = self.create_timer(1.0, self.timer_callback)
		self.get_logger().info('Drone Publisher Node Started')

	def timer_callback(self):
		msg = String()
		msg.data = 'Drone 1 online - all systems nominal'
		self.publisher_.publish(msg)
		self.get_logger().info(f'Publishing: {msg.data}')

def main(args=None):
	rclpy.init(args=args)
	node = DronePublisher()
	rclpy.spin(node)
	node.destroy_node()
	rclpy.shutdown()
if __name__ == '__main__':
	main()
