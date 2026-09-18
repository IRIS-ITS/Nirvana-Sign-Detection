#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

static const int MODEL_SIZE = 640;

struct Detection {
    int class_id;
    float confidence;
    cv::Rect box;
};

struct Letterbox {
    cv::Mat img;   // 640x640 padded image
    float scale;   // resize ratio applied to the original frame
    int padX, padY;
};

// YOLOv8-style letterbox: preserve aspect ratio, pad with 114 gray.
// Matches Ultralytics training preprocessing (instead of stretch resize).
static Letterbox letterbox(const cv::Mat& src) {
    Letterbox lb;
    float r = std::min(MODEL_SIZE / (float)src.cols, MODEL_SIZE / (float)src.rows);
    int nw = static_cast<int>(std::round(src.cols * r));
    int nh = static_cast<int>(std::round(src.rows * r));
    cv::Mat resized;
    cv::resize(src, resized, cv::Size(nw, nh));
    int dw = MODEL_SIZE - nw;
    int dh = MODEL_SIZE - nh;
    lb.padX = dw / 2;
    lb.padY = dh / 2;
    lb.scale = r;
    cv::copyMakeBorder(resized, lb.img, lb.padY, dh - lb.padY, lb.padX, dw - lb.padX,
                       cv::BORDER_CONSTANT, cv::Scalar(114, 114, 114));
    return lb;
}

// Run inference on one frame (already resized to camera resolution).
// Returns raw detections BEFORE NMS.
static std::vector<Detection> infer(cv::dnn::Net& net, const cv::Mat& frame,
                                    float confThreshold, const Letterbox& lb) {
    cv::Mat blob;
    cv::dnn::blobFromImage(lb.img, blob, 1.0 / 255.0, cv::Size(MODEL_SIZE, MODEL_SIZE),
                           cv::Scalar(), true, false);
    net.setInput(blob);
    cv::Mat rawOutput = net.forward();

    int channels = 8;
    int numAnchors = 8400;
    if (rawOutput.dims == 3) {
        channels = rawOutput.size[1];
        numAnchors = rawOutput.size[2];
    }

    cv::Mat output2D(channels, numAnchors, CV_32F, (float*)rawOutput.data);
    cv::Mat outMat;
    cv::transpose(output2D, outMat); // [8400, 8]

    std::vector<Detection> dets;
    for (int i = 0; i < outMat.rows; ++i) {
        float* row = outMat.ptr<float>(i);
        float cx = row[0], cy = row[1], w = row[2], h = row[3];

        float maxScore = 0.0f;
        int maxClassId = -1;
        for (int c = 0; c < 4; ++c) {
            if (row[4 + c] > maxScore) {
                maxScore = row[4 + c];
                maxClassId = c;
            }
        }
        if (maxScore < confThreshold) continue;

        // Inverse letterbox: 640-space -> original frame coordinates.
        float x1 = (cx - 0.5f * w - lb.padX) / lb.scale;
        float y1 = (cy - 0.5f * h - lb.padY) / lb.scale;
        float x2 = (cx + 0.5f * w - lb.padX) / lb.scale;
        float y2 = (cy + 0.5f * h - lb.padY) / lb.scale;

        int left = static_cast<int>(std::round(x1));
        int top = static_cast<int>(std::round(y1));
        int width = static_cast<int>(std::round(x2 - x1));
        int height = static_cast<int>(std::round(y2 - y1));

        // Boundary clamp (no silent edge-sticking: keep as-is, just clip).
        left = std::max(0, std::min(left, frame.cols - 1));
        top = std::max(0, std::min(top, frame.rows - 1));
        width = std::max(1, std::min(width, frame.cols - left));
        height = std::max(1, std::min(height, frame.rows - top));

        dets.push_back({maxClassId, maxScore, cv::Rect(left, top, width, height)});
    }
    return dets;
}

static std::vector<int> applyNMS(const std::vector<Detection>& dets,
                                 float confThreshold, float nmsThreshold) {
    std::vector<cv::Rect> boxes;
    std::vector<float> confs;
    for (const auto& d : dets) {
        boxes.push_back(d.box);
        confs.push_back(d.confidence);
    }
    std::vector<int> indices;
    if (!boxes.empty())
        cv::dnn::NMSBoxes(boxes, confs, confThreshold, nmsThreshold, indices);
    return indices;
}

static void drawDetections(cv::Mat& frame, const std::vector<Detection>& dets,
                           const std::vector<int>& indices,
                           const std::vector<std::string>& classNames,
                           const std::vector<cv::Scalar>& colors) {
    for (int idx : indices) {
        const Detection& d = dets[idx];
        cv::Scalar color = colors[d.class_id % colors.size()];
        std::string labelName =
            (d.class_id < (int)classNames.size()) ? classNames[d.class_id] : "unknown";
        // Debug aid: box size as % of frame (Phase 6).
        float wpct = 100.0f * d.box.width / frame.cols;
        float hpct = 100.0f * d.box.height / frame.rows;
        std::string labelText = labelName + " " + cv::format("%.2f %dx%d%%", d.confidence,
                                                             (int)std::round(wpct),
                                                             (int)std::round(hpct));
        cv::rectangle(frame, d.box, color, 2);

        int baseLine;
        cv::Size labelSize = cv::getTextSize(labelText, cv::FONT_HERSHEY_SIMPLEX, 0.6, 2, &baseLine);
        int labelTop = std::max(d.box.y, labelSize.height + 5);
        cv::rectangle(frame,
                      cv::Point(d.box.x, labelTop - labelSize.height - 5),
                      cv::Point(d.box.x + labelSize.width + 5, labelTop + baseLine),
                      color, cv::FILLED);
        cv::putText(frame, labelText, cv::Point(d.box.x + 2, labelTop - 2),
                    cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(0, 0, 0), 2);
    }
}

int main(int argc, char** argv) {
    std::vector<std::string> classNames = {"u_turn", "stop", "turn_left", "turn_right"};
    std::vector<cv::Scalar> colors = {
        cv::Scalar(255, 255, 0),   // u_turn: Cyan
        cv::Scalar(0, 0, 255),     // stop: Red
        cv::Scalar(0, 255, 255),   // turn_left: Yellow
        cv::Scalar(0, 255, 0)      // turn_right: Green
    };
    float confThreshold = 0.50f;
    float nmsThreshold = 0.45f;

    std::string modelPath = "models/best.onnx";
    cv::dnn::Net net = cv::dnn::readNetFromONNX(modelPath);
    if (net.empty()) {
        modelPath = "best.onnx";
        net = cv::dnn::readNetFromONNX(modelPath);
    }
    if (net.empty()) {
        std::cerr << "Error: Could not load ONNX model from models/best.onnx or best.onnx" << std::endl;
        return -1;
    }
    net.setPreferableBackend(cv::dnn::DNN_BACKEND_OPENCV);
    net.setPreferableTarget(cv::dnn::DNN_TARGET_CPU);
    std::cout << "Successfully loaded ONNX model: " << modelPath << std::endl;

    // Static-image mode: ./detect --image <path> [--save <out>]
    // Headless validation of the exact live pipeline (no camera needed).
    std::string imgArg, saveArg = "detect_out.jpg";
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--image" && i + 1 < argc) imgArg = argv[++i];
        if (a == "--save" && i + 1 < argc) saveArg = argv[++i];
    }
    if (!imgArg.empty()) {
        cv::Mat frame = cv::imread(imgArg);
        if (frame.empty()) {
            std::cerr << "Error: cannot read image " << imgArg << std::endl;
            return -1;
        }
        if (frame.cols != 640 || frame.rows != 480)
            cv::resize(frame, frame, cv::Size(640, 480));
        Letterbox lb = letterbox(frame);
        std::cout << "letterbox: scale=" << lb.scale << " pad=" << lb.padX << ","
                  << lb.padY << " img=" << lb.img.cols << "x" << lb.img.rows << std::endl;
        std::vector<Detection> dets = infer(net, frame, confThreshold, lb);
        std::vector<int> indices = applyNMS(dets, confThreshold, nmsThreshold);
        for (int idx : indices) {
            const Detection& d = dets[idx];
            std::cout << classNames[d.class_id] << " conf=" << d.confidence
                      << " box=" << d.box.x << "," << d.box.y
                      << "," << d.box.width << "x" << d.box.height << std::endl;
        }
        if (indices.empty()) std::cout << "no detections" << std::endl;
        drawDetections(frame, dets, indices, classNames, colors);
        cv::imwrite(saveArg, frame);
        std::cout << "saved " << saveArg << std::endl;
        return 0;
    }

    int cameraID = 2;
    cv::VideoCapture cap(cameraID);
    if (!cap.isOpened()) {
        std::cerr << "Error: Could not open camera with ID: " << cameraID << std::endl;
        return -1;
    }
    cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480);
    std::cout << "Camera initialized on ID " << cameraID << ". Press 'q' or ESC to exit." << std::endl;

    cv::Mat frame;
    double prevTime = cv::getTickCount();

    while (true) {
        cap >> frame;
        if (frame.empty()) {
            std::cerr << "Error: Captured empty frame." << std::endl;
            break;
        }
        // Enforce working resolution: some webcams ignore CAP_PROP settings.
        if (frame.cols != 640 || frame.rows != 480)
            cv::resize(frame, frame, cv::Size(640, 480));

        Letterbox lb = letterbox(frame);
        std::vector<Detection> dets = infer(net, frame, confThreshold, lb);
        std::vector<int> indices = applyNMS(dets, confThreshold, nmsThreshold);
        drawDetections(frame, dets, indices, classNames, colors);

        double currentTime = cv::getTickCount();
        double fps = cv::getTickFrequency() / (currentTime - prevTime);
        prevTime = currentTime;
        cv::putText(frame, cv::format("FPS: %.1f", fps), cv::Point(15, 35),
                    cv::FONT_HERSHEY_SIMPLEX, 0.8, cv::Scalar(0, 255, 0), 2);

        cv::imshow("Sign Detection - OpenCV DNN (YOLOv8)", frame);
        char key = (char)cv::waitKey(1);
        if (key == 'q' || key == 'Q' || key == 27) {
            std::cout << "Exiting sign detection..." << std::endl;
            break;
        }
    }

    cap.release();
    cv::destroyAllWindows();
    return 0;
}
