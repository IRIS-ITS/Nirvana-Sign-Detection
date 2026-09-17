import os
from label_u_turn import label_u_turn
from label_stop import label_stop
from label_turn_left import label_turn_left
from label_turn_right import label_turn_right

def main():
    print("starting auto labeling pipeline...")
    label_u_turn()
    label_stop()
    label_turn_left()
    label_turn_right()
    print("auto labeling complete.")

if __name__ == "__main__":
    main()
