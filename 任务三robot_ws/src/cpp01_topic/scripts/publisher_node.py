#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from cpp01_topic.msg import StudentInfo

class StudentPublisher(Node):
    def __init__(self):
        super().__init__("student_publisher")
        self.f_log=open ("log1.txt","a",encoding="utf-8")
        # 创建发布者，话题名student_topic，队列10
        self.pub = self.create_publisher(StudentInfo, "student_topic", 10)
        # 定时器1秒执行一次
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        msg = StudentInfo()
        msg.student_id = "2025115237"
        msg.student_name = "田展旗"
        self.pub.publish(msg)
        self.get_logger().info(f"发布：学号={msg.student_id}, 姓名={msg.student_name}")
        self.f_log.write(f"发布：学号={msg.student_id}, 姓名={msg.student_name}\n")
        self.f_log.flush()

def main(args=None):
    rclpy.init(args=args)
    node = StudentPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

