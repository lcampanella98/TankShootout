from game_button import Button
import pygame
import tools


class ButtonHandler:

    def __init__(self, btn_y, btn_width, btn_height, btn_space_of_screen, texts,
                 idle_colors, hover_colors, clicking_colors, button_text_color,
                 number_of_buttons, window_width, window_height, button_font, display_screen):
        self.__display_screen = display_screen
        self.__btn_y = btn_y
        self.__btn_width = btn_width
        self.__btn_height = btn_height
        self.__btn_space_of_screen = btn_space_of_screen
        self.__window_width = window_width
        self.__window_height = window_height
        self.__number_of_buttons = number_of_buttons
        self.__button_font = button_font
        self.__buttons = []

        self.__btn_x0 = self.__window_width * (1 - self.__btn_space_of_screen) / 2
        self.__btn_spacing_val = (self.__window_width * self.__btn_space_of_screen) / (self.__number_of_buttons - 1)

        for i in range(0, self.__number_of_buttons):
            self.__buttons.append(Button(texts[i],
                                  button_text_color,
                                  idle_colors[i],
                                  hover_colors[i],
                                  clicking_colors[i],
                                  self.__btn_x0 + i * self.__btn_spacing_val - self.__btn_width / 2,
                                  self.__btn_y, self.__btn_width,
                                  self.__btn_height, self.__button_font, i))

        self.__was_clicking = False
        self.__is_clicking = None
        self.__last_click_button_index = None
        self.__action = None
        self.__cur = None

    def draw_buttons(self, cur_pos, is_clicking):
        self.__cur = cur_pos
        self.__is_clicking = is_clicking
        clicked = False
        released = False
        if self.__is_clicking != self.__was_clicking:
            if self.__is_clicking:
                clicked = True
                released = False
            else:
                clicked = False
                released = True
        clicked_a_button = False
        for i in range(0, len(self.__buttons)):  # draws buttons to menu
            button = self.__buttons[i]
            if tools.is_point_within_rect(self.__cur, button.rect):
                if clicked:
                    clicked_a_button = True
                    self.__last_click_button_index = i
                    current_button_color = button.clicking_color

                else:
                    if released:
                        if self.__last_click_button_index == i:
                            self.__action = button.action_code  # do button action here!!!

                        current_button_color = button.idle_color
                    else:
                        if self.__is_clicking:
                            if self.__last_click_button_index == i:
                                current_button_color = button.clicking_color
                            else:
                                current_button_color = button.idle_color
                        else:  # hovering
                            current_button_color = button.hover_color
            else:
                current_button_color = button.idle_color

            if clicked and not clicked_a_button:
                self.__last_click_button_index = None

            pygame.draw.rect(self.__display_screen, current_button_color, button.rect)
            tools.text_to_button(button.text, button.rect, button.font, self.__display_screen, button.text_color)
        self.__was_clicking = self.__is_clicking

    def get_action(self):
        action = self.__action
        self.__action = None
        return action

    def set_button_text(self, text_array):
        for i in range(0, self.__number_of_buttons):
            self.__buttons[i].text = text_array[i]