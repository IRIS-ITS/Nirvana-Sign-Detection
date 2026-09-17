CXX = g++
CXXFLAGS = -std=c++17 $(shell pkg-config --cflags opencv4)
LIBS = $(shell pkg-config --libs opencv4)

TARGETS = camera take_u_turn take_stop take_turn_left take_turn_right take_background detect

all: $(TARGETS)

camera: scripts/camera.cpp
	$(CXX) $(CXXFLAGS) scripts/camera.cpp -o camera $(LIBS)

take_u_turn: scripts/take_u_turn.cpp
	$(CXX) $(CXXFLAGS) scripts/take_u_turn.cpp -o take_u_turn $(LIBS)

take_stop: scripts/take_stop.cpp
	$(CXX) $(CXXFLAGS) scripts/take_stop.cpp -o take_stop $(LIBS)

take_turn_left: scripts/take_turn_left.cpp
	$(CXX) $(CXXFLAGS) scripts/take_turn_left.cpp -o take_turn_left $(LIBS)

take_turn_right: scripts/take_turn_right.cpp
	$(CXX) $(CXXFLAGS) scripts/take_turn_right.cpp -o take_turn_right $(LIBS)

take_background: scripts/take_background.cpp
	$(CXX) $(CXXFLAGS) scripts/take_background.cpp -o take_background $(LIBS)

detect: scripts/detect.cpp
	$(CXX) $(CXXFLAGS) scripts/detect.cpp -o detect $(LIBS)

clean:
	rm -f $(TARGETS)

.PHONY: all clean
