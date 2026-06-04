import cv2
import numpy as np
import onnxruntime as ort

def letterbox(img, target_size=640):
    """YOLO标准预处理，补边缩放"""
    h, w = img.shape[:2]
    scale = min(target_size / w, target_size / h)
    nw, nh = int(w * scale), int(h * scale)
    img_resized = cv2.resize(img, (nw, nh))
    dw, dh = target_size - nw, target_size - nh
    dw /= 2
    dh /= 2
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img_pad = cv2.copyMakeBorder(img_resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114,114,114))
    return img_pad, scale, left, top

def xywh2xyxy(x):
    """中心坐标转换为左上角右下角坐标"""
    y = np.zeros_like(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2
    y[:, 1] = x[:, 1] - x[:, 3] / 2
    y[:, 2] = x[:, 0] + x[:, 2] / 2
    y[:, 3] = x[:, 1] + x[:, 3] / 2
    return y

def box_iou(box, boxes):
    inter_x1 = np.maximum(box[0], boxes[:, 0])
    inter_y1 = np.maximum(box[1], boxes[:, 1])
    inter_x2 = np.minimum(box[2], boxes[:, 2])
    inter_y2 = np.minimum(box[3], boxes[:, 3])
    inter_w = np.maximum(0, inter_x2 - inter_x1)
    inter_h = np.maximum(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    box_area = np.maximum(0, box[2] - box[0]) * np.maximum(0, box[3] - box[1])
    boxes_area = np.maximum(0, boxes[:, 2] - boxes[:, 0]) * np.maximum(0, boxes[:, 3] - boxes[:, 1])
    union = box_area + boxes_area - inter_area
    return inter_area / np.maximum(union, 1e-7)

def nms_numpy(boxes, scores, cls_idx, iou_thres=0.45):
    max_wh = 7680
    boxes_for_nms = boxes.copy()
    offsets = cls_idx.astype(np.float32)[:, None] * max_wh
    boxes_for_nms[:, [0, 2]] += offsets
    boxes_for_nms[:, [1, 3]] += offsets

    keep = []
    order = scores.argsort()[::-1]
    while order.size > 0:
        i = int(order[0])
        keep.append(i)
        if order.size == 1:
            break
        rest = order[1:]
        ious = box_iou(boxes_for_nms[i], boxes_for_nms[rest])
        order = rest[ious <= iou_thres]
    return keep

# ====================== GPU初始化 ======================
# CUDA优先，GPU推理
providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
model_path = r"C:\workspace\object detect system\back_system\yolov11n.onnx"
session = ort.InferenceSession(model_path, providers=providers)
input_name = session.get_inputs()[0].name
input_shape = session.get_inputs()[0].shape
INP_SIZE = input_shape[2] # 自动获取模型输入尺寸 (如 640)

# ====================== 推理配置 ======================
CONF_THRESH = 0.25
IOU_THRESH = 0.7
img_path = "drone6.jpg"
save_path = "result.jpg"

# 读取原图
img_origin = cv2.imread(img_path)
if img_origin is None:
    print(f"无法读取图像，请检查路径: {img_path}")
    exit()
h0, w0 = img_origin.shape[:2]

# 预处理
img_in, scale, pad_left, pad_top = letterbox(img_origin, INP_SIZE)
blob = img_in.astype(np.float32) / 255.0
blob = np.transpose(blob, [2, 0, 1])
blob = np.expand_dims(blob, axis=0)

# GPU正向推理
pred_out = session.run(None, {input_name: blob})[0]
pred = np.squeeze(pred_out).T  # 形状转换：[1, 4+classes, 8400] -> [8400, 4+classes]

# ================= 核心修复区：YOLOv11 输出解析 =================
# 1. 拆分坐标和类别概率
xywh = pred[:, :4]             # [8400, 4] 前4列是边界框中心点及宽高
cls_scores = pred[:, 4:]       # [8400, num_classes] 第4列之后全是各个类别的预测概率

# 2. 找到每个预测框的最大类别概率，及其对应的类别索引
conf = np.max(cls_scores, axis=-1)       # 提取最大概率作为该框的最终置信度
cls_idx = np.argmax(cls_scores, axis=-1) # 获取最大概率对应的类别索引(0, 1, 2...)

# 3. 过滤低置信度的框 (掩码过滤)
mask = conf > CONF_THRESH
xywh = xywh[mask]
conf = conf[mask]
cls_idx = cls_idx[mask]
# ================================================================

if len(xywh) == 0:
    cv2.imwrite(save_path, img_origin)
    print("无检测目标")
    exit()

# 坐标转换：中心点宽高 -> 左上角右下角
xyxy = xywh2xyxy(xywh)

# 去除预处理加的黑边(padding)、并映射回原图尺寸
xyxy[:, [0, 2]] -= pad_left
xyxy[:, [1, 3]] -= pad_top
xyxy /= scale

# NMS去重
keep_idx = nms_numpy(xyxy, conf, cls_idx, IOU_THRESH)

# 画框
# 随机生成80种颜色用于不同类别（固定随机种子保证每次颜色一致）
np.random.seed(42) 
colors = np.random.randint(0, 255, (80, 3), dtype=np.uint8)

for i in keep_idx:
    x1, y1, x2, y2 = xyxy[i].astype(np.int32)
    c = int(cls_idx[i])
    score = round(float(conf[i]), 3)
    
    # 标签文本，如果你有具体的类别名称（如 "car", "person"），可以在这里替换 c
    label = f"Class {c} {score}" 
    
    # 画矩形框
    cv2.rectangle(img_origin, (x1, y1), (x2, y2), colors[c].tolist(), 1)
    # 画文字标签
    # cv2.putText(img_origin, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[c].tolist(), 2)

# 保存并输出结果
cv2.imwrite(save_path, img_origin)
print(f"推理完成，成功检测到 {len(keep_idx)} 个目标！")
print(f"结果已保存至：{save_path}")
print(f"当前使用推理设备：{session.get_providers()}")