from os import listdir, times
import csv
import pygame
import sys
import time
import random

#Data Collection Initialize
data = []

# Initialize Pygame
pygame.init()

# Set the dimensions of the window
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

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
        cross_x = WINDOW_WIDTH*random.random()*.8
        cross_y = WINDOW_HEIGHT*random.random()*.8
        screen.fill(WHITE)
        screen.blit(cross,(cross_x,cross_y))
        pygame.display.flip()
        start = time.time()
        pressed = False
        while time.time()-start<2 and not pressed:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mousex,mousey = pygame.mouse.get_pos()
                    rad = 100
                    if abs(mousex-cross_x)<rad and abs(mousey-cross_y)<rad:
                        pressed=True
                        screen.fill(WHITE)
                        screen.blit(cross,(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
                        pygame.display.flip()
        time.sleep(2)
        screen.fill(WHITE)
        screen.blit(img, (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        # screen.blit(img, (0,0))
        pygame.display.flip()
        data.append(("DispStart",time.time()-START))
        time.sleep(3)
        data.append(("Dispend",time.time()-START))
    save_data("reaction.csv")



# Run the main function
if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()

