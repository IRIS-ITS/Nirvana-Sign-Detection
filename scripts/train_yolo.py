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
    abs_yaml_path = os.path.abspath(data_yaml)
    dataset_dir = os.path.dirname(abs_yaml_path)

    if not os.path.exists(abs_yaml_path):
        print(f"Error: {abs_yaml_path} not found.")
        return

    # Ensure path field in data.yaml points to absolute dataset path
    with open(abs_yaml_path, "r") as f:
        data_config = yaml.safe_load(f)

    data_config["path"] = dataset_dir
    with open(abs_yaml_path, "w") as f:
        yaml.dump(data_config, f, sort_keys=False)

    print(f"Loading YOLOv8n model...")
    model = YOLO("yolov8n.pt")

    print(f"Starting training on {abs_yaml_path} for {epochs} epochs...")
    results = model.train(
        data=abs_yaml_path,
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
