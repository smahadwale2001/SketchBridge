import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageOps
import os
import threading

class TraceTiler:
    def __init__(self, root):
        self.root = root
        self.root.title("Art Trace Pro: Precision Span Control")
        self.root.geometry("1200x900")
        
        self.raw_image = None
        self.tiles = []
        self.overlap_pct = 0.20 
        self.crop_rect = None
        self.point_color = "#FF0000"
        
        # Adjustable Variables
        self.canvas_w = tk.DoubleVar(value=48.0)
        self.canvas_h = tk.DoubleVar(value=36.0)
        self.screen_w = tk.DoubleVar(value=13.6)
        self.screen_h = tk.DoubleVar(value=7.6)
        self.point_thick = tk.IntVar(value=2)
        self.point_span = tk.IntVar(value=15)

        self.setup_ui()

    def setup_ui(self):
        self.ctrl_frame = tk.Frame(self.root, padx=20, pady=20, width=320, bg="#ecf0f1")
        self.ctrl_frame.pack(side="left", fill="y")

        tk.Label(self.ctrl_frame, text="1. CANVAS SIZE (IN)", font=('Arial', 10, 'bold'), bg="#ecf0f1").pack(anchor="w")
        tk.Entry(self.ctrl_frame, textvariable=self.canvas_w).pack(fill="x")
        tk.Entry(self.ctrl_frame, textvariable=self.canvas_h).pack(fill="x")

        tk.Label(self.ctrl_frame, text="\n2. SCREEN SIZE (IN)", font=('Arial', 10, 'bold'), bg="#ecf0f1").pack(anchor="w")
        tk.Entry(self.ctrl_frame, textvariable=self.screen_w).pack(fill="x")
        tk.Entry(self.ctrl_frame, textvariable=self.screen_h).pack(fill="x")

        tk.Label(self.ctrl_frame, text="\n3. POINT GEOMETRY", font=('Arial', 10, 'bold'), bg="#ecf0f1").pack(anchor="w")
        tk.Label(self.ctrl_frame, text="Thickness (Pixels):", bg="#ecf0f1").pack(anchor="w")
        tk.Scale(self.ctrl_frame, from_=1, to=8, orient="horizontal", variable=self.point_thick, bg="#ecf0f1").pack(fill="x")
        tk.Label(self.ctrl_frame, text="Span (Arm Length):", bg="#ecf0f1").pack(anchor="w")
        tk.Scale(self.ctrl_frame, from_=5, to=100, orient="horizontal", variable=self.point_span, bg="#ecf0f1").pack(fill="x")
        
        tk.Label(self.ctrl_frame, text="\nColor:", bg="#ecf0f1").pack(anchor="w")
        color_btn_frame = tk.Frame(self.ctrl_frame, bg="#ecf0f1")
        color_btn_frame.pack(fill="x", pady=5)
        self.color_preview = tk.Frame(color_btn_frame, width=25, height=25, bg=self.point_color, highlightbackground="black", highlightthickness=1)
        self.color_preview.pack(side="left", padx=5)
        tk.Button(color_btn_frame, text="Pick Color", command=self.choose_color).pack(side="left", fill="x", expand=True)

        tk.Button(self.ctrl_frame, text="UPLOAD IMAGE", command=self.load_image, bg="#3498db", fg="white", pady=10).pack(fill="x", pady=20)
        self.btn_save = tk.Button(self.ctrl_frame, text="SAVE TILES", command=self.save_tiles_action, bg="#04AA6D", fg="white",disabledforeground="white", state="disabled")
        self.btn_save.pack(fill="x", pady=5)
        self.btn_view = tk.Button(self.ctrl_frame, text="START TRACING", command=self.start_tracing_thread, bg="#FF0000", fg="white",disabledforeground="white", font=('bold'), state="disabled")
        self.btn_view.pack(fill="x", pady=5)

        self.preview_canvas = tk.Canvas(self.root, bg="#2c3e50", cursor="cross")
        self.preview_canvas.pack(side="right", expand=True, fill="both")
        self.preview_canvas.bind("<ButtonPress-1>", self.start_crop)
        self.preview_canvas.bind("<B1-Motion>", self.draw_crop)
        self.preview_canvas.bind("<ButtonRelease-1>", self.end_crop)

    def choose_color(self):
        color = colorchooser.askcolor(title="Select Tracepoint Color")[1]
        if color:
            self.point_color = color
            self.color_preview.config(bg=color)

    def load_image(self):
        path = filedialog.askopenfilename()
        if path:
            self.raw_image = Image.open(path).convert("RGB")
            self.btn_view.config(state="normal")
            self.btn_save.config(state="normal")
            self.update_preview()

    def update_preview(self):
        self.root.update()
        pw, ph = self.preview_canvas.winfo_width(), self.preview_canvas.winfo_height()
        ratio = min(pw/self.raw_image.width, ph/self.raw_image.height)
        new_size = (int(self.raw_image.width * ratio), int(self.raw_image.height * ratio))
        self.preview_img = self.raw_image.resize(new_size, Image.Resampling.LANCZOS)
        self.tk_preview = ImageTk.PhotoImage(self.preview_img)
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(pw//2, ph//2, image=self.tk_preview)
        self.draw_ratio = ratio

    def start_crop(self, event):
        self.s_x, self.s_y = event.x, event.y
        self.rect = self.preview_canvas.create_rectangle(self.s_x, self.s_y, event.x, event.y, outline="yellow")

    def draw_crop(self, event):
        self.preview_canvas.coords(self.rect, self.s_x, self.s_y, event.x, event.y)

    def end_crop(self, event):
        off_x = (self.preview_canvas.winfo_width() - self.preview_img.width) // 2
        off_y = (self.preview_canvas.winfo_height() - self.preview_img.height) // 2
        self.crop_rect = (
            (min(self.s_x, event.x) - off_x) / self.draw_ratio,
            (min(self.s_y, event.y) - off_y) / self.draw_ratio,
            (max(self.s_x, event.x) - off_x) / self.draw_ratio,
            (max(self.s_y, event.y) - off_y) / self.draw_ratio
        )

    def generate_global_tiles(self):
        source = self.raw_image.crop(self.crop_rect) if self.crop_rect else self.raw_image
        canvas_px_w = 2000 
        canvas_px_h = int(canvas_px_w * (self.canvas_h.get() / self.canvas_w.get()))
        
        canvas_base = Image.new("RGB", (canvas_px_w, canvas_px_h), (255, 255, 255))
        fitted_img = ImageOps.contain(source, (canvas_px_w, canvas_px_h))
        offset = ((canvas_px_w - fitted_img.width) // 2, (canvas_px_h - fitted_img.height) // 2)
        canvas_base.paste(fitted_img, offset)

        step_w_ratio = (self.screen_w.get() * (1 - self.overlap_pct)) / self.canvas_w.get()
        step_h_ratio = (self.screen_h.get() * (1 - self.overlap_pct)) / self.canvas_h.get()
        
        tile_px_w = int(canvas_px_w * (self.screen_w.get() / self.canvas_w.get()))
        tile_px_h = int(canvas_px_h * (self.screen_h.get() / self.canvas_h.get()))

        cols = int((1 - (self.screen_w.get()/self.canvas_w.get())) / step_w_ratio) + 2
        rows = int((1 - (self.screen_h.get()/self.canvas_h.get())) / step_h_ratio) + 2

        global_points = set()
        for r in range(rows):
            for c in range(cols):
                l = c * (tile_px_w * (1 - self.overlap_pct))
                t = r * (tile_px_h * (1 - self.overlap_pct))
                ins = 40 
                pts = [(l+ins, t+ins), (l+tile_px_w-ins, t+ins), 
                       (l+ins, t+tile_px_h-ins), (l+tile_px_w-ins, t+tile_px_h-ins), 
                       (l+tile_px_w/2, t+tile_px_h/2)]
                for p in pts: global_points.add(p)

        self.tiles = []
        thick = self.point_thick.get()
        span = self.point_span.get()

        for r in range(rows):
            row_list = []
            for c in range(cols):
                left = c * (tile_px_w * (1 - self.overlap_pct))
                top = r * (tile_px_h * (1 - self.overlap_pct))
                tile = canvas_base.crop((left, top, left + tile_px_w, top + tile_px_h))
                draw = ImageDraw.Draw(tile)
                
                for gx, gy in global_points:
                    if left <= gx <= left+tile_px_w and top <= gy <= top+tile_px_h:
                        lx, ly = gx - left, gy - top
                        draw.line([(lx-span, ly), (lx+span, ly)], fill=self.point_color, width=thick)
                        draw.line([(lx, ly-span), (lx, ly+span)], fill=self.point_color, width=thick)
                row_list.append(tile)
            self.tiles.append(row_list)

    def show_loading(self):
        self.loader = tk.Toplevel(self.root)
        self.loader.title("Processing")
        self.loader.geometry("300x150")
        self.loader.transient(self.root)
        self.loader.grab_set()
        
        center_x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 150
        center_y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 75
        self.loader.geometry(f"+{center_x}+{center_y}")
        
        tk.Label(self.loader, text="GENERATE TILES...", font=("Arial", 12, "bold")).pack(pady=20)
        tk.Label(self.loader, text="Processing high-res image\nPlease wait...").pack()

    def start_tracing_thread(self):
        self.show_loading()
        threading.Thread(target=self.run_background_gen).start()

    def run_background_gen(self):
        self.generate_global_tiles()
        self.root.after(0, self.finish_loading_and_open)

    def finish_loading_and_open(self):
        self.loader.destroy()
        self.open_viewer()

    def save_tiles_action(self):
        self.show_loading()
        threading.Thread(target=self.run_background_save).start()

    def run_background_save(self):
        self.generate_global_tiles()
        self.root.after(0, self.complete_save)

    def complete_save(self):
        self.loader.destroy()
        folder = filedialog.askdirectory()
        if folder:
            for r in range(len(self.tiles)):
                for c in range(len(self.tiles[0])):
                    self.tiles[r][c].save(os.path.join(folder, f"R{r+1}_C{c+1}.png"))
            messagebox.showinfo("Success", "Files exported.")

    def open_viewer(self):
        self.viewer = tk.Toplevel(self.root)
        self.viewer.attributes("-fullscreen", True)
        self.viewer.configure(bg="black")
        self.view_label = tk.Label(self.viewer, bg="black")
        self.view_label.pack(expand=True, fill="both")
        self.cur_r, self.cur_c = 0, 0
        self.viewer.bind("<Escape>", lambda e: self.viewer.destroy())
        self.viewer.bind("<Right>", lambda e: self.navigate(0, 1))
        self.viewer.bind("<Left>", lambda e: self.navigate(0, -1))
        self.viewer.bind("<Down>", lambda e: self.navigate(1, 0))
        self.viewer.bind("<Up>", lambda e: self.navigate(-1, 0))
        self.show_tile()

    def navigate(self, dr, dc):
        if 0 <= self.cur_r + dr < len(self.tiles) and 0 <= self.cur_c + dc < len(self.tiles[0]):
            self.cur_r += dr; self.cur_c += dc
            self.show_tile()

    def show_tile(self):
        img = self.tiles[self.cur_r][self.cur_c]
        sw, sh = self.viewer.winfo_screenwidth(), self.viewer.winfo_screenheight()
        resized = img.resize((sw, sh), Image.Resampling.LANCZOS)
        self.tk_tile = ImageTk.PhotoImage(resized)
        self.view_label.config(image=self.tk_tile)

if __name__ == "__main__":
    root = tk.Tk()
    app = TraceTiler(root)
    root.mainloop()