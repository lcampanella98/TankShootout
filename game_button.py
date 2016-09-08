class Button:

    def __init__(self, text, text_color, idle_color, hover_color,
                 clicking_color, x, y, width, height, font, action_code):

        self.text = text
        self.idle_color = idle_color
        self.hover_color = hover_color
        self.clicking_color = clicking_color
        self.text_color = text_color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.rect = (x, y, width, height)
        self.action_code = action_code
