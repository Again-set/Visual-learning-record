import cv2
import numpy as np


def nothing(x):
    pass

#h_mean = np.mean(hsv[:, :, 0])
#s_mean = np.mean(hsv[:, :, 1])
#v_mean = np.mean(hsv[:, :, 2])
#print(h_mean, s_mean, v_mean)

def main():
    # 1. 加载图像
    image_path = 'E:\mypyProject\main_tool\images//1.png'
    try:
        img = cv2.imread(image_path)
        img = cv2.resize(img, dsize=(300, 300))
        if img is None:
            raise FileNotFoundError
    except:
        print(f"未找到 {image_path}，生成测试图...")
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        cv2.rectangle(img, (0, 0), (200, 200), (0, 0, 255), -1)  # Red
        cv2.rectangle(img, (200, 0), (400, 200), (0, 255, 0), -1)  # Green
        cv2.rectangle(img, (400, 0), (600, 200), (255, 0, 0), -1)  # Blue
        cv2.rectangle(img, (0, 200), (300, 400), (255, 255, 255), -1)  # White
        cv2.rectangle(img, (300, 200), (600, 400), (0, 0, 0), -1)  # Black

    # 2. 转换到 HSV 色彩空间
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 3. 创建窗口和滑动条
    cv2.namedWindow('HSV Threshold Control')

    # H: 0-180, S: 0-255, V: 0-255
    cv2.createTrackbar('H Min', 'HSV Threshold Control', 0, 180, nothing)
    cv2.createTrackbar('H Max', 'HSV Threshold Control', 180, 180, nothing)
    cv2.createTrackbar('S Min', 'HSV Threshold Control', 0, 255, nothing)
    cv2.createTrackbar('S Max', 'HSV Threshold Control', 255, 255, nothing)
    cv2.createTrackbar('V Min', 'HSV Threshold Control', 0, 255, nothing)
    cv2.createTrackbar('V Max', 'HSV Threshold Control', 255, 255, nothing)

    # 默认选中红色 (红色跨越 0 点，这里先设一个普通范围演示，代码逻辑会处理跨越)
    cv2.setTrackbarPos('H Min', 'HSV Threshold Control', 0)
    cv2.setTrackbarPos('H Max', 'HSV Threshold Control', 10)
    cv2.setTrackbarPos('S Min', 'HSV Threshold Control', 43)
    cv2.setTrackbarPos('S Max', 'HSV Threshold Control', 255)
    cv2.setTrackbarPos('V Min', 'HSV Threshold Control', 46)
    cv2.setTrackbarPos('V Max', 'HSV Threshold Control', 255)

    print("操作指南:")
    print("- H (色相): 0-180 (红=0/180, 绿=60, 蓝=120)")
    print("- S (饱和度): 0-255 (越高颜色越纯)")
    print("- V (明度): 0-255 (越高越亮)")
    print("- 按 'q' 退出，按 's' 保存掩膜。")
    print("- 注意：如果选取红色，可能需要调节 H Min 接近 0 且 H Max 接近 180，代码会自动处理。")

    while True:
        h_min = cv2.getTrackbarPos('H Min', 'HSV Threshold Control')
        h_max = cv2.getTrackbarPos('H Max', 'HSV Threshold Control')
        s_min = cv2.getTrackbarPos('S Min', 'HSV Threshold Control')
        s_max = cv2.getTrackbarPos('S Max', 'HSV Threshold Control')
        v_min = cv2.getTrackbarPos('V Min', 'HSV Threshold Control')
        v_max = cv2.getTrackbarPos('V Max', 'HSV Threshold Control')

        # 确保 Min <= Max
        if h_min > h_max: h_min, h_max = h_max, h_min
        if s_min > s_max: s_min, s_max = s_max, s_min
        if v_min > v_max: v_min, v_max = v_max, v_min

        lower_bound = np.array([h_min, s_min, v_min])
        upper_bound = np.array([h_max, s_max, v_max])

        # 4. 创建掩膜 (处理红色跨越 0 点的特殊情况)
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)

        # 情况 A: 普通范围 (h_min < h_max)
        # 情况 B: 跨越 0 点 (例如 h_min=150, h_max=10 -> 实际是想选 150-180 和 0-10)
        # 注意：上面的滑动条逻辑强制了 min <= max，所以如果用户想选红色跨越区，
        # 通常需要分两次或者我们在这里做一个特殊判断：
        # 为了简化交互，我们允许用户手动设置两个范围，或者这里只做单范围。
        # *改进策略*：如果用户想把红色两头都选了，通常 H Min 设很小(0), H Max 设很大(180) 是不对的。
        # 标准做法：如果是红色，通常 H 在 0-10 或 170-180。
        # 这里我们保持单区间逻辑，但提示用户如果是红色，可能需要调节 S 和 V 来辅助，
        # 或者我们检测如果 h_min 很小且 h_max 很大，可能不是想要的。

        # 为了完美支持红色跨越，我们可以检测如果 h_min > h_max (但这被上面代码修正了)。
        # 另一种方法：提供两组 H 滑动条。为了保持界面简洁，这里采用**单区间**逻辑。
        # *技巧*：如果要选红色，建议先选 0-10，如果需要另一头，代码里可以硬编码或者增加复杂度。
        # 这里我们只实现标准的单区间 inRange。

        mask1 = cv2.inRange(hsv, lower_bound, upper_bound)

        # 特殊处理：如果用户意图是选红色（即范围很大，或者手动逻辑），这里不做自动合并，
        # 因为滑动条限制了 min<=max。
        # 若要选跨越红色的区域，用户通常需要调节 S/V 来排除干扰，或者接受只能选一半。
        # *更好的交互*：如果 h_min == 0 and h_max == 180，那是全选。
        # 如果用户想选 170-180 和 0-10，在这个单条形 UI 下做不到，除非我们允许 min > max。
        # 让我们修改逻辑：允许 H Min > H Max 来表示跨越！

        final_mask = np.zeros_like(mask1)
        h_min_raw = cv2.getTrackbarPos('H Min', 'HSV Threshold Control')
        h_max_raw = cv2.getTrackbarPos('H Max', 'HSV Threshold Control')

        if h_min_raw <= h_max_raw:
            # 普通区间
            lower = np.array([h_min_raw, s_min, v_min])
            upper = np.array([h_max_raw, s_max, v_max])
            final_mask = cv2.inRange(hsv, lower, upper)
        else:
            # 跨越区间 (例如 Min=150, Max=10 -> 150-180 和 0-10)
            lower1 = np.array([h_min_raw, s_min, v_min])
            upper1 = np.array([180, s_max, v_max])
            mask1 = cv2.inRange(hsv, lower1, upper1)

            lower2 = np.array([0, s_min, v_min])
            upper2 = np.array([h_max_raw, s_max, v_max])
            mask2 = cv2.inRange(hsv, lower2, upper2)

            final_mask = cv2.bitwise_or(mask1, mask2)

        # 5. 计算平均值
        count = cv2.countNonZero(final_mask)
        mean_hsv = [0, 0, 0]
        if count > 0:
            mean_val = cv2.mean(hsv, mask=final_mask)[:3]
            mean_hsv = mean_val
            status_text = f"Pixels: {count}"
        else:
            status_text = "No pixels selected"

        # 6. 可视化
        mask_color = cv2.cvtColor(final_mask, cv2.COLOR_GRAY2BGR)

        # 显示文字
        cv2.putText(mask_color, f"H: {mean_hsv[0]:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(mask_color, f"S: {mean_hsv[1]:.1f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(mask_color, f"V: {mean_hsv[2]:.1f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(mask_color, status_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # 显示当前范围
        range_text = f"Range: H[{h_min_raw}-{h_max_raw}] S[{s_min}-{s_max}] V[{v_min}-{v_max}]"
        if h_min_raw > h_max_raw:
            range_text += " (Wrap-around)"
        cv2.putText(img, range_text, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        h, w = img.shape[:2]
        if mask_color.shape[0] != h:
            mask_color = cv2.resize(mask_color, (w, h))

        combined = np.hstack((img, mask_color))
        cv2.imshow('HSV Threshold Control', combined)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite('mask_hsv.png', final_mask)
            print("掩膜已保存为 mask_hsv.png")

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()