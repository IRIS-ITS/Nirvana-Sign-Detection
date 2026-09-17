#include <iostream>
#include <string>
#include <filesystem>
#include <opencv2/opencv.hpp>

namespace fs = std::filesystem;

int main() {
    // Output directory path
    std::string saveDir = "example";
    
    // Automatically create directory example if it doesn't exist
    try {
        fs::create_directories(saveDir);
    } catch (const std::exception& e) {
        std::cerr << "Error creating directory: " << e.what() << std::endl;
        return -1;
    }

    // Determine starting file index (e.g., example1.jpg, example2.jpg, ...)
    int imgIndex = 1;
    while (fs::exists(saveDir + "/example" + std::to_string(imgIndex) + ".jpg")) {
        imgIndex++;
    }

    // change cap by 0,1 or 2 based on webcam index, if you have multiple cameras connected to your computer
    cv::VideoCapture cap(2);
    if (!cap.isOpened()) {
        std::cerr << "Error: Could not open camera (index 0). Please check camera connection." << std::endl;
        return -1;
    }

    // Set resolution to 640x480
    cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480);

    std::cout << " Save directory : " << saveDir << std::endl;
    std::cout << " Next image file: example" << imgIndex << ".jpg" << std::endl;
    std::cout << " Controls:" << std::endl;
    std::cout << "   - Press 's' : Save image (640x480)" << std::endl;
    std::cout << "   - Press 'q' : Quit program" << std::endl;

    cv::Mat frame;
    std::string statusText = "";
    int statusTimer = 0;

    while (true) {
        cap >> frame;
        if (frame.empty()) {
            std::cerr << "Error: Blank frame grabbed!" << std::endl;
            break;
        }

        // Force image resolution to 640x480 if hardware returns a different resolution
        if (frame.cols != 640 || frame.rows != 480) {
            cv::resize(frame, frame, cv::Size(640, 480));
        }

        // Clone frame for UI overlay display so saved raw frame stays clean
        cv::Mat displayFrame = frame.clone();

        // Overlay camera information and key bindings
        cv::putText(displayFrame, "Size: 640x480 | 's': Save | 'q': Exit", 
                    cv::Point(15, 30), cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(0, 255, 255), 2);

        // Show save notification on frame for ~1 second (30 frames)
        if (statusTimer > 0) {
            cv::putText(displayFrame, statusText, cv::Point(15, 65),
                        cv::FONT_HERSHEY_SIMPLEX, 0.65, cv::Scalar(0, 255, 0), 2);
            statusTimer--;
        }

        cv::imshow("Sign Capture - 640x480", displayFrame);

        int key = cv::waitKey(30);
        if (key == 's' || key == 'S') {
            std::string filename = saveDir + "/example" + std::to_string(imgIndex) + ".jpg";
            
            // Save clean original frame (without UI text)
            bool success = cv::imwrite(filename, frame);
            if (success) {
                std::cout << "[SAVED] " << filename << std::endl;
                statusText = "Saved: example" + std::to_string(imgIndex) + ".jpg";
                imgIndex++;
            } else {
                std::cerr << "[ERROR] Failed to save " << filename << std::endl;
                statusText = "ERROR: Failed to save frame!";
            }
            statusTimer = 30;
        } else if (key == 'q' || key == 'Q' || key == 27) { // 27 = ESC
            std::cout << "Exiting program..." << std::endl;
            break;
        }
    }

    cap.release();
    cv::destroyAllWindows();
    return 0;
}
