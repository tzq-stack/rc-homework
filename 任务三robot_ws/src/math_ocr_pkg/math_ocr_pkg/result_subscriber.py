#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from math_ocr_pkg.msg import CalcResult

class ResultSubscriber(Node):
    def __init__(self):
        super().__init__("result_subscriber")
        self.sub = self.create_subscription(
            CalcResult,
            "/calculation_result",
            self.callback,
            10
        )

    def callback(self, msg):
        expr_safe = msg.expr.replace("\n", "").strip()
        self.get_logger().info(f"【订阅接收】原始表达式：{expr_safe} | 计算结果：{msg.result:.2f}")

def main(args=None):
    rclpy.init(args=args)
    node = ResultSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

