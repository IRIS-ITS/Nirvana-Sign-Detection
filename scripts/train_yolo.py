import os
import yaml
from ultralytics import YOLO

def train_sign_model(
    data_yaml="dataset/data.yaml",
    epochs=50,
    imgsz=640,
    batch=16,
    project="runs/detect",
    name="sign_detection"
):
    if not os.path.exists(data_yaml):
        print(f"Error: {data_yaml} not found.")
        return

    print("Loading YOLOv8n model...")
    model = YOLO("yolov8n.pt")

    print(f"Starting training on {data_yaml} for {epochs} epochs...")
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project=project,
        name=name
    )

    print("Evaluating trained model...")
    metrics = model.val()
    print(f"mAP50-95: {metrics.box.map:.4f}")
    print(f"mAP50:    {metrics.box.map50:.4f}")

    print("Exporting model to ONNX format...")
    onnx_path = model.export(format="onnx", imgsz=imgsz)
    print(f"Exported ONNX model to: {onnx_path}")

if __name__ == "__main__":
    train_sign_model()
