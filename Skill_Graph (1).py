import tkinter as tk
from tkinter import ttk, messagebox

# ============================================================
# SKILL GRAPH
# Modern CSS-inspired desktop UI built entirely with Python.
# Uses Tkinter only — no HTML, CSS, JavaScript or Flask.
# ============================================================

APP_NAME = "Skill Graph"

# ----------------------------
# Color theme
# ----------------------------
BG = "#0b1120"
BG_LIGHT = "#111827"
CARD = "#172033"
CARD_LIGHT = "#1e293b"
BORDER = "#2b3953"

WHITE = "#f8fafc"
TEXT = "#dbe4f0"
MUTED = "#94a3b8"

BLUE = "#3b82f6"
BLUE_HOVER = "#2563eb"
BLUE_SOFT = "#172f59"

CYAN = "#22d3ee"
PURPLE = "#8b5cf6"
GREEN = "#22c55e"

SKILLS = {
    "Software Development":
        "Learn C/C++, Python or Java, data structures, algorithms, "
        "Git, databases and web/application development.",

    "Artificial Intelligence":
        "Learn Python, mathematics, statistics, machine learning, "
        "neural networks, data handling and AI frameworks.",

    "Data Science":
        "Learn Python, SQL, statistics, data visualization, Excel, "
        "data analysis and machine learning.",

    "Cybersecurity":
        "Learn networking, Linux, operating systems, security "
        "fundamentals, cryptography and ethical security practices.",

    "UI/UX Design":
        "Learn design principles, typography, color theory, Figma, "
        "user research, wireframing and prototyping.",

    "Business / Entrepreneurship":
        "Learn business fundamentals, market research, communication, "
        "finance, marketing and product development."
}


class SkillGraph(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Skill Graph — Career Roadmap")
        self.geometry("1080x820")
        self.minsize(900, 680)
        self.configure(bg=BG)

        self.education = tk.StringVar()
        self.interest = tk.StringVar()
        self.career = tk.StringVar()

        self.strength_vars = {
            "Problem Solving": tk.BooleanVar(),
            "Creativity": tk.BooleanVar(),
            "Communication": tk.BooleanVar(),
            "Mathematics": tk.BooleanVar()
        }

        self.setup_styles()
        self.create_interface()

    # ========================================================
    # Styling
    # ========================================================

    def setup_styles(self):
        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Skill.TCombobox",
            fieldbackground=CARD_LIGHT,
            background=CARD_LIGHT,
            foreground=WHITE,
            arrowcolor=CYAN,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
            padding=10,
            font=("Segoe UI", 11)
        )

        style.map(
            "Skill.TCombobox",
            fieldbackground=[("readonly", CARD_LIGHT)],
            foreground=[("readonly", WHITE)]
        )

        style.configure(
            "Skill.Vertical.TScrollbar",
            background=CARD_LIGHT,
            troughcolor=BG,
            bordercolor=BG,
            arrowcolor=MUTED
        )

    # ========================================================
    # Main interface
    # ========================================================

    def create_interface(self):

        # ----------------------------
        # Top navigation bar
        # ----------------------------
        header = tk.Frame(
            self,
            bg=BG,
            height=78
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        brand = tk.Frame(header, bg=BG)
        brand.pack(side="left", padx=42)

        tk.Label(
            brand,
            text="SKILL",
            bg=BG,
            fg=WHITE,
            font=("Segoe UI", 23, "bold")
        ).pack(side="left")

        tk.Label(
            brand,
            text=" GRAPH",
            bg=BG,
            fg=CYAN,
            font=("Segoe UI", 23, "bold")
        ).pack(side="left")

        tk.Label(
            header,
            text="CAREER INTELLIGENCE",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(side="right", padx=42)

        # ----------------------------
        # Hero
        # ----------------------------
        hero = tk.Frame(
            self,
            bg=BG_LIGHT,
            height=235,
            highlightthickness=1,
            highlightbackground=BORDER
        )
        hero.pack(fill="x")
        hero.pack_propagate(False)

        # Accent line
        tk.Frame(
            hero,
            bg=BLUE,
            height=4
        ).pack(fill="x", side="top")

        hero_inner = tk.Frame(
            hero,
            bg=BG_LIGHT
        )
        hero_inner.pack(expand=True)

        tk.Label(
            hero_inner,
            text="BUILD YOUR",
            bg=BG_LIGHT,
            fg=MUTED,
            font=("Segoe UI", 11, "bold")
        ).pack()

        tk.Label(
            hero_inner,
            text="Career Roadmap.",
            bg=BG_LIGHT,
            fg=WHITE,
            font=("Segoe UI", 38, "bold")
        ).pack(pady=(2, 7))

        tk.Label(
            hero_inner,
            text=(
                "Turn your interests and strengths into a clear path of skills, "
                "projects and experience."
            ),
            bg=BG_LIGHT,
            fg=TEXT,
            font=("Segoe UI", 12),
            wraplength=720,
            justify="center"
        ).pack()

        # ----------------------------
        # Scrollable area
        # ----------------------------
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            outer,
            bg=BG,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            outer,
            orient="vertical",
            command=self.canvas.yview,
            style="Skill.Vertical.TScrollbar"
        )

        self.content = tk.Frame(
            self.canvas,
            bg=BG
        )

        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw"
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.content.bind(
            "<Configure>",
            lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.bind(
            "<Configure>",
            self.resize_content
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            self.mouse_scroll
        )

        self.create_form()

    def resize_content(self, event):
        self.canvas.itemconfig(
            self.window_id,
            width=event.width
        )

    def mouse_scroll(self, event):
        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    # ========================================================
    # Form
    # ========================================================

    def create_form(self):

        card = self.create_card(self.content)
        card.pack(
            fill="x",
            padx=75,
            pady=38
        )

        # Heading
        heading_row = tk.Frame(card, bg=CARD)
        heading_row.pack(
            fill="x",
            padx=30,
            pady=(28, 25)
        )

        icon = tk.Label(
            heading_row,
            text="01",
            bg=BLUE_SOFT,
            fg=CYAN,
            font=("Segoe UI", 11, "bold"),
            padx=10,
            pady=7
        )
        icon.pack(side="left", padx=(0, 12))

        heading_text = tk.Frame(
            heading_row,
            bg=CARD
        )
        heading_text.pack(side="left")

        tk.Label(
            heading_text,
            text="Create Your Career Roadmap",
            bg=CARD,
            fg=WHITE,
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w")

        tk.Label(
            heading_text,
            text="Tell us where you are and where you want to go.",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(3, 0))

        # Education
        self.add_label(card, "CURRENT EDUCATION")

        education_box = ttk.Combobox(
            card,
            textvariable=self.education,
            state="readonly",
            values=[
                "School",
                "Intermediate / 12th",
                "B.Tech / Engineering",
                "Degree",
                "Diploma",
                "Other"
            ],
            style="Skill.TCombobox"
        )
        education_box.pack(
            fill="x",
            padx=30,
            pady=(0, 20)
        )

        # Interest
        self.add_label(card, "AREA OF INTEREST")

        interest_box = ttk.Combobox(
            card,
            textvariable=self.interest,
            state="readonly",
            values=list(SKILLS.keys()),
            style="Skill.TCombobox"
        )
        interest_box.pack(
            fill="x",
            padx=30,
            pady=(0, 20)
        )

        # Strengths
        self.add_label(card, "YOUR MAIN STRENGTHS")

        strength_frame = tk.Frame(
            card,
            bg=CARD
        )
        strength_frame.pack(
            fill="x",
            padx=25,
            pady=(0, 20)
        )

        for index, (name, variable) in enumerate(
            self.strength_vars.items()
        ):
            row = index // 2
            column = index % 2

            box = tk.Checkbutton(
                strength_frame,
                text=name,
                variable=variable,
                anchor="w",
                bg=CARD_LIGHT,
                fg=TEXT,
                activebackground=BLUE_SOFT,
                activeforeground=WHITE,
                selectcolor=BLUE_SOFT,
                font=("Segoe UI", 10),
                padx=13,
                pady=11,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=BORDER
            )

            box.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=5,
                pady=5
            )

        strength_frame.columnconfigure(0, weight=1)
        strength_frame.columnconfigure(1, weight=1)

        # Career
        self.add_label(card, "CAREER YOU WANT TO EXPLORE")

        career_entry = tk.Entry(
            card,
            textvariable=self.career,
            bg=CARD_LIGHT,
            fg=WHITE,
            insertbackground=CYAN,
            selectbackground=BLUE,
            selectforeground=WHITE,
            font=("Segoe UI", 11),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BLUE
        )
        career_entry.pack(
            fill="x",
            padx=30,
            ipady=11,
            pady=(0, 25)
        )

        # Button
        self.generate_button = tk.Button(
            card,
            text="GENERATE MY ROADMAP   →",
            command=self.generate_roadmap,
            bg=BLUE,
            fg=WHITE,
            activebackground=BLUE_HOVER,
            activeforeground=WHITE,
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            pady=14
        )
        self.generate_button.pack(
            fill="x",
            padx=30,
            pady=(0, 30)
        )

        self.generate_button.bind(
            "<Enter>",
            lambda e: self.generate_button.configure(
                bg=BLUE_HOVER
            )
        )
        self.generate_button.bind(
            "<Leave>",
            lambda e: self.generate_button.configure(
                bg=BLUE
            )
        )

        career_entry.bind(
            "<Return>",
            lambda event: self.generate_roadmap()
        )

        self.roadmap_area = None

    def create_card(self, parent):
        return tk.Frame(
            parent,
            bg=CARD,
            highlightthickness=1,
            highlightbackground=BORDER
        )

    def add_label(self, parent, text):
        tk.Label(
            parent,
            text=text,
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w",
            padx=30,
            pady=(0, 8)
        )

    # ========================================================
    # Roadmap generation
    # ========================================================

    def generate_roadmap(self):

        education = self.education.get().strip()
        interest = self.interest.get().strip()
        career = self.career.get().strip()

        if not education or not interest or not career:
            messagebox.showwarning(
                "Missing Information",
                "Please fill in all the required fields."
            )
            return

        strengths = [
            name
            for name, variable in self.strength_vars.items()
            if variable.get()
        ]

        if self.roadmap_area is not None:
            self.roadmap_area.destroy()

        self.roadmap_area = tk.Frame(
            self.content,
            bg=BG
        )
        self.roadmap_area.pack(
            fill="x",
            padx=75,
            pady=(0, 38)
        )

        # Section heading
        top = tk.Frame(
            self.roadmap_area,
            bg=BG
        )
        top.pack(fill="x", pady=(0, 15))

        tk.Label(
            top,
            text="02",
            bg=PURPLE,
            fg=WHITE,
            font=("Segoe UI", 10, "bold"),
            padx=9,
            pady=6
        ).pack(side="left", padx=(0, 12))

        tk.Label(
            top,
            text="YOUR PERSONALIZED ROADMAP",
            bg=BG,
            fg=WHITE,
            font=("Segoe UI", 17, "bold")
        ).pack(side="left")

        # Summary card
        summary = tk.Frame(
            self.roadmap_area,
            bg=CARD,
            highlightthickness=1,
            highlightbackground=BORDER
        )
        summary.pack(
            fill="x",
            pady=(0, 18)
        )

        tk.Frame(
            summary,
            bg=CYAN,
            width=5
        ).pack(
            side="left",
            fill="y"
        )

        summary_body = tk.Frame(
            summary,
            bg=CARD
        )
        summary_body.pack(
            fill="both",
            expand=True,
            padx=22,
            pady=20
        )

        tk.Label(
            summary_body,
            text=career,
            bg=CARD,
            fg=WHITE,
            font=("Segoe UI", 25, "bold")
        ).pack(anchor="w")

        tk.Label(
            summary_body,
            text=f"{education}  •  {interest}",
            bg=CARD,
            fg=CYAN,
            font=("Segoe UI", 10, "bold")
        ).pack(
            anchor="w",
            pady=(3, 10)
        )

        summary_text = (
            f"Based on your current level and interest, this roadmap "
            f"gives you a practical starting path for exploring {career}."
        )

        tk.Label(
            summary_body,
            text=summary_text,
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 10),
            wraplength=780,
            justify="left"
        ).pack(anchor="w")

        if strengths:
            tk.Label(
                summary_body,
                text="STRENGTHS  •  " + "   •   ".join(strengths),
                bg=CARD,
                fg=MUTED,
                font=("Segoe UI", 9, "bold"),
                wraplength=780,
                justify="left"
            ).pack(
                anchor="w",
                pady=(13, 0)
            )

        # Roadmap steps
        self.add_step(
            "01",
            "BUILD YOUR FOUNDATION",
            "Start with the fundamentals required for your field. "
            "Focus on programming basics, logical thinking, "
            "mathematics and computer fundamentals.",
            ["Programming", "Logic", "Computer Fundamentals"]
        )

        self.add_step(
            "02",
            "LEARN CORE SKILLS",
            SKILLS.get(
                interest,
                "Develop the technical skills commonly used in your chosen career."
            )
        )

        self.add_step(
            "03",
            "BUILD REAL PROJECTS",
            "Don't only watch tutorials. Build projects that "
            "demonstrate what you have learned.",
            ["Mini Projects", "GitHub", "Portfolio"]
        )

        self.add_step(
            "04",
            "GAIN EXPERIENCE",
            "Participate in hackathons, open-source projects, "
            "internships and college technical communities."
        )

        self.add_step(
            "05",
            "PREPARE FOR YOUR CAREER",
            "Build your resume, improve interview skills, "
            "practice technical questions and create a strong "
            "professional portfolio."
        )

        self.add_step(
            "06",
            "YOUR LONG-TERM GOAL",
            "Continue learning, specialize in a domain and "
            "regularly update your skills as the industry changes.",
            ["Specialize", "Keep Learning", "Stay Relevant"]
        )

        # Footer
        tk.Label(
            self.content,
            text="SKILL GRAPH  •  BUILD YOUR FUTURE",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(pady=(0, 30))

        self.update_idletasks()
        self.canvas.yview_moveto(1.0)

    # ========================================================
    # Roadmap card
    # ========================================================

    def add_step(self, number, title, description, tags=None):

        step = tk.Frame(
            self.roadmap_area,
            bg=CARD,
            highlightthickness=1,
            highlightbackground=BORDER
        )
        step.pack(
            fill="x",
            pady=6
        )

        # Number
        number_box = tk.Frame(
            step,
            bg=BLUE_SOFT,
            width=64
        )
        number_box.pack(
            side="left",
            fill="y"
        )
        number_box.pack_propagate(False)

        tk.Label(
            number_box,
            text=number,
            bg=BLUE_SOFT,
            fg=CYAN,
            font=("Segoe UI", 11, "bold")
        ).pack(expand=True)

        body = tk.Frame(
            step,
            bg=CARD
        )
        body.pack(
            side="left",
            fill="both",
            expand=True,
            padx=20,
            pady=17
        )

        tk.Label(
            body,
            text=title,
            bg=CARD,
            fg=WHITE,
            font=("Segoe UI", 12, "bold")
        ).pack(
            anchor="w",
            pady=(0, 7)
        )

        tk.Label(
            body,
            text=description,
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 10),
            wraplength=760,
            justify="left"
        ).pack(anchor="w")

        if tags:
            tags_frame = tk.Frame(
                body,
                bg=CARD
            )
            tags_frame.pack(
                anchor="w",
                pady=(11, 0)
            )

            for tag in tags:
                tk.Label(
                    tags_frame,
                    text=tag,
                    bg=BLUE_SOFT,
                    fg="#93c5fd",
                    font=("Segoe UI", 8, "bold"),
                    padx=9,
                    pady=5
                ).pack(
                    side="left",
                    padx=(0, 6)
                )


if __name__ == "__main__":
    app = SkillGraph()
    app.mainloop()
