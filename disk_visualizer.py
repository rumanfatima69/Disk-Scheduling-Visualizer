import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ================= Color Palette (Light Pastel Theme) =================

COLORS = {
    "bg":           "#F7F6F2",
    "topbar_bg":    "#EAF3DE",
    "topbar_fg":    "#27500A",
    "topbar_sub":   "#3B6D11",
    "input_bg":     "#FBEAF0",
    "input_border": "#F4C0D1",
    "input_label":  "#993556",
    "input_fg":     "#4B1528",
    "algo_bg":      "#E6F1FB",
    "algo_label":   "#185FA5",
    "algo_btn":     "#FFFFFF",
    "algo_btn_fg":  "#185FA5",
    "algo_active":  "#378ADD",
    "algo_active_fg": "#FFFFFF",
    "run_bg":       "#1D9E75",
    "run_hover":    "#0F6E56",
    "run_fg":       "#FFFFFF",
    "metric1_bg":   "#FAEEDA",
    "metric1_label":"#854F0B",
    "metric1_val":  "#633806",
    "metric2_bg":   "#E1F5EE",
    "metric2_label":"#0F6E56",
    "metric2_val":  "#085041",
    "metric3_bg":   "#EEEDFE",
    "metric3_label":"#534AB7",
    "metric3_val":  "#3C3489",
    "seq_bg":       "#F1EFE8",
    "seq_label":    "#5F5E5A",
    "chip_bg":      "#FFFFFF",
    "chip_fg":      "#2C2C2A",
    "chip_border":  "#D3D1C7",
    "head_chip_bg": "#EEEDFE",
    "head_chip_fg": "#3C3489",
    "chart_bg":     "#FFFFFF",
    "chart_border": "#D3D1C7",
    "chart_line":   "#1D9E75",
    "chart_point":  "#0F6E56",
    "chart_head":   "#7F77DD",
    "chart_fill":   "#E1F5EE",
    "chart_grid":   "#F1EFE8",
    "chart_tick":   "#888780",
    "err_bg":       "#FCEBEB",
    "err_fg":       "#A32D2D",
}

# ================= Algorithms =================

def fcfs(requests, head):
    sequence = [head] + requests
    movement = sum(abs(sequence[i] - sequence[i+1]) for i in range(len(sequence)-1))
    return sequence, movement

def sstf(requests, head):
    sequence = [head]
    reqs = requests.copy()
    movement = 0
    current = head
    while reqs:
        closest = min(reqs, key=lambda x: abs(x - current))
        movement += abs(current - closest)
        sequence.append(closest)
        current = closest
        reqs.remove(closest)
    return sequence, movement

def scan(requests, head, disk_size=200):
    sequence = [head]
    movement = 0
    left = sorted([r for r in requests if r < head], reverse=True)
    right = sorted([r for r in requests if r >= head])
    cur = head
    for r in right:
        movement += abs(cur - r); sequence.append(r); cur = r
    if left:
        movement += abs(cur - (disk_size - 1)); cur = disk_size - 1; sequence.append(cur)
        for r in left:
            movement += abs(cur - r); sequence.append(r); cur = r
    return sequence, movement

def c_scan(requests, head, disk_size=200):
    sequence = [head]
    movement = 0
    left = sorted([r for r in requests if r < head])
    right = sorted([r for r in requests if r >= head])
    cur = head
    for r in right:
        movement += abs(cur - r); sequence.append(r); cur = r
    if left:
        movement += abs(cur - (disk_size - 1)); sequence.append(disk_size - 1)
        sequence.append(0); cur = 0
        for r in left:
            movement += abs(cur - r); sequence.append(r); cur = r
    return sequence, movement

# ================= App =================

class DiskSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Disk Scheduling Visualizer")
        self.root.configure(bg=COLORS["bg"])
        self.root.geometry("720x820")
        self.root.resizable(True, True)

        self.selected_algo = tk.StringVar(value="FCFS")
        self.algo_buttons = {}
        self.canvas_widget = None

        self._build_ui()

    def _build_ui(self):
        outer = tk.Frame(self.root, bg=COLORS["bg"])
        outer.pack(fill="both", expand=True, padx=24, pady=20)

        self._build_topbar(outer)
        self._build_inputs(outer)
        self._build_algo_selector(outer)
        self._build_run_button(outer)
        self._build_metrics(outer)
        self._build_sequence(outer)
        self._build_chart_area(outer)

    # --- Placeholder helper ---
    def _add_placeholder(self, entry, text):
        """Show grey hint text; clear on focus, restore if left empty."""
        entry._placeholder = text
        entry._has_placeholder = True
        entry.insert(0, text)
        entry.config(fg="#AAAAAA")

        def on_focus_in(e):
            if entry._has_placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=COLORS["input_fg"])
                entry._has_placeholder = False

        def on_focus_out(e):
            if entry.get().strip() == "":
                entry.insert(0, entry._placeholder)
                entry.config(fg="#AAAAAA")
                entry._has_placeholder = True

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    # --- Topbar ---
    def _build_topbar(self, parent):
        bar = tk.Frame(parent, bg=COLORS["topbar_bg"], pady=12, padx=16)
        bar.pack(fill="x", pady=(0, 12))

        icon_box = tk.Frame(bar, bg="#C0DD97", width=36, height=36)
        icon_box.pack(side="left", padx=(0, 12))
        icon_box.pack_propagate(False)
        tk.Label(icon_box, text="◎", bg="#C0DD97", fg="#3B6D11",
                 font=("Arial", 16)).pack(expand=True)

        text_frame = tk.Frame(bar, bg=COLORS["topbar_bg"])
        text_frame.pack(side="left")
        tk.Label(text_frame, text="Disk Scheduling Visualizer",
                 bg=COLORS["topbar_bg"], fg=COLORS["topbar_fg"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(text_frame, text="Simulate FCFS, SSTF, SCAN, and C-SCAN algorithms",
                 bg=COLORS["topbar_bg"], fg=COLORS["topbar_sub"],
                 font=("Segoe UI", 10)).pack(anchor="w")

    # --- Inputs ---
    def _build_inputs(self, parent):
        card = tk.Frame(parent, bg=COLORS["input_bg"], pady=12, padx=16)
        card.pack(fill="x", pady=(0, 10))

        row = tk.Frame(card, bg=COLORS["input_bg"])
        row.pack(fill="x")
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)

        left = tk.Frame(row, bg=COLORS["input_bg"])
        left.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        tk.Label(left, text="DISK REQUESTS", bg=COLORS["input_bg"],
                 fg=COLORS["input_label"], font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.entry_requests = tk.Entry(left, font=("Segoe UI", 11),
                                       bg="white", fg=COLORS["input_fg"],
                                       relief="flat",
                                       highlightthickness=1,
                                       highlightbackground=COLORS["input_border"],
                                       highlightcolor="#D4537E")
        self._add_placeholder(self.entry_requests, "e.g. 98, 183, 37, 122, 14")
        self.entry_requests.pack(fill="x", ipady=6, pady=(4, 0))

        right = tk.Frame(row, bg=COLORS["input_bg"])
        right.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        tk.Label(right, text="INITIAL HEAD POSITION", bg=COLORS["input_bg"],
                 fg=COLORS["input_label"], font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.entry_head = tk.Entry(right, font=("Segoe UI", 11),
                                   bg="white", fg=COLORS["input_fg"],
                                   relief="flat",
                                   highlightthickness=1,
                                   highlightbackground=COLORS["input_border"],
                                   highlightcolor="#D4537E")
        self._add_placeholder(self.entry_head, "e.g. 53")
        self.entry_head.pack(fill="x", ipady=6, pady=(4, 0))

    # --- Algorithm selector ---
    def _build_algo_selector(self, parent):
        card = tk.Frame(parent, bg=COLORS["algo_bg"], pady=12, padx=16)
        card.pack(fill="x", pady=(0, 10))

        tk.Label(card, text="ALGORITHM", bg=COLORS["algo_bg"],
                 fg=COLORS["algo_label"], font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 8))

        btn_row = tk.Frame(card, bg=COLORS["algo_bg"])
        btn_row.pack(fill="x")

        for algo in ["FCFS", "SSTF", "SCAN", "C-SCAN"]:
            btn = tk.Button(btn_row, text=algo,
                            font=("Segoe UI", 11, "bold"),
                            bg=COLORS["algo_btn"], fg=COLORS["algo_btn_fg"],
                            relief="flat", bd=0, cursor="hand2",
                            padx=12, pady=8,
                            command=lambda a=algo: self.select_algo(a))
            btn.pack(side="left", expand=True, fill="x", padx=4)
            self.algo_buttons[algo] = btn

        self._highlight_algo("FCFS")

    def select_algo(self, algo):
        self.selected_algo.set(algo)
        self._highlight_algo(algo)

    def _highlight_algo(self, active):
        for name, btn in self.algo_buttons.items():
            if name == active:
                btn.config(bg=COLORS["algo_active"], fg=COLORS["algo_active_fg"])
            else:
                btn.config(bg=COLORS["algo_btn"], fg=COLORS["algo_btn_fg"])

    # --- Run button ---
    def _build_run_button(self, parent):
        self.run_btn = tk.Button(parent, text="▶  Run Algorithm",
                                 font=("Segoe UI", 12, "bold"),
                                 bg=COLORS["run_bg"], fg=COLORS["run_fg"],
                                 relief="flat", bd=0, cursor="hand2",
                                 pady=10, command=self.run_algorithm)
        self.run_btn.pack(fill="x", pady=(0, 16))
        self.run_btn.bind("<Enter>", lambda e: self.run_btn.config(bg=COLORS["run_hover"]))
        self.run_btn.bind("<Leave>", lambda e: self.run_btn.config(bg=COLORS["run_bg"]))

    # --- Metrics ---
    def _build_metrics(self, parent):
        self.metrics_frame = tk.Frame(parent, bg=COLORS["bg"])
        self.metrics_frame.pack(fill="x", pady=(0, 12))

        m_configs = [
            ("TOTAL MOVEMENT", "metric1_bg", "metric1_label", "metric1_val", "m_total", "cylinders traversed"),
            ("REQUESTS SERVED", "metric2_bg", "metric2_label", "metric2_val", "m_reqs", "in order"),
            ("ALGORITHM", "metric3_bg", "metric3_label", "metric3_val", "m_algo", "active"),
        ]

        self.metrics_frame.columnconfigure(0, weight=1)
        self.metrics_frame.columnconfigure(1, weight=1)
        self.metrics_frame.columnconfigure(2, weight=1)

        for i, (label, bg_key, lbl_key, val_key, attr, sub) in enumerate(m_configs):
            card = tk.Frame(self.metrics_frame, bg=COLORS[bg_key], pady=12, padx=14)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 6, 0))

            tk.Label(card, text=label, bg=COLORS[bg_key],
                     fg=COLORS[lbl_key], font=("Segoe UI", 8, "bold")).pack(anchor="w")

            val_lbl = tk.Label(card, text="—", bg=COLORS[bg_key],
                               fg=COLORS[val_key],
                               font=("Segoe UI", 20 if i < 2 else 14, "bold"))
            val_lbl.pack(anchor="w", pady=(4, 2))
            setattr(self, attr, val_lbl)

            tk.Label(card, text=sub, bg=COLORS[bg_key],
                     fg=COLORS[lbl_key], font=("Segoe UI", 9)).pack(anchor="w")

    # --- Sequence display ---
    def _build_sequence(self, parent):
        seq_outer = tk.Frame(parent, bg=COLORS["seq_bg"], pady=12, padx=16)
        seq_outer.pack(fill="x", pady=(0, 12))

        tk.Label(seq_outer, text="HEAD MOVEMENT SEQUENCE",
                 bg=COLORS["seq_bg"], fg=COLORS["seq_label"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 8))

        self.seq_frame = tk.Frame(seq_outer, bg=COLORS["seq_bg"])
        self.seq_frame.pack(fill="x")

    def _update_sequence(self, sequence):
        for widget in self.seq_frame.winfo_children():
            widget.destroy()

        row = tk.Frame(self.seq_frame, bg=COLORS["seq_bg"])
        row.pack(fill="x")

        for i, val in enumerate(sequence):
            if i > 0:
                tk.Label(row, text="→", bg=COLORS["seq_bg"],
                         fg=COLORS["chip_border"],
                         font=("Segoe UI", 10)).pack(side="left", padx=2)

            is_head = (i == 0)
            chip = tk.Label(row, text=str(val),
                            bg=COLORS["head_chip_bg"] if is_head else COLORS["chip_bg"],
                            fg=COLORS["head_chip_fg"] if is_head else COLORS["chip_fg"],
                            font=("Segoe UI", 10, "bold" if is_head else "normal"),
                            relief="flat", padx=8, pady=4,
                            highlightthickness=1,
                            highlightbackground=COLORS["head_chip_fg"] if is_head else COLORS["chip_border"])
            chip.pack(side="left")

    # --- Chart area ---
    def _build_chart_area(self, parent):
        self.chart_card = tk.Frame(parent, bg=COLORS["chart_bg"],
                                   highlightthickness=1,
                                   highlightbackground=COLORS["chart_border"])
        self.chart_card.pack(fill="both", expand=True, pady=(0, 8))

        tk.Label(self.chart_card, text="CYLINDER SWEEP PATH",
                 bg=COLORS["chart_bg"], fg=COLORS["seq_label"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(12, 0))

        self.chart_inner = tk.Frame(self.chart_card, bg=COLORS["chart_bg"])
        self.chart_inner.pack(fill="both", expand=True, padx=12, pady=8)

    def _plot_chart(self, sequence):
        for widget in self.chart_inner.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(6.5, 3.2), facecolor=COLORS["chart_bg"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORS["chart_bg"])

        steps = list(range(len(sequence)))
        labels = ["Start"] + [f"Step {i}" for i in range(1, len(sequence))]

        ax.plot(steps, sequence,
                color=COLORS["chart_line"], linewidth=2,
                marker="o", markersize=6,
                markerfacecolor=COLORS["chart_point"],
                markeredgecolor=COLORS["chart_point"])

        ax.plot(0, sequence[0],
                "o", markersize=9,
                markerfacecolor=COLORS["chart_head"],
                markeredgecolor=COLORS["head_chip_fg"])

        ax.fill_between(steps, sequence,
                        alpha=0.08, color=COLORS["chart_line"])

        for spine in ax.spines.values():
            spine.set_edgecolor(COLORS["chart_border"])
            spine.set_linewidth(0.8)

        ax.set_xticks(steps)
        ax.set_xticklabels(labels, fontsize=8,
                           color=COLORS["chart_tick"], rotation=40, ha="right")
        ax.tick_params(axis="y", labelsize=8, colors=COLORS["chart_tick"])
        ax.yaxis.label.set_color(COLORS["chart_tick"])
        ax.set_ylabel("Cylinder", fontsize=9, color=COLORS["chart_tick"])
        ax.grid(True, color=COLORS["chart_grid"], linewidth=0.8, linestyle="-")
        ax.set_axisbelow(True)

        fig.tight_layout(pad=1.2)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_inner)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()
        self.canvas_widget = canvas

    # --- Run ---
    def run_algorithm(self):
        raw_reqs = self.entry_requests.get().strip()
        raw_head = self.entry_head.get().strip()

        # Treat placeholder text or empty fields as missing input
        if (not raw_reqs or getattr(self.entry_requests, "_has_placeholder", False) or
                not raw_head or getattr(self.entry_head, "_has_placeholder", False)):
            messagebox.showwarning(
                "Missing Input",
                "Please enter both disk requests and the initial head position before running."
            )
            return

        try:
            requests = [int(x.strip()) for x in raw_reqs.split(",")]
            head = int(raw_head)
        except Exception:
            messagebox.showerror(
                "Invalid Input",
                "Requests must be comma-separated integers.\nExample: 98, 183, 37, 122\nHead must be a single integer."
            )
            return

        algo = self.selected_algo.get()
        if algo == "FCFS":
            seq, mv = fcfs(requests, head)
        elif algo == "SSTF":
            seq, mv = sstf(requests, head)
        elif algo == "SCAN":
            seq, mv = scan(requests, head)
        elif algo == "C-SCAN":
            seq, mv = c_scan(requests, head)
        else:
            return

        self.m_total.config(text=str(mv))
        self.m_reqs.config(text=str(len(requests)))
        self.m_algo.config(text=algo)

        self._update_sequence(seq)
        self._plot_chart(seq)


# ================= Entry Point =================

if __name__ == "__main__":
    root = tk.Tk()
    app = DiskSchedulerApp(root)
    root.mainloop()