import pygame
import math
import tools
import random


class Tank:

    def __init__(self, x, y, width, height, turret_radius, turret_width, wheel_radius, turret_length,
                 turret_angle_relative_to_positive_x_degrees, turret_min_angle, turret_max_angle, reload_time, fps, hits_until_death):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.turret_radius = int(turret_radius)
        self.turret_width = int(turret_width)
        self.wheel_radius = int(wheel_radius)
        self.turret_length = int(turret_length)
        self.turret_angle_degrees = turret_angle_relative_to_positive_x_degrees
        self.turret_min_angle = turret_min_angle
        self.turret_max_angle = turret_max_angle
        self.reload_time = reload_time
        self.fps = fps
        self.reload_time_left = 0
        self.hits_until_death = hits_until_death
        self.current_hits = 0
        self.dead = False

    def frame_elapsed(self):
        if self.is_reloading():
            self.reload_time_left -= 1 / self.fps

    def fire(self):
        self.reload_time_left = self.reload_time

    def restore_health(self):
        self.current_hits = 0

    def was_hit(self):
        self.current_hits += 1
        if self.current_hits >= self.hits_until_death:
            self.dead = True
            self.current_hits = self.hits_until_death

    def is_dead(self):
        return self.dead

    def draw_health_bar(self, game_display, border_color, healthy_fill_color, weak_fill_color):
        bar_height = 8
        bar_border_width = 2
        bar_length = 0.8 * self.width

        bar_y = self.y - self.turret_length
        bar_x = self.x - bar_length / 2

        fill_x = bar_x + bar_border_width / 2
        fill_y = bar_y + bar_border_width / 2

        health_ratio = (self.hits_until_death - self.current_hits) / self.hits_until_death
        if health_ratio > 0.33:
            fill_color = healthy_fill_color
        else:
            fill_color = weak_fill_color

        fill_height = bar_height - bar_border_width
        fill_width = (bar_length - bar_border_width) * health_ratio

        pygame.draw.rect(game_display, border_color, [bar_x, bar_y, bar_length, bar_height], bar_border_width)
        pygame.draw.rect(game_display, fill_color, [fill_x, fill_y, fill_width, fill_height])

    def is_reloading(self):
        return self.reload_time_left > 0

    def draw_tank(self, display, color, ):
        pygame.draw.circle(display,
                           color,
                           (self.x, self.y),
                           self.turret_radius)
        pygame.draw.rect(display, color, [self.x - self.width / 2, self.y, self.width, self.height])
        pygame.draw.line(display, color, (self.x, self.y),
                         self._get_turret_end_pos(self.turret_angle_degrees),
                         self.turret_width)
        num_wheels = 8
        x0 = self.x - self.width / 2
        spacing = float(self.width - 2 * self.wheel_radius) / (num_wheels - 1)
        wheel_y = self.y + self.height + int(self.wheel_radius / 4)
        for k in range(num_wheels):
            wheel_x_k = int(x0 + k * spacing + self.wheel_radius)
            pygame.draw.circle(display, color, (wheel_x_k, wheel_y), self.wheel_radius)

    def _get_turret_end_pos(self, angle):
        radians = math.radians(angle)
        x = self.x + int(self.turret_length * math.cos(radians))
        y = self.y - int(self.turret_length * math.sin(radians))
        return x, y

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def set_reload_time(self, time_in_seconds):
        self.reload_time = time_in_seconds
        self.reload_time_left = 0

    def increment_turret_angle(self, angle_increment_degrees):
        new_angle = self.turret_angle_degrees + angle_increment_degrees
        if self._is_turret_within_angle(new_angle):
            self.turret_angle_degrees = new_angle

    def _is_turret_within_angle(self, angle):
        if self.turret_min_angle <= angle <= self.turret_max_angle:
            return True
        else:
            return False

    def get_rect(self):
        return [self.x - self.width / 2, self.y - int(self.turret_radius), self.width,
                int(self.turret_radius) + self.height]

    def get_turret_vector(self):
        radians = math.radians(self.turret_angle_degrees)
        return self.turret_length * math.cos(radians), self.turret_length * math.sin(radians)


class AITank(Tank):

    def __init__(self, x, y, width, height, turret_radius, turret_width, wheel_radius, turret_length,
                 turret_angle_relative_to_positive_x_degrees, turret_min_angle, turret_max_angle, time_between_fires,
                 fps, hits_until_death, game_difficulty):
        super(AITank, self).__init__(x, y, width, height, turret_radius, turret_width, wheel_radius, turret_length,
                                     turret_angle_relative_to_positive_x_degrees,
                                     turret_min_angle, turret_max_angle, time_between_fires, fps, hits_until_death)
        self._game_difficulty = game_difficulty
        self._last_x = x
        if game_difficulty == 0:
            self._dir_change_value = None
        elif game_difficulty == 1:
            self._dir_change_value = self.fps * 2
        elif game_difficulty == 2:
            self._dir_change_value = int(self.fps * 1.2)
        self._current_direction_counter = self._dir_change_value
        self._easy_miss_radius = 200
        self._reaction_distance = 60 * (4 ** self._game_difficulty)
        self._random_miss_radius = int(self._easy_miss_radius * (1 / (3 ** game_difficulty)))

    # does NOT call Tank's "frame_elapsed()"
    # returns a shell if fired or "None" if not
    def update(self, enemy_tank, enemy_shells, barrier_x, back_wall_x):

        distance = math.fabs(self.x - enemy_tank.x + random.randrange(-self._random_miss_radius,
                                                                      self._random_miss_radius))
        g = TankShell.gravitational_acceleration
        angle_radians = math.radians(self.turret_angle_degrees)
        initial_velocity = math.sqrt(math.fabs(distance * g / math.sin(2 * angle_radians)))
        result = self._try_fire(initial_velocity)
        self._move_tank(enemy_shells, barrier_x, back_wall_x)
        return result

    def _move_tank(self, enemy_shells, barrier_x, back_wall_x):
        #  print(str(self._current_direction_counter) + " out of " + str(self._dir_change_value))
        enemy_shell_hit_locations = []
        tank_speed = 1
        for shell in enemy_shells:
            enemy_shell_hit_locations.append(shell.get_hit_x())

        right = 0
        left = 1
        choose = 2
        movement = None

        for i in range(len(enemy_shell_hit_locations)):
            hit_x = enemy_shell_hit_locations[i]
            if tools.point_within_interval(hit_x, self.x - self.width, self.x + self.width):
                if self.distance((self.x, self.y), enemy_shells[i].get_v()) > self._reaction_distance:
                    movement = choose
                    break

                if i == 0:
                    if not self._has_room_to_move_left(barrier_x, hit_x):
                        movement = right
                        break
                    if not self._has_room_to_move_right(back_wall_x, hit_x):
                        movement = left
                        break
                    if hit_x < self.x:
                        movement = right
                        break
                    else:
                        movement = left
                        break
                else:
                    first_shell_x = enemy_shell_hit_locations[0]
                    if first_shell_x < self.x:
                        if self._has_room_to_move_right(back_wall_x, first_shell_x):
                            movement = right
                            break
                        else:
                            movement = choose
                            break
                    else:
                        if self._has_room_to_move_left(barrier_x, self.x):
                            movement = left
                            break
                        else:
                            movement = choose
                            break
        if movement is None:
            movement = choose
        x_move = 0
        self._last_x = self.x
        if movement == right:
            x_move = tank_speed
        elif movement == left:
            x_move = -tank_speed
        elif movement == choose:
            if self._dir_change_value is not None:
                if self._current_direction_counter >= self._dir_change_value:
                    x_move = tank_speed
                    if not self._has_room_to_move_right(back_wall_x, self.x):
                        x_move *= -1
                    elif not self._has_room_to_move_left(barrier_x, self.x):
                        pass
                    else:
                        if bool(random.getrandbits(1)):
                            print("bool chosen")
                            x_move *= -1

                    self._current_direction_counter = 0
            else:
                x_move = 0

        if self._current_direction_counter is not None:
            self._current_direction_counter += 1
        self.set_pos(self.x + x_move, self.y)

    def move_back(self):
        self.set_pos(self._last_x, self.y)

    def _has_room_to_move_left(self, barrier_x, hit_x):
        return hit_x - barrier_x > self.width

    def _has_room_to_move_right(self, wall_x, hit_x):
        return wall_x - hit_x > self.width

    @staticmethod
    def distance(p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def _try_fire(self, initial_velocity):
        if not self.is_reloading():
            self.fire()
            return TankShell(self, initial_velocity, self.fps)
        else:
            return None


class TankShell:

    gravitational_acceleration = 500

    @staticmethod
    def vector_length(vector):
        return math.sqrt(vector[0] * vector[0] + vector[1] * vector[1])

    @staticmethod
    def vector_scale(vector, scale):
        return vector[0] * scale, vector[1] * scale

    def __init__(self, tank, initial_velocity, frames_per_second):
        turret_vector = tank.get_turret_vector()
        unit_turret_vector = self.vector_scale(turret_vector, 1 / self.vector_length(turret_vector))
        self.__v0 = self.vector_scale(unit_turret_vector, initial_velocity)
        self.__x0 = tank.x
        self.__y0 = tank.y
        self.__t = 0
        self.__v = self.__v0[0] + self.__x0, self.__v0[1] + self.__y0
        self.__time_increment = 1 / frames_per_second
        self.hit_x = (initial_velocity * initial_velocity *
                      math.sin(2 * math.atan2(turret_vector[1], turret_vector[0])) /
                      self.gravitational_acceleration + self.__x0)

    def get_hit_x(self):
        return self.hit_x

    def get_shell_angle(self):
        return math.atan2(self.__v[1], self.__v[0])

    def increment(self):
        self.__t += self.__time_increment
        x = self.__v0[0] * self.__t + self.__x0
        y = -self.__v0[1] * self.__t + 0.5 * TankShell.gravitational_acceleration * self.__t * self.__t + self.__y0
        self.__v = (int(x), int(y))

    def get_v(self):
        return self.__v


class Explosion:

    def __init__(self, fps, explode_time, radius, colors, display, location):
        self.fps = fps
        self.radius = radius
        self.current_magnitude = 1
        self.display = display
        self.explode_time = explode_time
        self.elapsed_time = 0
        self.time_increment = 1 / fps
        self.x = location[0]
        self.y = location[1]
        self.colors = colors

    def update(self):
        if self.still_exploding():
            self.elapsed_time += self.time_increment
            old_magnitude = self.current_magnitude
            self.current_magnitude = int(self.radius * self.elapsed_time / self.explode_time)
            for m in range(old_magnitude, self.current_magnitude):
                pygame.draw.circle(self.display, self.colors[random.randint(0, len(self.colors) - 1)],
                                   (self.x + random.randint(-m, m), self.y + random.randint(-m, m)),
                                   random.randint(1, 3))

    def still_exploding(self):
        return self.elapsed_time < self.explode_time
