def get_text_location_within_rect(text, rect, font):
    size = font.size(text)
    rect_top_left = (rect[0], rect[1])
    rect_width = rect[2]
    rect_height = rect[3]
    return rect_top_left[0] + rect_width / 2 - size[0] / 2, rect_top_left[1] + rect_height / 2 - size[1] / 2


def is_point_within_rect(point, rect):
    r_pos = (rect[0], rect[1])
    r_width = rect[2]
    r_height = rect[3]
    return r_pos[0] <= point[0] <= r_pos[0] + r_width and r_pos[1] <= point[1] <= r_pos[1] + r_height


def text_to_button(text, rect, font, game_display, color):
    text_coord = get_text_location_within_rect(text, rect, font)
    text_surface = font.render(text, True, color)
    game_display.blit(text_surface, text_coord)


def are_rects_colliding(rect1, rect2):
    x_collide = rect2[0] <= rect1[0] <= rect2[0] + rect2[2] or rect2[0] <= rect1[0] + rect1[2] <= rect2[0] + rect2[2]
    if not x_collide:
        return False
    y_collide = rect2[1] <= rect1[1] <= rect2[1] + rect2[3] or rect2[1] <= rect1[1] + rect1[3] <= rect2[1] + rect2[3]
    if not y_collide:
        return False
    return True


def point_within_interval(p, lower_bound, upper_bound):
    return lower_bound <= p <= upper_bound
