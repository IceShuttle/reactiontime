from os import listdir
import threading
import socket
import datetime
import websocket
import csv
import pygame
import sys
import time
import random

from pygame.math import clamp
from pylsl import StreamInfo, StreamOutlet,cf_string

import datetime
import math

def calculate_bytes_per_second(data_size, elapsed_time):
    bytes_per_second = data_size / elapsed_time
    return bytes_per_second

def calculate_samples_per_second(sample_size, elapsed_time):
    samples_per_second = sample_size / elapsed_time
    return samples_per_second



lock = threading.Lock()


info = StreamInfo(name='pygame', type='Markers', channel_count=8,
                  channel_format=cf_string, source_id='uid007')
ws = websocket.WebSocket()
ws.connect("ws://"+socket.gethostbyname("oric.local")+":81")
# Initialize the stream.
outlet = StreamOutlet(info)
name = input("Participant name: ")
end = False

dat = []

# Initialize Pygame
pygame.init()

# Set the dimensions of the window
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 800

# Set the colors
WHITE = (255, 255, 255)

# Set the display surface
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Reaction Time Test")

# Define a function to display images
def display_image(image_path):
    image = pygame.image.load(image_path)
    screen.blit(image, (0, 0))
    pygame.display.flip()

# Define a function to display a blank screen
def display_blank():
    screen.fill(WHITE)
    pygame.display.flip()

def save_data(file_path):
    with open(file_path,'w') as f:
        writer = csv.writer(f) 
        writer.writerows(dat)

def wait_for_mouse(cross_x, cross_y,time_limit):
    start = time.time()
    pressed = False
    while time.time()-start<time_limit and not pressed:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousex,mousey = pygame.mouse.get_pos()
                rad = 200
                if abs(mousex-cross_x)<rad and abs(mousey-cross_y)<rad:
                    pressed=True




# Main function to run the experiment
def main():
    img_paths = ["images/"+name for name in listdir("./images/")]
    # img_paths = img_paths[:2]
    cross = pygame.image.load("crosshair.png")
    random.shuffle(img_paths)  # Shuffle the order of images

    images = []
    for image_path in img_paths:
        images.append(pygame.image.load(image_path))
        
    
    START = time.time()
    for i,img in enumerate(images):
        cross_x = int(clamp(WINDOW_WIDTH*random.random(),WINDOW_WIDTH*.2,WINDOW_WIDTH*.8))
        cross_y = int(clamp(WINDOW_HEIGHT*random.random(),WINDOW_HEIGHT*.2,WINDOW_HEIGHT*.8))
        screen.fill(WHITE)
        screen.blit(cross,(cross_x,cross_y))
        pygame.display.flip()

        wait_for_mouse(cross_x,cross_y,2)

        screen.fill(WHITE)
        screen.blit(cross,(WINDOW_WIDTH/2-127, WINDOW_HEIGHT/2-127))
        pygame.display.flip()

        wait_for_mouse(WINDOW_WIDTH/2, WINDOW_HEIGHT/2,4)

        screen.fill(WHITE)
        size = img.get_rect().size
        screen.blit(img, (WINDOW_WIDTH/2-size[0]/2, WINDOW_HEIGHT/2-size[1]/2))
        pygame.display.flip()
        img_name = img_paths[i].removeprefix("images/")
        # outlet.push_sample(["start "+img_name for _ in range(8)])
        # dat.append([("start "+img_name,time.time()-START) for i in range(8)])
        with lock:
            dat.append(["start "+img_name for i in range(8)])
        time.sleep(5)
        # outlet.push_sample(["end "+img_name for _ in range(8)])
        # dat.append([("end "+img_name,time.time()-START) for i in range(8)])
        with lock:
            dat.append(["end "+img_name for i in range(8)])

    save_data(f"{name}.csv")
    ws.close()
    pygame.quit()
    sys.exit()

def eeg():
    data_size = 0
    sample_size = 0
    start_time = time.time()
    blockSize = 32
    previousSampleNumber = -1
    previousTimeStamp = -1
    previousData = []

    while(1):
        # dat.append([0 for i in range(8)])
        # time.sleep(0.2)

        try:
            data = ws.recv()
        except:
            print("Experiment Completed!")
            return
        data_size += len(data)

        current_time = time.time()
        elapsed_time = current_time - start_time

        # if elapsed_time >= 1.0:
        #     bytes_per_second = calculate_bytes_per_second(data_size, elapsed_time)
        #     print(f"Bytes per second: {bytes_per_second} BPS")
        #     data_size = 0  # Reset data size
        #     start_time = current_time

        if elapsed_time >= 10.00:
            samples_per_second = calculate_samples_per_second(sample_size, elapsed_time)
            # Get the current local time
            local_time = datetime.datetime.now()

            # Extract hours, minutes, and seconds
            hours = local_time.hour
            minutes = local_time.minute
            seconds = local_time.second

            print(f"Local Time: {hours:02d}:{minutes:02d}:{seconds:02d} Samples per second: {math.ceil(samples_per_second)} SPS")
            sample_size = 0  # Reset data size
            start_time = current_time

        if data and (type(data) is list or type(data) is bytes):
            # print("Packet size: ", len(data), "Bytes")
            for blockLocation in range(0, len(data), blockSize):
                sample_size += 1
                block = data[blockLocation:blockLocation + blockSize]
                # data_hex = ":".join("{:02x}".format(c) for c in data)
                timestamp = int.from_bytes(block[0:4], byteorder='little')
                sample_number = int.from_bytes(block[4:8], byteorder='little')
                channel_data = []
                for channel in range(0, 8):
                    channel_offset = 8 + (channel * 3)
                    sample = int.from_bytes(block[channel_offset:channel_offset + 3], byteorder='big', signed=True)
                    channel_data.append(sample)

                if previousSampleNumber == -1:
                    previousSampleNumber = sample_number
                    previousTimeStamp = timestamp
                    previousData = channel_data
                else:
                    if sample_number - previousSampleNumber > 1:
                        print("Sample Lost")
                        exit()
                    elif sample_number == previousSampleNumber:
                        print("Duplicate sample")
                        exit()
                    else:
                        # print(timestamp - previousTimeStamp)
                        previousTimeStamp = timestamp
                        previousSampleNumber = sample_number
                        previousData = channel_data

                # outlet.push_sample(channel_data)

                if(all(v == 0 for v in channel_data[:3]) and all(v > 0 for v in channel_data[4:])):
                    print("Blank Data: ",timestamp, sample_number, channel_data[0], channel_data[1], channel_data[2], channel_data[3], channel_data[4], channel_data[5], channel_data[6], channel_data[7])
                    exit()
                else:
                    print("EEG Data: ",timestamp, sample_number, channel_data[0], channel_data[1], channel_data[2], channel_data[3], channel_data[4], channel_data[5], channel_data[6], channel_data[7])
                    dat.append([channel_data[0], channel_data[1], channel_data[2], channel_data[3], channel_data[4], channel_data[5], channel_data[6], channel_data[7]])
        #             # outlet.push_sample(channel_data)



# Run the main function
if __name__ == "__main__":
    e = threading.Thread(target=eeg)
    e.start()
    main()

