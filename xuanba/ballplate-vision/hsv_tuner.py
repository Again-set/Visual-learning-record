# -*- coding: utf-8 -*-
"""HSV 阈值调参工具：用滑条实时标定小球颜色。

用法：
    python hsv_tuner.py
    拖动 H/S/V 上下限滑条，让掩码里只有小球是白色。
    把最终数值填进 config.py 的 BALL_HSV_RANGES。
"""
import cv2
import numpy as np
import config


def nothing(x):
    pass


def main():
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    if not cap.isOpened():
        print("无法打开摄像头，请检查 CAMERA_INDEX 和连接。")
        return

    cv2.namedWindow("tune")
    cv2.createTrackbar("H min", "tune", 0, 179, nothing)
    cv2.createTrackbar("H max", "tune", 179, 179, nothing)
    cv2.createTrackbar("S min", "tune", 0, 255, nothing)
    cv2.createTrackbar("S max", "tune", 255, 255, nothing)
    cv2.createTrackbar("V min", "tune", 0, 255, nothing)
    cv2.createTrackbar("V max", "tune", 255, 255, nothing)

    lower = upper = None
    print("拖动滑条直到掩码里只有小球是白色，按 q 退出。")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower = np.array([
            cv2.getTrackbarPos("H min", "tune"),
            cv2.getTrackbarPos("S min", "tune"),
            cv2.getTrackbarPos("V min", "tune"),
        ])
        upper = np.array([
            cv2.getTrackbarPos("H max", "tune"),
            cv2.getTrackbarPos("S max", "tune"),
            cv2.getTrackbarPos("V max", "tune"),
        ])
        mask = cv2.inRange(hsv, lower, upper)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        cv2.imshow("frame", frame)
        cv2.imshow("mask", mask)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    if lower is not None:
        print("当前 H/S/V 范围：")
        print("  lower =", lower.tolist())
        print("  upper =", upper.tolist())
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
