from os import listdir
import pygame
import sys
import time
import random

# Initialize Pygame
pygame.init()

# Set the dimensions of the window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

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

# Main function to run the experiment
def main():
    img_paths = ["images/"+name for name in listdir("./images/")]
    random.shuffle(img_paths)  # Shuffle the order of images

    images = []
    for image_path in img_paths:
        images.append(pygame.image.load(image_path))
        
    
    for img in images:
        screen.blit(img, (0, 0))
        pygame.display.flip()
        pygame.time.wait(2000)

        display_blank()
        start_time = time.time()

        # Wait for a response from the player
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    end_time = time.time()  # Record the end time
                    reaction_time = end_time - start_time  # Calculate the reaction time
                    print("Reaction time:", reaction_time)
                    break
            else:
                continue
            break

# Run the main function
if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()

