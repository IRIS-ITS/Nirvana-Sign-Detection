import os
import sys
import onnx
from onnx import numpy_helper
import numpy as np

def fix_onnx_for_opencv(onnx_path="best.onnx"):
    if not os.path.exists(onnx_path):
        print(f"Error: {onnx_path} not found.")
        return False

    model = onnx.load(onnx_path)
    modified = False

    for i, init in enumerate(model.graph.initializer):
        if init.name == "/model.22/Constant_15_output_0":
            arr = numpy_helper.to_array(init)
            if len(arr.shape) == 2 and arr.shape[0] == 1:
                arr = np.expand_dims(arr, axis=1) # Shape [1, 1, N]
            if len(arr.shape) == 3 and arr.shape[1] == 1:
                new_arr = np.repeat(arr, 4, axis=1) # Broadcast channel dim from 1 to 4
                new_init = numpy_helper.from_array(new_arr, name=init.name)
                model.graph.initializer[i].CopyFrom(new_init)
                modified = True
                print(f"Fixed initializer {init.name}: shape broadcasted to {new_arr.shape}")

    if modified:
        onnx.save(model, onnx_path)
        print(f"Successfully patched ONNX model for OpenCV 4.5.4 compatibility: {onnx_path}")
    else:
        print(f"ONNX model already patched or compatible: {onnx_path}")
    return True

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "best.onnx"
    fix_onnx_for_opencv(target)
