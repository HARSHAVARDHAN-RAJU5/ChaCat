# button.py
import pygame

font = None

def init_button_font():
    global font
    font = pygame.font.SysFont("comicsansms", 16)

class Button:
    def __init__(self, text, color, hover_color):
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.visible = False
        self.rect = pygame.Rect(0, 0, 0, 0)

    def draw(self, screen, x, y):
        if not self.visible:
            return
        
        text_surface = font.render(self.text, True, (255, 255, 255))
        padding = 14
        w = text_surface.get_width() + padding * 2
        h = text_surface.get_height() + padding

        self.rect = pygame.Rect(x, y, w, h)

        # shadow
        pygame.draw.rect(screen, (100, 100, 100), (x+4, y+4, w, h), border_radius=10)
        # main
        pygame.draw.rect(screen, self.color, (x, y, w, h), border_radius=10)
        # highlight
        pygame.draw.rect(screen, self.hover_color, (x+2, y+2, w-4, h//3), border_radius=8)
        # text
        screen.blit(text_surface, (x + padding, y + padding//2))

    def is_clicked(self, event):
        if self.visible and event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

yes_button = Button("yes <3", (80, 160, 80), (100, 190, 100))
no_button = Button("no :(", (180, 70, 70), (210, 90, 90))