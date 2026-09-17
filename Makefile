CXX = g++
CXXFLAGS = -std=c++17 $(shell pkg-config --cflags opencv4)
LIBS = $(shell pkg-config --libs opencv4)

TARGET = camera
SRC = camera.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET) $(LIBS)

clean:
	rm -f $(TARGET)

.PHONY: all clean
