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

NUM_POINTS = 72

POINTS_PER_CLUSTER = 3
NUM_CLUSTERS = NUM_POINTS // POINTS_PER_CLUSTER

POINT_RADIUS = 7
LINE_WIDTH = 2

# Xanh dương tươi
COLOR = (255, 140, 0)

BG_COLOR = (255, 255, 255)

OUTPUT_FILE = "video_intro.mp4"



# =========================================================
# TẠO CÁC CỤM ĐIỂM
# =========================================================
def create_clusters():

    clusters = []

    # =====================================================
    # BỐ TRÍ CÁC CỤM
    # =====================================================
    # 72 cụm -> 6 cột x 4 hàng
    cols = 6
    rows = 4

    # Khoảng cách giữa tâm các cụm
    spacing_x = 280
    spacing_y = 220

    # Tính kích thước toàn bộ khu vực chứa các cụm
    total_width = (cols - 1) * spacing_x
    total_height = (rows - 1) * spacing_y

    # Tâm màn hình
    screen_center_x = WIDTH / 2
    screen_center_y = HEIGHT / 2

    cluster_id = 0

    for row in range(rows):

        for col in range(cols):

            if cluster_id >= NUM_CLUSTERS:
                break

            # =================================================
            # TÍNH TÂM CỦA CỤM
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
            # TẠO 3 ĐIỂM TRONG CỤM
            # =================================================
            for i in range(3):

                angle = (2 * math.pi / 3) * i

                # Kích thước tam giác
                radius = random.uniform(25, 35)

                x = center_x + math.cos(angle) * radius
                y = center_y + math.sin(angle) * radius

                # Vận tốc chậm
                speed = random.uniform(0.4, 0.8)

                direction = random.uniform(
                    0,
                    math.pi * 2
                )

                vx = math.cos(direction) * speed
                vy = math.sin(direction) * speed

                cluster.append({
                    "x": x,
                    "y": y,
                    "vx": vx,
                    "vy": vy
                })

            clusters.append(cluster)

            cluster_id += 1

    return clusters


# =========================================================
# GIỚI HẠN CHUYỂN ĐỘNG CỦA CỤM
# =========================================================
def update_cluster(cluster):

    # Lấy trung tâm hiện tại của cụm
    center_x = sum(p["x"] for p in cluster) / 3
    center_y = sum(p["y"] for p in cluster) / 3

    # Vùng an toàn cho mỗi cụm
    margin = 45

    for p in cluster:

        p["x"] += p["vx"]
        p["y"] += p["vy"]

        # Không cho điểm ra khỏi màn hình
        if p["x"] < margin:
            p["x"] = margin
            p["vx"] *= -1

        if p["x"] > WIDTH - margin:
            p["x"] = WIDTH - margin
            p["vx"] *= -1

        if p["y"] < margin:
            p["y"] = margin
            p["vy"] *= -1

        if p["y"] > HEIGHT - margin:
            p["y"] = HEIGHT - margin
            p["vy"] *= -1


# =========================================================
# KIỂM TRA KHOẢNG CÁCH GIỮA CÁC CỤM
# =========================================================
def keep_clusters_separated(clusters):

    MIN_DISTANCE = 60

    for i in range(len(clusters)):

        for j in range(i + 1, len(clusters)):

            c1 = clusters[i]
            c2 = clusters[j]

            x1 = sum(p["x"] for p in c1) / 3
            y1 = sum(p["y"] for p in c1) / 3

            x2 = sum(p["x"] for p in c2) / 3
            y2 = sum(p["y"] for p in c2) / 3

            dx = x2 - x1
            dy = y2 - y1

            distance = math.sqrt(dx * dx + dy * dy)

            # Nếu 2 cụm quá gần nhau
            if distance < MIN_DISTANCE and distance > 0:

                push = (MIN_DISTANCE - distance) * 0.02

                nx = dx / distance
                ny = dy / distance

                for p in c1:
                    p["x"] -= nx * push
                    p["y"] -= ny * push

                for p in c2:
                    p["x"] += nx * push
                    p["y"] += ny * push


# =========================================================
# VẼ MỘT CỤM 3 ĐIỂM
# =========================================================
def draw_cluster(frame, cluster):

    p1 = cluster[0]
    p2 = cluster[1]
    p3 = cluster[2]

    pt1 = (int(p1["x"]), int(p1["y"]))
    pt2 = (int(p2["x"]), int(p2["y"]))
    pt3 = (int(p3["x"]), int(p3["y"]))

    # Nối 3 điểm thành tam giác
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

    # Vẽ 3 điểm
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

    # Tạo các cụm
    clusters = create_clusters()

    # Codec
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    out = cv2.VideoWriter(
        OUTPUT_FILE,
        fourcc,
        FPS,
        (WIDTH, HEIGHT)
    )

    total_frames = FPS * DURATION

    print("===================================")
    print("ĐANG TẠO VIDEO")
    print("===================================")
    print(f"Kích thước : {WIDTH} x {HEIGHT}")
    print(f"Số điểm   : {NUM_POINTS}")
    print(f"Số cụm     : {NUM_CLUSTERS}")
    print(f"Thời lượng : {DURATION} giây")
    print()

    # =====================================================
    # TẠO TỪNG FRAME
    # =====================================================
    for frame_number in range(total_frames):

        # Nền trắng
        frame = np.full(
            (HEIGHT, WIDTH, 3),
            BG_COLOR,
            dtype=np.uint8
        )

        # Di chuyển từng cụm
        for cluster in clusters:
            update_cluster(cluster)

        # Giữ khoảng cách giữa các cụm
        keep_clusters_separated(clusters)

        # Vẽ từng cụm
        for cluster in clusters:
            draw_cluster(frame, cluster)

        # Ghi video
        out.write(frame)

        # Hiển thị tiến trình
        if frame_number % FPS == 0:
            second = frame_number // FPS
            print(
                f"Đang render: "
                f"{second}/{DURATION} giây"
            )

    # Giải phóng
    out.release()

    print()
    print("===================================")
    print("HOÀN THÀNH!")
    print("===================================")
    print(f"File: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
