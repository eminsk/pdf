#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Dependencies:
# pip install PyMuPDF Pillow

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from typing import Optional, Tuple
import fitz  # PyMuPDF
from PIL import Image, ImageTk


class PDFViewer(tk.Tk):
    """
    Advanced PDF viewer with two-page spread and page flip animation.
    - Lazy rendering with minimal memory footprint
    - Single/dual page modes
    - Smooth page flip transition effect
    - Full zoom and navigation controls
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("PDF Viewer")
        self.geometry("1280x800")
        self.minsize(800, 600)

        # State
        self.doc: Optional[fitz.Document] = None
        self.page_count: int = 0
        self.page_index: int = 0
        self.zoom: float = 1.0
        self.fit_mode: bool = True
        self.dual_page_mode: bool = False
        self.filepath: Optional[Path] = None

        # Photos for current view
        self.photos: list = []

        # Animation state
        self.is_animating: bool = False
        self.animation_direction: int = 1  # 1 = forward, -1 = backward
        self.animation_progress: float = 0.0

        # Flags
        self._block_scale_callback = False

        # UI colors
        self.ui_bg = "#1d1f23"
        self.canvas_bg = "#111317"
        self.page_bg = "#f7f7f7"
        self.shadow = "#000000"
        self.accent = "#5ab4ff"
        self.fg = "#e8eaed"
        self.muted = "#a9b0b8"
        self.pad = 12

        self._style()
        self._build_ui()
        self._bind_keys()

    # ---------- UI setup ----------

    def _style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        self.configure(bg=self.ui_bg)
        style.configure("TFrame", background=self.ui_bg)
        style.configure("Toolbar.TFrame", background=self.ui_bg)
        style.configure("TButton",
                        background=self.ui_bg, foreground=self.fg,
                        borderwidth=0, padding=(10, 6))
        style.map("TButton",
                  background=[("active", "#2a2e33")],
                  relief=[("pressed", "sunken"), ("!pressed", "flat")])
        style.configure("TLabel", background=self.ui_bg, foreground=self.muted)
        style.configure("Accent.TButton", foreground=self.accent)
        style.configure("Page.TLabel", foreground=self.fg, font=("Segoe UI", 10, "bold"))
        style.configure("TScale", background=self.ui_bg, troughcolor="#2a2e33")

    def _build_ui(self) -> None:
        # Toolbar
        bar = ttk.Frame(self, style="Toolbar.TFrame")
        bar.pack(side="top", fill="x")

        new_btn = ttk.Button(bar, text="📂 Open", style="Accent.TButton", command=self._open_dialog)
        prev_btn = ttk.Button(bar, text="◀", command=lambda: self._go_animated(self.page_index - (2 if self.dual_page_mode else 1), -1))
        next_btn = ttk.Button(bar, text="▶", command=lambda: self._go_animated(self.page_index + (2 if self.dual_page_mode else 1), 1))
        zoom_out_btn = ttk.Button(bar, text="➖", command=self._zoom_out)
        zoom_in_btn = ttk.Button(bar, text="➕", command=self._zoom_in)
        fit_btn = ttk.Button(bar, text="🗖 Fit", command=self._toggle_fit)
        dual_btn = ttk.Button(bar, text="📖 Dual", command=self._toggle_dual_page)

        self.prev_btn = prev_btn
        self.next_btn = next_btn
        self.zoom_out_btn = zoom_out_btn
        self.zoom_in_btn = zoom_in_btn
        self.fit_btn = fit_btn
        self.dual_btn = dual_btn

        new_btn.pack(side="left", padx=(self.pad, 4), pady=(8, 8))
        prev_btn.pack(side="left", padx=2, pady=8)
        next_btn.pack(side="left", padx=2, pady=8)
        dual_btn.pack(side="left", padx=2, pady=8)
        zoom_out_btn.pack(side="left", padx=(16, 2), pady=8)
        zoom_in_btn.pack(side="left", padx=2, pady=8)
        fit_btn.pack(side="left", padx=2, pady=8)

        # Page slider + label
        right = ttk.Frame(bar, style="Toolbar.TFrame")
        right.pack(side="right", padx=(4, self.pad), pady=4)

        self.page_var = tk.DoubleVar(value=1.0)
        self.page_scale = ttk.Scale(right, from_=1, to=1,
                                     orient="horizontal",
                                     length=220,
                                     variable=self.page_var,
                                     command=self._on_scale)
        self.page_scale.state(["disabled"])
        self.page_label = ttk.Label(right, text="—/—", style="Page.TLabel")

        self.page_scale.pack(side="left", padx=8)
        self.page_label.pack(side="left", padx=4)

        # Canvas frame
        self.canvas_frame = ttk.Frame(self, style="TFrame")
        self.canvas_frame.pack(side="top", fill="both", expand=True, padx=self.pad, pady=(0, self.pad))

        self.canvas = tk.Canvas(self.canvas_frame, bg=self.canvas_bg, highlightthickness=0)
        self.h_scroll = ttk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.v_scroll = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        self.h_scroll.pack(side="bottom", fill="x")
        self.v_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="top", fill="both", expand=True)

        self.canvas.bind("<Configure>", lambda e: self.fit_mode and self.doc and self._render())
        self.canvas.bind("<ButtonPress-1>", self._scroll_start)
        self.canvas.bind("<B1-Motion>", self._scroll_move)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

        self._set_controls_state("disabled")

        # Hint overlay
        self.hint = ttk.Label(self, text="📂 Open a PDF (Ctrl+O)\nPrev/Next: ← → Zoom: +/- Fit: F Dual: D",
                              justify="center")
        self.hint.place(relx=0.5, rely=0.5, anchor="center")

    def _bind_keys(self) -> None:
        self.bind_all("<Control-o>", lambda e: self._open_dialog())
        self.bind_all("o", lambda e: self._open_dialog())
        self.bind_all("<Left>", lambda e: self._go_animated(self.page_index - (2 if self.dual_page_mode else 1), -1))
        self.bind_all("<Right>", lambda e: self._go_animated(self.page_index + (2 if self.dual_page_mode else 1), 1))
        self.bind_all("+", lambda e: self._zoom_in())
        self.bind_all("-", lambda e: self._zoom_out())
        self.bind_all("<Control-plus>", lambda e: self._zoom_in())
        self.bind_all("<Control-minus>", lambda e: self._zoom_out())
        self.bind_all("f", lambda e: self._toggle_fit())
        self.bind_all("F", lambda e: self._toggle_fit())
        self.bind_all("d", lambda e: self._toggle_dual_page())
        self.bind_all("D", lambda e: self._toggle_dual_page())

    # ---------- File handling ----------

    def _open_dialog(self) -> None:
        path = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*")),
        )
        path and self._load(Path(path))

    def _load(self, path: Path) -> None:
        self.doc and self.doc.close()
        self.doc = fitz.open(path.as_posix())
        self.filepath = path
        self.page_count = len(self.doc)
        self.page_index = 0
        self.zoom = 1.0
        self.fit_mode = True

        self.page_scale.configure(to=max(1, self.page_count))
        self._block_scale_callback = True
        try:
            self.page_scale.set(1.0)
        finally:
            self._block_scale_callback = False

        self.page_scale.state(["!disabled"])
        self._set_controls_state("!disabled")
        self.hint.place_forget()
        self._render()
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

    def _set_controls_state(self, state: str) -> None:
        for w in (self.prev_btn, self.next_btn, self.zoom_out_btn,
                  self.zoom_in_btn, self.fit_btn, self.dual_btn):
            w.state([state])

    # ---------- Navigation / zoom ----------

    def _go_animated(self, index: int, direction: int) -> None:
        """Navigate with flip animation"""
        if not self.doc or self.is_animating:
            return

        # При двухстраничном режиме корректируем индекс к четному
        if self.dual_page_mode:
            index = max(0, min(self.page_count - 1, index))
            if index % 2 != 0:
                index -= 1  # сделаем индекс четным
        else:
            index = max(0, min(self.page_count - 1, index))

        self._start_flip_animation(index, direction)

    def _start_flip_animation(self, target_idx: int, direction: int) -> None:
        """Initialize page flip animation"""
        if target_idx == self.page_index:
            return
        self.is_animating = True
        self.animation_direction = direction
        self.animation_progress = 0.0
        self.target_page_index = target_idx
        self._animate_flip()

    def _animate_flip(self) -> None:
        """Execute flip animation frame"""
        self.animation_progress = min(1.0, self.animation_progress + 0.15)

        # Render with perspective effect
        self._render_flip_frame()

        (self.animation_progress >= 1.0) and (
            setattr(self, 'page_index', self.target_page_index),
            setattr(self, 'is_animating', False),
            self._update_page_ui(),
            self._render()
        ) or self.after(30, self._animate_flip)

    def _render_flip_frame(self) -> None:
        """Render animation frame with flip effect"""
        self.canvas.delete("all")

        # Calculate flip transform
        progress = self.animation_progress
        scale_x = abs((1.0 - progress) if self.animation_direction > 0 else progress)
        scale_x = max(0.1, scale_x)

        # Render current or next page based on progress
        render_idx = self.page_index if progress < 0.5 else self.target_page_index
        pages_to_render = [render_idx] if not self.dual_page_mode or render_idx + 1 >= self.page_count else [render_idx, render_idx + 1]

        images = [self._get_page_image(idx) for idx in pages_to_render]

        # Combine images horizontally if dual mode
        combined = images[0] if len(images) == 1 else self._combine_images_horizontal(images)

        # Apply flip transform
        new_width = max(1, int(combined.width * scale_x))
        flipped = combined.resize((new_width, combined.height), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(flipped)
        self.photos = [photo]

        # Center on canvas
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        x = (cw - new_width) // 2
        y = (ch - flipped.height) // 2

        self.canvas.create_image(x, y, image=photo, anchor="nw")
        self.canvas.config(scrollregion=(0, 0, cw, ch))

    def _go(self, index: int) -> None:
        """Instant navigation without animation"""
        self.doc and self._set_page(sorted((0, index, self.page_count - 1))[1])

    def _set_page(self, idx: int) -> None:
        self.page_index = idx
        self._update_page_ui()
        self._render()

    def _update_page_ui(self) -> None:
        """Update page counter and slider"""
        self._block_scale_callback = True
        try:
            self.page_scale.set(self.page_index + 1)
        finally:
            self._block_scale_callback = False

    def _zoom_in(self) -> None:
        self.fit_mode = False
        self.zoom = sorted((0.2, self.zoom * 1.25, 6.0))[1]
        self._render()

    def _zoom_out(self) -> None:
        self.fit_mode = False
        self.zoom = sorted((0.2, self.zoom / 1.25, 6.0))[1]
        self._render()

    def _toggle_fit(self) -> None:
        self.fit_mode = not self.fit_mode
        self._render()

    def _toggle_dual_page(self) -> None:
        """Toggle between single and dual page view"""
        self.dual_page_mode = not self.dual_page_mode
        self.dual_btn.configure(text=f"{'📄' if self.dual_page_mode else '📖'} {'Single' if self.dual_page_mode else 'Dual'}")
        self._render()

    def _on_scale(self, v: str) -> None:
        self._block_scale_callback or (
            self._go(int(float(v)) - 1),
        )

    # ---------- Rendering ----------

    def _render(self) -> None:
        self.doc and self._render_pages()

    def _render_pages(self) -> None:
        """Render one or two pages depending on mode"""
        self.update_idletasks()

        # Determine pages to render
        pages_to_render = [self.page_index] if not self.dual_page_mode or self.page_index + 1 >= self.page_count else [self.page_index, self.page_index + 1]

        # Render each page
        images = [self._get_page_image(idx) for idx in pages_to_render]

        # Combine images if dual mode
        combined = images[0] if len(images) == 1 else self._combine_images_horizontal(images)

        # Display
        self._display_image(combined)
        self._update_status()

    def _get_page_image(self, page_idx: int) -> Image.Image:
        """Render single page to PIL Image"""
        page = self.doc.load_page(page_idx)
        rect = page.rect

        cw = max(1, self.canvas.winfo_width() - self.pad * 2)
        ch = max(1, self.canvas.winfo_height() - self.pad * 2)

        # Adjust canvas size for dual mode
        effective_cw = cw // 2 if self.dual_page_mode and self.page_index + 1 < self.page_count else cw

        fit_scale = min(effective_cw / rect.width, ch / rect.height)
        scale = (fit_scale, self.zoom)[not self.fit_mode]
        scale = sorted((0.2, scale, 8.0))[1]

        pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        mode = ("RGB", "RGBA")[pix.alpha > 0]
        return Image.frombytes(mode, (pix.width, pix.height), pix.samples)

    def _combine_images_horizontal(self, images: list) -> Image.Image:
        """Combine two images side by side"""
        widths, heights = zip(*[(img.width, img.height) for img in images])
        total_width = sum(widths) + self.pad
        max_height = max(heights)

        combined = Image.new('RGB', (total_width, max_height), color=(17, 19, 23))

        x_offset = 0
        for img in images:
            combined.paste(img, (x_offset, 0))
            x_offset += img.width + self.pad

        return combined

    def _display_image(self, img: Image.Image) -> None:
        photo = ImageTk.PhotoImage(img)
        self.photos = [photo]

        self.canvas.delete("all")
        w, h = photo.width(), photo.height()

        # Compute centered coordinates
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        x = (cw - w) // 2
        y = (ch - h) // 2

        # Shadow (необязательно)
        offset = 8
        self.canvas.create_rectangle(
            x + offset, y + offset, x + w + offset, y + h + offset,
            fill=self.shadow, outline="", stipple="gray50"
        )
        # Page background
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=self.page_bg, outline="")

        # Place image centered
        self.canvas.create_image(x, y, image=photo, anchor="nw")
        self.canvas.config(scrollregion=(0, 0, max(cw, w), max(ch, h)))

    def _update_status(self) -> None:
        """Update title and page label"""
        name = (self.filepath and self.filepath.name) or "Untitled"
        page_display = f"{self.page_index + 1}-{min(self.page_index + 2, self.page_count)}" if self.dual_page_mode and self.page_index + 1 < self.page_count else f"{self.page_index + 1}"
        self.title(f"{name} — Page {page_display}/{self.page_count}")
        self.page_label.config(text=f"{page_display}/{self.page_count}")

    def _scroll_start(self, event) -> None:
        self.canvas.scan_mark(event.x, event.y)

    def _scroll_move(self, event) -> None:
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def _on_mousewheel(self, event) -> None:
        (event.num == 5 or event.delta < 0) and self.canvas.yview_scroll(1, "unit") or (
            (event.num == 4 or event.delta > 0) and self.canvas.yview_scroll(-1, "unit")
        )


if __name__ == "__main__":
    PDFViewer().mainloop()
