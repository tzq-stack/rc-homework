import cv2
import numpy as np
from pupil_apriltags import Detector

TAG_FAMILY = "tag36h11"      
# 作业指定标签家族
TAG_SIZE = 0.11         
# AprilTag实际物理边长，单位：米（6cm）

# 相机内参：笔记本摄像头没有标定，使用近似默认值
FX, FY = 600, 600
CX, CY = 320, 240
camera_params = [FX, FY, CX, CY]

# 创建AprilTag检测器
detector = Detector(families=TAG_FAMILY)

# 打开摄像头，0为笔记本内置摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

print("AprilTag检测程序")
print("ESC键退出程序")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # AprilTag检测需要灰度图像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 检测Tag，同时解算位姿（平移、旋转）
    tags = detector.detect(
        gray,
        estimate_tag_pose=True,
        camera_params=camera_params,
        tag_size=TAG_SIZE
    )

    # 循环处理每一个检测到的Tag，支持多个Tag同时出现
    for tag in tags:
        # 绘制Tag外框
        corners = tag.corners.astype(np.int32)
        cv2.polylines(frame, [corners], True, (0, 255, 0), 2)

        # 像素中心坐标 
        cx, cy = int(tag.center[0]), int(tag.center[1])
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        # 打印输出ID、像素中心、三维位姿
        tag_id = tag.tag_id
        t = tag.pose_t.flatten()   # 平移向量 x,y,z (米)
        R = tag.pose_R             # 旋转矩阵
        print(f"Tag ID:{tag_id} ")
        print(f"像素中心：x={cx}, y={cy}")
        print(f"平移T(米): x={t[0]:.3f}, y={t[1]:.3f}, z={t[2]:.3f}")
        print(f"旋转矩阵R:\n{R}")

        # 在图像上绘制ID文字
        cv2.putText(frame, f"ID:{tag_id}", (cx-40, cy-20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # 4.绘制3D坐标轴 X红 Y绿 Z蓝 
        axis_len = 0.04
        axis_3d = np.float32([
            [axis_len, 0, 0],
            [0, axis_len, 0],
            [0, 0, axis_len],
            [0, 0, 0]
        ])
        # 3D点投影到2D图像
        axis_2d, _ = cv2.projectPoints(axis_3d, tag.pose_R, tag.pose_t,
                                       np.array([[FX,0,CX],[0,FY,CY],[0,0,1]]), None)
        axis_2d = axis_2d.astype(int)
        origin = tuple(axis_2d[3][0])
        cv2.line(frame, origin, tuple(axis_2d[0][0]), (0,0,255), 2)   # X红
        cv2.line(frame, origin, tuple(axis_2d[1][0]), (0,255,0), 2)   # Y绿
        cv2.line(frame, origin, tuple(axis_2d[2][0]), (255,0,0), 2)   # Z蓝

    # 显示结果窗口
    cv2.imshow("AprilTag Detect", frame)

    # ESC键退出
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()