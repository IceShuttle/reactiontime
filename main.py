from os import listdir, times
import csv
import pygame
import sys
import time
import random

from pygame.math import clamp

#Data Collection Initialize
data = []

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
        writer.writerow(("Name","Time(s)"))
        writer.writerows(data)

def wait_for_mouse(cross, cross_x, cross_y,time_limit):
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
    cross = pygame.image.load("cross.png")
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

        wait_for_mouse(cross,cross_x,cross_y,2)

        screen.fill(WHITE)
        screen.blit(cross,(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        pygame.display.flip()

        wait_for_mouse(cross,WINDOW_WIDTH/2, WINDOW_HEIGHT/2,4)

        screen.fill(WHITE)
        size = img.get_rect().size
        screen.blit(img, (WINDOW_WIDTH/2-size[0]/2, WINDOW_HEIGHT/2-size[1]/2))
        pygame.display.flip()
        img_name = img_paths[i].removeprefix("images/")
        data.append(("Start "+img_name,time.time()-START))
        time.sleep(3)
        data.append(("End "+img_name,time.time()-START))
    save_data("reaction.csv")



# Run the main function
if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()

