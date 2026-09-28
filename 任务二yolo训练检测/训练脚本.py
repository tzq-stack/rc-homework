from ultralytics import YOLO

if __name__ == '__main__':
    # 加载YOLO11n预训练权重，采用迁移学习，在预训练模型基础上训练自定义数据集
    model = YOLO("yolo11n.pt")

    # 启动模型训练
    train_result = model.train(
        data="tzq.yaml",        # 数据集配置文件，使用相对路径，描述训练/验证数据集路径与类别信息
        epochs=50,              # 训练总轮数
        imgsz=640,              # 输入网络的图像分辨率，图片会被缩放至该尺寸
        batch=2,                # 批次大小，受笔记本显存限制设置为2
        cache=False,            # 关闭图片缓存，减少内存占用
        workers=0,              # Windows系统设置为0，避免多进程加载数据集报错
        augment=True,           # 开启整体数据增强，提升模型泛化能力
        weight_decay=0.0025,    # 权重衰减，正则化手段，抑制模型过拟合
        mosaic=1.0,             # mosaic数据增强概率，多张图片拼接合成新样本
        mixup=0.15,             # mixup增强概率，图像混合增强，提升鲁棒性
        hsv_h=0.015,            # HSV色相随机扰动幅度
        hsv_s=0.7,              # HSV饱和度随机扰动幅度
        hsv_v=0.4,              # HSV亮度随机扰动幅度
        cos_lr=True,            # 余弦退火学习率调度，学习率按余弦曲线平滑下降
        patience=None,          # 关闭早停策略，完整跑完所有epochs
        val=True,               # 训练过程中开启验证集评估，用于保存best.pt最优权重
        save=True               # 开启模型保存，保存最优best.pt与最后一轮last.pt权重
    )

    print("模型评估")
    # 使用val验证集做离线评估，获取mAP量化指标
    metrics = model.val()
    # 打印mAP@50指标，保留4位小数，衡量模型检测精度
    print(f"mAP50: {metrics.box.map50:.4f}")
