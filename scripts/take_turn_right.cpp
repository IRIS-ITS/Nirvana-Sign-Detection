#include <iostream>
#include <string>
#include <filesystem>
#include <opencv2/opencv.hpp>

namespace fs = std::filesystem;

int main() {
    const std::string className = "turn_right";
    const std::string saveDir = "result/raw/" + className;
    int cameraID = 2; // Ganti indeks kamera di sini jika perlu (cth: 0, 1, 2)

    try {
        fs::create_directories(saveDir);
    } catch (const std::exception& e) {
        std::cerr << "Failed to create directory: " << e.what() << std::endl;
        return -1;
    }

    int imgIndex = 1;
    while (fs::exists(saveDir + "/" + className + std::to_string(imgIndex) + ".jpg")) {
        imgIndex++;
    }

    cv::VideoCapture cap(cameraID);
    if (!cap.isOpened()) {
        std::cerr << "Error: Cannot open camera " << cameraID << std::endl;
        return -1;
    }

    cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap.set(cv::CAP_PROP_FRAME_HEIGHT, 480);

    std::cout << "Class: TURN RIGHT | Path: " << saveDir << std::endl;
    std::cout << "'s': save | 'SPACE': auto-record | 'q': quit" << std::endl;

    cv::Mat frame;
    bool isAutoRecording = false;
    std::string statusText = "";
    int statusTimer = 0;
    int sessionSaved = 0;

    while (true) {
        cap >> frame;
        if (frame.empty()) break;

        if (frame.cols != 640 || frame.rows != 480) {
            cv::resize(frame, frame, cv::Size(640, 480));
        }

        cv::Mat displayFrame = frame.clone();

        cv::putText(displayFrame, "Class: TURN RIGHT (640x480)", cv::Point(15, 30),
                    cv::FONT_HERSHEY_SIMPLEX, 0.65, cv::Scalar(255, 255, 255), 2);
        cv::putText(displayFrame, "'s': Save | 'SPACE': Auto REC | 'q': Quit", cv::Point(15, 55),
                    cv::FONT_HERSHEY_SIMPLEX, 0.55, cv::Scalar(0, 255, 255), 1);

        if (isAutoRecording) {
            std::string filename = saveDir + "/" + className + std::to_string(imgIndex) + ".jpg";
            if (cv::imwrite(filename, frame)) {
                imgIndex++;
                sessionSaved++;
            }
            cv::circle(displayFrame, cv::Point(610, 30), 8, cv::Scalar(0, 0, 255), -1);
            cv::putText(displayFrame, "REC (" + std::to_string(sessionSaved) + ")", cv::Point(510, 35),
                        cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(0, 0, 255), 2);
        } else if (statusTimer > 0) {
            cv::putText(displayFrame, statusText, cv::Point(15, 85),
                        cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(0, 255, 0), 2);
            statusTimer--;
        }

        cv::imshow("Capture - TURN RIGHT", displayFrame);

        int key = cv::waitKey(30);
        if (key == 's' || key == 'S') {
            std::string filename = saveDir + "/" + className + std::to_string(imgIndex) + ".jpg";
            if (cv::imwrite(filename, frame)) {
                std::cout << "Saved " << filename << std::endl;
                statusText = "Saved: " + className + std::to_string(imgIndex) + ".jpg";
                imgIndex++;
            } else {
                std::cerr << "Failed to save " << filename << std::endl;
                statusText = "Save failed";
            }
            statusTimer = 30;
        } else if (key == 32) {
            isAutoRecording = !isAutoRecording;
            if (isAutoRecording) {
                sessionSaved = 0;
                std::cout << "Auto-recording started..." << std::endl;
            } else {
                std::cout << "Auto-recording stopped. Saved " << sessionSaved << " images." << std::endl;
                statusText = "REC Stopped (" + std::to_string(sessionSaved) + " saved)";
                statusTimer = 45;
            }
        } else if (key == 'q' || key == 'Q' || key == 27) {
            break;
        }
    }

    cap.release();
    cv::destroyAllWindows();
    return 0;
}
