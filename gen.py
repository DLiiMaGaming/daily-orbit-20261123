# gen.py — draws the Daily Orbit front page for Monday 23 November 2026.
# Pure Python standard library. Deterministic: same bytes on every run.
# Run:  python3 gen.py   (writes entry.png next to this file)
import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette (newsprint) ----
PAPER = (246, 241, 227)
INK = (20, 20, 20)
RED = (176, 42, 30)
BLUE = (29, 78, 137)
TEAL = (14, 110, 105)
GOLD = (176, 132, 20)
GREY = (110, 106, 96)
LIGHT = (232, 226, 208)
WHITE = (255, 255, 255)
SEA = (168, 198, 214)
LAND = (222, 208, 170)

# ---- 5x7 bitmap font (uppercase + digits + punctuation) ----
# Each glyph: 7 rows of 5 bits, '#' = on.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '>': ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    '<': ("00001", "00010", "00100", "01000", "00100", "00010", "00001"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        if fill:
            for dy in range(-r, r + 1):
                dx = int((r * r - dy * dy) ** 0.5)
                self.fill_rect(cx - dx, cy + dy, dx * 2 + 1, 1, c)
        else:
            for a in range(360):
                import math
                self.set(cx + int(r * math.cos(math.radians(a))),
                         cy + int(r * math.sin(math.radians(a))), c)

    def poly(self, pts, c):
        # scanline fill of a simple polygon
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, c)

    def text(self, x, y, s, scale=1, c=INK):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch)
            if g is None:
                ch2 = {'—': '-', '–': '-', '’': "'", '‘': "'", '“': '"',
                       '”': '"', '…': '.', '•': '*', '·': '.', '×': 'X',
                       '°': 'O'}.get(ch)
                g = FONT.get(ch2, FONT[' ']) if ch2 else FONT[' ']
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale=1, c=INK):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, max_chars):
        words = s.split(' ')
        lines, cur = [], ''
        for w in words:
            if cur and len(cur) + 1 + len(w) > max_chars:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + ' ' + w).strip()
        if cur:
            lines.append(cur)
        return lines


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        out += struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        return out

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', comp) + chunk(b'IEND', b''))

# ---- THE DAY'S NEWS: 50 stories, each verified to 23 November 2026 ----
# (headline, deck with source, region)
# Regions: NA North America, LA Latin America, EU Europe, ME Middle East,
#          AF Africa, AS Asia, OC Oceania
STORIES = [
    ("COP31 ENDS WITH NO DEAL", "Closed Sun 22 Nov; Mon: UN chief 'deeply disappointed' - UN NEWS/AP", "EU"),
    ("RUSSIAN STRIKE KILLS 11 IN DYMER", "Boy, 7, pulled alive from rubble; drones hit Kyiv schools at dawn - REUTERS/BBC", "EU"),
    ("UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA", "Zelensky: 7 sea drones sank Merkury at Benghazi - FRANCE 24/BBC", "AF"),
    ("NIKKEI -5.06%, S&P 500 -3.7% IN AI SELL-OFF", "Tech rout spreads across Asia; gold +3.14% as investors flee to safety - ONETURN", "AS"),
    ("DEMOCRATS WIN BIGGEST HOUSE MAJORITY SINCE 1992", "Recount confirms Hubbard win in N. Carolina; Dems hold 258 seats - BBC", "NA"),
    ("NVIDIA CHIP PROBE WIDENS", "US investigates Megaspeed, Alice Huang over chip sales to China - GEORGE/ONETURN", "NA"),
    ("TRUMP SIGNS COMMON CENTS ACT", "Penny's 232-year run ends as coin is retired - GEORGE", "NA"),
    ("DRONE STRIKES KILL 5 CHILDREN IN KHARTOUM", "Homes destroyed, UN building damaged in Khartoum and Omdurman - FRANCE 24", "AF"),
    ("PARAMILITARY ATTACK KILLS 24 IN SOUTH SUDAN", "Civilians killed in latest paramilitary assault - ONETURN", "AF"),
    ("HOUTHIS CLAIM STRIKE ON SAUDI REFINERY", "Saudi strike hits Hodeida in reply - ONETURN", "ME"),
    ("SETTLER ARSON IN WEST BANK CONDEMNED", "Eisenkot calls attacks 'Jewish terrorism' as villages raided - FRANCE 24", "ME"),
    ("GAZA WAR LEFT WIDESPREAD CONTAMINATION", "Experts: toxic wasteland after assault, new report says - ONETURN", "ME"),
    ("BAHRAIN ACCUSES IRAN OF STRIKING CIVILIAN SITE", "Two tankers hit in Strait of Hormuz - FRANCE 24", "ME"),
    ("IRAN VOWS 'ALL MEANS' AGAINST US BLOCKADE", "Tehran warns as pressure mounts - ONETURN", "ME"),
    ("NETANYAHU, EISENKOT END COALITION TALKS", "No deal in Israel as talks collapse - ONETURN", "ME"),
    ("RUSSIAN FREIGHTER ABLAZE IN BALTIC", "Sparta II hit by drone, drifts into Finnish waters - GEORGE/FRANCE 24", "EU"),
    ("DENMARK: RUSSIA PLOTTED TO KILL RAPPER", "Ukrainian-American rapper targeted, intelligence says - GEORGE", "EU"),
    ("NATO'S DILEMMA OVER PRIVATE TECH", "Militaries lean on private AI; sovereignty at stake - FRANCE 24", "EU"),
    ("THOUSANDS RALLY IN ISTANBUL VS MEDIA TAKEOVER", "Protesters march against press crackdown - ONETURN", "EU"),
    ("FIVE EU STATES BACK RWANDA DEPORTATION CENTRES", "Migration deal moves forward - ONETURN", "EU"),
    ("BURNHAM: EU DEAL COULD MAKE DECADE 'MUCH BETTER'", "UK PM tells MPs as reset advances - ONETURN", "EU"),
    ("DOJ ADMITS US CITIZEN DEPORTED TO MEXICO", "Justice Dept concedes wrongful removal - ONETURN", "NA"),
    ("ICE VIDEO SPARKS SEATTLE PROTESTS", "Father, daughter detained on camera - ONETURN", "NA"),
    ("US ARMY TO DETONATE EXPLOSIVES IN IOWA", "Unstable lead azide stockpile; court order defied - ONETURN", "NA"),
    ("NINE SHOT AT CALIFORNIA CONCERT", "Strathmore, central California - ONETURN", "NA"),
    ("NEPAL PM VISITS INDIA", "Balen Shah in Delhi; India pledges aid - ONETURN", "AS"),
    ("KENYA, DR CONGO AGREE TO RESTORE TIES", "Neighbours mend relations - ONETURN", "AF"),
    ("NIGERIA ENDS JAIL FOR ATTEMPTED SUICIDE", "Reform moves forward in Abuja - ONETURN", "AF"),
    ("FIGHTING NEAR EBOLA AREA DISRUPTS RESPONSE", "Eastern DR Congo outbreak work hit - ONETURN", "AF"),
    ("SOUTH KOREA EXPORTS TOP $1 TRILLION", "First time ever; 4th economy to do so, on AI chip demand - SIMPLELIFE", "AS"),
    ("TAIWAN BANS SHORT SELLING BELOW CLOSE", "Stocks swing 1,578 pts intraday; TSMC +2% - EVENTGRAPH", "AS"),
    ("BELGIAN AIRPORTS SHUT BY STRIKE", "Anti-austerity walkout grounds flights - ONETURN", "EU"),
    ("CAPITA SHARES PLUNGE 67% AS BOSS QUITS", "London outsourcing giant in freefall - ONETURN", "EU"),
    ("CONOCOPHILLIPS EXITS NORWAY IN $4.4BN DEAL", "Energy major sells out of Stavanger - ONETURN", "EU"),
    ("TATA STEEL BUYS $1.67BN STAKE IN APL APOLLO", "India's top steel pipe maker - ONETURN", "AS"),
    ("SOUTH KOREA MINISTER QUITS OVER EXAM CHEATING", "AI-driven scandal ends tenure - FRANCE 24", "AS"),
    ("FRANCE CANDIDATES QUESTION UKRAINE AID", "Leading hopefuls split ahead of spring vote - SIMPLELIFE", "EU"),
    ("LE PEN DENIES LEAKED-INFO TIP", "From French interior ministry official - SIMPLELIFE", "EU"),
    ("SYRIA, EU SEEK NORMALISATION", "Diplomats worry over migration focus - NEWSMEDIAHOUSE", "ME"),
    ("RIEMANN PROOF CONFIRMED", "Lean, Mathlib verify Alpoge proof; 160-year problem falls - EVENTGRAPH", "NA"),
    ("METR: AI OUTPACING SAFETY TESTING", "Task length doubles every 3.6 months - EVENTGRAPH", "NA"),
    ("OPENAI: PERPLEXITY AS SHARED AI METRIC", "Chief scientist proposes yardstick - EVENTGRAPH", "NA"),
    ("CHINESE HACKERS USE AI FRAMEWORK 'CAIRN'", "Suspected attacks on East Asian universities - SIMPLELIFE", "AS"),
    ("ROBOT SUB FINDS VOLCANOES IN MARIANA TRENCH", "Unprecedented activity on ocean floor - ONETURN", "OC"),
    ("LEWIS PUGH SWIMS STRAIT OF HORMUZ", "Endurance swim in tense waters - ONETURN", "ME"),
    ("SKUBAL AGREES RECORD $450M METS DEAL", "9 years; largest ever for a pitcher - AP", "NA"),
    ("GUKESH DEFENDS CHESS TITLE FROM TUESDAY", "Vs Sindarov in Geneva; youngest final ever - REUTERS", "EU"),
    ("OTTERS RETURN TO KUALA LUMPUR RIVER", "Once-polluted waterway revives - ONETURN", "AS"),
    ("NEPAL FIRST LOSS AND DAMAGE PAYOUT", "UN fund pays out for climate harm - ONETURN", "AS"),
    ("DOCTOR WHO: 63 YEARS AGO TODAY", "First episode aired 23 Nov 1963 - ONETURN", "EU"),
]

# ---- UTC timeline (approx. times, marked ~) ----
TIMELINE = [
    ("~00:00", "MONDAY OPENS IN ASIA: NIKKEI DIVES"),
    ("~02:00", "TAIWAN BANS SHORT SELLING"),
    ("~04:00", "DYMER: BOY, 7, PULLED ALIVE"),
    ("~06:00", "NIKKEI CLOSES -5.06%"),
    ("~09:00", "ZELENSKY CONFIRMS MERKURY SUNK"),
    ("~12:00", "GUTERRES: 'DEEPLY DISAPPOINTED'"),
    ("~14:00", "HUBBARD RECOUNT CONFIRMED"),
    ("~20:00", "TRUMP SIGNS PENNY ACT"),
]

# ---- DATE CHECK: stories left out because they are NOT 23 Nov ----
DATE_CHECK = [
    "SHENZHEN SUMMIT + 'DECLARATION TOWARD PEACE' - THU 19 NOV",
    "JENSEN HUANG RESIGNS AS NVIDIA CEO - THU 12 NOV (PROBES GO ON)",
    "'EL CHAPO ISIDRO' CAPTURED IN SINALOA - FRI 20 NOV",
    "BEPICOLOMBO REACHES MERCURY ORBIT - SAT 21 NOV",
    "BANTEN CANDY FACTORY FIRE, 24 KILLED - SAT 21 NOV",
    "ALCARAZ - MARQUEZ - LIVERPOOL 4-0 MAN UTD - NFL WK 11 - SUN 22 NOV",
]
DATE_CHECK_NOT_YET = ("NOT YET: WORLD CHESS CHAMPIONSHIP STARTS TUE 24 NOV - "
                      "THANKSGIVING THU 26 NOV - COP32 ADDIS ABABA")

NUMBERS = [
    ("NIKKEI", "-5.06%"),
    ("S&P 500", "-3.70%"),
    ("GOLD", "+3.14%"),
    ("DEM HOUSE SEATS", "258"),
    ("KILLED IN DYMER", "11"),
    ("KILLED, S. SUDAN", "24"),
    ("SKUBAL DEAL", "$450M"),
    ("KOREA EXPORTS", "$1T"),
]

# Map pins: (number, label, lon, lat)
PINS = [
    (1, "ANTALYA", 30.7, 36.9),
    (2, "DYMER", 30.5, 50.5),
    (3, "BENGHAZI", 20.1, 32.1),
    (4, "KHARTOUM", 32.5, 15.6),
    (5, "GAZA", 34.4, 31.5),
    (6, "HORMUZ", 56.5, 26.5),
    (7, "BRUSSELS", 4.4, 50.8),
    (8, "LONDON", -0.1, 51.5),
    (9, "WASHINGTON", -77.0, 38.9),
    (10, "BRASILIA", -47.9, -15.8),
    (11, "SEOUL", 127.0, 37.5),
    (12, "TAIPEI", 121.5, 25.0),
]

# Simplified continent polygons (lon, lat) for the equirectangular map.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-65, 62), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-80, 26), (-85, 30), (-90, 21), (-97, 16), (-105, 20), (-115, 28),
     (-125, 40), (-125, 49), (-135, 58), (-155, 58), (-165, 60)],
    # Greenland
    [(-58, 64), (-45, 60), (-32, 68), (-40, 76), (-55, 76), (-60, 70)],
    # South America
    [(-80, 9), (-72, 11), (-62, 9), (-52, 5), (-44, -3), (-35, -8),
     (-40, -20), (-48, -28), (-58, -38), (-65, -45), (-70, -52),
     (-73, -44), (-73, -30), (-77, -12), (-80, -3), (-81, 1)],
    # Africa
    [(-17, 15), (-10, 31), (0, 36), (10, 37), (20, 32), (30, 31),
     (35, 28), (43, 12), (51, 11), (48, 2), (40, -5), (36, -18),
     (32, -28), (20, -35), (16, -28), (12, -18), (9, -1), (9, 4),
     (-8, 4), (-13, 8), (-17, 12)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 58), (10, 62),
     (18, 69), (30, 70), (45, 68), (60, 69), (80, 73), (100, 76),
     (120, 73), (140, 72), (160, 70), (178, 66), (170, 60),
     (158, 52), (142, 45), (135, 35), (127, 33), (120, 28),
     (110, 20), (105, 9), (100, 8), (95, 15), (90, 22), (80, 15),
     (75, 8), (70, 20), (60, 25), (52, 26), (48, 30), (43, 12),
     (40, 15), (35, 28), (30, 36), (22, 37), (15, 40), (8, 44),
     (3, 43), (-2, 37)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (1, 51)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 38), (141, 42), (144, 44),
     (142, 45), (140, 40), (135, 34), (131, 33)],
    # SE Asia islands
    [(95, 5), (98, 2), (101, -2), (104, -6), (110, -7), (115, -8),
     (120, -10), (125, -9), (130, -3), (135, -4), (140, -8),
     (138, -2), (132, 0), (128, 2), (122, 0), (118, 2), (112, 4),
     (105, 2), (100, 6)],
    # Australia
    [(114, -22), (114, -32), (120, -34), (130, -32), (136, -35),
     (140, -38), (146, -39), (150, -37), (153, -27), (150, -22),
     (146, -19), (142, -11), (136, -12), (130, -13), (122, -17),
     (115, -20)],
]

# ---- layout ----
def draw_masthead(cv):
    cv.rect(4, 4, 1016, 1016, INK, 3)
    cv.text_center(512, 14, "THE DAILY ORBIT", 5, INK)
    cv.hline(16, 66, 992, RED, 2)
    cv.text(16, 74, "50 STORIES - 7 REGIONS", 1, INK)
    cv.text_center(512, 72, "MONDAY 23 NOVEMBER 2026", 2, RED)
    cv.text(1012 - text_width("DATE-CHECKED", 1), 74, "DATE-CHECKED", 1, INK)
    cv.hline(12, 90, 1000, INK, 3)


def draw_timeline(cv):
    cv.text(16, 98, "THE DAY IN UTC", 1, RED)
    cv.text(1012 - text_width("ALL TIMES APPROXIMATE", 1), 98,
            "ALL TIMES APPROXIMATE", 1, GREY)
    seg = 1000 // len(TIMELINE)
    for i, (t, label) in enumerate(TIMELINE):
        x = 16 + i * seg
        cv.text(x, 110, t, 1, RED)
        for j, ln in enumerate(cv.wrap(label, seg // 6 - 1)):
            cv.text(x, 120 + j * 8, ln, 1, INK)
        if i:
            cv.vline(x - 4, 108, 30, GREY)
    cv.hline(12, 142, 1000, INK, 2)


def ill_dymer(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (222, 214, 190))
    # damaged apartment block
    cv.fill_rect(x + 60, y + 18, 70, h - 18, (70, 66, 60))
    cv.poly([(x + 60, y + 18), (x + 95, y + 4), (x + 130, y + 18)], (70, 66, 60))
    for wy in range(y + 26, y + h - 8, 12):
        for wx in (x + 68, x + 84, x + 100, x + 116):
            cv.fill_rect(wx, wy, 6, 7, PAPER)
    cv.line(x + 78, y + 30, x + 92, y + 55, INK)
    cv.line(x + 112, y + 22, x + 104, y + 48, INK)
    # rubble
    cv.poly([(x + 150, y + h - 6), (x + 180, y + h - 34), (x + 215, y + h - 6)],
            (120, 112, 96))
    cv.poly([(x + 215, y + h - 6), (x + 245, y + h - 26), (x + 280, y + h - 6)],
            (100, 94, 80))
    # dust / smoke
    cv.circle(x + 250, y + 22, 10, GREY)
    cv.circle(x + 272, y + 34, 13, GREY)
    cv.circle(x + 292, y + 20, 8, GREY)
    # rescue ladder
    cv.line(x + 30, y + h - 6, x + 52, y + 30, RED)
    cv.line(x + 38, y + h - 6, x + 60, y + 30, RED)


def ill_markets(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.line(x + 24, y + 10, x + 24, y + h - 14, INK)
    cv.line(x + 24, y + h - 14, x + w - 10, y + h - 14, INK)
    bars = [62, 52, 44, 34, 22, 12]
    bw = (w - 50) // len(bars)
    for i, bh in enumerate(bars):
        bx = x + 34 + i * bw
        cv.fill_rect(bx, y + h - 16 - bh, bw - 6, bh, BLUE)
    pts = [(x + 34 + i * bw + (bw - 6) // 2, y + h - 20 - bh)
           for i, bh in enumerate(bars)]
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED)
        cv.line(pts[i][0], pts[i][1] + 1, pts[i + 1][0], pts[i + 1][1] + 1, RED)
    # down arrow
    ax, ay = x + w - 34, y + 12
    cv.line(ax, ay, ax, ay + 22, RED)
    cv.line(ax, ay, ax - 6, ay + 8, RED)
    cv.line(ax, ay, ax + 6, ay + 8, RED)
    cv.line(ax, ay + 22, ax - 6, ay + 14, RED)
    cv.line(ax, ay + 22, ax + 6, ay + 14, RED)
    cv.text(x + 30, y + 4, "-5.06%", 1, RED)


def ill_ship(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, SEA)
    for k in range(3):
        wy = y + h - 18 - k * 14
        for wx in range(x + 8, x + w - 8, 24):
            cv.line(wx, wy, wx + 12, wy + 3, WHITE)
            cv.line(wx + 12, wy + 3, wx + 24, wy, WHITE)
    # sinking corvette, tilted
    cv.poly([(x + 90, y + 34), (x + 240, y + 52), (x + 225, y + 66),
             (x + 105, y + 52)], (60, 60, 66))
    cv.line(x + 150, y + 40, x + 150, y + 12, INK)
    cv.line(x + 150, y + 12, x + 178, y + 22, RED)
    cv.circle(x + 110, y + 26, 7, (90, 90, 90))
    cv.circle(x + 128, y + 18, 10, (90, 90, 90))
    cv.circle(x + 150, y + 12, 6, (90, 90, 90))
    # drone above
    cv.fill_rect(x + 250, y + 14, 22, 6, INK)
    cv.line(x + 248, y + 17, x + 274, y + 17, INK)


BIG = [
    ("RUSSIAN STRIKE KILLS 11 IN DYMER",
     "Boy, 7, pulled alive from rubble; Kyiv schools hit at dawn - REUTERS",
     ill_dymer),
    ("AI SELL-OFF SINKS MARKETS",
     "Nikkei -5.06%, S&P 500 -3.7%; gold +3.14% as fear spreads - ONETURN",
     ill_markets),
    ("UKRAINE SINKS RUSSIAN WARSHIP",
     "Sea drones sink corvette Merkury at Benghazi; 2nd vessel hit - FRANCE 24",
     ill_ship),
]


def draw_big(cv):
    for i, (head, deck, ill) in enumerate(BIG):
        x = 12 + i * 338
        cv.rect(x, 148, 324, 86, INK, 1)
        ill(cv, x + 1, 149, 322, 84)
        yy = 240
        for ln in cv.wrap(head, 26):
            cv.text(x + 2, yy, ln, 2, RED if i != 1 else INK)
            yy += 16
        yy += 2
        for ln in cv.wrap(deck, 53):
            cv.text(x + 2, yy, ln, 1, INK)
            yy += 8
    cv.hline(12, 320, 1000, INK, 2)


def draw_map(cv):
    x0, y0, x1, y1 = 20, 352, 644, 500
    cv.text(16, 330, "WHERE IT HAPPENED", 1, RED)
    cv.text(1012 - text_width("12 PINS - 7 REGIONS", 1), 330,
            "12 PINS - 7 REGIONS", 1, GREY)
    cv.fill_rect(x0, y0, x1 - x0, y1 - y0, SEA)
    cv.rect(x0, y0, x1 - x0, y1 - y0, INK, 1)
    # graticule
    for lon in range(-120, 181, 60):
        gx = x0 + (lon + 180) / 360 * (x1 - x0)
        cv.vline(int(gx), y0, y1 - y0, (190, 212, 224))
    for lat in (-30, 0, 30, 60):
        gy = y0 + (84 - lat) / 144 * (y1 - y0)
        cv.hline(x0, int(gy), x1 - x0, (190, 212, 224))

    def proj(lon, lat):
        return (x0 + (lon + 180) / 360 * (x1 - x0),
                y0 + (84 - lat) / 144 * (y1 - y0))

    for poly in CONTINENTS:
        pts = [(int(px), int(py)) for px, py in
               (proj(lon, lat) for lon, lat in poly)]
        cv.poly(pts, LAND)
        for i in range(len(pts)):
            cv.line(pts[i][0], pts[i][1],
                    pts[(i + 1) % len(pts)][0], pts[(i + 1) % len(pts)][1],
                    (150, 138, 104))
    # manual nudges so close pins stay readable (schematic map)
    nudge = {1: (6, 4), 2: (-8, -4), 4: (0, 8), 5: (0, 10),
             7: (10, 6), 12: (-6, 6)}
    # absolute label positions, staggered so the Europe/ME cluster reads
    label_xy = {1: (340, 408), 2: (340, 356), 3: (308, 398), 4: (398, 434),
                5: (380, 424), 6: (438, 418), 7: (330, 366), 8: (283, 376),
                9: (207, 402), 10: (258, 459), 11: (561, 404), 12: (491, 422)}
    for num, label, lon, lat in PINS:
        px, py = proj(lon, lat)
        dx, dy = nudge.get(num, (0, 0))
        px, py = int(px) + dx, int(py) + dy
        cv.circle(px, py, 6, RED)
        cv.circle(px, py, 6, WHITE, fill=False)
        s = str(num)
        cv.text(px - text_width(s, 1) // 2, py - 3, s, 1, WHITE)
        lx, ly = label_xy[num]
        cv.text(lx, ly, label, 1, INK)


def draw_numbers(cv):
    x, y = 660, 324
    cv.rect(x, y, 352, 184, INK, 1)
    cv.text(x + 10, y + 8, "BY THE NUMBERS", 1, RED)
    cv.hline(x + 10, y + 20, 332, GREY)
    yy = y + 28
    for label, val in NUMBERS:
        cv.text(x + 10, yy, label, 1, INK)
        cv.text(x + 342 - text_width(val, 2), yy - 3, val, 2, RED)
        yy += 19


def draw_list(cv):
    cv.text(16, 514, "50 STORIES, NUMBERED - EVERY ONE FROM THIS MONDAY",
            1, RED)
    cv.hline(12, 528, 1000, INK, 1)
    y0 = 534
    for col in range(2):
        x = 12 + col * 506
        y = y0
        for n in range(col * 25, col * 25 + 25):
            head, deck, region = STORIES[n]
            cv.text(x, y, "%02d. %s" % (n + 1, head), 1, INK)
            cv.text(x + 4, y + 8, deck, 1, (60, 58, 52))
            cv.text(x + 494 - text_width(region, 1), y, region, 1, RED)
            y += 15
    cv.hline(12, 910, 1000, INK, 1)


def draw_datecheck(cv):
    y = 916
    cv.fill_rect(12, y, 1000, 78, LIGHT)
    cv.rect(12, y, 1000, 78, INK, 1)
    cv.text(22, y + 6, "DATE CHECK - LEFT OUT ON PURPOSE (NOT 23 NOVEMBER)",
            1, RED)
    yy = y + 20
    for i in range(0, 6, 2):
        cv.text(22, yy, "X " + DATE_CHECK[i], 1, INK)
        cv.text(516, yy, "X " + DATE_CHECK[i + 1], 1, INK)
        yy += 10
    cv.text(22, yy + 2, DATE_CHECK_NOT_YET, 1, INK)
    cv.text(16, 998,
            "EVERY STORY HERE HAPPENED, OR WAS FIRST REPORTED, ON MONDAY "
            "23 NOVEMBER 2026 - THE DAILY ORBIT", 1, INK)


def build():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_timeline(cv)
    draw_big(cv)
    draw_map(cv)
    draw_numbers(cv)
    draw_list(cv)
    draw_datecheck(cv)
    return png_bytes(cv)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    data = build()
    with open(out, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (out, len(data)))
