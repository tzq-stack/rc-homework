#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from cpp01_topic.msg import StudentInfo

class StudentSubscriber(Node):
    def __init__(self):
        super().__init__("student_subscriber")
        self.sub = self.create_subscription(
            StudentInfo,
            "student_topic",
            self.callback,
            10
        )

    def callback(self, msg):
        # 收到消息打印学号姓名
        self.get_logger().info(f"接收：学号={msg.student_id}，姓名={msg.student_name}")

def main(args=None):
    rclpy.init(args=args)
    node = StudentSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

