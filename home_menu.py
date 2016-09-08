import pygame
from button_handler import ButtonHandler


class HomeMenu:

    def __init__(self, game):
        self.__game = game
        self.__should_run_menu_loop = True
        self.__btn_y = 450
        self.__btn_width = 160
        self.__btn_height = 40
        self.__btn_space_of_screen = 0.75
        self.__difficulties = ["easy", "medium", "hard"]
        self.__difficulty = "easy"
        self._my_button_font = self.__game.get_font(20)

        self._button_texts = ["Play", "Difficulty: " + self.__difficulty.capitalize(), "Controls", "Quit"]
        button_idle_colors = [game.green, game.purple, game.yellow, game.red]
        button_hover_colors = [game.light_green, game.light_purple, game.light_yellow, game.light_red]
        button_clicking_colors = [game.dark_green, game.dark_purple, game.dark_yellow, game.dark_red]
        self.__button_text_color = game.black

        self.__number_of_buttons = 4

        self.__action = None
        self.__my_button_handler = ButtonHandler(self.__btn_y, self.__btn_width, self.__btn_height,
                                                 self.__btn_space_of_screen, self._button_texts, button_idle_colors,
                                                 button_hover_colors, button_clicking_colors, self.__button_text_color,
                                                 self.__number_of_buttons, self.__game.window_width,
                                                 self.__game.window_height, self._my_button_font,
                                                 self.__game.game_display)
        self.__in_controls_screen = False

    def __show_info_messages(self):
        self.__game.game_display.fill(self.__game.background_color)
        self.__game.message_to_screen(self.__game.med_font,
                                      "Welcome to " + self.__game.title, self.__game.green, y_displace=-100)
        self.__game.message_to_screen(self.__game.small_font,
                                      "The objective is to shoot and destroy", self.__game.black, y_displace=-30)
        self.__game.message_to_screen(self.__game.small_font,
                                      "the enemy tank before they destroy you!", self.__game.black, y_displace=0)

    def run_menu(self):

        while self.__should_run_menu_loop:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__game.quit_game()

            self.__game.game_display.fill(self.__game.background_color)
            if self.__in_controls_screen:
                self.__show_controls_messages()
            else:
                self.__show_info_messages()

            self.__my_button_handler.draw_buttons(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0])
            self.__action = self.__my_button_handler.get_action()
            self.__do_action()
            pygame.display.update()
            self.__game.clock.tick(self.__game.in_game_fps)

        return self.__difficulties.index(self.__difficulty)

    def __do_action(self):
        if self.__action is not None:
            if self.__action == 0:
                self.__should_run_menu_loop = False
            elif self.__action == 1:
                self._toggle_difficulty()
            elif self.__action == 2:
                self.__toggle_controls_screen()
            elif self.__action == 3:
                self.__game.quit_game()

    def _toggle_difficulty(self):
        index = self.__difficulties.index(self.__difficulty)
        if index >= len(self.__difficulties) - 1:
            index = 0
        else:
            index += 1
        self.__difficulty = self.__difficulties[index]
        self._update_handler_text(1, "Difficulty: " + self.__difficulty.capitalize())

    def __toggle_controls_screen(self):
        if self.__in_controls_screen:
            self.__in_controls_screen = False
            self._update_handler_text(2, "Controls")
        else:
            self.__in_controls_screen = True
            self._update_handler_text(2, "Back")

    def _update_handler_text(self, index, new_text):
        self._button_texts[index] = new_text
        self.__my_button_handler.set_button_text(self._button_texts)

    def __show_controls_messages(self):
        self.__game.message_to_screen(self.__game.large_font, "Controls", self.__game.green, -100)
        self.__game.message_to_screen(self.__game.small_font, "Fire: Spacebar", self.__game.black, -30)
        self.__game.message_to_screen(self.__game.small_font, "Move Turret: Up and Down Arrows", self.__game.black, 0)
        self.__game.message_to_screen(self.__game.small_font, "Move Tank: Left and Right Arrows", self.__game.black, 30)
        self.__game.message_to_screen(self.__game.small_font, "Change Shell Power: A and D", self.__game.black, 60)
        self.__game.message_to_screen(self.__game.small_font, "Pause: E", self.__game.black, 90)
