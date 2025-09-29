import cv2
import numpy as np
import mediapipe as mp
from collections import deque
import csv
import time
import os

def angle_deg_3d(a, b, c):
    ba = a - b
    bc = c - b
    na = np.linalg.norm(ba)
    nc = np.linalg.norm(bc)
    if na < 1e-8 or nc < 1e-8:
        return np.nan
    cosang = np.dot(ba, bc) / (na * nc)
    cosang = np.clip(cosang, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosang)))

def choose_leg(lm2d):
    L_HIP, L_KNEE, L_ANKLE = 23, 25, 27
    R_HIP, R_KNEE, R_ANKLE = 24, 26, 28
    lmin = min(lm2d[i].visibility for i in (L_HIP, L_KNEE, L_ANKLE))
    rmin = min(lm2d[i].visibility for i in (R_HIP, R_KNEE, R_ANKLE))
    return ("left", (L_HIP, L_KNEE, L_ANKLE)) if lmin >= rmin else ("right", (R_HIP, R_KNEE, R_ANKLE))

cap = cv2.VideoCapture(0)  # or replace with video path
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("❌ Camera not found. Select iPhone as camera in macOS or try another index.")
    raise SystemExit

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

buf = deque(maxlen=300)

# Always save CSVs inside "examples/" folder
os.makedirs("examples", exist_ok=True)
session_name = f"examples/session_{time.strftime('%Y%m%d_%H%M%S')}.csv"

with open(session_name, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["timestamp", "side", "angle_deg", "p50", "p95", "risk", "stroke_count", "phase"])

    print(f"📂 Logging session to {session_name}")

    stroke_count = 0
    prev_angle = None
    threshold = 100
    start_time = time.time()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose.process(rgb)

            angle, side = np.nan, "unknown"

            if res.pose_landmarks and res.pose_world_landmarks:
                lm2d = res.pose_landmarks.landmark
                side, ids = choose_leg(lm2d)

                world = np.array([[p.x, p.y, p.z] for p in res.pose_world_landmarks.landmark], dtype=np.float32)
                hip_i, knee_i, ankle_i = ids
                hip, knee, ankle = world[hip_i], world[knee_i], world[ankle_i]
                angle = angle_deg_3d(hip, knee, ankle)

                h, w = frame.shape[:2]
                def px(idx): return int(lm2d[idx].x * w), int(lm2d[idx].y * h)
                cv2.circle(frame, px(hip_i), 6, (0, 255, 0), -1)
                cv2.circle(frame, px(knee_i), 6, (0, 255, 0), -1)
                cv2.circle(frame, px(ankle_i), 6, (0, 255, 0), -1)
                cv2.line(frame, px(hip_i), px(knee_i), (0, 255, 255), 3)
                cv2.line(frame, px(ankle_i), px(knee_i), (0, 255, 255), 3)

            if not np.isnan(angle):
                if prev_angle is not None and prev_angle > threshold and angle <= threshold:
                    stroke_count += 1
                prev_angle = angle

            buf.append(angle)
            vals = np.array([v for v in buf if not np.isnan(v)], dtype=float)

            p50 = float(np.percentile(vals, 50)) if vals.size else np.nan
            p95 = float(np.percentile(vals, 95)) if vals.size else np.nan

            risk = "OK"
            if vals.size:
                if p95 > 155:
                    risk = "Overextension risk"
                elif p95 < 145:
                    risk = "High flexion risk"

            elapsed = time.time() - start_time
            if elapsed < 10:
                phase = "Warmup"
            elif elapsed < 25:
                phase = "Main"
            else:
                phase = "Cooldown"

            csv_writer.writerow([time.time(), side, angle, p50, p95, risk, stroke_count, phase])
            csv_file.flush()  # write instantly

            cv2.putText(frame, f"Side: {side}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Knee angle: {angle:.1f} deg", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"p50: {p50:.1f}  p95: {p95:.1f}  {risk}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Strokes: {stroke_count}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(frame, f"Phase: {phase}", (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)

            cv2.imshow("Cycling Biomech", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("⏹️ Stopped manually")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"✅ Session saved to {session_name}")
