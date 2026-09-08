import cv2
import numpy as np
import random
import math

# =========================================================
# CẤU HÌNH VIDEO FULL HD
# =========================================================
WIDTH = 1920
HEIGHT = 1080

FPS = 30
DURATION = 8

# 72 điểm = 24 cụm
NUM_POINTS = 72

POINTS_PER_CLUSTER = 3
NUM_CLUSTERS = NUM_POINTS // POINTS_PER_CLUSTER

POINT_RADIUS = 7
LINE_WIDTH = 2

# =========================================================
# MÀU SẮC
# =========================================================

# RGB: (0, 140, 255)
# OpenCV BGR: (255, 140, 0)
COLOR = (255, 140, 0)

BG_COLOR = (255, 255, 255)

OUTPUT_FILE = "video_intro.mp4"


# =========================================================
# TẠO CÁC CỤM
# =========================================================
def create_clusters():

    clusters = []

    # =====================================================
    # BỐ TRÍ 24 CỤM
    # 6 cột x 4 hàng
    # =====================================================
    cols = 6
    rows = 4

    # Khoảng cách giữa các tâm cụm
    spacing_x = 280
    spacing_y = 220

    total_width = (cols - 1) * spacing_x
    total_height = (rows - 1) * spacing_y

    screen_center_x = WIDTH / 2
    screen_center_y = HEIGHT / 2

    cluster_id = 0

    for row in range(rows):

        for col in range(cols):

            if cluster_id >= NUM_CLUSTERS:
                break

            # =================================================
            # TÂM CỐ ĐỊNH CỦA CỤM
            # =================================================
            center_x = (
                screen_center_x
                - total_width / 2
                + col * spacing_x
            )

            center_y = (
                screen_center_y
                - total_height / 2
                + row * spacing_y
            )

            cluster = []

            # =================================================
            # TẠO 3 ĐIỂM
            # =================================================
            for i in range(3):

                # ---------------------------------------------
                # Vị trí ban đầu gần tâm
                # ---------------------------------------------
                angle = (2 * math.pi / 3) * i

                radius = random.uniform(25, 35)

                x = (
                    center_x
                    + math.cos(angle) * radius
                )

                y = (
                    center_y
                    + math.sin(angle) * radius
                )

                # ---------------------------------------------
                # Vận tốc ban đầu
                # ---------------------------------------------
                speed = random.uniform(1.8, 3.0)

                direction = random.uniform(
                    0,
                    math.pi * 2
                )

                vx = math.cos(direction) * speed
                vy = math.sin(direction) * speed

                # ---------------------------------------------
                # Mỗi điểm có một pha chuyển động riêng
                # ---------------------------------------------
                phase_x = random.uniform(
                    0,
                    math.pi * 2
                )

                phase_y = random.uniform(
                    0,
                    math.pi * 2
                )

                # Tần số dao động
                freq_x = random.uniform(
                    0.015,
                    0.035
                )

                freq_y = random.uniform(
                    0.015,
                    0.035
                )

                cluster.append({

                    # Vị trí
                    "x": x,
                    "y": y,

                    # Tâm cố định
                    "center_x": center_x,
                    "center_y": center_y,

                    # Vận tốc
                    "vx": vx,
                    "vy": vy,

                    # Pha
                    "phase_x": phase_x,
                    "phase_y": phase_y,

                    # Tần số
                    "freq_x": freq_x,
                    "freq_y": freq_y,

                    # Biên độ tối đa
                    "max_radius": random.uniform(
                        35,
                        55
                    )
                })

            clusters.append(cluster)

            cluster_id += 1

    return clusters


# =========================================================
# CẬP NHẬT CHUYỂN ĐỘNG
# =========================================================
def update_cluster(cluster, frame_number):

    for p in cluster:

        # =================================================
        # 1. CHUYỂN ĐỘNG TỰ DO
        # =================================================

        p["x"] += p["vx"]
        p["y"] += p["vy"]

        # =================================================
        # 2. THAY ĐỔI HƯỚNG NHẸ
        # =================================================
        # Tạo cảm giác chuyển động tự nhiên,
        # không chạy thẳng mãi một hướng.

        p["vx"] += random.uniform(
            -0.08,
            0.08
        )

        p["vy"] += random.uniform(
            -0.08,
            0.08
        )

        # =================================================
        # 3. GIỚI HẠN TỐC ĐỘ
        # =================================================

        speed = math.sqrt(
            p["vx"] ** 2
            + p["vy"] ** 2
        )

        MAX_SPEED = 3.5
        MIN_SPEED = 1.0

        if speed > MAX_SPEED:

            p["vx"] = (
                p["vx"]
                / speed
                * MAX_SPEED
            )

            p["vy"] = (
                p["vy"]
                / speed
                * MAX_SPEED
            )

        elif speed < MIN_SPEED:

            if speed == 0:

                direction = random.uniform(
                    0,
                    math.pi * 2
                )

                p["vx"] = math.cos(direction)
                p["vy"] = math.sin(direction)

            else:

                p["vx"] = (
                    p["vx"]
                    / speed
                    * MIN_SPEED
                )

                p["vy"] = (
                    p["vy"]
                    / speed
                    * MIN_SPEED
                )

        # =================================================
        # 4. TÍNH KHOẢNG CÁCH ĐẾN TÂM CỤM
        # =================================================

        dx = p["x"] - p["center_x"]
        dy = p["y"] - p["center_y"]

        distance = math.sqrt(
            dx * dx + dy * dy
        )

        max_radius = p["max_radius"]

        # =================================================
        # 5. NẾU ĐIỂM ĐI QUÁ XA
        # =================================================
        # Không teleport.
        # Chỉ đổi hướng nhẹ về tâm.

        if distance > max_radius:

            nx = dx / distance
            ny = dy / distance

            # Đẩy ngược về tâm
            force = 0.35

            p["vx"] -= nx * force
            p["vy"] -= ny * force

        # =================================================
        # 6. KHÔNG CHO ĐIỂM RA KHỎI MÀN HÌNH
        # =================================================

        margin = 20

        if p["x"] < margin:

            p["x"] = margin
            p["vx"] = abs(p["vx"])

        if p["x"] > WIDTH - margin:

            p["x"] = WIDTH - margin
            p["vx"] = -abs(p["vx"])

        if p["y"] < margin:

            p["y"] = margin
            p["vy"] = abs(p["vy"])

        if p["y"] > HEIGHT - margin:

            p["y"] = HEIGHT - margin
            p["vy"] = -abs(p["vy"])


# =========================================================
# VẼ CỤM
# =========================================================
def draw_cluster(frame, cluster):

    p1 = cluster[0]
    p2 = cluster[1]
    p3 = cluster[2]

    pt1 = (
        int(p1["x"]),
        int(p1["y"])
    )

    pt2 = (
        int(p2["x"]),
        int(p2["y"])
    )

    pt3 = (
        int(p3["x"]),
        int(p3["y"])
    )

    # =====================================================
    # NỐI 3 ĐIỂM
    # =====================================================

    cv2.line(
        frame,
        pt1,
        pt2,
        COLOR,
        LINE_WIDTH,
        cv2.LINE_AA
    )

    cv2.line(
        frame,
        pt2,
        pt3,
        COLOR,
        LINE_WIDTH,
        cv2.LINE_AA
    )

    cv2.line(
        frame,
        pt3,
        pt1,
        COLOR,
        LINE_WIDTH,
        cv2.LINE_AA
    )

    # =====================================================
    # VẼ 3 ĐIỂM
    # =====================================================

    for p in cluster:

        center = (
            int(p["x"]),
            int(p["y"])
        )

        cv2.circle(
            frame,
            center,
            POINT_RADIUS,
            COLOR,
            -1,
            cv2.LINE_AA
        )


# =========================================================
# MAIN
# =========================================================
def main():

    # =====================================================
    # TẠO CỤM
    # =====================================================

    clusters = create_clusters()

    # =====================================================
    # VIDEO WRITER
    # =====================================================

    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    out = cv2.VideoWriter(
        OUTPUT_FILE,
        fourcc,
        FPS,
        (WIDTH, HEIGHT)
    )

    total_frames = FPS * DURATION

    # =====================================================
    # THÔNG TIN
    # =====================================================

    print("===================================")
    print("ĐANG TẠO VIDEO")
    print("===================================")

    print(
        f"Kích thước : "
        f"{WIDTH} x {HEIGHT}"
    )

    print(
        f"FPS        : "
        f"{FPS}"
    )

    print(
        f"Số điểm    : "
        f"{NUM_POINTS}"
    )

    print(
        f"Số cụm     : "
        f"{NUM_CLUSTERS}"
    )

    print(
        f"Thời lượng : "
        f"{DURATION} giây"
    )

    print()

    # =====================================================
    # RENDER
    # =====================================================

    for frame_number in range(
        total_frames
    ):

        # -------------------------------------------------
        # NỀN TRẮNG
        # -------------------------------------------------

        frame = np.full(
            (
                HEIGHT,
                WIDTH,
                3
            ),
            BG_COLOR,
            dtype=np.uint8
        )

        # -------------------------------------------------
        # CẬP NHẬT
        # -------------------------------------------------

        for cluster in clusters:

            update_cluster(
                cluster,
                frame_number
            )

        # -------------------------------------------------
        # VẼ
        # -------------------------------------------------

        for cluster in clusters:

            draw_cluster(
                frame,
                cluster
            )

        # -------------------------------------------------
        # GHI VIDEO
        # -------------------------------------------------

        out.write(frame)

        # -------------------------------------------------
        # TIẾN TRÌNH
        # -------------------------------------------------

        if frame_number % FPS == 0:

            second = (
                frame_number // FPS
            )

            print(
                f"Đang render: "
                f"{second}/{DURATION} giây"
            )

    # =====================================================
    # KẾT THÚC
    # =====================================================

    out.release()

    print()
    print("===================================")
    print("HOÀN THÀNH!")
    print("===================================")
    print(
        f"File: {OUTPUT_FILE}"
    )


# =========================================================
# CHẠY
# =========================================================

if __name__ == "__main__":
    main()
