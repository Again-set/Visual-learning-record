# -*- coding: utf-8 -*-
"""与 STM32 的串口通信封装。

文本行协议，每行以 \\n 结尾：
  小球位置：X:123.4,Y:234.5,C:8
  目标轨迹：R:6,9,8
"""
import serial


class SerialLink:
    def __init__(self, port, baud=115200, enabled=True):
        self.port = port
        self.baud = baud
        self.enabled = enabled
        self.ser = None

    def open(self):
        if not self.enabled:
            return
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
            print(f"串口已打开: {self.port} @ {self.baud}")
        except Exception as e:
            print(f"串口打开失败: {e}")
            self.ser = None

    def send_position(self, x_mm, y_mm, cell):
        """发送小球位置。"""
        if self.ser is None:
            return
        line = f"X:{x_mm:.1f},Y:{y_mm:.1f},C:{cell}\n"
        self.ser.write(line.encode("ascii"))

    def send_route(self, cells):
        """发送目标轨迹。"""
        if self.ser is None:
            return
        line = "R:" + ",".join(str(c) for c in cells) + "\n"
        self.ser.write(line.encode("ascii"))

    def close(self):
        if self.ser is not None:
            self.ser.close()
            self.ser = None
