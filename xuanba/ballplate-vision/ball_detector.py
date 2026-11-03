# -*- coding: utf-8 -*-
"""小球检测：HSV 颜色分割 + 轮廓 + 质心。"""
import cv2
import numpy as np
import config
from utils import get_contours


class BallDetector:
    def __init__(self, hsv_ranges=None):
        # 默认取 config.BALL_HSV_RANGES；也可临时传入别的范围
        self.ranges = hsv_ranges if hsv_ranges is not None else config.BALL_HSV_RANGES

    def detect(self, frame_bgr):
        """检测小球，返回 (found, (cx, cy), mask)。

        found: 是否找到小球
        cx, cy: 球心像素坐标
        mask: 二值掩码（调试显示用）
        """
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

        # 多段阈值并集（兼容红色这种 H 值跨 0/180 的颜色）
        mask = None
        for (lower, upper) in self.ranges:
            m = cv2.inRange(hsv, lower, upper)
            mask = m if mask is None else cv2.bitwise_or(mask, m)

        # 形态学：开运算去噪点，闭运算填小球内部反光小洞
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours = get_contours(mask)
        if not contours:
            return False, (0.0, 0.0), mask

        # 取面积最大的轮廓作为小球
        c = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(c)
        if area < config.MIN_BALL_AREA or area > config.MAX_BALL_AREA:
            return False, (0.0, 0.0), mask

        # 用图像矩求质心（比外接矩形中心更准）
        M = cv2.moments(c)
        if M["m00"] <= 0:
            return False, (0.0, 0.0), mask
        cx = M["m10"] / M["m00"]
        cy = M["m01"] / M["m00"]
        return True, (cx, cy), mask
