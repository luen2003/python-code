import cv2
import numpy as np
import random
import math

WIDTH = 1920
HEIGHT = 1080

FPS = 30
DURATION = 8

OUTPUT_FILE = "intro_video.mp4"

NUM_POINTS = 64

POINTS_PER_CLUSTER = 3
NUM_CLUSTERS = NUM_POINTS // POINTS_PER_CLUSTER

POINT_RADIUS = 7
OUTER_POINT_RADIUS = 5

LINE_WIDTH = 2

CENTER_X = WIDTH / 2
CENTER_Y = HEIGHT / 2

DISTRIBUTION_X = 680
DISTRIBUTION_Y = 380

MIN_CLUSTER_DISTANCE = 175 
MAX_ATTEMPTS = 50000

MAX_CONNECTION_DISTANCE = 380

MIN_EXTRA_CONNECTIONS = 0
MAX_EXTRA_CONNECTIONS = 1

EXTRA_CONNECTION_PROBABILITY = 0.12

OUTER_POINT_MIN_SPEED = 0.45
OUTER_POINT_MAX_SPEED = 1.5

OUTER_POINT_MAX_RADIUS_MIN = 35
OUTER_POINT_MAX_RADIUS_MAX = 65

OUTER_POINT_WANDER_FORCE = 0.018
OUTER_POINT_RETURN_FORCE = 0.20

NUM_DOT_GROUPS = 4

DOT_GROUP_MIN_SPEED = 0.25
DOT_GROUP_MAX_SPEED = 0.75

DOT_GROUP_WAVE_MIN = 0.015
DOT_GROUP_WAVE_MAX = 0.045

DOT_GROUP_SWAY_MIN = 3.0
DOT_GROUP_SWAY_MAX = 9.0

COLOR = (
    255,
    140,
    0
)

CONNECTION_COLOR = COLOR

BG_COLOR = (
    255,
    255,
    255
)

FILL_COLOR = (
    255,
    220,
    170
)

FILL_ALPHA = 0.58

MIN_FILLED_CLUSTERS = 7
MAX_FILLED_CLUSTERS = 10

MIN_SPEED = 0.45
MAX_SPEED = 2.0

CLUSTER_MAX_RADIUS_MIN = 38
CLUSTER_MAX_RADIUS_MAX = 62

def create_cluster_centers():
    centers = []
    attempts = 0
    margin = 120

    while len(centers) < NUM_CLUSTERS and attempts < MAX_ATTEMPTS:
        attempts += 1

        x = random.gauss(CENTER_X, DISTRIBUTION_X / 2.2)
        y = random.gauss(CENTER_Y, DISTRIBUTION_Y / 2.2)

        if x < margin or x > WIDTH - margin or y < margin or y > HEIGHT - margin:
            continue

        valid = True
        for cx, cy in centers:
            if math.hypot(x - cx, y - cy) < MIN_CLUSTER_DISTANCE:
                valid = False
                break

        if valid:
            centers.append((x, y))

    # FALLBACK
    if len(centers) < NUM_CLUSTERS:
        attempts = 0
        while len(centers) < NUM_CLUSTERS and attempts < MAX_ATTEMPTS:
            attempts += 1
            x = random.uniform(150, WIDTH - 150)
            y = random.uniform(120, HEIGHT - 120)

            valid = True
            for cx, cy in centers:
                if math.hypot(x - cx, y - cy) < 130:
                    valid = False
                    break

            if valid:
                centers.append((x, y))

    if len(centers) != NUM_CLUSTERS:
        raise RuntimeError("Không thể tạo đủ cụm chính.")

    return centers

def create_clusters():
    clusters = []
    centers = create_cluster_centers()

    number_filled = random.randint(MIN_FILLED_CLUSTERS, MAX_FILLED_CLUSTERS)
    filled_ids = set(random.sample(range(NUM_CLUSTERS), number_filled))

    for cluster_id in range(NUM_CLUSTERS):
        center_x, center_y = centers[cluster_id]
        points = []
        base_rotation = random.uniform(0, math.pi * 2)

        for i in range(POINTS_PER_CLUSTER):
            angle = base_rotation + i * 2 * math.pi / 3 + random.uniform(-0.20, 0.20)
            radius = random.uniform(24, 42)

            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius

            speed = random.uniform(MIN_SPEED, MAX_SPEED)
            direction = random.uniform(0, math.pi * 2)

            points.append({
                "x": x,
                "y": y,
                "center_x": center_x,
                "center_y": center_y,
                "vx": math.cos(direction) * speed,
                "vy": math.sin(direction) * speed,
                "phase": random.uniform(0, math.pi * 2),
                "phase_speed": random.uniform(0.008, 0.018),
                "max_radius": random.uniform(CLUSTER_MAX_RADIUS_MIN, CLUSTER_MAX_RADIUS_MAX)
            })

        clusters.append({
            "points": points,
            "center_x": center_x,
            "center_y": center_y,
            "filled": (cluster_id in filled_ids)
        })

    return clusters

def cluster_distance(clusters, a, b):
    return math.hypot(
        clusters[a]["center_x"] - clusters[b]["center_x"],
        clusters[a]["center_y"] - clusters[b]["center_y"]
    )


def connection_exists(connections, a, b):
    for connection in connections:
        ca, cb = connection["cluster_a"], connection["cluster_b"]
        if (ca == a and cb == b) or (ca == b and cb == a):
            return True
    return False

def add_connection(connections, cluster_a, cluster_b):
    if cluster_a == cluster_b or connection_exists(connections, cluster_a, cluster_b):
        return

    point_a = random.randrange(POINTS_PER_CLUSTER)
    point_b = random.randrange(POINTS_PER_CLUSTER)

    connections.append({
        "cluster_a": cluster_a,
        "point_a": point_a,
        "cluster_b": cluster_b,
        "point_b": point_b
    })

def create_connections(clusters):
    connections = []
    connected = {0}
    remaining = set(range(1, NUM_CLUSTERS))

    while remaining:
        best_pair = None
        best_distance = float("inf")

        for a in connected:
            for b in remaining:
                distance = cluster_distance(clusters, a, b)
                if distance < best_distance:
                    best_distance = distance
                    best_pair = (a, b)

        if best_pair is None:
            break

        a, b = best_pair
        add_connection(connections, a, b)
        connected.add(b)
        remaining.remove(b)

    if len(connected) != NUM_CLUSTERS:
        raise RuntimeError("Mạng chính không liên thông.")

    # CONNECTION PHỤ (RẤT ÍT)
    for cluster_a in range(NUM_CLUSTERS):
        if random.random() > EXTRA_CONNECTION_PROBABILITY:
            continue

        candidates = []
        for cluster_b in range(NUM_CLUSTERS):
            if cluster_a == cluster_b or connection_exists(connections, cluster_a, cluster_b):
                continue

            distance = cluster_distance(clusters, cluster_a, cluster_b)
            if distance <= MAX_CONNECTION_DISTANCE:
                candidates.append((cluster_b, distance))

        if not candidates:
            continue

        random.shuffle(candidates)
        candidates.sort(key=lambda item: item[1] * random.uniform(0.85, 1.15))

        number_extra = random.randint(MIN_EXTRA_CONNECTIONS, MAX_EXTRA_CONNECTIONS)
        for cluster_b, _ in candidates[:number_extra]:
            add_connection(connections, cluster_a, cluster_b)

    return connections

def create_dot_groups(clusters):
    dot_groups = []
    attempts = 0
    max_attempts = 5000
    margin = 160

    while len(dot_groups) < NUM_DOT_GROUPS and attempts < max_attempts:
        attempts += 1

        center_x = random.gauss(CENTER_X, DISTRIBUTION_X / 2.8)
        center_y = random.gauss(CENTER_Y, DISTRIBUTION_Y / 2.8)

        if center_x < margin or center_x > WIDTH - margin or center_y < margin or center_y > HEIGHT - margin:
            continue

        too_close = False
        for cluster in clusters:
            if math.hypot(center_x - cluster["center_x"], center_y - cluster["center_y"]) < 145:
                too_close = True
                break

        if too_close:
            continue

        direction = random.uniform(0, math.pi * 2)
        speed = random.uniform(DOT_GROUP_MIN_SPEED, DOT_GROUP_MAX_SPEED)

        points = []
        for i in range(4):
            point_radius = random.uniform(40, 75)
            point_angle = (i * 2 * math.pi / 4) + random.uniform(-0.3, 0.3)

            px = center_x + math.cos(point_angle) * point_radius
            py = center_y + math.sin(point_angle) * point_radius

            p_speed = random.uniform(OUTER_POINT_MIN_SPEED, OUTER_POINT_MAX_SPEED)
            p_dir = random.uniform(0, math.pi * 2)

            points.append({
                "x": px,
                "y": py,
                "vx": math.cos(p_dir) * p_speed,
                "vy": math.sin(p_dir) * p_speed,
                "phase": random.uniform(0, math.pi * 2),
                "phase_speed": random.uniform(0.008, 0.018),
                "max_radius": point_radius * 1.2
            })

        # TÌM TAM GIÁC GẦN NHẤT CỐ ĐỊNH CHO NHÓM NÀY
        min_dist = float("inf")
        best_dot_idx = -1
        best_cluster_idx = -1
        best_point_idx = -1

        for d_idx, p in enumerate(points):
            for c_idx, cluster in enumerate(clusters):
                for cp_idx, cp in enumerate(cluster["points"]):
                    dist = math.hypot(p["x"] - cp["x"], p["y"] - cp["y"])
                    if dist < min_dist:
                        min_dist = dist
                        best_dot_idx = d_idx
                        best_cluster_idx = c_idx
                        best_point_idx = cp_idx

        dot_groups.append({
            "center_x": center_x,
            "center_y": center_y,
            "vx": math.cos(direction) * speed,
            "vy": math.sin(direction) * speed,
            "phase": random.uniform(0, math.pi * 2),
            "phase_speed": random.uniform(DOT_GROUP_WAVE_MIN, DOT_GROUP_WAVE_MAX),
            "sway_amount": random.uniform(DOT_GROUP_SWAY_MIN, DOT_GROUP_SWAY_MAX),
            "sway_direction": random.uniform(0, math.pi * 2),
            "points": points,
            "best_dot_idx": best_dot_idx,
            "best_cluster_idx": best_cluster_idx,
            "best_point_idx": best_point_idx
        })

    return dot_groups

def update_cluster(cluster, frame_number):
    for p in cluster["points"]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]

        p["phase"] += p["phase_speed"]
        p["vx"] += math.sin(p["phase"]) * 0.018
        p["vy"] += math.cos(p["phase"]) * 0.018

        speed = math.hypot(p["vx"], p["vy"])
        if speed > MAX_SPEED:
            p["vx"] = (p["vx"] / speed) * MAX_SPEED
            p["vy"] = (p["vy"] / speed) * MAX_SPEED
        elif speed < MIN_SPEED:
            if speed == 0:
                direction = random.uniform(0, math.pi * 2)
                p["vx"] = math.cos(direction)
                p["vy"] = math.sin(direction)
            else:
                p["vx"] = (p["vx"] / speed) * MIN_SPEED
                p["vy"] = (p["vy"] / speed) * MIN_SPEED

        dx = p["x"] - p["center_x"]
        dy = p["y"] - p["center_y"]
        distance = math.hypot(dx, dy)

        if distance > p["max_radius"] and distance > 0:
            p["vx"] -= (dx / distance) * 0.20
            p["vy"] -= (dy / distance) * 0.20


def update_dot_group(group):
    group["phase"] += group["phase_speed"]
    group["center_x"] += group["vx"]
    group["center_y"] += group["vy"]

    sway = math.sin(group["phase"]) * group["sway_amount"]
    group["center_x"] += math.cos(group["sway_direction"]) * sway * 0.12
    group["center_y"] += math.sin(group["sway_direction"]) * sway * 0.12

    margin = 100
    if group["center_x"] < margin:
        group["center_x"] = margin
        group["vx"] = abs(group["vx"])
    elif group["center_x"] > WIDTH - margin:
        group["center_x"] = WIDTH - margin
        group["vx"] = -abs(group["vx"])

    if group["center_y"] < margin:
        group["center_y"] = margin
        group["vy"] = abs(group["vy"])
    elif group["center_y"] > HEIGHT - margin:
        group["center_y"] = HEIGHT - margin
        group["vy"] = -abs(group["vy"])

    for p in group["points"]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]

        p["phase"] += p["phase_speed"]
        p["vx"] += math.sin(p["phase"]) * OUTER_POINT_WANDER_FORCE
        p["vy"] += math.cos(p["phase"]) * OUTER_POINT_WANDER_FORCE

        speed = math.hypot(p["vx"], p["vy"])
        if speed > OUTER_POINT_MAX_SPEED:
            p["vx"] = (p["vx"] / speed) * OUTER_POINT_MAX_SPEED
            p["vy"] = (p["vy"] / speed) * OUTER_POINT_MAX_SPEED
        elif speed < OUTER_POINT_MIN_SPEED and speed > 0:
            p["vx"] = (p["vx"] / speed) * OUTER_POINT_MIN_SPEED
            p["vy"] = (p["vy"] / speed) * OUTER_POINT_MIN_SPEED

        dx = p["x"] - group["center_x"]
        dy = p["y"] - group["center_y"]
        distance = math.hypot(dx, dy)

        if distance > p["max_radius"] and distance > 0:
            p["vx"] -= (dx / distance) * OUTER_POINT_RETURN_FORCE
            p["vy"] -= (dy / distance) * OUTER_POINT_RETURN_FORCE

def draw_connections(frame, clusters, connections):
    for connection in connections:
        p1 = clusters[connection["cluster_a"]]["points"][connection["point_a"]]
        p2 = clusters[connection["cluster_b"]]["points"][connection["point_b"]]
        cv2.line(
            frame,
            (int(p1["x"]), int(p1["y"])),
            (int(p2["x"]), int(p2["y"])),
            CONNECTION_COLOR,
            LINE_WIDTH,
            cv2.LINE_AA
        )


def draw_dot_groups(frame, dot_groups, clusters):
    for group in dot_groups:
        points = group["points"]

        for i in range(3):
            cv2.line(
                frame,
                (int(points[i]["x"]), int(points[i]["y"])),
                (int(points[i + 1]["x"]), int(points[i + 1]["y"])),
                COLOR,
                LINE_WIDTH,
                cv2.LINE_AA
            )

        b_dot = group["best_dot_idx"]
        b_cls = group["best_cluster_idx"]
        b_pt = group["best_point_idx"]

        if b_dot != -1 and b_cls != -1 and b_pt != -1:
            p_dot = points[b_dot]
            p_target = clusters[b_cls]["points"][b_pt]
            cv2.line(
                frame,
                (int(p_dot["x"]), int(p_dot["y"])),
                (int(p_target["x"]), int(p_target["y"])),
                CONNECTION_COLOR,
                LINE_WIDTH,
                cv2.LINE_AA
            )

        for p in points:
            cv2.circle(
                frame,
                (int(p["x"]), int(p["y"])),
                OUTER_POINT_RADIUS,
                COLOR,
                -1,
                cv2.LINE_AA
            )


def draw_cluster(frame, cluster):
    points = cluster["points"]
    pt1 = (int(points[0]["x"]), int(points[0]["y"]))
    pt2 = (int(points[1]["x"]), int(points[1]["y"]))
    pt3 = (int(points[2]["x"]), int(points[2]["y"]))

    if cluster["filled"]:
        triangle = np.array([pt1, pt2, pt3], dtype=np.int32)
        overlay = frame.copy()
        cv2.fillPoly(overlay, [triangle], FILL_COLOR)
        cv2.addWeighted(overlay, FILL_ALPHA, frame, 1 - FILL_ALPHA, 0, frame)

    cv2.line(frame, pt1, pt2, COLOR, LINE_WIDTH, cv2.LINE_AA)
    cv2.line(frame, pt2, pt3, COLOR, LINE_WIDTH, cv2.LINE_AA)
    cv2.line(frame, pt3, pt1, COLOR, LINE_WIDTH, cv2.LINE_AA)

    for p in points:
        cv2.circle(
            frame,
            (int(p["x"]), int(p["y"])),
            POINT_RADIUS,
            COLOR,
            -1,
            cv2.LINE_AA
        )

def main():
    clusters = create_clusters()
    connections = create_connections(clusters)
    dot_groups = create_dot_groups(clusters)

    filled_count = sum(1 for cluster in clusters if cluster["filled"])

    print("==============================================")
    print("ĐANG TẠO VIDEO (PHIÊN BẢN TỐI GIẢN)")
    print("==============================================")
    print(f"Kích thước          : {WIDTH} x {HEIGHT}")
    print(f"FPS                 : {FPS}")
    print(f"Thời lượng          : {DURATION} giây")
    print(f"Điểm chính          : {NUM_POINTS}")
    print(f"Cụm chính           : {NUM_CLUSTERS}")
    print(f"Connection chính    : {len(connections)}")
    print(f"Tam giác chính fill : {filled_count}")
    print(f"Nhóm gấp khúc (4ch) : {len(dot_groups)}")
    print("Mạng chính          : LIÊN THÔNG")
    print("==============================================\n")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(OUTPUT_FILE, fourcc, FPS, (WIDTH, HEIGHT))

    if not out.isOpened():
        print("LỖI: Không thể tạo video!")
        return

    total_frames = FPS * DURATION

    for frame_number in range(total_frames):
        frame = np.full((HEIGHT, WIDTH, 3), BG_COLOR, dtype=np.uint8)

        for cluster in clusters:
            update_cluster(cluster, frame_number)

        for group in dot_groups:
            update_dot_group(group)

        draw_connections(frame, clusters, connections)

        for cluster in clusters:
            draw_cluster(frame, cluster)

        draw_dot_groups(frame, dot_groups, clusters)

        out.write(frame)

        if frame_number % FPS == 0:
            print(f"Đang render: {frame_number // FPS}/{DURATION} giây")

    out.release()
    print("\n==============================================")
    print("HOÀN THÀNH!")
    print("==============================================")
    print(f"File: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()