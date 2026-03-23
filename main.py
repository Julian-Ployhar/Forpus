import threading
import tkinter as tk
from math import sin

try:
    import pyttsx3
except ModuleNotFoundError:
    pyttsx3 = None


BG = "#090b0a"
PANEL = "#141816"
TEXT_BG = "#101412"
ACCENT = "#5BD6A7"
ACCENT_DIM = "#2F7F68"
TEXT = "#F4FFF9"
MUTED = "#92A79D"

drift = 0.0
meter_bloom = 0.08
voice_live = False


def post_line(message):
    shell.after(0, footer_note.set, message)


def toggle_talk(enabled):
    state = tk.NORMAL if enabled else tk.DISABLED
    shell.after(0, lambda: talk_btn.config(state=state))


def tune_meter(active=None, level=None):
    global voice_live, meter_bloom

    if active is not None:
        voice_live = active
    if level is not None:
        meter_bloom = max(meter_bloom, level)


def nudge_meter(active=None, level=None):
    shell.after(0, lambda: tune_meter(active=active, level=level))


def paint_bars():
    global drift, meter_bloom

    width = max(pulse_board.winfo_width(), 440)
    height = max(pulse_board.winfo_height(), 104)
    center_y = height / 2
    lane_count = 34
    lane_width = width / lane_count
    floor = 4

    pulse_board.delete("all")
    pulse_board.create_rectangle(0, 0, width, height, fill=TEXT_BG, outline="")

    idle_mark = 0.24 if voice_live else 0.05
    if voice_live:
        meter_bloom = max(idle_mark, meter_bloom * 0.92)
    else:
        meter_bloom = idle_mark + (meter_bloom - idle_mark) * 0.82

    drift += 0.28 if voice_live else 0.12

    for index in range(lane_count):
        x = index * lane_width + lane_width / 2
        spread = abs((index - (lane_count - 1) / 2) / (lane_count / 2))
        envelope = max(0.22, 1.0 - spread**1.7)
        motion = abs(sin(drift + index * 0.41))
        shimmer = abs(sin(drift * 0.63 + index * 0.21))
        amplitude = floor + (height * 0.34 * meter_bloom * envelope * (0.45 + motion * 0.55))
        amplitude += height * 0.06 * meter_bloom * shimmer

        x0 = x - lane_width * 0.2
        x1 = x + lane_width * 0.2
        y0 = center_y - amplitude
        y1 = center_y + amplitude
        color = ACCENT if voice_live else ACCENT_DIM
        pulse_board.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

    shell.after(33, paint_bars)


def read_copy():
    copy = pad.get("1.0", tk.END).strip()
    if not copy:
        post_line("Enter text first.")
        return

    if pyttsx3 is None:
        post_line("pyttsx3 is not installed in this interpreter.")
        return

    toggle_talk(False)
    post_line("Starting speech...")
    nudge_meter(active=True, level=0.28)
    threading.Thread(target=spin_voice, args=(copy,), daemon=True).start()


def spin_voice(copy):
    mouth = None
    try:
        post_line("Speaking...")
        # Create the engine inside the worker thread because Windows SAPI is thread-affine.
        mouth = pyttsx3.init()
        mouth.setProperty("rate", 185)
        mouth.connect("started-utterance", lambda name: nudge_meter(active=True, level=0.32))
        mouth.connect(
            "started-word",
            lambda name, location, length: nudge_meter(level=min(0.95, 0.28 + length * 0.045)),
        )
        mouth.connect("finished-utterance", lambda name, completed: nudge_meter(active=False, level=0.12))
        mouth.say(copy)
        mouth.runAndWait()
        post_line("Ready.")
    except Exception as exc:
        post_line(f"Error: {exc}")
        nudge_meter(active=False, level=0.08)
    finally:
        if mouth is not None:
            try:
                mouth.stop()
            except Exception:
                pass
        nudge_meter(active=False, level=0.08)
        toggle_talk(True)


shell = tk.Tk()
shell.title("Forpus")
shell.geometry("560x620")
shell.minsize(520, 580)
shell.configure(bg=BG)

mast = tk.Frame(shell, bg=BG)
mast.pack(fill="x", padx=24, pady=(22, 10))

title = tk.Label(
    mast,
    text="Forpus",
    fg=TEXT,
    bg=BG,
    font=("Segoe UI", 26, "bold"),
)
title.pack(anchor="w")

subtitle = tk.Label(
    mast,
    text="text and PDF reader",
    fg=MUTED,
    bg=BG,
    font=("Segoe UI", 11),
)
subtitle.pack(anchor="w")

paper = tk.Frame(shell, bg=PANEL)
paper.pack(fill="both", expand=True, padx=24, pady=(0, 12))

editor_header = tk.Label(
    paper,
    text="Reader",
    fg=TEXT,
    bg=PANEL,
    anchor="w",
    padx=14,
    pady=10,
    font=("Segoe UI", 12, "bold"),
)
editor_header.pack(fill="x")

pad = tk.Text(
    paper,
    height=16,
    wrap="word",
    bg=TEXT_BG,
    fg=TEXT,
    insertbackground=TEXT,
    bd=0,
    highlightthickness=0,
    padx=14,
    pady=14,
)
pad.pack(fill="both", expand=True, padx=10, pady=(0, 10))

switches = tk.Frame(shell, bg=BG)
switches.pack(fill="x", padx=24, pady=(0, 10))

talk_btn = tk.Button(
    switches,
    text="Speak",
    command=read_copy,
    bg="#26362f",
    fg=TEXT,
    activebackground="#335145",
    activeforeground=TEXT,
    relief="flat",
    padx=18,
    pady=8,
)
talk_btn.pack(anchor="w")

pulse_board = tk.Canvas(shell, height=104, bg=TEXT_BG, bd=0, highlightthickness=0)
pulse_board.pack(fill="x", padx=24, pady=(0, 12))

footer_note = tk.StringVar(value="Ready.")
status = tk.Label(
    shell,
    textvariable=footer_note,
    fg=MUTED,
    bg=BG,
    wraplength=500,
    justify="left",
    anchor="w",
)
status.pack(fill="x", padx=24, pady=(0, 6))

hint = tk.Label(
    shell,
    text="Type directly into this box, then press Speak.",
    fg="#6D8178",
    bg=BG,
    wraplength=500,
    justify="left",
    anchor="w",
)
hint.pack(fill="x", padx=24, pady=(0, 18))

paint_bars()

shell.mainloop()
