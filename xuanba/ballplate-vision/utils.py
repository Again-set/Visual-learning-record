# -*- coding: utf-8 -*-
"""小工具：findContours 兼容封装、四角排序。"""
import cv2
import numpy as np


def get_contours(binary):
    """兼容 OpenCV 3/4/5 的 findContours 封装，返回轮廓列表。"""
    res = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # OpenCV3 返回 (image, contours, hierarchy)；OpenCV4/5 返回 (contours, hierarchy)
    if len(res) == 3:
        return res[1]
    return res[0]


def order_points(pts):
    """把 4 个点按 左上、右上、右下、左下 排序。"""
    pts = np.asarray(pts, dtype="float32").reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # 左上：x + y 最小
    rect[2] = pts[np.argmax(s)]   # 右下：x + y 最大
    d = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(d)]   # 右上：y - x 最小
    rect[3] = pts[np.argmax(d)]   # 左下：y - x 最大
    return rect
