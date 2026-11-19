"""Native Pygame replay of the actual Python search; no network or browser."""
import math
import os
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

BG = "#f2f4f6"
INK = "#26323e"
MUTED = "#626e7b"
LINE = "#dce1e6"
ACCENT = "#356b99"
MAP_BG = "#19232d"


def validate_window(size, fps=60):
    if not isinstance(size, (tuple, list)) or len(size) != 2 or any(
            type(v) is not int for v in size) or size[0] < 480 or size[1] < 420:
        raise ValueError("WINDOW_SIZE must contain integers of at least (480, 420)")
    if type(fps) is not int or not 1 <= fps <= 240:
        raise ValueError("FPS must be an integer from 1 to 240")


class Replay:
    def __init__(self, session):
        self.session = session
        self.result = session["result"]
        self.path = self.result["path"]
        self.events = self.result["events"] if session["playback"]["show_search"] else []
        self.search_end = len(self.events)
        self.end = self.search_end + max(0, len(self.path) - 1)
        self.frame = 0.0
        self.playing = self.end > 0
        self._reset()

    def _reset(self):
        self.index = 0
        self.expanded = set()
        start = self.events[0]["state"] if self.events else self.session["map"]["start"]
        self.open_states = {tuple(start): tuple(start[:2])}

    def seek(self, frame):
        self.frame = max(0.0, min(self.end, float(frame)))
        count = min(self.search_end, int(self.frame))
        if count < self.index:
            self._reset()
        while self.index < count:
            event = self.events[self.index]
            self.index += 1
            self.open_states.pop(tuple(event["state"]), None)
            self.expanded.add(tuple(event["state"][:2]))
            for state in event["discovered"]:
                self.open_states[tuple(state)] = tuple(state[:2])

    def advance(self, seconds):
        if not self.playing:
            return
        settings = self.session["playback"]
        frame = self.frame
        if frame < self.search_end:
            used = min(seconds, (self.search_end - frame) / settings["search_speed"])
            frame = min(self.search_end, frame + used * settings["search_speed"])
            seconds -= used
        if frame >= self.search_end:
            frame = min(self.end, frame + seconds * settings["robot_speed"])
        self.seek(frame)
        if self.frame >= self.end:
            self.playing = False

    def toggle(self):
        if not self.end:
            return
        if self.frame >= self.end:
            self.seek(0)
        self.playing = not self.playing

    @property
    def phase(self):
        if self.frame < self.search_end:
            return "Exploring the map"
        if self.result["status"] != "found":
            return {"no_path": "No route exists", "not_implemented": "Complete the Python TODOs; details in terminal",
                    "disabled": "Bonus disabled; see config.json", "limit": "Search limit reached; outcome unknown"}.get(
                        self.result["status"], "Search stopped")
        return "Rescue complete" if self.frame >= self.end else "Robot following the route"


class Renderer:
    def __init__(self, session):
        self.session = session
        self.grid = session["map"]
        self.font = pygame.font.SysFont("segoeui", 16)
        self.small = pygame.font.SysFont("segoeui", 12)
        self.title = pygame.font.SysFont("segoeui", 22, bold=True)
        self.buttons = []
        self.timeline = pygame.Rect(0, 0, 1, 1)

    def text(self, surface, text, position, color=INK, font=None, max_width=None):
        font = font or self.font
        if max_width is not None:
            while text and font.size(text)[0] > max_width:
                text = text[:-2] if text.endswith("~") else text[:-1] + "~"
        surface.blit(font.render(text, True, color), position)

    def draw(self, surface, replay):
        width, height = surface.get_size()
        surface.fill(BG)
        left, right = 22, width - 22
        self.text(surface, "+", (left, 15), ACCENT, self.title)
        self.text(surface, "Rescue Robot", (left + 26, 15), font=self.title)
        hint = "Settings: run_setup.py | Results: terminal"
        if width >= 850:
            self.text(surface, hint, (right - self.small.size(hint)[0], 24), MUTED, self.small)
        panel = pygame.Rect(left, 61, right - left, height - 98)
        pygame.draw.rect(surface, "white", panel, border_radius=6)
        self.text(surface, self.grid["name"], (left + 16, 72), max_width=panel.width - 145)
        label = "{} | {} | {} x {}".format(self.session["algorithm"], self.session["mode"],
                                            len(self.grid["cells"][0]), len(self.grid["cells"]))
        self.text(surface, label, (left + 16, 96), MUTED, self.small, panel.width - 36)
        status = {"found": "ROUTE FOUND", "no_path": "NO ROUTE", "not_implemented": "TODO",
                  "disabled": "BONUS OFF", "limit": "LIMIT REACHED"}.get(replay.result["status"], "STOPPED")
        status_color = "#3a7050" if replay.result["status"] == "found" else "#8b6425"
        self.text(surface, status, (right - self.small.size(status)[0] - 15, 77), status_color, self.small)
        # Two legend rows leave the map and transport usable on smaller windows.
        legend_height = 46 if width < 760 else 32
        map_rect = pygame.Rect(left + 1, 122, panel.width - 2, panel.bottom - 122 - legend_height - 64)
        pygame.draw.rect(surface, MAP_BG, map_rect)
        self.draw_map(surface, map_rect, replay)
        self.draw_legend(surface, map_rect.bottom + 10, left + 16, right - 15)
        transport_y = panel.bottom - 57
        pygame.draw.line(surface, LINE, (left, transport_y - 5), (right, transport_y - 5))
        self.draw_transport(surface, replay, left + 14, transport_y, right - 16)
        pygame.draw.rect(surface, LINE, panel, 1, border_radius=6)
        footer = "Space: play / pause | Right: next step | Home: rewind | Esc: close"
        if replay.result["trace_truncated"]:
            footer = "Replay truncated; full search result in terminal. " + footer
        self.text(surface, footer, (left, height - 27), MUTED, self.small, width - 44)

    def draw_map(self, surface, rect, replay):
        rows, cols = len(self.grid["cells"]), len(self.grid["cells"][0])
        size = min((rect.width - 40) / cols, (rect.height - 32) / rows)
        x, y = rect.centerx - cols * size / 2, rect.centery - rows * size / 2
        center = lambda p: (round(x + (p[1] + .5) * size), round(y + (p[0] + .5) * size))
        frontier = set(replay.open_states.values())
        for r, row in enumerate(self.grid["cells"]):
            for c, tile in enumerate(row):
                color = {".": "#172833", "#": "#344653", "r": "#4c4134", "h": "#512f31"}[tile]
                if tile != "#" and replay.index:
                    if (r, c) in replay.expanded:
                        color = "#5c5434"
                    if (r, c) in frontier:
                        color = "#205251"
                cell = pygame.Rect(round(x + c * size + 1), round(y + r * size + 1),
                                   max(1, round(size - 2)), max(1, round(size - 2)))
                pygame.draw.rect(surface, color, cell, border_radius=max(0, min(3, round(size * .12))))
                if tile == "#" and size > 7:
                    pygame.draw.line(surface, "#425766", (cell.left + 2, cell.top + 2), (cell.right - 2, cell.top + 2), max(1, round(size * .07)))
                if tile == "r" and size > 11:
                    for dx, dy in ((.27, .3), (.55, .56)):
                        pygame.draw.rect(surface, "#796a50", (x + (c + dx) * size, y + (r + dy) * size, max(1, size * .16), max(1, size * .16)))
                if tile == "h" and size > 11:
                    pygame.draw.polygon(surface, "#a35f5c", [(x + (c + .23) * size, y + (r + .72) * size),
                        (x + (c + .5) * size, y + (r + .23) * size), (x + (c + .77) * size, y + (r + .72) * size)], 1)
        if replay.index and replay.frame < replay.search_end:
            p = center(replay.events[replay.index - 1]["state"])
            pygame.draw.rect(surface, "#e9bd67", (p[0] - size * .45, p[1] - size * .45, max(1, size * .9), max(1, size * .9)), 1, border_radius=2)
        path_visible = replay.path and replay.frame >= replay.search_end
        if path_visible and len(replay.path) > 1:
            pygame.draw.lines(surface, "#ff795f", False, [center(p) for p in replay.path], max(2, round(size * .13)))
        visited = set(tuple(p) for p in replay.path[:int(replay.frame - replay.search_end) + 1]) if path_visible else set()
        for i, goal in enumerate(self.grid["goals"]):
            p = center(goal)
            reached = tuple(goal) in visited
            pygame.draw.circle(surface, "#315c4b" if reached else "#23463f", p, max(2, round(size * .35)))
            pygame.draw.circle(surface, "#60927a" if reached else "#71decb", p, max(2, round(size * .35)), 1)
            arm = max(1, round(size * .13))
            pygame.draw.line(surface, "#a2f5d7", (p[0] - arm, p[1]), (p[0] + arm, p[1]), max(1, round(size * .08)))
            pygame.draw.line(surface, "#a2f5d7", (p[0], p[1] - arm), (p[0], p[1] + arm), max(1, round(size * .08)))
            if len(self.grid["goals"]) > 1 and size > 20:
                self.text(surface, str(i + 1), (p[0] + size * .3, p[1] - size * .4), "#dfffee", self.small)
        robot = self.grid["start"]
        if path_visible:
            t = min(len(replay.path) - 1, replay.frame - replay.search_end)
            a, b = replay.path[int(t)], replay.path[min(len(replay.path) - 1, int(t) + 1)]
            f = t % 1
            robot = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        p = center(robot)
        body = pygame.Rect(round(p[0] - size * .3), round(p[1] - size * .29), max(2, round(size * .6)), max(2, round(size * .58)))
        pygame.draw.rect(surface, "#65b7ff", body, border_radius=max(1, round(size * .16)))
        pygame.draw.rect(surface, "#badfff", body, 1, border_radius=max(1, round(size * .16)))
        pygame.draw.rect(surface, "#153346", (p[0] - size * .2, p[1] - size * .12, max(1, size * .4), max(1, size * .23)), border_radius=1)
        for dx in (-.13, .06):
            pygame.draw.rect(surface, "#b6f4ff", (p[0] + size * dx, p[1] - size * .05, max(1, size * .07), max(1, size * .07)))

    def draw_legend(self, surface, y, left, right):
        items = (("Robot", "#65b7ff"), ("Victim", "#71decb"), ("Wall", "#425866"),
                 ("Rubble", "#88714e"), ("Hazard", "#aa615a"), ("Frontier", "#3f827e"),
                 ("Expanded", "#9b8d56"), ("Route", "#ff795f"))
        x = left
        for label, color in items:
            length = self.small.size(label)[0] + 28
            if x + length > right:
                x, y = left, y + 17
            pygame.draw.rect(surface, color, (x, y + 4, 8, 8), border_radius=2)
            self.text(surface, label, (x + 13, y), MUTED, self.small)
            x += length

    def draw_transport(self, surface, replay, x, y, right):
        self.buttons = [pygame.Rect(x + i * 40, y + 8, 34, 34) for i in range(3)]
        color = ACCENT if replay.end else "#9cabb7"
        for i, button in enumerate(self.buttons):
            if i == 1:
                pygame.draw.rect(surface, color, button, border_radius=4)
                if replay.playing:
                    for offset in (-5, 3):
                        pygame.draw.rect(surface, "white", (button.centerx + offset, button.centery - 7, 3, 14))
                else:
                    pygame.draw.polygon(surface, "white", [(button.centerx - 4, button.centery - 7), (button.centerx - 4, button.centery + 7), (button.centerx + 7, button.centery)])
            else:
                cx, cy = button.center
                direction = -1 if i == 0 else 1
                pygame.draw.polygon(surface, color, [(cx - 4 * direction, cy - 6), (cx - 4 * direction, cy + 6), (cx + 4 * direction, cy)])
                pygame.draw.line(surface, color, (cx + 7 * direction, cy - 6), (cx + 7 * direction, cy + 6), 2)
        tx = x + 135
        self.text(surface, replay.phase, (tx, y), MUTED, self.small, right - tx)
        self.timeline = pygame.Rect(tx, y + 23, max(1, right - tx), 18)
        center_y = self.timeline.centery
        pygame.draw.line(surface, "#bac5ce", (tx, center_y), (right, center_y), 3)
        end_x = tx + round(self.timeline.width * replay.frame / replay.end) if replay.end else tx
        pygame.draw.line(surface, color, (tx, center_y), (end_x, center_y), 3)
        pygame.draw.circle(surface, color, (end_x, center_y), 6)


def handle_event(event, replay, renderer, dragging=False):
    """Pure event handling except window resize, which belongs to animate()."""
    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
        return False, False
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            replay.toggle()
        elif event.key == pygame.K_RIGHT:
            replay.playing = False
            replay.seek(math.floor(replay.frame) + 1)
        elif event.key == pygame.K_HOME:
            replay.playing = False
            replay.seek(0)
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for i, rect in enumerate(renderer.buttons):
            if rect.collidepoint(event.pos):
                if i == 1:
                    replay.toggle()
                else:
                    replay.playing = False
                    replay.seek(0 if i == 0 else math.floor(replay.frame) + 1)
        if renderer.timeline.collidepoint(event.pos) and replay.end:
            dragging = True
    if dragging and event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
        replay.playing = False
        replay.seek((event.pos[0] - renderer.timeline.left) / renderer.timeline.width * replay.end)
    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        dragging = False
    return True, dragging


def animate(session, size=(1180, 860), fps=60):
    validate_window(size, fps)
    pygame.display.init()
    pygame.font.init()
    try:
        pygame.display.set_caption("Rescue Robot - Pygame")
        surface = pygame.display.set_mode(size, pygame.RESIZABLE)
        replay, renderer = Replay(session), Renderer(session)
        clock = pygame.time.Clock()
        running, dragging = True, False
        renderer.draw(surface, replay)
        print("Pygame window opened. Space: pause/play, Right: step, Home: rewind, Esc: close.", flush=True)
        while running:
            dt = min(clock.tick(fps) / 1000, .1)
            for event in pygame.event.get():
                running, dragging = handle_event(event, replay, renderer, dragging)
                if not running:
                    break
                if event.type == pygame.VIDEORESIZE:
                    surface = pygame.display.set_mode((max(480, event.w), max(420, event.h)), pygame.RESIZABLE)
            if not running:
                break
            replay.advance(dt)
            renderer.draw(surface, replay)
            pygame.display.flip()
    finally:
        pygame.quit()


def save_snapshot(session, size, destination):
    validate_window(size)
    pygame.font.init()
    try:
        surface = pygame.Surface(size)
        replay = Replay(session)
        replay.seek(replay.end)
        replay.playing = False
        Renderer(session).draw(surface, replay)
        destination.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(surface, str(destination))
        print("Pygame snapshot saved: " + str(destination), flush=True)
    finally:
        pygame.font.quit()
