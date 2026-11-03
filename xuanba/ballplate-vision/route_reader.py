# -*- coding: utf-8 -*-
"""图纸涂黑九宫格轨迹识别（发挥部分）。

用法（命令行测试）：
    python route_reader.py 图纸照片.jpg
"""
import sys
import cv2
import numpy as np
import config
from utils import get_contours, order_points

SIZE = 300  # 矫正后的边长（像素）


def find_grid_corners(gray):
    """找九宫格外框四角（左上、右上、右下、左下）。找不到返回 None。"""
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours = get_contours(bw)
    if not contours:
        return None
    c = max(contours, key=cv2.contourArea)
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    if len(approx) == 4:
        return order_points(approx.reshape(4, 2))
    # 退而求其次：用最小外接矩形
    rect = cv2.minAreaRect(c)
    return order_points(cv2.boxPoints(rect))


def read_route(image_bgr, fill_threshold=None):
    """识别涂黑九宫格轨迹。

    返回 (cells, warped)：
      cells: 被涂黑方格编号序列（默认按编号升序；若检测到起点标记则起点排最前）
      warped: 透视矫正后的灰度图（调试显示用）
    找不到九宫格时返回 (None, None)。
    """
    if fill_threshold is None:
        fill_threshold = config.ROUTE_FILL_THRESHOLD

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    corners = find_grid_corners(gray)
    if corners is None:
        return None, None

    dst = np.float32([[0, 0], [SIZE, 0], [SIZE, SIZE], [0, SIZE]])
    M = cv2.getPerspectiveTransform(corners, dst)
    warped = cv2.warpPerspective(gray, M, (SIZE, SIZE))

    # 深色（网格线 + 涂黑）→ 白色
    _, bw = cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    cell = SIZE // config.GRID
    margin = int(cell * 0.15)          # 填充判定区边距，避开网格线
    center_margin = int(cell * 0.3)    # 起点标记检测区（中心 40%）

    filled = []
    start = None
    for r in range(config.GRID):
        for c in range(config.GRID):
            n = r * config.GRID + c + 1
            x0, x1 = c * cell + margin, (c + 1) * cell - margin
            y0, y1 = r * cell + margin, (r + 1) * cell - margin
            fill_ratio = np.mean(bw[y0:y1, x0:x1] > 0)
            if fill_ratio >= fill_threshold:
                filled.append(n)
                # 起点标记：涂黑格中心若有明显白点/缺口
                cx0, cx1 = c * cell + center_margin, (c + 1) * cell - center_margin
                cy0, cy1 = r * cell + center_margin, (r + 1) * cell - center_margin
                white_ratio = np.mean(bw[cy0:cy1, cx0:cx1] == 0)
                if white_ratio >= config.START_MARK_WHITE_RATIO and start is None:
                    start = n

    cells = sorted(filled)
    if start is not None and start in cells:
        cells.remove(start)
        cells = [start] + cells
    return cells, warped


def main():
    if len(sys.argv) < 2:
        print("用法: python route_reader.py 图纸照片.jpg")
        return
    img = cv2.imread(sys.argv[1])
    if img is None:
        print("读图失败:", sys.argv[1])
        return
    cells, warped = read_route(img)
    if cells is None:
        print("未找到九宫格，请检查图纸是否完整、外框是否清晰。")
        return
    print("识别到的轨迹（方格编号序列）:", cells)
    if warped is not None:
        # 在矫正图上标出每格编号，方便核对
        disp = cv2.cvtColor(warped, cv2.COLOR_GRAY2BGR)
        cell = SIZE // config.GRID
        for r in range(config.GRID):
            for c in range(config.GRID):
                n = r * config.GRID + c + 1
                cx = c * cell + cell // 2
                cy = r * cell + cell // 2
                cv2.putText(disp, str(n), (cx - 10, cy + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.imshow("warped grid", disp)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
