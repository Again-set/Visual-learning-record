from collections.abc import Sequence
from dataclasses import dataclass, field
import sys

import cv2
import numpy as np

Point = tuple[int, int]
CORNER_NAMES = ("left-top", "right-top", "right-bottom", "left-bottom")
WINDOW_NAME = "Two ROI Camera Calibrator"


@dataclass
class CalibrationState:
    frozen: bool = False
    points: list[Point] = field(default_factory=list)
    frozen_frame: object | None = None

    def add_point(self, x: int, y: int) -> None:
        if self.frozen and len(self.points) < 8:
            self.points.append((int(x), int(y)))

    def undo(self) -> None:
        if self.frozen and self.points:
            self.points.pop()

    def reset_points(self) -> None:
        if self.frozen:
            self.points.clear()

    def resume_live(self) -> None:
        self.frozen = False
        self.points.clear()
        self.frozen_frame = None


def get_prompt(point_count: int) -> str:
    if not 0 <= point_count <= 8:
        raise ValueError("point_count must be between 0 and 8")
    if point_count == 8:
        return "Press ENTER to print coordinates"
    roi_number = point_count // 4 + 1
    corner_name = CORNER_NAMES[point_count % 4]
    return f"ROI {roi_number}: click {corner_name}"


def split_rois(points: Sequence[Point]) -> tuple[list[Point], list[Point]]:
    if len(points) != 8:
        raise ValueError("exactly 8 points are required")
    normalized = [(int(x), int(y)) for x, y in points]
    return normalized[:4], normalized[4:]


def format_rois(points: Sequence[Point]) -> str:
    roi_1, roi_2 = split_rois(points)
    return f"ROI 1: {roi_1}\nROI 2: {roi_2}"


def draw_overlay(frame: np.ndarray, state: CalibrationState) -> np.ndarray:
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (overlay.shape[1], 32), (0, 0, 0), -1)
    prompt = get_prompt(len(state.points)) if state.frozen else "SPACE: freeze | ESC: quit"
    cv2.putText(
        overlay,
        prompt,
        (8, 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )

    for index, point in enumerate(state.points, start=1):
        cv2.circle(overlay, point, 5, (0, 0, 255), -1)
        cv2.putText(
            overlay,
            str(index),
            (point[0] + 7, point[1] - 7),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )

    for roi_points, color in ((state.points[:4], (0, 255, 0)), (state.points[4:], (0, 255, 255))):
        if len(roi_points) >= 2:
            polyline = np.array(roi_points, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(overlay, [polyline], len(roi_points) == 4, color, 2)

    return overlay


def open_camera():
    if sys.platform.startswith("win"):
        capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if capture.isOpened():
            return capture
        capture.release()
    return cv2.VideoCapture(0)


def main() -> int:
    capture = None
    try:
        capture = open_camera()

        if not capture.isOpened():
            print("Error: cannot open camera 0", file=sys.stderr)
            return 1

        state = CalibrationState()

        def on_mouse(event: int, x: int, y: int, flags: int, param: object) -> None:
            if event == cv2.EVENT_LBUTTONDOWN:
                state.add_point(x, y)
            elif event == cv2.EVENT_RBUTTONDOWN:
                state.undo()

        cv2.namedWindow(WINDOW_NAME)
        cv2.setMouseCallback(WINDOW_NAME, on_mouse)

        while True:
            if state.frozen:
                frame = state.frozen_frame
            else:
                success, frame = capture.read()
                if not success:
                    print("Error: cannot read from camera 0", file=sys.stderr)
                    return 1

            if not isinstance(frame, np.ndarray):
                print("Error: cannot read from camera 0", file=sys.stderr)
                return 1

            cv2.imshow(WINDOW_NAME, draw_overlay(frame, state))
            key = cv2.waitKey(1) & 0xFF

            if key == 27:
                return 0
            if key == ord(" "):
                if state.frozen:
                    state.resume_live()
                else:
                    state.frozen_frame = frame.copy()
                    state.frozen = True
            elif key in (ord("r"), ord("R")):
                state.reset_points()
            elif key in (10, 13) and state.frozen and len(state.points) == 8:
                print(format_rois(state.points))
                return 0
    finally:
        if capture is not None:
            capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    raise SystemExit(main())
