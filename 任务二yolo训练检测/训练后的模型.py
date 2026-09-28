import os
os.environ["HF_HUB_OFFLINE"] = "1"
from ultralytics import YOLO
if __name__ == '__main__':
    model = YOLO(r"./best.pt")
    res = model.predict(
        source=r"./data/test/images",
        conf=0.15,
        save=True
    )
    print("推理完成")
