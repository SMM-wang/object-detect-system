from collections import Counter


def analyze_image(objects):
    if not objects:
        return "未检测到目标，建议结合原始图像继续人工复核。"
    counts = Counter(item["className"] for item in objects)
    parts = [f"{name} {count} 个" for name, count in counts.most_common()]
    return f"画面中检测到 {sum(counts.values())} 个目标，其中包括" + "、".join(parts) + "。"


def analyze_video(summary):
    total = summary.get("totalObjects", 0)
    if total == 0:
        return "视频抽帧检测完成，未检测到目标。"
    classes = summary.get("classes", {})
    parts = [f"{name} {count} 个" for name, count in sorted(classes.items(), key=lambda item: item[1], reverse=True)]
    return f"视频抽帧检测完成，共检测到 {total} 个目标，其中包括" + "、".join(parts) + "。"
