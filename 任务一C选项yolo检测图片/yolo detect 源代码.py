# 我是使用anaconda 里面下载的ultralytics安装的yolo环境使用的pycharm,所以老师们如果直接打开执行不了请一定要告诉我
"""
YOLO11 图片目标检测 · 终端可视化
    点击运行 → 自动检测 test.jpg
    命令行 → python yolo11_detect.py test.jpg --model yolo11x.pt --conf 0.3
    代码调用 → detect_image("my_photo.jpg", conf=0.5)
"""
import argparse
import sys
from pathlib import Path
from collections import Counter
from ultralytics import YOLO

# ── 终端颜色 ──────────────────────────────────────────
C = {
    "red":    "\033[91m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "blue":   "\033[94m",
    "cyan":   "\033[96m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
    "reset":  "\033[0m",
}

# ── COCO 标签中英对照 ─────────────────────────────────
CN_LABEL = {
    "person": "人", "bicycle": "自行车", "car": "汽车", "motorcycle": "摩托车",
    "airplane": "飞机", "bus": "公交车", "train": "火车", "truck": "卡车", "boat": "船",
    "traffic light": "红绿灯", "fire hydrant": "消防栓", "stop sign": "停止标志",
    "parking meter": "停车计时器", "bench": "长椅", "bird": "鸟", "cat": "猫",
    "dog": "狗", "horse": "马", "sheep": "羊", "cow": "牛", "elephant": "大象",
    "bear": "熊", "zebra": "斑马", "giraffe": "长颈鹿", "backpack": "背包",
    "umbrella": "雨伞", "handbag": "手提包", "tie": "领带", "suitcase": "行李箱",
    "frisbee": "飞盘", "skis": "滑雪板", "snowboard": "滑雪板", "sports ball": "球",
    "kite": "风筝", "baseball bat": "棒球棒", "baseball glove": "棒球手套",
    "skateboard": "滑板", "surfboard": "冲浪板", "tennis racket": "网球拍",
    "bottle": "瓶子", "wine glass": "酒杯", "cup": "杯子", "fork": "叉子",
    "knife": "刀", "spoon": "勺子", "bowl": "碗", "banana": "香蕉", "apple": "苹果",
    "sandwich": "三明治", "orange": "橘子", "broccoli": "西兰花", "carrot": "胡萝卜",
    "hot dog": "热狗", "pizza": "披萨", "donut": "甜甜圈", "cake": "蛋糕",
    "chair": "椅子", "couch": "沙发", "potted plant": "盆栽", "bed": "床",
    "dining table": "餐桌", "toilet": "马桶", "tv": "电视", "laptop": "笔记本电脑",
    "mouse": "鼠标", "remote": "遥控器", "keyboard": "键盘", "cell phone": "手机",
    "microwave": "微波炉", "oven": "烤箱", "toaster": "烤面包机", "sink": "水槽",
    "refrigerator": "冰箱", "book": "书", "clock": "时钟", "vase": "花瓶",
    "scissors": "剪刀", "teddy bear": "泰迪熊", "hair drier": "吹风机",
    "toothbrush": "牙刷",
}

def cn(label: str) -> str:
    """英文标签 → 中文"""
    return CN_LABEL.get(label, label)

def bar(conf: float, width: int = 20) -> str:
    """置信度可视化进度条"""
    n = int(conf * width)
    if conf >= 0.8:
        color, char = C["green"], "█"
    elif conf >= 0.5:
        color, char = C["yellow"], "▓"
    else:
        color, char = C["red"], "▒"
    return color + char * n + C["dim"] + "░" * (width - n) + C["reset"]


def detect_image(image_path: str, model: str = "yolo11n.pt",
                 conf: float = 0.4, iou: float = 0.7,
                 output: str = None) -> list:
    """
    对单张图片执行 YOLO11 目标检测，终端打印结果，标注图自动保存。

    参数:
        image_path: 图片路径
        model:      模型名称 (yolo11n.pt / yolo11s.pt / yolo11x.pt 等)
        conf:       置信度阈值，低于此值的目标被忽略
        iou:        IoU 阈值
        output:     输出目录 (默认 runs/detect)
    返回:
        ultralytics Results 列表
    """
    img_path = Path(image_path)
    if not img_path.exists():
        print(f"{C['red']}找不到图片: {img_path.absolute()}{C['reset']}")
        sys.exit(1)

    # ── 加载模型 ──
    print(f"\n{C['bold']}{C['cyan']}▸ 加载模型{C['reset']}: {model}")
    yolo = YOLO(model)

    # ── 推理 ──
    print(f"{C['bold']}{C['cyan']}▸ 正在检测{C['reset']}: {img_path.name} (置信度阈值 ≥{conf})")
    results = yolo.predict(
        source=str(img_path),
        conf=conf,
        iou=iou,
        save=True,
        show=False,
        verbose=False,
        project=output,
    )

    # ── 终端渲染 ──
    for r in results:
        boxes = r.boxes
        names = r.names

        if boxes is None or len(boxes) == 0:
            print(f"\n  {C['dim']}未检测到任何物体{C['reset']}\n")
            return results

        # 按置信度降序排列
        data = []
        for b in boxes:
            cls_id = int(b.cls.item())
            score = b.conf.item()
            en_label = names.get(cls_id, f"class_{cls_id}")
            data.append((score, cls_id, en_label))

        data.sort(key=lambda x: x[0], reverse=True)

        # ── 表格 ──
        print(f"\n{C['bold']}╭{'─'*68}╮{C['reset']}")
        print(f"{C['bold']}│{C['reset']}  {C['bold']}检测结果{ C['reset']:<59s}{C['bold']}│{C['reset']}")
        print(f"{C['bold']}├{'─'*10}┬{'─'*20}┬{'─'*10}┬{'─'*24}┤{C['reset']}")

        counter = Counter()
        for score, cid, en in data:
            counter[en] += 1

        i = 1
        for score, cid, en in data:
            zh = cn(en)
            pct = f"{score*100:.1f}%"
            idx = f"#{i}"
            b = bar(score)
            print(f"{C['bold']}│{C['reset']} {idx:<8s} {C['bold']}{zh:<18s}{C['reset']} {pct:<9s} {b} {C['bold']}│{C['reset']}")
            i += 1

        print(f"{C['bold']}╰{'─'*10}┴{'─'*20}┴{'─'*10}┴{'─'*24}╯{C['reset']}")

        # ── 汇总统计 ──
        print(f"\n{C['bold']}{C['cyan']}▸ 统计汇总{C['reset']}")
        print(f"  共检测到 {C['bold']}{len(data)}{C['reset']} 个物体，涉及 {len(counter)} 个类别：")

        sorted_cats = counter.most_common()
        max_conf_per_cls = {}
        for score, cid, en in data:
            if en not in max_conf_per_cls:
                max_conf_per_cls[en] = score

        for en_label, count in sorted_cats:
            zh = cn(en_label)
            mc = max_conf_per_cls.get(en_label, 0)
            icon = "🟢" if mc >= 0.8 else ("🟡" if mc >= 0.5 else "🔴")
            print(f"  {icon} {C['bold']}{zh:<12s}{C['reset']} ×{count:<3}  {C['dim']}(最高置信度 {mc*100:.1f}%){C['reset']}")

        # ── 场景速写 ──
        top3 = sorted_cats[:3]
        if top3:
            desc = "、".join([f"{count}个{cn(en)}" for en, count in top3])
            print(f"\n{C['bold']}{C['yellow']}▸ 场景速写{C['reset']}: 画面中有 {desc}")

        # ── 保存路径 ──
        saved = Path(yolo.predictor.save_dir) if yolo.predictor else Path("runs/detect")
        print(f"\n{C['green']}▸ 标注图片已保存{C['reset']}: {saved.absolute()}\n")

    return results


# ── Python 入口 ──────────────────────────────────────
if __name__ == "__main__":
    # 命令行带参数 → 走 argparse；直接点击运行 → 自动检测 test.jpg
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="YOLO11 图片检测")
        parser.add_argument("image", help="图片路径")
        parser.add_argument("--model", default="yolo11n.pt")
        parser.add_argument("--conf", type=float, default=0.4)
        parser.add_argument("--iou", type=float, default=0.7)
        parser.add_argument("--output", default=None)
        args = parser.parse_args()
        detect_image(args.image, model=args.model, conf=args.conf,
                     iou=args.iou, output=args.output)
    else:
        detect_image("test.jpg")
