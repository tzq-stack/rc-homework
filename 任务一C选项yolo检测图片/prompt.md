(tips:if 图片看不到可以打开ipynb的prompt查看)
prompt1
指令：用ultralytics写YOLO11图片检测完整代码，读取同目录test.jpg。识别结果保存本地，不要弹出图片窗口
AI回复摘要
文件：E:\ASUS\yolo11_detect.py
用法：python yolo11_detect.py（同目录放 test.jpg）
结果保存在 runs/detect/，不弹窗
![image.png](attachment:image.png)


prompt 2
指令：要求代码执行的时候在终端展示，能够打印出检测到什么物体，置信度（方便观察）
AI回复：
1.读取同目录 test.jpg，用 YOLO11 检测
2.终端打印中文标签 + 置信度 + 彩色进度条
3.按置信度降序排列，汇总分类统计，给出一句话场景速写
4.标注图自动保存到 runs/detect/，不弹窗
![image.png](attachment:image.png)



prompt 3
指令：推理时设置置信度阈值0.4，置信低于0.4的目标既不要打印输出，也不要在保存的图片上绘制检测框
AI回复：
推理完成后增加置信度阈值筛选逻辑，过滤掉0.4以下可信度低的检测框，终端仅输出有效目标，降低误检带来的干扰
![image.png](attachment:image.png)



prompt 4
指令：把全部检测代码封装成函数detect_image(image_path)，加上Python入口，直接点运行就自动检测test.jpg
AI回复：
封装检测函数，添加`if __name__ == "__main__"`，运行脚本自动执行图片检测。
![image.png](attachment:image.png)



prompt 5
指令：最后给代码加上注释，通俗易懂
AI回复：
给关键代码增加中文注释
![image.png](attachment:image.png)