#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

struct Detection {
    int class_id;
    float confidence;
    cv::Rect box;
};

int main() {
    int cameraID = 2;
    std::vector<std::string> classNames = {"u_turn", "stop", "turn_left", "turn_right"};
    std::vector<cv::Scalar> colors = {
        cv::Scalar(255, 255, 0),   // u_turn: Cyan
        cv::Scalar(0, 0, 255),     // stop: Red
        cv::Scalar(0, 255, 255),   // turn_left: Yellow
        cv::Scalar(0, 255, 0)      // turn_right: Green
    };

    std::string modelPath = "models/best.onnx";
    cv::dnn::Net net = cv::dnn::readNetFromONNX(modelPath);
    if (net.empty()) {
        modelPath = "best.onnx";
        net = cv::dnn::readNetFromONNX(modelPath);
    }

    if (net.empty()) {
        std::cerr << "Error: Could not load ONNX model from models/best.onnx or best.onnx" << std::endl;
        std::cerr << "Please ensure best.onnx is downloaded and placed in models/ or the project root." << std::endl;
        return -1;
    }

    net.setPreferableBackend(cv::dnn::DNN_BACKEND_OPENCV);
    net.setPreferableTarget(cv::dnn::DNN_TARGET_CPU);
    std::cout << "Successfully loaded ONNX model: " << modelPath << std::endl;

    cv::VideoCapture cap(cameraID);
    if (!cap.isOpened()) {
        std::cerr << "Error: Could not open camera with ID: " << cameraID << std::endl;
        return -1;
    }

    cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480);
    std::cout << "Camera initialized on ID " << cameraID << "." << std::endl;
    std::cout << "Controls:" << std::endl;
    std::cout << "  '+' / '=' : Increase bounding box scale" << std::endl;
    std::cout << "  '-' / '_' : Decrease bounding box scale" << std::endl;
    std::cout << "  'q' / ESC : Exit program" << std::endl;

    cv::Mat frame;
    float confThreshold = 0.65f;
    float nmsThreshold = 0.45f;
    float boxScale = 0.50f; // Scale factor for tight bounding box display (default 50%)

    double prevTime = cv::getTickCount();

    while (true) {
        cap >> frame;
        if (frame.empty()) {
            std::cerr << "Error: Captured empty frame." << std::endl;
            break;
        }

        int frameW = frame.cols;
        int frameH = frame.rows;

        // Preprocess frame for YOLOv8 (640x640 input blob)
        cv::Mat blob;
        cv::dnn::blobFromImage(frame, blob, 1.0 / 255.0, cv::Size(640, 640), cv::Scalar(), true, false);
        net.setInput(blob);

        // Forward pass
        cv::Mat rawOutput = net.forward();

        // Parse YOLOv8 ONNX output tensor (shape [1, 8, 8400])
        int channels = 8;
        int numAnchors = 8400;
        if (rawOutput.dims == 3) {
            channels = rawOutput.size[1];
            numAnchors = rawOutput.size[2];
        }

        // Construct 2D Mat [channels, numAnchors] directly from raw float pointer
        cv::Mat output2D(channels, numAnchors, CV_32F, (float*)rawOutput.data);
        cv::Mat outMat;
        cv::transpose(output2D, outMat); // Shape [8400, 8]

        std::vector<int> classIds;
        std::vector<float> confidences;
        std::vector<cv::Rect> boxes;

        float scaleX = (float)frameW / 640.0f;
        float scaleY = (float)frameH / 640.0f;

        for (int i = 0; i < outMat.rows; ++i) {
            float* row = outMat.ptr<float>(i);
            float cx = row[0];
            float cy = row[1];
            float w = row[2];
            float h = row[3];

            // Extract class probabilities (indices 4 to 7)
            float maxScore = 0.0f;
            int maxClassId = -1;
            for (int c = 0; c < 4; ++c) {
                float score = row[4 + c];
                if (score > maxScore) {
                    maxScore = score;
                    maxClassId = c;
                }
            }

            if (maxScore >= confThreshold) {
                // Apply visual boxScale multiplier to tightly fit bounding box
                float scaledW = w * boxScale;
                float scaledH = h * boxScale;

                int left = static_cast<int>((cx - 0.5f * scaledW) * scaleX);
                int top = static_cast<int>((cy - 0.5f * scaledH) * scaleY);
                int width = static_cast<int>(scaledW * scaleX);
                int height = static_cast<int>(scaledH * scaleY);

                // Boundary check
                left = std::max(0, std::min(left, frameW - 1));
                top = std::max(0, std::min(top, frameH - 1));
                width = std::max(1, std::min(width, frameW - left));
                height = std::max(1, std::min(height, frameH - top));

                boxes.push_back(cv::Rect(left, top, width, height));
                confidences.push_back(maxScore);
                classIds.push_back(maxClassId);
            }
        }

        // Non-Maximum Suppression (NMS)
        std::vector<int> indices;
        cv::dnn::NMSBoxes(boxes, confidences, confThreshold, nmsThreshold, indices);

        // Draw bounding boxes and labels
        for (int idx : indices) {
            cv::Rect box = boxes[idx];
            int classId = classIds[idx];
            float conf = confidences[idx];

            cv::Scalar color = colors[classId % colors.size()];
            std::string labelName = (classId < classNames.size()) ? classNames[classId] : "unknown";
            std::string labelText = labelName + " " + cv::format("%.2f", conf);

            cv::rectangle(frame, box, color, 2);

            int baseLine;
            cv::Size labelSize = cv::getTextSize(labelText, cv::FONT_HERSHEY_SIMPLEX, 0.6, 2, &baseLine);
            int labelTop = std::max(box.y, labelSize.height + 5);

            cv::rectangle(frame,
                          cv::Point(box.x, labelTop - labelSize.height - 5),
                          cv::Point(box.x + labelSize.width + 5, labelTop + baseLine),
                          color, cv::FILLED);

            cv::putText(frame, labelText,
                        cv::Point(box.x + 2, labelTop - 2),
                        cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(0, 0, 0), 2);
        }

        // Calculate and display FPS and Box Scale
        double currentTime = cv::getTickCount();
        double fps = cv::getTickFrequency() / (currentTime - prevTime);
        prevTime = currentTime;

        std::string overlayText = cv::format("FPS: %.1f | Box Scale: %.2fx (+/-)", fps, boxScale);
        cv::putText(frame, overlayText, cv::Point(15, 35),
                    cv::FONT_HERSHEY_SIMPLEX, 0.7, cv::Scalar(0, 255, 0), 2);

        cv::imshow("Sign Detection - OpenCV DNN (YOLOv8)", frame);

        char key = (char)cv::waitKey(1);
        if (key == 'q' || key == 'Q' || key == 27) { // 27 = ESC
            std::cout << "Exiting sign detection..." << std::endl;
            break;
        } else if (key == '+' || key == '=') {
            boxScale = std::min(1.50f, boxScale + 0.05f);
            std::cout << "Increased Box Scale to: " << cv::format("%.2f", boxScale) << std::endl;
        } else if (key == '-' || key == '_') {
            boxScale = std::max(0.15f, boxScale - 0.05f);
            std::cout << "Decreased Box Scale to: " << cv::format("%.2f", boxScale) << std::endl;
        }
    }

    cap.release();
    cv::destroyAllWindows();
    return 0;
}
