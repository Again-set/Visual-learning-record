# 滚球系统视觉（树莓派 + USB 摄像头）

完整方案见 `视觉方案.md`。

## 安装依赖（树莓派）

```bash
sudo apt update
sudo apt install -y python3-opencv python3-pyserial
# 或用 pip：pip install opencv-python numpy pyserial
```

## 运行顺序

1. `python3 hsv_tuner.py` —— 标定小球 HSV 颜色，把数值填进 `config.py`
2. `python3 calibrate.py` —— 点平板四角，生成 `calibrate.npz`
3. `python3 route_reader.py 图纸.jpg` —— （可选）测试涂黑九宫格轨迹识别
4. `python3 main.py` —— 主流程；接好 STM32 后把 `config.ENABLE_SERIAL` 改成 `True`

## 文件

| 文件 | 作用 |
|------|------|
| config.py | 全局参数 |
| ball_detector.py | 小球检测 |
| calibrate.py | 相机标定 |
| hsv_tuner.py | HSV 调参 |
| route_reader.py | 涂黑九宫格轨迹识别 |
| serial_link.py | 串口封装 |
| main.py | 主流程 |
| utils.py | 小工具 |
