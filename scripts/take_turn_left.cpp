#include <iostream>
#include <string>
#include <filesystem>
#include <opencv2/opencv.hpp>

namespace fs = std::filesystem;

int main() {
    const std::string className = "turn_left";
    const std::string saveDir = "result/" + className;
    
    // Automatically create output directory result/turn_left if it doesn't exist
    try {
        fs::create_directories(saveDir);
    } catch (const std::exception& e) {
        std::cerr << "Error creating directory: " << e.what() << std::endl;
        return -1;
    }

    // Determine starting file index (turn_left1.jpg, turn_left2.jpg, ...)
    int imgIndex = 1;
    while (fs::exists(saveDir + "/" + className + std::to_string(imgIndex) + ".jpg")) {
        imgIndex++;
    }

    // Open camera (tries camera 0, fallback to 2 and 1)
    cv::VideoCapture cap(0);
    if (!cap.isOpened()) cap.open(2);
    if (!cap.isOpened()) cap.open(1);
    if (!cap.isOpened()) {
        std::cerr << "Error: Could not open any camera (tried index 0, 2, 1)." << std::endl;
        return -1;
    }

    // Set resolution to 640x480
    cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480);

    std::cout << "==========================================" << std::endl;
    std::cout << "  Capture Dataset: TURN LEFT              " << std::endl;
    std::cout << "==========================================" << std::endl;
    std::cout << " Target Directory : " << saveDir << std::endl;
    std::cout << " Next Image File  : " << className << imgIndex << ".jpg" << std::endl;
    std::cout << " Controls:" << std::endl;
    std::cout << "   - Press 's'     : Save single frame" << std::endl;
    std::cout << "   - Press 'SPACE' : Toggle Auto FPS Recording (REC)" << std::endl;
    std::cout << "   - Press 'q'     : Quit program" << std::endl;
    std::cout << "==========================================" << std::endl;

    cv::Mat frame;
    bool isAutoRecording = false;
    std::string statusText = "";
    int statusTimer = 0;
    int savedCountSession = 0;

    while (true) {
        cap >> frame;
        if (frame.empty()) {
            std::cerr << "Error: Blank frame captured!" << std::endl;
            break;
        }

        // Force resolution to 640x480
        if (frame.cols != 640 || frame.rows != 480) {
            cv::resize(frame, frame, cv::Size(640, 480));
        }

        // Clone frame for UI overlay display so saved raw frames remain clean
        cv::Mat displayFrame = frame.clone();

        // Draw HUD UI
        cv::putText(displayFrame, "Class: TURN LEFT (640x480)", cv::Point(15, 30),
                    cv::FONT_HERSHEY_SIMPLEX, 0.65, cv::Scalar(255, 255, 255), 2);
        
        cv::putText(displayFrame, "'s': Save | 'SPACE': Auto REC | 'q': Exit", cv::Point(15, 55),
                    cv::FONT_HERSHEY_SIMPLEX, 0.55, cv::Scalar(0, 255, 255), 1);

        // Auto Recording Logic
        if (isAutoRecording) {
            std::string filename = saveDir + "/" + className + std::to_string(imgIndex) + ".jpg";
            if (cv::imwrite(filename, frame)) {
                imgIndex++;
                savedCountSession++;
            }
            // Draw REC status indicator on camera view
            cv::circle(displayFrame, cv::Point(610, 30), 10, cv::Scalar(0, 0, 255), -1);
            cv::putText(displayFrame, "REC (" + std::to_string(savedCountSession) + ")", cv::Point(510, 35),
                        cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(0, 0, 255), 2);
        } else if (statusTimer > 0) {
            cv::putText(displayFrame, statusText, cv::Point(15, 85),
                        cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(0, 255, 0), 2);
            statusTimer--;
        }

        cv::imshow("Dataset Capture - TURN LEFT", displayFrame);

        int key = cv::waitKey(30);
        if (key == 's' || key == 'S') {
            std::string filename = saveDir + "/" + className + std::to_string(imgIndex) + ".jpg";
            if (cv::imwrite(filename, frame)) {
                std::cout << "[SAVED] " << filename << std::endl;
                statusText = "Saved: " + className + std::to_string(imgIndex) + ".jpg";
                imgIndex++;
            } else {
                std::cerr << "[ERROR] Failed to save " << filename << std::endl;
                statusText = "ERROR: Save failed!";
            }
            statusTimer = 30;
        } else if (key == 32) { // SPACE key
            isAutoRecording = !isAutoRecording;
            if (isAutoRecording) {
                savedCountSession = 0;
                std::cout << "[AUTO REC] Started recording TURN LEFT frames..." << std::endl;
            } else {
                std::cout << "[AUTO REC] Stopped recording. Saved " << savedCountSession << " images." << std::endl;
                statusText = "Auto REC Stopped (" + std::to_string(savedCountSession) + " saved)";
                statusTimer = 45;
            }
        } else if (key == 'q' || key == 'Q' || key == 27) { // 27 = ESC
            std::cout << "Exiting TURN LEFT capture program..." << std::endl;
            break;
        }
    }

    cap.release();
    cv::destroyAllWindows();
    return 0;
}
