import pygame

debug = True

def dprint(debug, print_message):
    if debug:
        print(print_message)


def alt_rotate(image, pos, origin_pos, angle):
    # offset from pivot to center
    image_rect = image.get_rect(topleft=(pos[0] - origin_pos[0], pos[1] - origin_pos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    # rotated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

    return rotated_image, rotated_image_rect


class World:
    def __init__(self, time_step_size, air_density, gravity, FPS):
        self.time_step_size = time_step_size
        self.air_density = air_density
        self.gravity = gravity
        self.FPS = FPS


# Much knowledge from https://asawicki.info/Mirror/Car%20Physics%20for%20Games/Car%20Physics%20for%20Games.html
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, position, mass, car_type, car_actual_length, window, world):
        pygame.sprite.Sprite.__init__(self)

        self.window = window
        self.world = world

        # image management
        self.scale = 0.1 # TODO: Fix scaling of turning to be more fun
        self.position = pygame.math.Vector2(position)
        self.image_clean = pygame.image.load(f'assets/image/car_{car_type}.png').convert_alpha()
        self.original_size = max(self.image_clean.get_width(), self.image_clean.get_height())  # get length of car (make sure it is loaded either along x or y axis)
        # TODO: make sure the initial vehicle length acquisition loads the image in such that an accurate length can be measured
        self.aspect_ratio = self.image_clean.get_width() / self.image_clean.get_height()
        self.image_clean = pygame.transform.scale(self.image_clean,
                                                  (int(self.original_size * self.scale * self.aspect_ratio),
                                                   int(self.original_size * self.scale)))  # (width, height)
        self.clean_rect = self.image_clean.get_rect(center=self.position)
        self.image = self.image_clean
        self.rect = self.image.get_rect(center=self.position)

        # controls
        self.accelerating = False
        self.throttle = 0
        self.throttle_lag_time = 1  # in seconds
        self.engine_unthrottle_time = 0.5  # in seconds
        self.braking = False
        self.brake_percent = 0
        self.turning_left = False
        self.turning_right = False

        # parameters
        self.real_length = car_actual_length  # In meters. We use this to determine the pixels per meter scaling for the world
        self.length = self.original_size * self.scale  # length in pixels
        dprint(debug, f'Car pixel length.: {self.length}')
        self.scale_adjustment = self.length / self.real_length  # gives result in pixels per meter
        dprint(debug, f'Scale adj.: {self.scale_adjustment}')
        self.position = pygame.math.Vector2(position)  # [x, y] in meters from origin
        self.velocity = pygame.math.Vector2(0, 0)  # m^s
        self.acceleration = pygame.math.Vector2(0, 0)  # m/s^2
        self.speed = 0
        self.mass = mass  # kg
        self.engine_force = 0  # N*m
        self.engine_force_max = 650  # N * m
        self.orientation = pygame.math.Vector2(0, 1)  # direction vector u

        # air drag
        self.drag_coefficient = 0.3  # C_d (from corvette example)
        self.front_area = 2.2  # m^2 # TODO: implement complex drag

        # rolling resistance
        self.rolling_resistance_coefficient = 0.03  # approximation from paper. Added a bit since they only estimate wheel resistance: https://www.matec-conferences.org/articles/matecconf/pdf/2019/03/matecconf_mms18_01005.pdf

        # forces (all N * m)
        self.force_traction = pygame.math.Vector2(0, 0)
        self.force_drag = pygame.math.Vector2(0, 0)
        self.force_rolling_resistance = pygame.math.Vector2(0, 0)

        # self.lateral_force
        # TODO: later

    def update(self):
        # Translate controls into engine force
        if self.accelerating and self.throttle < 1:
            self.throttle += 1/(self.throttle_lag_time * self.world.FPS)
        else:
            if self.throttle != 0 and self.throttle - 0.1 > 0:
                self.throttle -= 0.1  # self.throttle / (self.engine_unthrottle_time * self.world.FPS)  # TODO: fix this (takes way longer than expected, zeno paradox issue)

        self.calculate_position()
        self.draw()

    def calculate_position(self):
        self.speed = self.velocity.magnitude()
        # dprint(debug, f'Speed: {self.speed}')
        self.force_traction = self.orientation * self.engine_force_max * self.throttle
        # dprint(debug, f'Traction force: {self.force_traction}')
        self.force_drag = -self.drag_coefficient * self.velocity * self.speed
        # dprint(debug, f'Drag force: {self.force_drag}')
        self.force_rolling_resistance = -self.rolling_resistance_coefficient * self.velocity
        # dprint(debug, f'Rolling Resistance force: {self.force_rolling_resistance}')

        # calculate changes in vehicle position (euler method numerical integration)
        # TODO: upgrade to Runge-Kutta integration
        total_force: pygame.math.Vector2 = self.force_traction + self.force_drag + self.force_rolling_resistance
        # dprint(debug, f'Total force: {total_force}')
        self.acceleration = total_force / self.mass
        # dprint(debug, f'Acceleration: {self.acceleration}')
        self.velocity += self.acceleration * self.world.time_step_size
        dprint(debug, f'Velocity: {self.velocity}')
        # scale adjustment converts the position we calculated in meters to the screen position in pixels
        self.position += self.velocity * self.world.time_step_size * self.scale_adjustment
        # dprint(debug, f'Position: {self.position}')

    def draw(self):
        self.rect.center = self.position
        self.window.blit(self.image, self.rect)


# TODO: add complex engine_force
# TODO: add low-speed turning
# TODO: add high-speed turning
# TODO: add weight shifting and resultant change in traction
