#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
from math_ocr_pkg.msg import CalcResult


def safe_eval(single_line_expr: str):
    expr = single_line_expr.replace(" ", "")
    allowed_chars = "0123456789+-*/."
    clean_expr = ""
    for c in expr:
        if c in allowed_chars:
            clean_expr += c

    # 核心校验：开头必须数字，结尾必须数字
    if len(clean_expr) < 3:
        return None, clean_expr
    if not clean_expr[0].isdigit():
        return None, clean_expr
    if not clean_expr[-1].isdigit():
        return None, clean_expr
    # 中间至少要有一个运算符
    ops = {"+","-","*","/"}
    if not any(o in clean_expr for o in ops):
        return None, clean_expr

    bad_end = {"*", "/", "."}
    bad_start = {"*", "/", "."}
    if clean_expr[-1] in bad_end:
        return None, clean_expr
    if clean_expr[0] in bad_start:
        return None, clean_expr

    try:
        res = eval(clean_expr, {"__builtins__": None}, {})
        return float(res), clean_expr
    except Exception:
        return None, clean_expr


class MathOcrPublisher(Node):
    def __init__(self):
        super().__init__("math_ocr_publisher")
        self.f_log=open ("log.txt","a",encoding="utf-8")
        self.declare_parameter("cam_id", 0)
        self.declare_parameter("width", 1280)
        self.declare_parameter("height", 720)
        cam_id = self.get_parameter("cam_id").value
        w = self.get_parameter("width").value
        h = self.get_parameter("height").value

        self.pub = self.create_publisher(CalcResult, "/calculation_result", 10)
        self.cap = cv2.VideoCapture(cam_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        self.timer = self.create_timer(0.3, self.image_callback)

    def image_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warn("摄像头读取失败")
            return

        h, w = frame.shape[:2]
        x1 = int(w * 0.25)
        y1 = int(h * 0.35)
        x2 = int(w * 0.75)
        y2 = int(h * 0.65)
        roi = frame[y1:y2, x1:x2]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3,3), 0)
        _, bin_img = cv2.threshold(gray,160,255,cv2.THRESH_BINARY)

        kernel = np.ones((2,2), np.uint8)
        bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel)
        bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, kernel)

        # tesseract白名单，只允许数字+-*/.
        whitelist = r'0123456789+-*/.'
        config = fr'--oem 3 --psm 7 -c tessedit_char_whitelist="{whitelist}"'
        ocr_text = pytesseract.image_to_string(bin_img, config=config).strip()

        self.get_logger().info(f"OCR原始:{repr(ocr_text)}")

        candidate_expr = None
        lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
        for line in lines:
            candidate_expr = line
            break

        calc_result = None
        clean_str = ""
        if candidate_expr is not None:
            calc_result, clean_str = safe_eval(candidate_expr)

        msg = CalcResult()
        msg.expr = clean_str
        if calc_result is not None:
            msg.result = calc_result
            self.pub.publish(msg)
            self.get_logger().info(f"有效算式 expr={clean_str} 结果={calc_result:.2f}")
            self.f_log.write(f"识别算式 expr={clean_str} 结果={calc_result:.2f}\n")
            self.f_log.flush()
        else:
            msg.result = 0.0
            self.get_logger().warn(f"不满足头尾数字规则 raw:{candidate_expr}")
            self.f_log.write(f"识别失败raw={candidate_expr}\n")
            self.f_log.flush()

        cv2.imshow("camera", frame)
        cv2.imshow("bin_ocr", bin_img)
        cv2.waitKey(1)

    def destroy_node(self):
        self.cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MathOcrPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

