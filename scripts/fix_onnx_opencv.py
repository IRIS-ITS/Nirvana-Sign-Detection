import os
import sys
import onnx
from onnx import numpy_helper, helper
import numpy as np

# Fix 1 (legacy, OpenCV 4.5.4): broadcast stride initializer [1,1,N] -> [1,4,N].
# Fix 2 (OpenCV 5.x new graph engine): it computes Sub(const, tensor) as
#   tensor - const (reversed!). Verified with isolated Sub unit test:
#   Sub(C=10, X) returned x-10 instead of 10-x, blowing decoded boxes up to
#   full-frame (w~642) while class scores stayed correct.
#   Workaround: rewrite every const-first Sub(C, X) as Add(C, Neg(X)).
#   (Tensor-tensor Sub is unaffected and left untouched.)


def _fix_stride_broadcast(model):
    modified = False
    for i, init in enumerate(model.graph.initializer):
        if init.name == "/model.22/Constant_15_output_0":
            arr = numpy_helper.to_array(init)
            if len(arr.shape) == 2 and arr.shape[0] == 1:
                arr = np.expand_dims(arr, axis=1)  # Shape [1, 1, N]
            if len(arr.shape) == 3 and arr.shape[1] == 1:
                new_arr = np.repeat(arr, 4, axis=1)  # Broadcast channel dim from 1 to 4
                new_init = numpy_helper.from_array(new_arr, name=init.name)
                model.graph.initializer[i].CopyFrom(new_init)
                modified = True
                print(f"Fixed initializer {init.name}: shape broadcasted to {new_arr.shape}")
    return modified


def _fix_sub_const_first(model):
    consts = {i.name for i in model.graph.initializer}
    fixed = []
    for n in model.graph.node:
        if (n.op_type == "Sub" and len(n.input) == 2
                and n.input[0] in consts and n.input[1] not in consts):
            fixed.append(n.name)
    if not fixed:
        return False
    graph = model.graph
    for name in fixed:
        node = next(n for n in graph.node if n.name == name)
        c_in, x_in = node.input[0], node.input[1]
        out = node.output[0]
        neg_out = out + "__neg"
        neg = helper.make_node("Neg", [x_in], [neg_out], name=name + "__Neg")
        add = helper.make_node("Add", [c_in, neg_out], [out], name=name + "__AddFix")
        pos = next(i for i, n in enumerate(graph.node) if n.name == name)
        remaining = [n for n in graph.node if n.name != name]
        new_nodes = remaining[:pos] + [neg, add] + remaining[pos:]
        del graph.node[:]
        graph.node.extend(new_nodes)
        print(f"Fixed {name}: Sub(const, tensor) rewritten as Add(const, Neg(tensor))")
    return True


def fix_onnx_for_opencv(onnx_path="../models/best.onnx"):
    if not os.path.exists(onnx_path):
        print(f"Error: {onnx_path} not found.")
        return False

    model = onnx.load(onnx_path)
    m1 = _fix_stride_broadcast(model)
    m2 = _fix_sub_const_first(model)

    if m1 or m2:
        # Numerical equivalence check (patched model must match original)
        try:
            import onnxruntime as ort
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as tf:
                tmp = tf.name
            onnx.save(model, tmp)
            rng = np.random.RandomState(0)
            dummy = rng.rand(1, 3, 640, 640).astype(np.float32)
            a = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"]).run(None, {"images": dummy})[0]
            b = ort.InferenceSession(tmp, providers=["CPUExecutionProvider"]).run(None, {"images": dummy})[0]
            diff = float(np.abs(a - b).max())
            os.unlink(tmp)
            print(f"Equivalence check maxabsdiff: {diff:.3e}")
            if diff > 1e-4:
                print("ABORT: patched model diverges from original!")
                return False
        except ImportError:
            print("onnxruntime not available, skipping equivalence check")
        onnx.save(model, onnx_path)
        print(f"Successfully patched ONNX model for OpenCV DNN compatibility: {onnx_path}")
    else:
        print(f"ONNX model already patched or compatible: {onnx_path}")
    return True


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "../models/best.onnx"
    fix_onnx_for_opencv(target)
