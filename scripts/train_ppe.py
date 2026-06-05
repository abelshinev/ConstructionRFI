from ultralytics import RTDETR
import os

def main():
    # 1. Initialize the base COCO model (it will download automatically if missing)
    model = RTDETR('rtdetr-l.pt')

    # 2. Point this to the data.yaml file inside the folder Roboflow just downloaded
    # Update this path to match your actual download location!
    dataset_yaml_path = os.path.abspath('./PPE-Detection-1/data.yaml')

    # 3. Kick off the training loop
    print("Starting RT-DETR Fine-Tuning...")
    results = model.train(
        data=dataset_yaml_path,
        epochs=50,             # 50 is a great overnight baseline
        imgsz=640,             # Standard resolution
        batch=8,               # Safe batch size to prevent CUDA Out of Memory
        device=0,              # Explicitly forces it to use your Nvidia GPU
        project='ppe_model',   # Folder where your new weights will be saved
        name='run_1'
    )

if __name__ == '__main__':
    main()