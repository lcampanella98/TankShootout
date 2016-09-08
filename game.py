import pygame
from home_menu import HomeMenu
from tank import Tank, TankShell, Explosion, AITank
import random
import tools
from button_handler import ButtonHandler


class Game:

    white = (255, 255, 255)
    black = (0, 0, 0)

    purple = (109, 58, 240)
    light_purple = (141, 100, 245)
    dark_purple = (103, 7, 230)

    red = (255, 0, 0)
    light_red = (255, 41, 41)
    dark_red = (227, 0, 0)

    green = (0, 155, 0)
    light_green = (0, 230, 0)
    dark_green = (0, 120, 0)

    yellow = (235, 225, 0)
    light_yellow = (255, 252, 74)
    dark_yellow = (209, 206, 0)

    def __init__(self):

        pygame.init()

        self.background_color = self.white
        self.window_width = 800
        self.window_height = 600

        self.game_display = pygame.display.set_mode((self.window_width, self.window_height))
        self.title = 'Tank Shootout'
        pygame.display.set_caption(self.title)
        self.clock = pygame.time.Clock()
        self.in_game_fps = 60
        self.pause_fps = 5

        self.game_difficulty = 0

        self.font_name = "impact"
        self.small_font = pygame.font.SysFont(self.font_name, 25)
        self.med_font = pygame.font.SysFont(self.font_name, 50)
        self.large_font = pygame.font.SysFont(self.font_name, 80)
        self.game_home_menu = HomeMenu(game=self)

        #  tank shell power bar
        self.tank_max_power = 360
        self.tank_min_power = 300
        self.power_bar_loc = (30, 30)
        self.power_bar_width = 60
        self.power_bar_height = 200
        self.power_settings = []
        self.power_colors = [self.light_green, self.green, self.yellow, self.dark_yellow, self.light_red, self.red]
        self.num_power_settings = 6
        for i in range(self.num_power_settings):
            setting = self.tank_min_power + i * (self.tank_max_power - self.tank_min_power)
            self.power_settings.append(setting)

        self.current_power_setting = int(self.num_power_settings / 2)

        #  explosions
        self.explosion_time = 0.2
        self.explosion_radius = 40
        self.current_explosions = []
        self.explosion_colors = [self.red, self.light_red, self.yellow, self.light_yellow]

        #  ground
        self.ground_level_y = self.window_height * 0.85

        #  tank definitions
        self.tank_move_increment = 2
        self.tank_turret_angular_velocity = 40
        self.tank_turret_angle_increment = float(self.tank_turret_angular_velocity) / self.in_game_fps
        self.tank_reload_time = 0.3

        #  player tank
        self.main_tank = self.get_player_tank()

        #  enemy tank
        self.enemy_tank = self.get_enemy_tank()

        #  barrier initialization
        self.barrier_window_range = 0.4
        self.barrier = None

        #  shell array
        self.player_shells_in_air = []
        self.enemy_shells_in_air = []

    def get_font(self, size):
        return pygame.font.SysFont(self.font_name, size)

    def init_game_state(self):
        self.set_barrier()
        self.current_power_setting = int(self.num_power_settings / 2)
        self.current_explosions = []

        self.main_tank = self.get_player_tank()
        self.enemy_tank = self.get_enemy_tank()

        self.player_shells_in_air = []
        self.enemy_shells_in_air = []

    def get_enemy_tank(self):
        t_width = 40
        t_height = 15
        t_turret_radius = 10
        t_turret_width = 3
        t_wheel_radius = 3
        t_min_angle = 5
        t_max_angle = 80
        t_turret_length = 35
        t_y = self.ground_level_y - t_height - t_wheel_radius
        enemy_x = self.window_width * 0.9
        enemy_reload_time = 1
        enemy_turret_angle = 60
        enemy_hits_until_death = 2
        return (AITank(enemy_x, t_y, t_width, t_height, t_turret_radius,
                       t_turret_width, t_wheel_radius, t_turret_length,
                       180 - enemy_turret_angle, 180 - t_min_angle, 180 - t_max_angle,
                       enemy_reload_time, self.in_game_fps, enemy_hits_until_death, self.game_difficulty))

    def get_player_tank(self):
        t_width = 40
        t_height = 15
        t_turret_radius = 10
        t_turret_width = 3
        t_wheel_radius = 3
        t_turret_length = 35
        t_angle = 5
        t_min_angle = 5
        t_max_angle = 80
        t_x = self.window_width * 0.1
        t_y = self.ground_level_y - t_height - t_wheel_radius
        t_hits_until_death = 5
        return (Tank(t_x, t_y,
                     t_width, t_height, t_turret_radius,
                     t_turret_width, t_wheel_radius, t_turret_length,
                     t_angle, t_min_angle, t_max_angle, self.tank_reload_time,
                     self.in_game_fps, t_hits_until_death))

    def draw_ground(self):
        pygame.draw.rect(self.game_display, self.light_green,
                         [0, self.ground_level_y, self.window_width, self.window_height - self.ground_level_y])

    def get_shell_power_from_percentage(self, percent):
        return int(self.tank_min_power + percent / 100 * (self.tank_max_power - self.tank_min_power))

    def get_percentage_from_shell_power(self, power):
        return 100 * (power - self.tank_min_power) / (self.tank_max_power - self.tank_min_power)

    def draw_power_bar(self):
        border_width = 4
        pygame.draw.rect(self.game_display, self.black, [self.power_bar_loc[0], self.power_bar_loc[1],
                                                         self.power_bar_width, self.power_bar_height], border_width)
        block_size = (self.power_bar_height - border_width) / self.num_power_settings
        fill_y = self.power_bar_loc[1] + self.power_bar_height - border_width / 2
        fill_width = self.power_bar_width - border_width
        for i in range(self.current_power_setting + 1):
            fill_x = self.power_bar_loc[0] + border_width / 2
            fill_y -= block_size
            pygame.draw.rect(self.game_display, self.power_colors[i], [fill_x, fill_y, fill_width, block_size + 2])

    def pause(self):
        paused = True
        self.message_to_screen(self.large_font, "Paused", self.black, y_displace=-100)
        self.message_to_screen(self.small_font, "Press C to continue or Q to quit", self.black, y_displace=25)
        pygame.display.update()
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        paused = False
                        break
                    elif event.key == pygame.K_q:
                        self.quit_game()

    def message_to_screen(self, font, msg, color, y_displace=0):

        screen_text = font.render(msg, True, color)
        size = font.size(msg)
        self.game_display.blit(screen_text, [self.window_width / 2 - size[0] / 2,
                                             self.window_height / 2 - size[1] / 2 + y_displace])

    def draw_barrier(self):
        pygame.draw.rect(self.game_display, self.black, self.barrier)

    def set_barrier(self):

        x = self.window_width / 2 + random.randint(-self.barrier_window_range / 2 * self.window_width,
                                                   self.barrier_window_range / 2 * self.window_width)
        y0 = self.ground_level_y
        y1 = y0 - int(random.randrange(int(self.ground_level_y / 4), int(self.ground_level_y / 3)))
        width = 20
        self.barrier = [x, y1, width, y0 - y1]

    def fire_shell(self):
        self.player_shells_in_air.append(TankShell(self.main_tank,
                                                   self.power_settings[self.current_power_setting], self.in_game_fps))

    def add_explosion(self, x, y):
        self.current_explosions.append(Explosion(self.in_game_fps, self.explosion_time, self.explosion_radius,
                                                 self.explosion_colors, self.game_display, (x, y)))

    def update_explosions(self):
        for explosion in self.current_explosions:
            if explosion.still_exploding():
                explosion.update()
            else:
                self.current_explosions.remove(explosion)

    @staticmethod
    def shell_hit(tank):
        tank.was_hit()

    def draw_shells(self, enemy_tank, shells_list):
        for shell in shells_list:
            shell.increment()
            v = shell.get_v()
            shell_collided_with_barrier = tools.is_point_within_rect(v, self.barrier) or self.ground_level_y < v[1]
            shell_collided_with_enemy = tools.is_point_within_rect(v,
                                                                   [enemy_tank.x - enemy_tank.width / 2,
                                                                    enemy_tank.y + enemy_tank.turret_radius,
                                                                    enemy_tank.width, enemy_tank.height])
            was_collision = False
            if shell_collided_with_enemy or shell_collided_with_barrier:
                was_collision = True

            if was_collision:
                self.add_explosion(v[0], v[1])
                shells_list.remove(shell)
                if shell_collided_with_barrier:
                    pass
                elif shell_collided_with_enemy:
                    self.shell_hit(enemy_tank)
                else:
                    pass
            else:
                pygame.draw.circle(self.game_display, self.red, v, 2)

    @staticmethod
    def quit_game():
        pygame.quit()
        quit()

    def game_loop(self):

        game_exit = False

        space_down = False

        tank_x_increment = 0
        tank_angle_increment = 0
        if self.game_difficulty == 0:
            self.main_tank.set_reload_time(0.35)
            self.enemy_tank.set_reload_time(1.00)
        elif self.game_difficulty == 1:
            self.main_tank.set_reload_time(0.50)
            self.enemy_tank.set_reload_time(0.85)
        elif self.game_difficulty == 2:
            self.main_tank.set_reload_time(0.65)
            self.enemy_tank.set_reload_time(0.70)

        while not game_exit:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        tank_x_increment = -self.tank_move_increment

                    elif event.key == pygame.K_RIGHT:
                        tank_x_increment = self.tank_move_increment

                    elif event.key == pygame.K_UP:
                        tank_angle_increment = self.tank_turret_angle_increment

                    elif event.key == pygame.K_DOWN:
                        tank_angle_increment = -self.tank_turret_angle_increment

                    elif event.key == pygame.K_e:
                        tank_angle_increment = 0
                        tank_x_increment = 0
                        self.pause()

                    elif event.key == pygame.K_a:
                        if self.current_power_setting > 0:
                            self.current_power_setting -= 1
                    elif event.key == pygame.K_d:
                        if self.current_power_setting < self.num_power_settings - 1:
                            self.current_power_setting += 1

                    elif event.key == pygame.K_SPACE:
                        space_down = True

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        if tank_x_increment < 0:
                            tank_x_increment = 0

                    elif event.key == pygame.K_RIGHT:
                        if tank_x_increment > 0:
                            tank_x_increment = 0

                    elif event.key == pygame.K_UP:
                        if tank_angle_increment > 0:
                            tank_angle_increment = 0
                    elif event.key == pygame.K_DOWN:
                        if tank_angle_increment < 0:
                            tank_angle_increment = 0
                    elif event.key == pygame.K_SPACE:
                        space_down = False

            self.main_tank.frame_elapsed()
            self.enemy_tank.frame_elapsed()

            self.game_display.fill(self.background_color)

            self.draw_power_bar()

            old_main_tank_x = self.main_tank.x
            self.main_tank.set_pos(old_main_tank_x + tank_x_increment, self.main_tank.y)
            if (tools.are_rects_colliding(self.main_tank.get_rect(), self.barrier) or
                    (self.main_tank.x - self.main_tank.width / 2 < 0)):
                self.main_tank.x = old_main_tank_x

            if space_down:
                if not self.main_tank.is_reloading():
                    self.fire_shell()
                    self.main_tank.fire()

            enemy_shell = self.enemy_tank.update(self.main_tank,
                                                 self.player_shells_in_air,
                                                 self.barrier[0], self.window_width)
            if enemy_shell is not None:
                self.enemy_shells_in_air.append(enemy_shell)

            if (tools.are_rects_colliding(self.enemy_tank.get_rect(), self.barrier) or
                    (self.enemy_tank.x + self.enemy_tank.width / 2 > self.window_width)):
                self.enemy_tank.move_back()

            self.main_tank.increment_turret_angle(tank_angle_increment)
            self.main_tank.draw_tank(self.game_display, self.black)
            self.enemy_tank.draw_tank(self.game_display, self.red)
            self.draw_barrier()
            self.draw_ground()
            self.draw_shells(self.enemy_tank, self.player_shells_in_air)
            self.draw_shells(self.main_tank, self.enemy_shells_in_air)
            self.check_deaths()
            self.main_tank.draw_health_bar(self.game_display, self.black, self.green, self.red)
            self.enemy_tank.draw_health_bar(self.game_display, self.black, self.green, self.red)

            self.update_explosions()

            pygame.display.update()
            self.clock.tick(self.in_game_fps)

    def check_deaths(self):
        if self.main_tank.is_dead():
            self.game_over(False)
        elif self.enemy_tank.is_dead():
            self.game_over(True)

    def game_over(self, won):
        btn_handler = ButtonHandler(self.window_height*0.7, 200, 50, 0.6,
                                    ["Play Again", "Main Menu", "Quit"],
                                    [self.green, self.yellow, self.red],
                                    [self.light_green, self.light_yellow, self.light_red],
                                    [self.dark_green, self.dark_yellow, self.dark_red],
                                    self.black, 3, self.window_width, self.window_height, self.small_font,
                                    self.game_display)

        if won:
            big_message = "You Win!"
            big_color = self.green
        else:
            big_message = "You Lose!"
            big_color = self.red

        while True:
            self.game_display.fill(self.background_color)
            self.message_to_screen(self.large_font, big_message, big_color)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit_game()
            btn_handler.draw_buttons(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0])
            action = btn_handler.get_action()
            if action is not None:
                if action == 0:
                    self.play_new_game_now()
                    break
                elif action == 1:
                    self.start_game()
                    break
                elif action == 2:
                    self.quit_game()
                    break
                else:
                    self.quit_game()
                    break

            pygame.display.update()
            self.clock.tick(self.in_game_fps)

    def play_new_game_now(self):
        self.init_game_state()
        self.game_loop()

    def new_home_menu(self):
        self.game_home_menu = HomeMenu(self)

    def start_game(self):
        self.new_home_menu()
        self.game_difficulty = self.game_home_menu.run_menu()
        self.init_game_state()
        self.play_new_game_now()

    def draw_rect_points(self, rect):
        pygame.draw.rect(self.game_display, self.red, [rect[0], rect[1], 2, 2])
        pygame.draw.rect(self.game_display, self.red, [rect[0] + rect[2], rect[1], 2, 2])
        pygame.draw.rect(self.game_display, self.red, [rect[0], rect[1] + rect[3], 2, 2])
        pygame.draw.rect(self.game_display, self.red, [rect[0] + rect[2], rect[1] + rect[3], 2, 2])
