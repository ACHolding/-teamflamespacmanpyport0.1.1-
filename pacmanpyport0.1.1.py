# pr files = off
# TEAM FLAMES PRESENTS — AC's PACMAN ultra 0.1
# full arcade pac-man engine · famicom pirate shell (hummer-team style)
#
# pr reference video (youtube) — pac-man arcade attract / board:
#   https://www.youtube.com/watch?v=W5yeZSOEFq4   Pac-Man (Namco 1980) Attract Mode 60fps
#   https://www.youtube.com/watch?v=dScq4P5gn4A   Arcade Game: Pac-Man (1980 Namco/Midway)
#   https://www.youtube.com/watch?v=-CbyAk3Sn9I    Pac-Man Original (Arcade 1980)
#   https://www.youtube.com/watch?v=v8BT43ZWSTY    Pac-Man intermissions
#
# pr reference video (youtube) — team hummer / somari presents shell:
#   https://www.youtube.com/watch?v=PAcBMm0xXPk   The Hummer (NES) — Team Hummer title
#   https://www.youtube.com/watch?v=DNRBcjhT2Wc   Somari (NES) Playthrough — Somari Team Presents
#   https://www.youtube.com/watch?v=3dGBMGI43GA   Street Fighter II NES — Hummer Team
#
# presents cadence mirrors Sonic/Somari/Hummer "TEAM ___ PRESENTS" black card;
# attract mirrors Namco 1980 nickname board + chase / fright reverse.
import pygame, math, random, sys
from array import array

pygame.init()
W, H = 224, 288
SC = 2
FPS = 60
TILE, COLS, ROWS, TOP = 8, 28, 31, 24
STEP = 1.0 / 120.0

UP, LEFT, DOWN, RIGHT = (0, -1), (-1, 0), (0, 1), (1, 0)
DIRS = (UP, LEFT, DOWN, RIGHT)
OPP = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

# raw NES 2C02 — no blue tint (hummer carts were harsh CRT)
_NES = (
    (0x66,0x66,0x66),(0x00,0x2A,0x88),(0x14,0x12,0xA7),(0x3B,0x00,0xA4),
    (0x5C,0x00,0x7E),(0x6E,0x00,0x40),(0x6C,0x06,0x00),(0x56,0x1D,0x00),
    (0x33,0x35,0x00),(0x0B,0x48,0x00),(0x00,0x52,0x00),(0x00,0x4F,0x08),
    (0x00,0x40,0x4D),(0,0,0),(0,0,0),(0,0,0),
    (0xAD,0xAD,0xAD),(0x15,0x5F,0xD9),(0x42,0x40,0xFF),(0x75,0x27,0xFE),
    (0xA0,0x1A,0xCC),(0xB7,0x1E,0x7B),(0xB5,0x31,0x20),(0x99,0x4E,0x00),
    (0x6B,0x6D,0x00),(0x38,0x87,0x00),(0x0C,0x93,0x00),(0x00,0x8F,0x32),
    (0x00,0x7C,0x8D),(0,0,0),(0,0,0),(0,0,0),
    (0xFF,0xFE,0xFF),(0x64,0xB0,0xFF),(0x92,0x90,0xFF),(0xC6,0x76,0xFF),
    (0xF3,0x6A,0xFF),(0xFE,0x6E,0xCC),(0xFE,0x81,0x70),(0xEA,0x9E,0x22),
    (0xBC,0xBE,0x00),(0x88,0xD8,0x00),(0x5C,0xE4,0x30),(0x45,0xE0,0x82),
    (0x48,0xCD,0xDE),(0x4F,0x4F,0x4F),(0,0,0),(0,0,0),
    (0xFF,0xFE,0xFF),(0xC0,0xDF,0xFF),(0xD3,0xD2,0xFF),(0xE8,0xC8,0xFF),
    (0xFB,0xC2,0xFF),(0xFE,0xC4,0xEA),(0xFE,0xCC,0xC5),(0xF7,0xD8,0xA5),
    (0xE4,0xE5,0x94),(0xCF,0xEF,0x96),(0xBD,0xF4,0xAB),(0xB3,0xF3,0xCC),
    (0xB5,0xEB,0xF2),(0xB8,0xB8,0xB8),(0,0,0),(0,0,0),
)
PAL = _NES

BLACK   = (0, 0, 0)
WALL    = PAL[0x11]
DOOR    = PAL[0x25]
DOT     = PAL[0x36]
PELLET  = PAL[0x36]
PAC     = PAL[0x28]
GHOSTS  = (PAL[0x16], PAL[0x25], PAL[0x22], PAL[0x27])
FRIGHT  = PAL[0x12]
GOLD    = PAL[0x28]
MENU_HI = PAL[0x16]
WHITE   = (255, 255, 255)
RED     = PAL[0x16]
CYAN    = PAL[0x21]
PINK    = PAL[0x25]
GRAY    = PAL[0x00]

GHOST_NAMES  = ("SHADOW", "SPEEDY", "BASHFUL", "POKEY")
GHOST_ALIAS  = ("BLINKY", "PINKY", "INKY", "CLYDE")

# arcade fruit by level (1-indexed clamp)
FRUITS = (
    ("cherry", 100),
    ("straw", 300),
    ("orange", 500),
    ("apple", 700),
    ("melon", 1000),
    ("galaxian", 2000),
    ("bell", 3000),
    ("key", 5000),
)

# fright seconds by level (arcade-ish)
FRIGHT_SEC = (
    6.0, 5.0, 4.0, 3.0, 2.0, 5.0, 2.0, 2.0, 1.0, 5.0,
    2.0, 1.0, 1.0, 3.0, 1.0, 1.0, 0.0, 1.0,
)

# scatter/chase periods (seconds) — arcade table
MODE_WAVES = (7, 20, 7, 20, 5, 20, 5, float("inf"))

# tunnel tiles (slow ghosts)
TUNNEL = {(x, 14) for x in list(range(0, 6)) + list(range(22, 28))}

LAYOUT = (
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.##          ##.#     ",
    "     #.## ###--### ##.#     ",
    "######.## #      # ##.######",
    "      .   #      #   .      ",
    "######.## #      # ##.######",
    "     #.## ######## ##.#     ",
    "     #.##          ##.#     ",
    "     #.## ######## ##.#     ",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#o..##.......  .......##..o#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################",
)

# ── synth (2A03 square · hummer-cart sting) ──────────────────────────────
class Synth:
    RATE = 22050
    def __init__(self):
        self.ok = False
        self.muted = False
        self.s = {}
        try:
            pygame.mixer.pre_init(self.RATE, -16, 1, 256)
            pygame.mixer.init(self.RATE, -16, 1, 256)
            pygame.mixer.set_num_channels(4)
            self.ch = [pygame.mixer.Channel(i) for i in range(4)]
            self.ok = True
            self._build()
        except Exception:
            self.ok = False

    def _synth(self, dur, f, vol=0.18, sq=True):
        n = max(1, int(self.RATE * dur))
        buf = array("h")
        ph = 0.0
        for i in range(n):
            t = i / self.RATE
            fr = f(t) if callable(f) else f
            ph = (ph + max(0.0, fr) / self.RATE) % 1.0
            wv = 1.0 if ph < 0.5 else -1.0 if sq else 1.0 - 4.0 * abs(ph - 0.5)
            env = min(1.0, i / 60, (n - 1 - i) / 120)
            v = int(wv * env * vol * 32767)
            buf.append(max(-32768, min(32767, v)))
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _build(self):
        self.s["waka"]   = self._synth(0.07, lambda t: 240 + 520 * t)
        self.s["waka2"]  = self._synth(0.07, lambda t: 760 - 520 * t)
        self.s["pellet"] = self._synth(0.30, lambda t: 180 + 1400 * t)
        self.s["ghost"]  = self._synth(0.35, lambda t: 350 + 2200 * t + 65 * math.sin(t * 90))
        self.s["death"]  = self._synth(1.40, lambda t: max(50, 780 * (1 - t / 1.5) + 90 * math.sin(t * 60)), 0.20)
        self.s["fruit"]  = self._synth(0.25, lambda t: 880 if t < 0.12 else 1320, 0.16)
        self.s["menu"]   = self._synth(0.08, lambda t: 660, 0.14)
        self.s["sel"]    = self._synth(0.14, lambda t: 880 + 200 * t, 0.18)
        self.s["intro"]  = self._synth(0.45, lambda t: 520 + 700 * t, 0.16)
        self.s["extra"]  = self._synth(0.55, lambda t: 520 + 1200 * t, 0.22)
        self.s["clear"]  = self._synth(0.70, lambda t: 440 + 660 * t, 0.20)
        # TEAM FLAMES / hummer-style presents fanfare
        self.s["presents"] = self._synth(
            1.15,
            lambda t: (
                196 if t < 0.18 else 262 if t < 0.36 else 330 if t < 0.54
                else 392 if t < 0.78 else 523
            ),
            0.22,
        )
        self.s["credit"] = self._synth(0.12, lambda t: 880, 0.16)

    def play(self, name, ch=2):
        if self.ok and not self.muted and name in self.s:
            self.ch[ch].play(self.s[name])

    def toggle(self):
        self.muted = not self.muted
        if self.ok:
            for c in self.ch:
                c.stop()

# ── actors ───────────────────────────────────────────────────────────────
class Actor:
    __slots__ = ("tile", "direction", "target", "progress")
    def __init__(self, tile, direction=LEFT):
        self.tile = tile
        self.direction = direction
        self.target = None
        self.progress = 0.0

    @property
    def pos(self):
        if self.target is None:
            return self.tile
        return (self.tile[0] + self.direction[0] * self.progress,
                self.tile[1] + self.direction[1] * self.progress)

    def reverse(self):
        self.direction = OPP[self.direction]
        if self.target is not None:
            self.tile, self.target = self.target, self.tile
            self.progress = 1.0 - self.progress

    def move(self, dist, graph, choose, arrive=None):
        while dist > 1e-9:
            if self.target is None:
                d = choose(self)
                if d not in graph.get(self.tile, {}):
                    return
                self.direction = d
                self.target = graph[self.tile][d]
                self.progress = 0.0
            amt = min(dist, 1.0 - self.progress)
            self.progress += amt
            dist -= amt
            if self.progress >= 1.0 - 1e-9:
                self.tile = self.target
                self.target = None
                self.progress = 0.0
                if arrive and arrive(self) is False:
                    return

# ── maze ─────────────────────────────────────────────────────────────────
class Maze:
    def __init__(self):
        self.dots = {(x, y) for y, r in enumerate(LAYOUT) for x, c in enumerate(r) if c == "."}
        self.pellets = {(x, y) for y, r in enumerate(LAYOUT) for x, c in enumerate(r) if c == "o"}
        floor = {(x, y) for y, r in enumerate(LAYOUT) for x, c in enumerate(r) if c != "#"}
        doors = {(13, 12), (14, 12)}
        def flood(allowed):
            seen = {(13, 23)}
            q = [(13, 23)]
            while q:
                t = q.pop()
                for d in DIRS:
                    n = ((t[0] + d[0]) % COLS, t[1] + d[1])
                    if n in allowed and n not in seen:
                        seen.add(n)
                        q.append(n)
            return seen
        self.inside = flood(floor)
        self.outside = flood(floor - doors)
        self.total = len(self.dots) + len(self.pellets)
        self.graph = self._graph(self.outside)
        self.house = self._graph(self.inside)
        self.home_field = self._dist((13, 14), self.house)
        self.exit_field = self._dist((13, 11), self.house)
        self.walls = self._render()

    @staticmethod
    def _graph(tiles):
        g = {}
        for t in tiles:
            g[t] = {}
            for d in DIRS:
                n = ((t[0] + d[0]) % COLS, t[1] + d[1])
                if n in tiles:
                    g[t][d] = n
        return g

    @staticmethod
    def _dist(target, graph):
        out = {target: 0}
        q = [target]
        while q:
            t = q.pop()
            for n in graph.get(t, {}).values():
                if n not in out:
                    out[n] = out[t] + 1
                    q.append(n)
        return out

    def _render(self):
        s = pygame.Surface((W, H))
        s.fill(BLACK)
        for y, row in enumerate(LAYOUT):
            for x, c in enumerate(row):
                if c != "#":
                    continue
                px, py = x * TILE, TOP + y * TILE
                u = (x, y - 1) in self.inside
                d = (x, y + 1) in self.inside
                l = (x - 1, y) in self.inside
                r = (x + 1, y) in self.inside
                x0, x1 = px + (2 if l else 0), px + (5 if r else 7)
                y0, y1 = py + (2 if u else 0), py + (5 if d else 7)
                if u:
                    pygame.draw.line(s, WALL, (x0, py + 2), (x1, py + 2))
                if d:
                    pygame.draw.line(s, WALL, (x0, py + 5), (x1, py + 5))
                if l:
                    pygame.draw.line(s, WALL, (px + 2, y0), (px + 2, y1))
                if r:
                    pygame.draw.line(s, WALL, (px + 5, y0), (px + 5, y1))
        # ghost-house door
        pygame.draw.line(s, DOOR, (13 * TILE + 1, TOP + 12 * TILE + 3),
                         (15 * TILE - 1, TOP + 12 * TILE + 3), 2)
        return s

# ── ghosts ───────────────────────────────────────────────────────────────
class Ghost(Actor):
    # personal leave thresholds after a life loss
    LEAVE = (0, 0, 7, 17)

    def __init__(self, i):
        super().__init__(((13, 11), (13, 14), (11, 14), (15, 14))[i], LEFT if i == 0 else UP)
        self.i = i
        self.state = "normal" if i == 0 else "house"
        self.fright = False
        self.dot_count = 0
        self.wait = 0.0 if i == 0 else 0.4 + i * 0.15

# ── game ─────────────────────────────────────────────────────────────────
class Game:
    KILL = 256
    FRUIT_DOTS = (70, 170)
    EXTRA_LIFE = (10000,)

    def __init__(self, attract=False):
        self.maze = Maze()
        self.synth = None
        self.rng = random.Random(0xF1A3E5 if attract else None)
        self.attract = attract
        self.state = "intro"
        self.intro_t = 0.0
        self.timer = 0.0
        self.score = 0
        self.high = 0
        self.lives = 3 if not attract else 0
        self.level = 1
        self.next_extra = 0
        self.fruit_history = []
        self.global_dots = 0
        self.use_global = False
        self.popups = []  # (x, y, text, life)
        self.first_life = True
        self.reset(full=True)

    def fruit_idx(self):
        return min(len(FRUITS) - 1, max(0, self.level - 1) if self.level < 13 else 7)

    def fright_time(self):
        i = min(len(FRIGHT_SEC) - 1, self.level - 1)
        return FRIGHT_SEC[i]

    def reset(self, full=False):
        """full=True clears maze (new level / new game). False = life lost."""
        self.pac = Actor((13, 23), LEFT)
        self.queued = LEFT
        self.ghosts = [Ghost(i) for i in range(4)]
        if full:
            self.dots = set(self.maze.dots)
            self.pellets = set(self.maze.pellets)
            self.fruit_cleared = 0
            self.fruit_used = 0
            self.global_dots = 0
            self.use_global = False
            if self.level >= self.KILL:
                self._kill_screen()
        self.fright = 0.0
        self.mode_time = 0.0
        self.wave = 0
        self.mode = "scatter"
        self.chain = 0
        self.death = 0.0
        self.fruit_timer = 0.0
        self.fruit_score = 0
        self.fruit_pos = (13.5, 17)
        self.clear_t = 0.0
        self.popups = []
        if full and self.level >= self.KILL:
            pass

    def _kill_screen(self):
        rng = random.Random(0x100)
        for y in range(ROWS):
            for x in range(COLS // 2, COLS):
                if LAYOUT[y][x] != "#" and rng.random() < 0.40:
                    self.dots.add((x, y))
        for (x, y) in list(self.dots):
            if rng.random() < 0.30:
                self.dots.add((x, y))

    def remaining(self):
        return len(self.dots) + len(self.pellets)

    def eaten_count(self):
        return self.maze.total - self.remaining()

    def elroy(self):
        """Cruise Elroy stage for Blinky: 0 / 1 / 2."""
        left = self.remaining()
        if self.level == 1:
            t1, t2 = 20, 10
        elif self.level < 5:
            t1, t2 = 30, 15
        else:
            t1, t2 = 40, 20
        if left <= t2:
            return 2
        if left <= t1:
            return 1
        return 0

    def add_score(self, pts):
        if self.attract:
            return
        self.score += pts
        while self.next_extra < len(self.EXTRA_LIFE) and self.score >= self.EXTRA_LIFE[self.next_extra]:
            self.lives += 1
            self.next_extra += 1
            if self.synth:
                self.synth.play("extra")
        self.high = max(self.high, self.score)

    def popup(self, pos, text):
        self.popups.append([pos[0], pos[1], text, 1.0])

    def choose_pac(self, a):
        ch = self.maze.graph.get(a.tile, {})
        if self.queued in ch:
            return self.queued
        return a.direction if a.direction in ch else None

    def target(self, g):
        corners = ((25, -3), (2, -3), (27, 32), (0, 32))
        if self.mode == "scatter" and not (g.i == 0 and self.elroy() > 0):
            return corners[g.i]
        px, py = self.pac.tile
        dx, dy = self.pac.direction
        if g.i == 0:
            return (px, py)
        if g.i == 1:
            return (px + dx * 4 - (4 if dy == -1 else 0), py + dy * 4)
        if g.i == 2:
            ax, ay = px + dx * 2 - (2 if dy == -1 else 0), py + dy * 2
            bx, by = self.ghosts[0].tile
            return (2 * ax - bx, 2 * ay - by)
        if (g.tile[0] - px) ** 2 + (g.tile[1] - py) ** 2 >= 64:
            return (px, py)
        return corners[3]

    def choose_ghost(self, g):
        if g.state in ("eyes", "exit"):
            gr = self.maze.house.get(g.tile, {})
            field = self.maze.home_field if g.state == "eyes" else self.maze.exit_field
            if not gr:
                return None
            return min(gr, key=lambda d: field.get(gr[d], 9999))
        ch = self.maze.graph.get(g.tile, {})
        avail = [d for d in DIRS if d in ch and d != OPP[g.direction]]
        if not avail:
            back = OPP[g.direction]
            return back if back in ch else None
        if g.fright:
            return self.rng.choice(avail)
        # ghost preference: can't go UP at these tiles (arcade)
        if g.tile in ((12, 11), (15, 11), (12, 23), (15, 23)):
            f = [d for d in avail if d != UP]
            if f:
                avail = f
        t = self.target(g)
        return min(avail, key=lambda d: (ch[d][0] - t[0]) ** 2 + (ch[d][1] - t[1]) ** 2)

    def arrive_ghost(self, g):
        if g.state == "eyes" and g.tile == (13, 14):
            g.state = "house"
            g.fright = False
            g.wait = 0.35
            g.dot_count = 0
            return False
        if g.state == "exit" and g.tile == (13, 11):
            g.state = "normal"
            g.direction = LEFT
            return False
        return True

    def maybe_release(self, g):
        if g.state != "house" or g.wait > 0:
            return
        if self.use_global:
            # after a death: global dots (Inky 7 / Clyde 17 simplified → then free)
            if self.level >= 3:
                need = 0
            elif self.level == 2:
                need = (0, 0, 0, 50)[g.i]
            else:
                need = (0, 0, 7, 17)[g.i]
            if self.global_dots >= need:
                g.state = "exit"
            return
        # first life of a level: arcade 0 / 0 / 30 / 60
        need = (0, 0, 30, 60)[g.i]
        if g.dot_count >= need or (g.i <= 1 and g.wait <= 0):
            g.state = "exit"

    def pac_speed(self):
        if self.level == 1:
            sp = 7.6
        elif self.level < 5:
            sp = 8.55
        elif self.level < 21:
            sp = 9.5
        else:
            sp = 8.55
        if self.fright > 0:
            sp *= 1.07
        return sp

    def ghost_speed(self, g):
        if g.state == "eyes":
            return 15.0
        if g.state == "exit":
            return 4.0
        if self.level == 1:
            sp = 7.15
        elif self.level < 5:
            sp = 8.1
        else:
            sp = 9.05
        if g.i == 0:
            e = self.elroy()
            if e == 1:
                sp *= 1.05
            elif e == 2:
                sp *= 1.10
        if g.fright:
            sp *= 0.55
        if g.tile in TUNNEL or (g.target in TUNNEL if g.target else False):
            sp *= 0.50
        return sp

    def update_ghost(self, g, dt):
        if g.state == "house":
            g.wait = max(0.0, g.wait - dt)
            self.maybe_release(g)
            if g.state == "house":
                # bob in house
                return
        sp = self.ghost_speed(g)
        graph = self.maze.house if g.state in ("eyes", "exit", "house") else self.maze.graph
        if g.state == "house":
            return
        g.move(sp * dt, graph, self.choose_ghost, self.arrive_ghost)

    def update(self, dt):
        self.timer += dt
        # score popups
        for p in self.popups:
            p[3] -= dt
            p[1] -= dt * 0.6
        self.popups = [p for p in self.popups if p[3] > 0]

        if self.state == "intro":
            self.intro_t += dt
            # full Namco attract board (~ghosts + pts + chase) before READY
            hold = 9.5 if self.attract else 8.5
            if self.intro_t >= hold:
                self.state = "ready"
                self.timer = 0.0
            return
        if self.state == "ready":
            if self.timer >= (1.5 if self.attract else 2.0):
                self.state = "play"
                self.timer = 0.0
            return
        if self.state == "clear":
            self.clear_t += dt
            if self.clear_t >= 2.0:
                self.level += 1
                self.first_life = False
                self.reset(full=True)
                self.state = "ready"
                self.timer = 0.0
                if self.synth:
                    self.synth.play("intro")
            return
        if self.state == "dying":
            self.death += dt
            if self.death > 1.5:
                if self.attract:
                    self.state = "over"
                    return
                self.lives -= 1
                if self.lives <= 0:
                    self.state = "over"
                    self.timer = 0.0
                else:
                    self.use_global = True
                    self.global_dots = 0
                    self.reset(full=False)
                    self.state = "ready"
                    self.timer = 0.0
            return
        if self.state == "over":
            return

        if self.fruit_timer > 0:
            self.fruit_timer = max(0.0, self.fruit_timer - dt)

        if self.fright > 0:
            self.fright = max(0.0, self.fright - dt)
            if self.fright == 0:
                for g in self.ghosts:
                    g.fright = False
        else:
            self.mode_time += dt
            if self.mode_time >= MODE_WAVES[self.wave]:
                self.mode_time = 0.0
                self.wave = min(self.wave + 1, 7)
                self.mode = "scatter" if self.wave % 2 == 0 else "chase"
                for g in self.ghosts:
                    if g.state == "normal":
                        g.reverse()

        # attract: random-ish queued turns
        if self.attract and self.timer > 0.4:
            if self.rng.random() < 0.04:
                ch = self.maze.graph.get(self.pac.tile, {})
                if ch:
                    self.queued = self.rng.choice(list(ch.keys()))

        if self.queued == OPP[self.pac.direction]:
            self.pac.reverse()
        self.pac.move(self.pac_speed() * dt, self.maze.graph, self.choose_pac, self.eat)
        for g in self.ghosts:
            self.update_ghost(g, dt)
        self.collide()

        if self.fruit_timer > 0:
            fx, fy = self.fruit_pos
            px, py = self.pac.pos
            if abs(px - fx) < 0.9 and abs(py - fy) < 0.7:
                idx = self.fruit_idx()
                pts = FRUITS[idx][1]
                self.add_score(pts)
                self.fruit_score = pts
                self.fruit_timer = 0.0
                self.popup((fx, fy), str(pts))
                if self.synth:
                    self.synth.play("fruit")

        if self.attract and self.timer > 25.0:
            self.state = "over"

    def _credit_dot(self, ghost_i=None):
        """Increment release counters when a pellet/dot is eaten."""
        self.fruit_cleared += 1
        self.global_dots += 1
        if not self.use_global:
            # credit the first house ghost that still needs dots
            for g in self.ghosts:
                if g.state == "house" and g.i > 0:
                    g.dot_count += 1
                    break

    def eat(self, a):
        t = a.tile
        if t in self.dots:
            self.dots.discard(t)
            self.add_score(10)
            if self.synth:
                self.synth.play("waka" if self.score % 20 == 0 else "waka2", 1)
        elif t in self.pellets:
            self.pellets.discard(t)
            self.add_score(50)
            ft = self.fright_time()
            self.fright = ft
            self.chain = 0
            if ft > 0:
                for g in self.ghosts:
                    if g.state != "eyes":
                        g.fright = True
                        if g.state == "normal":
                            g.reverse()
            if self.synth:
                self.synth.play("pellet")
        else:
            return True
        self._credit_dot()
        if self.level < self.KILL:
            if self.fruit_cleared in self.FRUIT_DOTS and self.fruit_used < 2:
                self.fruit_used += 1
                self.fruit_timer = 9.0 + self.rng.random() * 0.5
                kind = FRUITS[self.fruit_idx()][0]
                self.fruit_history.append(kind)
                if len(self.fruit_history) > 7:
                    self.fruit_history.pop(0)
        if self.remaining() == 0 and self.level < self.KILL and not self.attract:
            self.state = "clear"
            self.clear_t = 0.0
            if self.synth:
                self.synth.play("clear")
            return False
        return False

    def collide(self):
        px, py = self.pac.pos
        for g in self.ghosts:
            if g.state != "normal":
                continue
            gx, gy = g.pos
            dx = abs(px - gx)
            dx = min(dx, COLS - dx)
            if dx * dx + (py - gy) ** 2 >= 0.64 ** 2:
                continue
            if g.fright:
                self.chain += 1
                pts = 200 * 2 ** min(3, self.chain - 1)
                self.add_score(pts)
                self.popup((gx, gy), str(pts))
                g.state = "eyes"
                g.fright = False
                if self.synth:
                    self.synth.play("ghost")
            else:
                self.state = "dying"
                self.death = 0.0
                if self.synth:
                    self.synth.play("death")
                return

    def key(self, k):
        if self.attract:
            return
        m = {pygame.K_UP: UP, pygame.K_w: UP, pygame.K_LEFT: LEFT, pygame.K_a: LEFT,
             pygame.K_DOWN: DOWN, pygame.K_s: DOWN, pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT}
        if k in m:
            self.queued = m[k]

# ── draw helpers ─────────────────────────────────────────────────────────
def draw_pac(s, x, y, d, t, death=None, r=6, color=None):
    col = color if color else PAC
    ang = math.atan2(d[1], d[0])
    m = 0.08 + 0.65 * abs(math.sin(t * 15))
    if death is not None:
        if death >= 1:
            return
        ang = -math.pi / 2
        m = min(math.pi - 0.01, death * math.pi)
    pts = [(round(x), round(y))]
    for i in range(33):
        a = ang + m + (math.tau - 2 * m) * i / 32
        pts.append((round(x + math.cos(a) * r), round(y + math.sin(a) * r)))
    pygame.draw.polygon(s, col, pts)

def draw_ghost(s, x, y, i, d, t, fear=False, flash=False, eyes=False, r=6):
    x, y, r = round(x), round(y), r
    col = (255, 255, 255) if flash else (FRIGHT if fear else GHOSTS[i])
    if not eyes:
        pygame.draw.circle(s, col, (x, y - 1), r)
        pygame.draw.rect(s, col, (x - r, y - 1, r * 2 + 1, r + 1))
        off = int(t * 10) % 2
        feet = [(x - r, y + 1), (x + r, y + 1)]
        feet += [(x + r - k * r / 3, y + r - (2 if (k + off) % 2 else 0)) for k in range(7)]
        pygame.draw.polygon(s, col, feet)
    if fear and not eyes:
        ink = (255, 65, 65) if flash else (255, 255, 255)
        for dx in (-2, 2):
            pygame.draw.rect(s, ink, (x + dx - 1, y - 2, 2, 2))
        pygame.draw.lines(s, ink, False, [(x - 4 + k, y + 3 + k % 2) for k in range(9)])
    else:
        for dx in (-3, 3):
            pygame.draw.ellipse(s, (255, 255, 255), (x + dx - 2, y - 4, 5, 6))
            pygame.draw.rect(s, (25, 60, 230), (x + dx - 1 + d[0], y - 2 + d[1], 2, 3))

def draw_fruit(s, x, y, kind, r=5):
    x, y = round(x), round(y)
    if kind == "cherry":
        pygame.draw.circle(s, RED, (x - 2, y + 1), r - 1)
        pygame.draw.circle(s, RED, (x + 3, y + 2), r - 1)
        pygame.draw.line(s, PAL[0x19], (x - 2, y - 1), (x + 1, y - 4), 1)
        pygame.draw.line(s, PAL[0x19], (x + 3, y), (x + 1, y - 4), 1)
    elif kind == "straw":
        pygame.draw.polygon(s, RED, [(x, y + r), (x - r, y - 2), (x + r, y - 2)])
        pygame.draw.rect(s, PAL[0x19], (x - 1, y - r, 3, 3))
    elif kind == "orange":
        pygame.draw.circle(s, PAL[0x27], (x, y), r)
        pygame.draw.rect(s, PAL[0x19], (x - 1, y - r, 2, 3))
    elif kind == "apple":
        pygame.draw.circle(s, RED, (x, y + 1), r)
        pygame.draw.rect(s, PAL[0x19], (x - 1, y - r + 1, 2, 3))
    elif kind == "melon":
        pygame.draw.ellipse(s, PAL[0x19], (x - r, y - r + 1, r * 2, r * 2 - 1))
        pygame.draw.line(s, PAL[0x29], (x, y - r + 2), (x, y + r - 1), 1)
    elif kind == "galaxian":
        pygame.draw.polygon(s, GOLD, [(x, y - r), (x - r, y + 2), (x, y), (x + r, y + 2)])
        pygame.draw.polygon(s, RED, [(x, y - 2), (x - 3, y + r), (x + 3, y + r)])
    elif kind == "bell":
        pygame.draw.circle(s, GOLD, (x, y - 1), r - 1)
        pygame.draw.rect(s, GOLD, (x - r + 1, y - 1, (r - 1) * 2, r))
        pygame.draw.rect(s, WHITE, (x - 1, y + r - 2, 3, 2))
    else:  # key
        pygame.draw.circle(s, CYAN, (x - 1, y - 2), 3)
        pygame.draw.rect(s, CYAN, (x, y - 1, 5, 2))
        pygame.draw.rect(s, CYAN, (x + 3, y + 1, 2, 3))

# ── fonts ────────────────────────────────────────────────────────────────
BIG = MED = SML = TINY = None

def init_fonts():
    global BIG, MED, SML, TINY
    BIG = pygame.font.Font(None, 48)
    MED = pygame.font.Font(None, 22)
    SML = pygame.font.Font(None, 14)
    TINY = pygame.font.Font(None, 12)

def text_center(s, msg, font, color, y):
    img = font.render(msg, True, color)
    s.blit(img, (W // 2 - img.get_width() // 2, y))

def text_left(s, msg, font, color, x, y):
    s.blit(font.render(msg, True, color), (x, y))

def text_right(s, msg, font, color, x, y):
    img = font.render(msg, True, color)
    s.blit(img, (x - img.get_width(), y))

# ── HUD ──────────────────────────────────────────────────────────────────
def draw_hud(s, g):
    text_left(s, "1UP", SML, WHITE, 4, 2)
    blink = int(g.timer * 4) % 2 == 0
    if blink or g.state != "play":
        text_left(s, f"{g.score:06d}", SML, WHITE, 4, 12)
    text_center(s, "HIGH SCORE", SML, WHITE, 2)
    text_center(s, f"{g.high:06d}", SML, WHITE, 12)
    text_right(s, f"LV{g.level:03d}", SML, GOLD, W - 4, 2)

    lx, ly = 6, H - 10
    show_lives = max(0, g.lives - (0 if g.state in ("dying", "over") else 1))
    for i in range(min(5, show_lives)):
        draw_pac(s, lx + i * 14, ly, LEFT, 0.07, r=5)

    fx = W - 6
    for i, kind in enumerate(reversed(g.fruit_history[-7:])):
        draw_fruit(s, fx - i * 14 - 6, ly, kind, r=5)

    if g.fruit_timer > 0:
        kind = FRUITS[g.fruit_idx()][0]
        cx, cy = g.fruit_pos
        draw_fruit(s, cx * TILE, TOP + cy * TILE, kind, r=5)

    for px, py, txt, life in g.popups:
        col = GOLD if life > 0.4 else WHITE
        img = TINY.render(txt, True, col)
        s.blit(img, (int(px * TILE + 4 - img.get_width() // 2),
                     int(TOP + py * TILE)))

# ── team flames presents ─────────────────────────────────────────────────
# ref: Somari / The Hummer "TEAM ___ PRESENTS" (yt: PAcBMm0xXPk, DNRBcjhT2Wc)
# layout = Sonic Team Presents cart card: black · red TEAM line · white PRESENTS
PRESENTS_HOLD = 3.4

def draw_presents(s, t):
    s.fill(BLACK)
    # hold black a beat (cart boot silence), then hard pop — no soft fade
    if t < 0.40:
        return
    # TEAM FLAMES in red (Hummer/Somari red logo line)
    text_center(s, "TEAM FLAMES", BIG, RED, H // 2 - 28)
    if t >= 0.95:
        # PRESENTS in white, slightly smaller, centered under team
        text_center(s, "PRESENTS", MED, WHITE, H // 2 + 12)
    # hard cut to black frames at end (NES blanking feel)
    if t >= PRESENTS_HOLD - 0.40 and int(t * 18) % 2 == 0:
        s.fill(BLACK)

# ── ghost intro / attract board ──────────────────────────────────────────
# ref: Pac-Man Namco 1980 attract (yt: W5yeZSOEFq4, dScq4P5gn4A)
# CHARACTER / NICKNAME → ghosts → 10 pts / 50 pts → chase demo

def draw_ghost_intro(s, game, t):
    s.fill(BLACK)
    # top credit strip like Midway board (yt attract: W5yeZSOEFq4)
    text_left(s, "1UP", SML, WHITE, 24, 2)
    text_left(s, "00", SML, WHITE, 28, 12)
    text_center(s, "HIGH SCORE", SML, WHITE, 2)
    text_center(s, "00", SML, WHITE, 12)

    text_center(s, "CHARACTER / NICKNAME", MED, GOLD, 36)

    reveal = min(4, int(t / 0.90))
    for i in range(4):
        y = 58 + i * 32
        show = i < reveal or (i == reveal and int(t * 10) % 2 == 0)
        if show and i <= reveal:
            draw_ghost(s, 36, y + 8, i, LEFT, t, r=8)
            # arcade uses -SHADOW  /  "BLINKY" coloring
            text_left(s, f"-{GHOST_NAMES[i]}", SML, GHOSTS[i], 56, y)
            text_left(s, f'"{GHOST_ALIAS[i]}"', MED, GHOSTS[i], 56, y + 12)

    # point legend (after ghosts) — from attract board
    if t >= 4.0:
        # 10 pts dot
        pygame.draw.rect(s, DOT, (W // 2 - 40, 196, 2, 2))
        text_left(s, "10 pts", SML, WHITE, W // 2 - 28, 192)
        # 50 pts energizer
        pygame.draw.circle(s, PELLET, (W // 2 - 39, 212), 4)
        text_left(s, "50 pts", SML, WHITE, W // 2 - 28, 208)

    # chase strip along bottom (pac flees, then fright reverse)
    if t >= 5.2:
        phase = t - 5.2
        y = H - 36
        if phase < 3.0:
            # ghosts chase pac left→right
            px = -20 + phase * 90
            draw_pac(s, px, y, RIGHT, t, r=7)
            for i in range(4):
                draw_ghost(s, px - 24 - i * 20, y, i, RIGHT, t, r=7)
        else:
            # pellet flash + pac chases frightened ghosts right→left
            px = W + 20 - (phase - 3.0) * 90
            draw_pac(s, px, y, LEFT, t, r=7)
            for i in range(4):
                draw_ghost(s, px + 24 + i * 20, y, i, LEFT, t, fear=True, r=7)

    if not game.attract:
        text_center(s, "ENTER SKIP", TINY, GRAY, H - 12)
        text_center(s, f"LEVEL {game.level:03d}", TINY, GRAY, H - 24)
    else:
        text_center(s, "TEAM FLAMES  1999", TINY, GRAY, H - 12)

# ── menus / title (hummer title board) ───────────────────────────────────
MENU_ITEMS = ("1 PLAYER", "HELP", "ABOUT", "EXIT")

class Menu:
    def __init__(self):
        self.idx = 0
        self.t = 0.0
        self.state = "main"
        self.idle = 0.0

    def key(self, k, synth):
        self.idle = 0.0
        if self.state != "main":
            if k in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE, pygame.K_BACKSPACE):
                self.state = "main"
                synth.play("menu")
            return None
        if k in (pygame.K_UP, pygame.K_w):
            self.idx = (self.idx - 1) % len(MENU_ITEMS)
            synth.play("menu")
        elif k in (pygame.K_DOWN, pygame.K_s):
            self.idx = (self.idx + 1) % len(MENU_ITEMS)
            synth.play("menu")
        elif k in (pygame.K_RETURN, pygame.K_SPACE):
            synth.play("sel")
            item = MENU_ITEMS[self.idx]
            if item == "1 PLAYER":
                return "play"
            if item == "HELP":
                self.state = "help"
            if item == "ABOUT":
                self.state = "about"
            if item == "EXIT":
                return "quit"
        return None

    def update(self, dt):
        self.t += dt
        if self.state == "main":
            self.idle += dt
            if self.idle >= 12.0:
                self.idle = 0.0
                return "attract"
        return None

    def draw(self, s):
        s.fill(BLACK)
        # Hummer-cart title board: red TEAM strip, big title, copyright footer
        # ref yt: PAcBMm0xXPk (The Hummer), DNRBcjhT2Wc (Somari)
        text_center(s, "TEAM FLAMES", SML, RED, 16)
        text_center(s, "PRESENTS", TINY, WHITE, 30)
        text_center(s, "PAC-MAN", BIG, GOLD, 48)
        text_center(s, "ULTRA", MED, WHITE, 88)
        # thin red rules like multicart banners
        pygame.draw.line(s, RED, (24, 42), (W - 24, 42), 1)
        pygame.draw.line(s, RED, (24, 108), (W - 24, 108), 1)
        text_center(s, "files=off  sfx=2A03", TINY, GRAY, 114)

        if self.state == "main":
            for i, label in enumerate(MENU_ITEMS):
                y = 132 + i * 20
                if i == self.idx:
                    txt = MED.render("* " + label + " *", True, MENU_HI)
                    if int(self.t * 6) % 2 == 0:
                        s.blit(txt, (W // 2 - txt.get_width() // 2, y))
                else:
                    txt = MED.render(label, True, WHITE)
                    s.blit(txt, (W // 2 - txt.get_width() // 2, y))
            # parade — Pac chased by ghosts (arcade attract motif)
            px = (int(self.t * 40) % (W + 80)) - 30
            draw_pac(s, px, H - 52, RIGHT, self.t, r=7)
            for i in range(4):
                draw_ghost(s, px - 26 - i * 20, H - 52, i, RIGHT, self.t, r=7)
            text_center(s, "PRESS START", SML, GOLD if int(self.t * 3) % 2 == 0 else GRAY, H - 34)
            text_center(s, "(C)1999-2026 TEAM FLAMES", TINY, GRAY, H - 18)
        elif self.state == "help":
            text_center(s, "HELP", BIG, GOLD, 20)
            lines = (
                "ARROWS / WASD .. MOVE",
                "M .............. MUTE",
                "ESC ............ BACK",
                "",
                "EAT ALL DOTS",
                "POWER PELLET = FRIGHT",
                "200 400 800 1600",
                "FRUIT AT 70 / 170",
                "ELROY WHEN LOW DOTS",
                "LEVEL 256 = KILL",
                "",
                "ENTER / ESC",
            )
            for i, line in enumerate(lines):
                text_center(s, line, SML, WHITE if line and line[0].isalpha() else GRAY, 70 + i * 13)
        elif self.state == "about":
            text_center(s, "ABOUT", BIG, GOLD, 20)
            lines = (
                "TEAM FLAMES PRESENTS",
                "AC'S PACMAN ULTRA 0.1",
                "",
                "FULL ARCADE ENGINE",
                "SCATTER / CHASE / FRIGHT",
                "GHOST HOUSE + EYES",
                "TUNNEL SLOW · ELROY",
                "FRUIT · EXTRA LIFE",
                "KILL SCREEN 256",
                "",
                "HUMMER-TEAM STYLE SHELL",
                "FILES = OFF · NO ROM",
                "",
                "AC · ACHOLDING",
            )
            for i, line in enumerate(lines):
                col = RED if "TEAM FLAMES" in line else (GOLD if i < 2 else GRAY)
                text_center(s, line, SML, col, 58 + i * 13)

# ── in-game render ───────────────────────────────────────────────────────
def draw_game(canvas, g):
    canvas.fill(BLACK)
    # level-clear flash walls white
    if g.state == "clear" and int(g.clear_t * 8) % 2 == 0:
        flash = g.maze.walls.copy()
        flash.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
        canvas.blit(g.maze.walls, (0, 0))
        # white outline flash
        for y, row in enumerate(LAYOUT):
            for x, c in enumerate(row):
                if c == "#":
                    pygame.draw.rect(canvas, WHITE, (x * TILE + 2, TOP + y * TILE + 2, 4, 4))
    else:
        canvas.blit(g.maze.walls, (0, 0))

    for (x, y) in g.dots:
        pygame.draw.rect(canvas, DOT, (x * TILE + 3, TOP + y * TILE + 3, 2, 2))
    if int(g.timer * 4) % 2 == 0:
        for (x, y) in g.pellets:
            pygame.draw.circle(canvas, PELLET, (x * TILE + 4, TOP + y * TILE + 4), 4)

    if g.state != "dying" or g.death < 0.35:
        for gh in g.ghosts:
            if g.state == "dying":
                break
            gx, gy = gh.pos
            flash = gh.fright and g.fright < 2 and int(g.timer * 8) % 2 == 0
            for off in (-W, 0, W):
                draw_ghost(canvas, gx * TILE + 4 + off, TOP + gy * TILE + 4, gh.i, gh.direction, g.timer,
                           fear=gh.fright, flash=flash, eyes=(gh.state == "eyes"))

    if g.state != "clear":
        px, py = g.pac.pos
        dth = max(0.0, (g.death - 0.35) / 1.1) if g.state == "dying" else None
        for off in (-W, 0, W):
            draw_pac(canvas, px * TILE + 4 + off, TOP + py * TILE + 4, g.pac.direction, g.timer, death=dth)

    draw_hud(canvas, g)

    if g.level >= Game.KILL:
        warn = SML.render("KILL SCREEN", True, RED)
        canvas.blit(warn, (W // 2 - warn.get_width() // 2, TOP + 6))

    if g.state == "ready":
        txt = SML.render("READY!", True, GOLD)
        canvas.blit(txt, (W // 2 - txt.get_width() // 2, TOP + 17 * TILE))
        if g.attract:
            text_center(canvas, "GAME  OVER", SML, RED, TOP + 14 * TILE)
    elif g.state == "over":
        txt = SML.render("GAME OVER", True, RED)
        canvas.blit(txt, (W // 2 - txt.get_width() // 2, TOP + 17 * TILE))
        if not g.attract:
            text_center(canvas, "ESC = MENU", TINY, GRAY, TOP + 19 * TILE)
    elif g.state == "clear":
        txt = SML.render("LEVEL CLEAR", True, GOLD)
        canvas.blit(txt, (W // 2 - txt.get_width() // 2, TOP + 17 * TILE))

# ── main ─────────────────────────────────────────────────────────────────
def main():
    pygame.display.set_caption("TEAM FLAMES — AC's PACMAN")
    screen = pygame.display.set_mode((W * SC, H * SC), pygame.RESIZABLE)
    canvas = pygame.Surface((W, H))
    clock = pygame.time.Clock()
    init_fonts()
    menu = Menu()
    synth = Synth()
    game = None
    high = 0
    mode = "presents"
    presents_t = 0.0
    synth.play("presents")
    acc = 0.0
    run = True
    while run:
        dt = min(clock.tick(FPS) / 1000.0, 0.1)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    synth.toggle()
                    continue
                if mode == "presents":
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                        mode = "menu"
                        presents_t = PRESENTS_HOLD
                        synth.play("credit")
                elif mode == "menu":
                    action = menu.key(e.key, synth)
                    if action == "play":
                        game = Game()
                        game.synth = synth
                        game.high = high
                        synth.play("intro")
                        mode = "game"
                    elif action == "quit":
                        run = False
                elif mode == "attract":
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                        mode = "menu"
                        menu.idle = 0.0
                        synth.play("credit")
                else:
                    if e.key == pygame.K_ESCAPE:
                        if game:
                            high = max(high, game.score, game.high)
                        mode = "menu"
                        menu.state = "main"
                        menu.idx = 0
                        menu.idle = 0.0
                    elif game.state == "intro" and e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game.state = "ready"
                        game.timer = 0.0
                    elif game.state == "over" and e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        high = max(high, game.score, game.high)
                        mode = "menu"
                        menu.idle = 0.0
                    else:
                        game.key(e.key)

        acc += dt
        while acc >= STEP:
            if mode == "presents":
                presents_t += STEP
                if presents_t >= PRESENTS_HOLD:
                    mode = "menu"
            elif mode == "menu":
                act = menu.update(STEP)
                if act == "attract":
                    game = Game(attract=True)
                    game.synth = None
                    game.high = high
                    mode = "attract"
            elif mode in ("game", "attract"):
                game.update(STEP)
                if mode == "attract" and game.state == "over":
                    mode = "menu"
                    menu.idle = 0.0
                if mode == "game" and game:
                    high = max(high, game.score, game.high)
                    game.high = high
            acc -= STEP

        if mode == "presents":
            draw_presents(canvas, presents_t)
        elif mode == "menu":
            menu.draw(canvas)
        elif mode == "attract":
            if game.state == "intro":
                draw_ghost_intro(canvas, game, game.intro_t)
            else:
                draw_game(canvas, game)
            text_center(canvas, "ATTRACT", TINY, GRAY, H - 8)
        elif game.state == "intro":
            draw_ghost_intro(canvas, game, game.intro_t)
        else:
            draw_game(canvas, game)

        sw, sh = screen.get_size()
        f = max(1, min(sw // W, sh // H))
        size = (W * f, H * f)
        screen.fill(BLACK)
        screen.blit(pygame.transform.scale(canvas, size), ((sw - size[0]) // 2, (sh - size[1]) // 2))
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
