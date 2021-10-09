# This is a sample Python script.
import pygame
from vehicle import Vehicle
from vehicle import World

# TODO: traction
# TODO: skidding
# TODO: sound
# TODO: update braking-- space to emergency brake, s/down to reverse


pygame.init()

SCREEN_HEIGHT = 1000
SCREEN_WIDTH = 1520
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("project-rc")

clock = pygame.time.Clock()
FPS = 30
# Colors as always via https://coolors.co
GREEN = '#0FA98F'  # "Zomp" green
RED = '#DB5A42'

rho = 1.225  # air density (kg/m^3)
gravity = 9.8  # m/s^2

world = World(1/FPS, rho, gravity, FPS)
player = Vehicle([100, 100], 1527, "purple", 5.7, window, world)  # mass from Corvette C8

run = True
while run:
    clock.tick(FPS)
    window.fill(RED)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                player.turning_left = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                player.turning_right = True
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                player.accelerating = True
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                player.braking = True
            if event.key == pygame.K_SPACE:
                player.emergency_braking = True
            if event.key == pygame.K_ESCAPE:
                run = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                player.turning_left = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                player.turning_right = False
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                player.accelerating = False
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                player.braking = False

    player.update()

    # DEBUG
    # pygame.draw.line(window, [0, 0, 0], player.rect.center, (player.rect.centerx + player.dir[0],  player.rect.centery + player.dir[1]))
    # pygame.draw.line(window, [255, 0, 0], player.rect.center, (int(player.rect.centerx + math.sin(player.angle) * 2), int(player.rect.centery + math.cos(player.angle)) * 2))
    # pygame.draw.circle(window, [0,0,0], player.rect.center, 75  * player.scale, 2)

    pygame.display.update()
