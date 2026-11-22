import manimgx as m

PAPER = "#0E1110"
INK = "#ECEDE6"
MUTED = "#9AA19A"
RULE = "#2C322E"
VERM = "#FF6B4A"
TEAL = "#4FD1C5"
GREEN = "#67C77D"
AMBER = "#F0B75C"


def header(scene, kicker, title):
    scene.camera.background_color = PAPER
    k = m.Text(kicker, font_size=20, weight="BOLD").set_color(VERM)
    t = m.Text(title, font_size=38, weight="BOLD").set_color(INK)
    k.to_corner(m.UL, buff=0.55)
    t.next_to(k, m.DOWN, buff=0.18).align_to(k, m.LEFT)
    line = m.Line(m.LEFT * 5.8, m.RIGHT * 5.8, color=RULE, stroke_width=1.5)
    line.next_to(t, m.DOWN, buff=0.28)
    scene.add(k, t, line)
    return t


class ImageRace(m.Scene):
    def construct(self):
        header(self, "01 / IMAGE MODELS", "Images per hour, both GPUs busy")
        items = [("FLUX", 374, VERM), ("QWEN", 150, TEAL),
                 ("Z-IMG", 147, GREEN), ("SDXL", 107, INK)]
        maxv = 400
        baseline = -1.7
        bars, labels, nums = [], [], []
        for i, (name, val, col) in enumerate(items):
            h = val / maxv * 3.0
            x = -4.5 + i * 3.0
            r = m.Rectangle(width=1.5, height=h, color=col, fill_color=col,
                            fill_opacity=1, stroke_width=0)
            r.move_to([x, baseline + h / 2, 0])
            bars.append(r)
            lab = m.Text(name, font_size=20, weight="BOLD").set_color(MUTED)
            lab.move_to([x, baseline - 0.45, 0])
            labels.append(lab)
            num = m.Text(str(val), font_size=30, weight="BOLD").set_color(col)
            num.move_to([x, baseline + h + 0.35, 0])
            nums.append(num)
        axis = m.Line([-5.6, baseline, 0], [5.6, baseline, 0], color=MUTED, stroke_width=1.5)
        self.add(axis)
        self.play(m.LaggedStart(*[m.GrowFromEdge(b, m.DOWN) for b in bars], lag_ratio=0.12))
        self.play(m.LaggedStart(*[m.FadeIn(n, shift=m.DOWN * 0.15) for n in nums], lag_ratio=0.08))
        self.add(*labels)
        note = m.Text("batched, dual-GPU, 1024px", font_size=18).set_color(MUTED)
        note.to_corner(m.DR, buff=0.5)
        self.play(m.FadeIn(note))
        self.wait(0.6)


class QualitySpeed(m.Scene):
    def construct(self):
        header(self, "02 / QUALITY vs SPEED", "Prompt alignment against throughput")
        ax = m.Axes(x_range=[0, 400, 100], y_range=[0.35, 0.40, 0.01],
                    x_length=8.2, y_length=3.4, tips=False,
                    axis_config={"color": MUTED, "stroke_width": 1.5})
        ax.shift(m.DOWN * 0.35)
        self.play(m.Create(ax))
        pts = [(374, 0.3924, VERM, "FLUX"), (150, 0.3839, TEAL, "QWEN"),
               (147, 0.3814, GREEN, "Z-IMG"), (107, 0.3894, INK, "SDXL")]
        anims, extras = [], []
        for x, y, col, name in pts:
            dot = m.Dot(ax.c2p(x, y), radius=0.12, color=col, fill_color=col)
            anims.append(m.GrowFromCenter(dot))
            lab = m.Text(name, font_size=17, weight="BOLD").set_color(MUTED)
            lab.next_to(dot, m.RIGHT, buff=0.18)
            if name == "QWEN":
                lab.shift(m.RIGHT * 0.35 + m.DOWN * 0.30)
            elif name == "Z-IMG":
                lab.shift(m.RIGHT * 0.35 + m.DOWN * 0.48)
            elif name == "SDXL":
                lab.shift(m.LEFT * 0.95 + m.UP * 0.36)
            extras.append(lab)
        self.play(m.LaggedStart(*anims, lag_ratio=0.12))
        self.add(*extras)
        xl = m.Text("images / hour", font_size=18).set_color(MUTED)
        xl.next_to(ax, m.DOWN, buff=0.25)
        yl = m.Text("CLIP cosine", font_size=18).set_color(MUTED)
        yl.next_to(ax, m.LEFT, buff=0.3).rotate(m.PI / 2)
        self.play(m.FadeIn(xl), m.FadeIn(yl))
        self.wait(0.6)


class VideoRace(m.Scene):
    def construct(self):
        header(self, "03 / VIDEO CLIPS", "Same 49 frames, wildly different time")
        items = [("CogVideoX-2b", 1053, INK), ("LTX 2B distilled", 27, VERM)]
        maxv = 1100
        y0 = 0.7
        self.add(m.Line([-5.6, 1.8, 0], [5.6, 1.8, 0], color=RULE, stroke_width=1))
        self.add(m.Line([-5.6, -1.0, 0], [5.6, -1.0, 0], color=RULE, stroke_width=1))
        bars, labels, nums = [], [], []
        for i, (name, val, col) in enumerate(items):
            y = y0 - i * 2.05
            w = val / maxv * 8.0
            r = m.Rectangle(width=w, height=0.6, color=col, fill_color=col,
                            fill_opacity=1, stroke_width=0)
            r.move_to([-5.6 + w / 2, y, 0])
            bars.append(r)
            lab = m.Text(name, font_size=20, weight="BOLD").set_color(MUTED)
            lab.move_to([-5.6, y + 0.75, 0]).align_to([-5.6, 0, 0], m.LEFT)
            labels.append(lab)
            num = m.Text(f"{val} s", font_size=26, weight="BOLD").set_color(col)
            num.move_to([-5.6 + w + 0.6, y, 0])
            nums.append(num)
        self.play(m.LaggedStart(*[m.GrowFromEdge(b, m.LEFT) for b in bars], lag_ratio=0.15))
        self.play(m.LaggedStart(*[m.FadeIn(n, shift=m.LEFT * 0.2) for n in nums], lag_ratio=0.1))
        self.add(*labels)
        note = m.Text("38x faster, same frame count", font_size=22, weight="BOLD").set_color(VERM)
        note.to_corner(m.DR, buff=0.5)
        self.play(m.FadeIn(note))
        self.wait(0.6)


class MemoryWall(m.Scene):
    def construct(self):
        header(self, "04 / H3 MEMORY WALL", "Weights versus a single T4")
        items = [("BF16", 126.0, INK), ("FP8", 64.1, AMBER), ("4-bit", 33.1, TEAL)]
        maxv = 140
        baseline = -1.7
        bars, labels, nums = [], [], []
        for i, (name, val, col) in enumerate(items):
            h = val / maxv * 3.0
            x = -3.6 + i * 3.6
            r = m.Rectangle(width=1.6, height=h, color=col, fill_color=col,
                            fill_opacity=1, stroke_width=0)
            r.move_to([x, baseline + h / 2, 0])
            bars.append(r)
            lab = m.Text(name, font_size=20, weight="BOLD").set_color(MUTED)
            lab.move_to([x, baseline - 0.42, 0])
            labels.append(lab)
            num = m.Text(f"{val:g}", font_size=24, weight="BOLD").set_color(col)
            num.move_to([x, baseline + h + 0.3, 0])
            nums.append(num)
        limit_y = baseline + 30 / maxv * 3.0
        limit = m.DashedLine([-5.6, limit_y, 0], [5.6, limit_y, 0], color=VERM, stroke_width=2)
        llab = m.Text("15 GB VRAM", font_size=18, weight="BOLD").set_color(VERM)
        llab.move_to([-1.8, limit_y - 0.32, 0])
        self.play(m.LaggedStart(*[m.GrowFromEdge(b, m.DOWN) for b in bars], lag_ratio=0.12))
        self.add(*labels)
        self.play(m.Create(limit), m.FadeIn(llab))
        self.play(m.LaggedStart(*[m.FadeIn(n, shift=m.DOWN * 0.12) for n in nums], lag_ratio=0.08))
        note = m.Text("even 4-bit cannot fit with activations", font_size=17).set_color(MUTED)
        note.to_corner(m.DR, buff=0.5)
        self.play(m.FadeIn(note))
        self.wait(0.6)


def hbars(scene, items, maxv, width=7.6, y0=1.1, step=0.78, note=None):
    """Draw a ranked horizontal bar chart with labels and value annotations."""
    for i, (name, value, label, col) in enumerate(items):
        y = y0 - i * step
        w = value / maxv * width
        bar = m.Rectangle(width=w, height=0.42, color=col, fill_color=col,
                          fill_opacity=1, stroke_width=0)
        bar.move_to([-5.6 + w / 2, y, 0])
        scene.play(m.GrowFromEdge(bar, m.LEFT), run_time=0.35)
        txt = m.Text(name, font_size=17, weight="BOLD").set_color(MUTED)
        txt.move_to([-5.6, y + 0.36, 0]).align_to([-5.6, 0, 0], m.LEFT)
        val = m.Text(label, font_size=20, weight="BOLD").set_color(col)
        val.move_to([-5.6 + w + 0.85, y, 0])
        scene.add(txt, val)
    if note:
        n = m.Text(note, font_size=16).set_color(MUTED)
        n.to_corner(m.DR, buff=0.55)
        scene.play(m.FadeIn(n))


class LlmSpeed(m.Scene):
    def construct(self):
        header(self, "01 / CHAT MODELS", "Replies per second, warm model")
        hbars(self, [("LFM 8B A1B", 119, "119", VERM), ("Spark 1.7B", 100, "100", TEAL),
                     ("Qwen Coder 30B", 71, "71", GREEN), ("Spark 4B", 54, "54", TEAL),
                     ("Gemma 4 12B", 21, "21", INK), ("Qwen 27B", 13, "13", MUTED)],
              130, note="higher is better · one or two T4s")


class ToolEval(m.Scene):
    def construct(self):
        header(self, "02 / TOOL USE", "How well the model used tools")
        hbars(self, [("Overall quality", 73, "73", VERM), ("Responsiveness", 74, "74", TEAL),
                     ("Deployability", 73, "73", GREEN), ("Weakest category", 33, "33", MUTED)],
              100, note="15 tasks · score out of 100")


class AgentTasks(m.Scene):
    def construct(self):
        header(self, "03 / AGENTS", "Agent tasks completed")
        hbars(self, [("Spark 1.7B", 2, "2 of 3", TEAL), ("Spark 4B", 3, "3 of 3", VERM)],
              3, width=5.5, note="same tasks, one T4 each")


class TernarySpeed(m.Scene):
    def construct(self):
        header(self, "04 / LONG CONTEXT", "Ternary 27B reply speed")
        hbars(self, [("One T4", 15.1, "15.1", TEAL), ("Two T4s", 22.9, "22.9", VERM)],
              25, width=5.5, note="tokens per second · higher is better")


class TuneMemory(m.Scene):
    def construct(self):
        header(self, "05 / FINE-TUNING", "Memory used to train an 8B model")
        hbars(self, [("Unsloth", 7.1, "7.1 GB", GREEN), ("Soup + Unsloth", 7.1, "7.1 GB", TEAL),
                     ("Stock transformers", 14.9, "14.9 GB", MUTED), ("Stock, blocked", 14.8, "OOM", VERM)],
              16, note="same model, data and settings")


class InklingSpeed(m.Scene):
    def construct(self):
        header(self, "02 / INKLING-2-MINI", "Reply speed by quant, one T4")
        hbars(self, [("IQ1_M (1-bit)", 26.5, "26.5", TEAL),
                     ("AD-IQ2_M (recommended)", 26.1, "26.1", VERM),
                     ("Q2_K_XL", 25.1, "25.1", TEAL),
                     ("Q3_K_XL (best quality that fits)", 24.3, "24.3", GREEN),
                     ("IQ3_XXS", 23.0, "23.0", TEAL),
                     ("AD-IQ3_S", 22.3, "22.3", AMBER)],
              30, note="tokens per second · higher is better")


class InklingWall(m.Scene):
    def construct(self):
        header(self, "02 / INKLING-2-MINI", "Quant file size versus one T4")
        items = [("IQ1_M", 7.46, TEAL), ("AD-IQ2", 8.06, TEAL), ("Q2_K_XL", 8.51, TEAL),
                 ("IQ3_XXS", 10.86, TEAL), ("AD-IQ3_S", 12.43, TEAL), ("Q3_K_XL", 12.69, GREEN),
                 ("AD-Q4_K", 15.46, VERM), ("Q4_K_M", 15.46, VERM),
                 ("Q4_K_XL", 16.42, VERM), ("Q8_K_XL", 21.30, VERM)]
        maxv = 24
        baseline = -1.9
        bars, labels, nums = [], [], []
        for i, (name, val, col) in enumerate(items):
            h = val / maxv * 3.2
            x = -5.0 + i * 1.11
            r = m.Rectangle(width=0.82, height=h, color=col, fill_color=col,
                            fill_opacity=1, stroke_width=0)
            r.move_to([x, baseline + h / 2, 0])
            bars.append(r)
            lab = m.Text(name, font_size=15, weight="BOLD").set_color(MUTED)
            lab.move_to([x, baseline - 0.36, 0])
            labels.append(lab)
            num = m.Text(f"{val:g}", font_size=19, weight="BOLD").set_color(INK)
            if val > 15:  # over the wall: lift the number above the bar top
                num.move_to([x, baseline + h + 0.26, 0])
            else:         # fits: keep it inside the bar, clear of the line
                num.move_to([x, baseline + h - 0.26, 0])
            nums.append(num)
        axis = m.Line([-5.6, baseline, 0], [5.6, baseline, 0], color=MUTED, stroke_width=1.5)
        self.add(axis)
        limit_y = baseline + 15.0 / maxv * 3.2
        limit = m.DashedLine([-5.6, limit_y, 0], [5.6, limit_y, 0], color=VERM, stroke_width=2)
        llab = m.Text("15 GB VRAM", font_size=17, weight="BOLD").set_color(VERM)
        llab.move_to([-3.6, limit_y - 0.34, 0])
        self.play(m.LaggedStart(*[m.GrowFromEdge(b, m.DOWN) for b in bars], lag_ratio=0.08))
        self.add(*labels)
        self.play(m.Create(limit), m.FadeIn(llab))
        self.play(m.LaggedStart(*[m.FadeIn(n, shift=m.DOWN * 0.12) for n in nums], lag_ratio=0.06))
        note = m.Text("green fits one card · red needs a split that does not exist", font_size=16).set_color(MUTED)
        note.to_corner(m.DR, buff=0.5)
        self.play(m.FadeIn(note))
        self.wait(0.6)
