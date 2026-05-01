import pygame
import math
import os
import sys
import random
import time

from reactions import set_state, get_state, update_state, reminder_reactions
from reminder import check_reminders
from bubble import init_font, show_bubble, update_bubble, draw_bubble
from button import init_button_font, yes_button, no_button
from chatbox import init_chatbox_fonts, draw_chatbox, handle_event as chat_handle_event

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def setup_transparency(hwnd):
    try:
        import ctypes
        import win32gui
        import win32con
        ctypes.windll.user32.SetWindowLongW(
            hwnd, -20,
            ctypes.windll.user32.GetWindowLongW(hwnd, -20) | 0x80000
        )
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0x00FF00FF, 0, 0x1)
        win32gui.SetWindowPos(
            hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
    except Exception:
        pass

os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
pygame.init()

# ── init all fonts together after pygame.init() ───────────────────────────────
init_font()
init_chatbox_fonts()
init_button_font()

info = pygame.display.Info()
SCREEN_W, SCREEN_H = info.current_w, info.current_h

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.NOFRAME)
hwnd = pygame.display.get_wm_info().get("window")
if hwnd:
    setup_transparency(hwnd)

pygame.display.set_caption("chacat")
clock = pygame.time.Clock()

images = {
    "neutral":  pygame.transform.scale(pygame.image.load(resource_path("cat/neutral.png")), (200, 200)),
    "sad":      pygame.transform.scale(pygame.image.load(resource_path("cat/sad.png")), (200, 200)),
    "angry":    pygame.transform.scale(pygame.image.load(resource_path("cat/angry.png")), (200, 200)),
    "sleeping": pygame.transform.scale(pygame.image.load(resource_path("cat/sleeping.png")), (200, 200)),
    "judging":  pygame.transform.scale(pygame.image.load(resource_path("cat/judging.png")), (200, 200)),
    "back":     pygame.transform.scale(pygame.image.load(resource_path("cat/back_turned.png")), (200, 200)),
    "love":     pygame.transform.scale(pygame.image.load(resource_path("cat/love.png")), (200, 200)),
    "mm":       pygame.transform.scale(pygame.image.load(resource_path("cat/mm.png")), (200, 200)),
    "excited":  pygame.transform.scale(pygame.image.load(resource_path("cat/excited.png")), (200, 200)),
}

tick = 0
reminder_timer = 0
active_reminder = None
last_triggered = {}

love_timer = 0
love_phrases = ["i love you <3", "thanks for being in my life <3", "ummahh!! <3"]

sleep_triggered = False
sleep_followup_timer = 0

dragging = False
cat_x = 100
cat_y = SCREEN_H - 220          # start near bottom left
offset_x, offset_y = 0, 0

chat_open = False
send_rect = None
input_rect = None

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # number keys only work when chat is closed
            if not chat_open:
                if event.key == pygame.K_1: set_state("neutral")
                if event.key == pygame.K_2: set_state("sad")
                if event.key == pygame.K_3: set_state("angry")
                if event.key == pygame.K_4: set_state("sleeping")
                if event.key == pygame.K_5: set_state("judging")
                if event.key == pygame.K_6: set_state("back")
                if event.key == pygame.K_7: set_state("love")
                if event.key == pygame.K_8: set_state("mm")
                if event.key == pygame.K_9: set_state("excited")

        # ── pass keyboard events to chatbox when open ─────────────────────
        if chat_open:
            chat_handle_event(event, send_rect, input_rect,
                              on_state_change=lambda s: set_state(s, duration=1800))

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cat_rect = pygame.Rect(cat_x, cat_y, 200, 200)

            # ── cat click: toggle chat open/closed ────────────────────────
            if cat_rect.collidepoint(event.pos):
                chat_open = not chat_open
                dragging = False    # don't drag when toggling chat
            else:
                # ── yes/no buttons (only when chat closed) ────────────────
                if not chat_open:
                    clicked_button = False

                    if active_reminder and yes_button.is_clicked(event):
                        reaction = reminder_reactions[active_reminder]["yes"]
                        yes_button.visible = False
                        no_button.visible = False
                        set_state(reaction["state"], duration=reaction["duration"])
                        show_bubble(reaction["bubble"], duration=reaction["duration"])
                        active_reminder = None
                        reminder_timer = 0
                        clicked_button = True

                    if active_reminder and no_button.is_clicked(event):
                        reaction = reminder_reactions[active_reminder]["no"]
                        yes_button.visible = False
                        no_button.visible = False
                        set_state(reaction["state"], duration=reaction["duration"])
                        show_bubble(reaction["bubble"], duration=reaction["duration"])
                        active_reminder = None
                        reminder_timer = 0
                        clicked_button = True

                    if not clicked_button:
                        dragging = True
                        offset_x = cat_x - event.pos[0]
                        offset_y = cat_y - event.pos[1]

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging = False

        if event.type == pygame.MOUSEMOTION and dragging:
            cat_x = event.pos[0] + offset_x
            cat_y = event.pos[1] + offset_y

    # ── timers ────────────────────────────────────────────────────────────────
    love_timer += 1
    if love_timer >= 108000:
        love_timer = 0
        set_state("love", duration=600)
        show_bubble(random.choice(love_phrases), duration=600)

    tick += 1
    update_bubble()
    update_state()

    if active_reminder:
        reminder_timer += 1
        if reminder_timer == 300: set_state("angry")
        if reminder_timer == 600: set_state("back")

    if tick % 60 == 0:
        reminder = check_reminders()
        now_real = time.time()
        if reminder and now_real - last_triggered.get(reminder, 0) >= 300:
            last_triggered[reminder] = now_real

            if reminder == "food":
                active_reminder = "food"
                reminder_timer = 0
                set_state("neutral")
                show_bubble(reminder_reactions["food"]["question"])
                yes_button.visible = True
                no_button.visible = True

            elif reminder == "sleep":
                set_state("sleeping")
                show_bubble("time to sleep <3", duration=36000)
                sleep_triggered = True
                sleep_followup_timer = 0

            elif reminder == "grocery":
                active_reminder = "grocery"
                reminder_timer = 0
                set_state("sad")
                show_bubble(reminder_reactions["grocery"]["question"])
                yes_button.visible = True
                no_button.visible = True

            elif reminder == "bath":
                active_reminder = "bath"
                reminder_timer = 0
                set_state("excited")
                show_bubble(reminder_reactions["bath"]["question"])
                yes_button.visible = True
                no_button.visible = True

    if sleep_triggered:
        sleep_followup_timer += 1
        if sleep_followup_timer >= 3600:
            sleep_triggered = False
            sleep_followup_timer = 0
            set_state("angry")
            show_bubble("WHY ARE YOU STILL AWAKE?! >:(", duration=600)

    # ── clamp cat to screen ───────────────────────────────────────────────────
    cat_x = max(0, min(cat_x, SCREEN_W - 200))
    cat_y = max(0, min(cat_y, SCREEN_H - 200))

    # ── draw ──────────────────────────────────────────────────────────────────
    bob = int(math.sin(tick * 0.05) * 5)
    screen.fill((255, 0, 255))
    screen.blit(images[get_state()], (cat_x, cat_y + bob))
    draw_bubble(screen, cat_x, cat_y, SCREEN_H)

    # yes/no buttons only when chat is closed
    if not chat_open:
        btn_y = min(cat_y + 150, SCREEN_H - 60)
        yes_button.draw(screen, cat_x + 10, btn_y)
        no_button.draw(screen, cat_x + 110, btn_y)

    # chat UI on top of everything
    if chat_open:
        send_rect, input_rect = draw_chatbox(screen, cat_x, cat_y, SCREEN_W, SCREEN_H)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()