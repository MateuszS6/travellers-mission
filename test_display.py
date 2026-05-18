import os

os.environ["SDL_VIDEODRIVER"] = "x11"
os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
os.environ["MESA_LOADER_DRIVER_OVERRIDE"] = "llvmpipe"

import pygame

pygame.init()
screen = pygame.display.set_mode((500, 400))
pygame.display.set_caption("Display Test")

running = True
while running:
    screen.fill((255, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()