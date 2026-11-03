# -*- coding: utf-8 -*-
"""主流程：相机采图 → 小球检测 → 像素→毫米 → 九宫格 → 串口下发。

按键：
  q   退出
  r   把当前帧当作“图纸”做一次轨迹识别（调试发挥部分用）
"""
import cv2
import numpy as np
import config
from ball_detector import BallDetector
from route_reader import read_route
from serial_link import SerialLink


def load_homography():
    try:
        d = np.load(config.CALIB_FILE)
        return d["H"]
    except FileNotFoundError:
        print(f"未找到标定文件 {config.CALIB_FILE}，请先运行 calibrate.py。")
        print("（无标定时仍能显示检测结果，但不会输出毫米坐标）")
        return None


def pixel_to_mm(px, H):
    pts = np.array([[px]], dtype="float32")
    out = cv2.perspectiveTransform(pts, H)
    return float(out[0][0][0]), float(out[0][0][1])


def mm_to_cell(x, y):
    col = int(x // config.CELL_SIZE_MM)
    row = int(y // config.CELL_SIZE_MM)
    col = min(max(col, 0), config.GRID - 1)
    row = min(max(row, 0), config.GRID - 1)
    return row * config.GRID + col + 1


def main():
    H = load_homography()
    detector = BallDetector()
    link = SerialLink(config.SERIAL_PORT, config.SERIAL_BAUD, config.ENABLE_SERIAL)
    link.open()

    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    if not cap.isOpened():
        print("无法打开摄像头，请检查 CAMERA_INDEX 和连接。")
        return

    smooth = None  # EMA 平滑后的 (x_mm, y_mm)

    print("运行中… 按 q 退出，按 r 做一次轨迹识别。")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        found, center, mask = detector.detect(frame)

        if found:
            cx, cy = center
            cv2.circle(frame, (int(cx), int(cy)), 5, (0, 255, 0), -1)
            if H is not None:
                x_mm, y_mm = pixel_to_mm((cx, cy), H)
                # EMA 平滑，抑制抖动
                if smooth is None:
                    smooth = (x_mm, y_mm)
                else:
                    a = config.EMA_ALPHA
                    smooth = (a * x_mm + (1 - a) * smooth[0],
                              a * y_mm + (1 - a) * smooth[1])
                cell = mm_to_cell(*smooth)
                link.send_position(smooth[0], smooth[1], cell)
                cv2.putText(frame, f"({smooth[0]:.0f},{smooth[1]:.0f})mm cell{cell}",
                            (int(cx) + 8, int(cy) - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # 左上角显示掩码，便于确认分割效果
        small = cv2.resize(mask, (160, 120))
        frame[0:120, 0:160] = cv2.cvtColor(small, cv2.COLOR_GRAY2BGR)
        cv2.putText(frame, "mask", (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        cv2.imshow("ballplate", frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord("q"):
            break
        elif k == ord("r"):
            cells, _ = read_route(frame)
            if cells is None:
                print("轨迹识别：未找到九宫格")
            else:
                print("轨迹识别结果:", cells)
                link.send_route(cells)

    cap.release()
    link.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
