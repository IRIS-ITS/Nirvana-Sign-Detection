#include <iostream>
#include <string>
#include <filesystem>
#include <opencv2/opencv.hpp>

namespace fs = std::filesystem;

int main() {
    std::string saveDir = "example";

    try {
        fs::create_directories(saveDir);
    } catch (const std::exception& e) {
        std::cerr << "Failed to create directory: " << e.what() << std::endl;
        return -1;
    }

    int imgIndex = 1;
    while (fs::exists(saveDir + "/example" + std::to_string(imgIndex) + ".jpg")) {
        imgIndex++;
    }

    cv::VideoCapture cap(0);
    if (!cap.isOpened()) cap.open(2);
    if (!cap.isOpened()) cap.open(1);
    if (!cap.isOpened()) {
        std::cerr << "Error: Camera not found." << std::endl;
        return -1;
    }

    cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480);

    std::cout << "Saving to: " << saveDir << std::endl;
    std::cout << "Press 's' to save, 'q' to quit." << std::endl;

    cv::Mat frame;
    std::string statusText = "";
    int statusTimer = 0;

    while (true) {
        cap >> frame;
        if (frame.empty()) break;

        if (frame.cols != 640 || frame.rows != 480) {
            cv::resize(frame, frame, cv::Size(640, 480));
        }

        cv::Mat displayFrame = frame.clone();
        cv::putText(displayFrame, "640x480 | 's': Save | 'q': Quit", 
                    cv::Point(15, 30), cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(0, 255, 255), 2);

        if (statusTimer > 0) {
            cv::putText(displayFrame, statusText, cv::Point(15, 65),
                        cv::FONT_HERSHEY_SIMPLEX, 0.65, cv::Scalar(0, 255, 0), 2);
            statusTimer--;
        }

        cv::imshow("Camera Capture", displayFrame);

        int key = cv::waitKey(30);
        if (key == 's' || key == 'S') {
            std::string filename = saveDir + "/example" + std::to_string(imgIndex) + ".jpg";
            if (cv::imwrite(filename, frame)) {
                std::cout << "Saved " << filename << std::endl;
                statusText = "Saved: example" + std::to_string(imgIndex) + ".jpg";
                imgIndex++;
            } else {
                std::cerr << "Failed to save " << filename << std::endl;
                statusText = "Save failed";
            }
            statusTimer = 30;
        } else if (key == 'q' || key == 'Q' || key == 27) {
            break;
        }
    }

    cap.release();
    cv::destroyAllWindows();
    return 0;
}
