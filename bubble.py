import pygame

bubble_text = ""
bubble_visible = False
bubble_timer = 0
bubble_duration = 1800

font = None

def init_font():
    global font
    font = pygame.font.SysFont("comicsansms", 16)

def show_bubble(text, duration=1800):
    global bubble_text, bubble_visible, bubble_timer, bubble_duration
    bubble_text = text
    bubble_visible = True
    bubble_timer = 0
    bubble_duration = duration

def update_bubble():
    global bubble_visible, bubble_timer
    if bubble_visible:
        bubble_timer += 1
        if bubble_timer >= bubble_duration:
            bubble_visible = False

def wrap_text(text, max_chars=28):
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())
    return lines

def draw_bubble(screen, cat_x, cat_y, screen_h=1080):
    if not bubble_visible:
        return

    lines = wrap_text(bubble_text)
    padding = 14
    line_height = font.get_linesize()
    text_width = max(font.size(line)[0] for line in lines)
    rect_w = text_width + padding * 2
    rect_h = (line_height * len(lines)) + padding

    bx = cat_x + (200 // 2) - (rect_w // 2)
    by = cat_y - rect_h - 10
    # Clamp bubble so it doesn't go off top
    by = max(10, by)
    # Clamp bubble so it doesn't go off bottom
    by = min(screen_h - rect_h - 10, by)

    pygame.draw.rect(screen, (180, 180, 180), (bx+4, by+4, rect_w, rect_h), border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), (bx, by, rect_w, rect_h), border_radius=10)
    pygame.draw.rect(screen, (240, 240, 240), (bx+2, by+2, rect_w-4, rect_h//3), border_radius=8)

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, (50, 50, 50))
        screen.blit(text_surface, (bx + padding, by + padding//2 + i * line_height))
