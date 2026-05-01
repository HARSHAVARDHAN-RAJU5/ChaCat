import pygame
import threading
from chat import chat

# ── colours ──────────────────────────────────────────────────────────────────
WHITE       = (255, 255, 255)
MAGENTA     = (255,   0, 255)   # transparent key
BOX_BG      = (255, 255, 255)
BOX_BORDER  = (210, 190, 220)
BOX_SHADOW  = (190, 175, 200)
USER_BUBBLE = (220, 180, 210)
USER_TEXT   = ( 58,  26,  51)
CAT_BUBBLE  = (245, 240, 255)
CAT_BORDER  = (210, 195, 230)
CAT_TEXT    = ( 50,  40,  60)
INPUT_BG    = (255, 255, 255)
INPUT_BORDER= (200, 180, 215)
SEND_BG     = (200, 165, 195)
SEND_TEXT   = ( 58,  26,  51)
SEND_HOVER  = (180, 140, 175)
SCROLL_COL  = (210, 190, 220)
PLACEHOLDER = (180, 165, 190)

# ── layout constants ──────────────────────────────────────────────────────────
CAT_W, CAT_H   = 200, 200      # real cat sprite size
INPUT_W        = 300           # input box width (beside cat)
CHAT_W         = CAT_W + INPUT_W  # chat box spans full width of cat+input
CHAT_H         = 400           # chat box height
INPUT_H        = 46            # type box height
SEND_W         = 60
GAP            = 6             # gap between chat box and input row
PADDING        = 14
BUBBLE_RADIUS  = 12
FONT_SIZE      = 15
SMALL_SIZE     = 13

# ── module state ─────────────────────────────────────────────────────────────
_font        = None
_small_font  = None
_initialized = False

messages     = []              # list of {"role": "user"/"hacha", "text": str}
input_text   = ""
scroll_offset= 0               # pixels scrolled up from bottom
_thinking    = False           # waiting for Gemini reply
_pending_state = None          # cat state returned by chat(), applied via callback

# ── init ──────────────────────────────────────────────────────────────────────
def init_chatbox_fonts():
    global _font, _small_font, _initialized
    if _initialized:
        return
    _font       = pygame.font.SysFont("segoeui", FONT_SIZE)
    _small_font = pygame.font.SysFont("segoeui", SMALL_SIZE)
    _initialized = True

# ── text wrapping ─────────────────────────────────────────────────────────────
def _wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines if lines else [""]

# ── bubble size helper ────────────────────────────────────────────────────────
def _bubble_size(text, font, max_w):
    lines = _wrap_text(text, font, max_w)
    lh    = font.get_linesize()
    w     = max(font.size(l)[0] for l in lines) + PADDING * 2
    h     = len(lines) * lh + PADDING
    return w, h, lines

# ── draw a rounded rect with shadow ──────────────────────────────────────────
def _draw_box(surf, rect, bg, border, shadow, radius=16):
    sx = pygame.Rect(rect.x + 3, rect.y + 3, rect.width, rect.height)
    pygame.draw.rect(surf, shadow, sx, border_radius=radius)
    pygame.draw.rect(surf, bg,     rect, border_radius=radius)
    pygame.draw.rect(surf, border, rect, width=2, border_radius=radius)

# ── measure total message list height ────────────────────────────────────────
def _total_content_height(inner_w):
    if not _font:
        return 0
    total = PADDING
    max_bw = inner_w - PADDING * 2 - 12
    for msg in messages:
        _, h, _ = _bubble_size(msg["text"], _font, max_bw)
        total += h + 8
    return total

# ── main draw function — call every tick while chat is open ───────────────────
def draw_chatbox(screen, cat_x, cat_y, screen_w, screen_h):
    if not _initialized:
        return

    # ── position: chat box spans full width above cat+input row ──────────
    box_x = cat_x
    box_x = max(4, min(box_x, screen_w - CHAT_W - 4))

    input_y = cat_y                          # input row aligns with cat top
    box_y   = input_y - CHAT_H - GAP
    box_y   = max(4, box_y)

    chat_rect  = pygame.Rect(box_x, box_y, CHAT_W, CHAT_H)
    # input box starts right beside the cat (cat occupies left CAT_W px)
    input_rect = pygame.Rect(box_x + CAT_W, input_y, INPUT_W, INPUT_H)
    send_rect  = pygame.Rect(input_rect.right - SEND_W - 6, input_y + 7, SEND_W, INPUT_H - 14)

    # ── draw chat box ─────────────────────────────────────────────────────
    _draw_box(screen, chat_rect, BOX_BG, BOX_BORDER, BOX_SHADOW, radius=18)

    # clip inner area
    inner = pygame.Rect(box_x + 4, box_y + 4, CHAT_W - 8, CHAT_H - 8)
    old_clip = screen.get_clip()
    screen.set_clip(inner)

    inner_w    = CHAT_W - 8
    max_bw     = inner_w - PADDING * 2 - 12
    content_h  = _total_content_height(inner_w)
    max_scroll = max(0, content_h - CHAT_H + PADDING)
    # clamp scroll
    global scroll_offset
    scroll_offset = max(0, min(scroll_offset, max_scroll))

    draw_y = box_y + PADDING - scroll_offset + max(0, CHAT_H - content_h)

    for msg in messages:
        bw, bh, lines = _bubble_size(msg["text"], _font, max_bw)
        lh = _font.get_linesize()

        if msg["role"] == "hacha":
            bx = box_x + 8
            brect = pygame.Rect(bx, draw_y, bw, bh)
            pygame.draw.rect(screen, (185, 170, 195), pygame.Rect(bx+2, draw_y+2, bw, bh), border_radius=BUBBLE_RADIUS)
            pygame.draw.rect(screen, CAT_BUBBLE, brect, border_radius=BUBBLE_RADIUS)
            pygame.draw.rect(screen, CAT_BORDER, brect, width=1, border_radius=BUBBLE_RADIUS)
            for i, line in enumerate(lines):
                surf = _font.render(line, True, CAT_TEXT)
                screen.blit(surf, (bx + PADDING, draw_y + PADDING // 2 + i * lh))
        else:
            bx = box_x + CHAT_W - bw - 10
            brect = pygame.Rect(bx, draw_y, bw, bh)
            pygame.draw.rect(screen, (165, 130, 155), pygame.Rect(bx+2, draw_y+2, bw, bh), border_radius=BUBBLE_RADIUS)
            pygame.draw.rect(screen, USER_BUBBLE, brect, border_radius=BUBBLE_RADIUS)
            for i, line in enumerate(lines):
                surf = _font.render(line, True, USER_TEXT)
                screen.blit(surf, (bx + PADDING, draw_y + PADDING // 2 + i * lh))

        draw_y += bh + 8

    # thinking dots
    if _thinking:
        dots = "..." 
        surf = _font.render(dots, True, PLACEHOLDER)
        screen.blit(surf, (box_x + 12, draw_y))

    screen.set_clip(old_clip)

    # scrollbar
    if max_scroll > 0:
        bar_h    = max(20, int(CHAT_H * CHAT_H / content_h))
        bar_y    = box_y + int(scroll_offset / max_scroll * (CHAT_H - bar_h))
        bar_rect = pygame.Rect(box_x + CHAT_W - 7, bar_y, 4, bar_h)
        pygame.draw.rect(screen, SCROLL_COL, bar_rect, border_radius=2)

    # ── draw input box ────────────────────────────────────────────────────
    _draw_box(screen, input_rect, INPUT_BG, INPUT_BORDER, BOX_SHADOW, radius=14)

    mx, my = pygame.mouse.get_pos()
    send_col = SEND_HOVER if send_rect.collidepoint(mx, my) else SEND_BG
    pygame.draw.rect(screen, send_col, send_rect, border_radius=8)
    send_surf = _small_font.render("send", True, SEND_TEXT)
    screen.blit(send_surf, (send_rect.centerx - send_surf.get_width()//2,
                             send_rect.centery - send_surf.get_height()//2))

    # input text — clip from left when overflowing
    text_area_w = input_rect.width - SEND_W - 20
    old_clip2 = screen.get_clip()
    screen.set_clip(pygame.Rect(input_rect.x + 8, input_rect.y, text_area_w, INPUT_H))
    if input_text:
        txt_surf = _font.render(input_text, True, CAT_TEXT)
        tx = input_rect.x + 8
        if txt_surf.get_width() > text_area_w:
            tx = input_rect.x + 8 + text_area_w - txt_surf.get_width()
        screen.blit(txt_surf, (tx, input_rect.centery - txt_surf.get_height()//2))
        # blinking cursor after text
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = min(tx + txt_surf.get_width() + 1, input_rect.x + 8 + text_area_w - 2)
            cursor_y = input_rect.centery - txt_surf.get_height() // 2
            pygame.draw.line(screen, CAT_TEXT, (cursor_x, cursor_y), (cursor_x, cursor_y + txt_surf.get_height()), 2)
    else:
        ph = _font.render("say something...", True, PLACEHOLDER)
        screen.blit(ph, (input_rect.x + 10, input_rect.centery - ph.get_height()//2))
        # blinking cursor at start when empty
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_y = input_rect.centery - ph.get_height() // 2
            pygame.draw.line(screen, PLACEHOLDER, (input_rect.x + 10, cursor_y), (input_rect.x + 10, cursor_y + ph.get_height()), 2)
    screen.set_clip(old_clip2)

    return send_rect, input_rect

# ── send a message ────────────────────────────────────────────────────────────
def _do_send(on_state_change):
    global _thinking, _pending_state, input_text
    text = input_text.strip()
    if not text or _thinking:
        return
    messages.append({"role": "user", "text": text})
    input_text   = ""
    _thinking    = True
    scroll_offset_to_bottom()

    def _thread():
        global _thinking
        reply, cat_state = chat(text)
        messages.append({"role": "hacha", "text": reply})
        _thinking = False
        scroll_offset_to_bottom()
        if on_state_change:
            on_state_change(cat_state)

    threading.Thread(target=_thread, daemon=True).start()

def scroll_offset_to_bottom():
    global scroll_offset
    scroll_offset = 999999   # will be clamped in draw

# ── event handler — call from main.py event loop ──────────────────────────────
def handle_event(event, send_rect, input_rect, on_state_change=None):
    global input_text, scroll_offset

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
            _do_send(on_state_change)
        elif event.key == pygame.K_BACKSPACE:
            input_text = input_text[:-1]
        else:
            if event.unicode and event.unicode.isprintable():
                input_text += event.unicode

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            if send_rect and send_rect.collidepoint(event.pos):
                _do_send(on_state_change)
        if event.button == 4:   # scroll up
            scroll_offset = max(0, scroll_offset - 30)
        if event.button == 5:   # scroll down
            scroll_offset += 30

def reset_chat():
    global messages, input_text, scroll_offset, _thinking
    messages      = []
    input_text    = ""
    scroll_offset = 0
    _thinking     = False