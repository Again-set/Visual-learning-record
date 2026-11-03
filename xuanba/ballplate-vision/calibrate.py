# -*- coding: utf-8 -*-
"""相机标定：点击平板四角，求像素→毫米的单应矩阵。

用法：
    python calibrate.py
    1) 在画面里按 左上 → 右上 → 右下 → 左下 顺序点击平板四角；
    2) 按 s 保存到 config.CALIB_FILE，按 r 清空重选，按 q 退出。
"""
import cv2
import numpy as np
import config

corners = []


def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(corners) < 4:
        corners.append((x, y))
        print(f"已点 {len(corners)}/4：({x}, {y})")


def main():
    global corners
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    if not cap.isOpened():
        print("无法打开摄像头，请检查 CAMERA_INDEX 和连接。")
        return

    cv2.namedWindow("calibrate")
    cv2.setMouseCallback("calibrate", on_mouse)

    # 平板四角对应的物理坐标（毫米）：左上、右上、右下、左下
    dst = np.float32([
        [0.0, 0.0],
        [config.PLATE_SIZE_MM, 0.0],
        [config.PLATE_SIZE_MM, config.PLATE_SIZE_MM],
        [0.0, config.PLATE_SIZE_MM],
    ])

    print("请按 左上→右上→右下→左下 顺序点击平板四角，然后按 s 保存。")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        disp = frame.copy()
        for i, p in enumerate(corners):
            cv2.circle(disp, p, 4, (0, 0, 255), -1)
            cv2.putText(disp, str(i + 1), (p[0] + 8, p[1] - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        if len(corners) == 4:
            cv2.polylines(disp, [np.array(corners, dtype=np.int32)], True, (0, 255, 0), 2)
            cv2.putText(disp, "按 s 保存 / r 重选", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("calibrate", disp)

        k = cv2.waitKey(1) & 0xFF
        if k == ord("s") and len(corners) == 4:
            H, _ = cv2.findHomography(np.float32(corners), dst)
            np.savez(config.CALIB_FILE, H=H)
            print(f"单应矩阵已保存到 {config.CALIB_FILE}")
            print("H =\n", H)
            break
        elif k == ord("r"):
            corners = []
            print("已清空，重新选择四角。")
        elif k == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
