Apriltag运行说明

本程序调用摄像头实时检测 “tag36h11” 家族的AprilTag标记。程序可以输出每个标签的ID、像素中心坐标、三维位姿信息（旋转矩阵、平移向量）；在图像上绘制标签外框、标签ID以及代表三维姿态的XYZ坐标轴，支持画面中同时出现多个AprilTag标签的识别与解算。本实验采用作业要求的模拟默认相机内参，未执行真实相机标定。

依赖库安装
主要是在终端，激活conda环境后，安装opencv的pupi-apritag
pip install opencv-python numpy pupil‑apriltags
再在代码里面应用pupil-apriltag的Detector创建检测器即可获得外参

主要命令包括
detector = Detector(families=TAG_FAMILY)
创建检测器

tags = detector.detect(
        gray,
        estimate_tag_pose=True,
        camera_params=camera_params,
        tag_size=TAG_SIZE
    )
对灰度图进行检测，开启三维微子和外参的计算

axis_2d, _ = cv2.projectPoints(axis_3d, tag.pose_R, tag.pose_t,
                    np.array([[FX,0,CX],[0,FY,CY],[0,0,1]]), None)
这一步是将三维坐标轴进行2D图片转换