# --- START OF FILE image_distance_measurement.py ---

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, colorchooser, font as tkfont
from PIL import Image, ImageTk, ExifTags
import math
import os
import traceback

# Define Measurement Modes
MODE_LINE = "line"
MODE_CIRCLE = "circle"

class ImageDistanceMeasurementTool:
    def __init__(self, root):
        self.root = root
        self.root.title("圖像距離與圓直徑測量工具 v3.0\nImage Distance & Circle Tool v3.0") 
        self.root.geometry("1200x850") 

        #直接設置顏色和字體屬性
        # 中文和英文文字顏色在此處設置，以進行區分
        self.chinese_color = "blue" 
        self.english_color = "darkgreen" 
        self.default_font_family = tkfont.nametofont("TkDefaultFont").cget("family")
        self.default_font_size = tkfont.nametofont("TkDefaultFont").cget("size")
        
        self.common_titles = {
            "confirm": "確認\nConfirm", "info": "提示\nInfo", "warning": "警告\nWarning",
            "error": "錯誤\nError", "input_error": "輸入錯誤\nInput Error",
            "calc_failed": "計算失敗\nCalculation Failed", "calc_error": "計算錯誤\nCalculation Error",
            "success": "成功\nSuccess", "library_missing": "缺少庫\nLibrary Missing"
        }
        
        self.image_a = None; self.image_b = None; self.photo_a = None; self.photo_b = None
        self.points_a = []; self.points_b = []; self.scale_value = 0.0
        self.image_a_path = ""; self.image_b_path = ""; self.image_a_display = {}; self.image_b_display = {}
        self.zoom_factor_a = 1.0; self.zoom_factor_b = 1.0
        
        self.point_a_color_var = tk.StringVar(value="red"); self.point_a_radius_var = tk.IntVar(value=2) 
        self.point_b_color_var = tk.StringVar(value="blue"); self.point_b_radius_var = tk.IntVar(value=2)

        self.measurement_mode = tk.StringVar(value=MODE_LINE) 

        # --- Crosshair line IDs ---
        self.crosshair_line_h_a = None
        self.crosshair_line_v_a = None
        self.crosshair_color = "gray70" # Color for the crosshair

        # --- Main Content Frame ---
        self.main_content_frame = tk.Frame(self.root)
        self.main_content_frame.pack(fill=tk.BOTH, expand=True)

        # Initial UI Build
        self.build_ui()
        
        # 移動到 build_ui 之後，確保 log_text 已經被創建
        self.log_initial_messages()

    def build_ui(self):
        """Builds the UI structure."""
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()
            
        self.outer_paned_window = tk.PanedWindow(self.main_content_frame, orient=tk.VERTICAL, sashrelief=tk.RAISED, sashwidth=6)
        self.outer_paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5) 
        self.main_image_paned_window = tk.PanedWindow(self.outer_paned_window, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=6)
        self.left_panel_frame = tk.Frame(self.main_image_paned_window, borderwidth=1, relief=tk.SUNKEN)
        self.main_image_paned_window.add(self.left_panel_frame, minsize=250, stretch="always") 
        self.right_panel_frame = tk.Frame(self.main_image_paned_window, borderwidth=1, relief=tk.SUNKEN)
        self.main_image_paned_window.add(self.right_panel_frame, minsize=250, stretch="always")
        self.outer_paned_window.add(self.main_image_paned_window, minsize=400, stretch="always")
        self.bottom_container_frame = tk.Frame(self.outer_paned_window) 
        
        self.setup_image_panel_a(self.left_panel_frame) 
        self.setup_image_panel_b(self.right_panel_frame) 
        self.setup_bottom_panel_content(self.bottom_container_frame)
        self.outer_paned_window.add(self.bottom_container_frame, minsize=150, stretch="never")  

    def log_initial_messages(self):
        self.log_message("應用程序已啟動。\nApplication started.")
        self.log_message("提示: 使用鼠標左鍵選擇點，中/右鍵拖動圖片。\nTip: Left-click to select points, Middle/Right-click to pan image.")
        self.log_message("提示: 可在圖片控制區調整點的顏色和大小。\nTip: Adjust point color and size in the image control area.")
        self.log_message("點擊右上角 '使用說明' 按鈕查看詳細操作指南。\nClick 'Instructions' button for detailed guide.")

    def _create_bilingual_label_widget(self, parent, initial_cn_text, initial_en_text, font_size_delta=0, font_weight="normal", fixed_color=None, relief=tk.FLAT, borderwidth=0, justify_cn='left', justify_en='left'):
        container = tk.Frame(parent, bg=parent.cget("bg"), relief=relief, borderwidth=borderwidth)
        widget_font = tkfont.Font(family=self.default_font_family, size=self.default_font_size + font_size_delta, weight=font_weight)
        lbl_cn = tk.Label(container, text=initial_cn_text, font=widget_font, fg=fixed_color if fixed_color else self.chinese_color, bg=container.cget("bg"), justify=justify_cn, anchor='w')
        lbl_en = tk.Label(container, text=initial_en_text, font=widget_font, fg=fixed_color if fixed_color else self.english_color, bg=container.cget("bg"), justify=justify_en, anchor='w')
        if initial_cn_text: lbl_cn.pack(fill=tk.X) 
        if initial_en_text: lbl_en.pack(fill=tk.X)
        def update_text(cn_text, en_text):
            lbl_cn.config(text=cn_text); lbl_en.config(text=en_text)
            if cn_text and cn_text.strip(): lbl_cn.pack(fill=tk.X, anchor='w', before=lbl_en if en_text and en_text.strip() else None)
            else: lbl_cn.pack_forget()
            if en_text and en_text.strip(): lbl_en.pack(fill=tk.X, anchor='w')
            else: lbl_en.pack_forget()
        container.update_text = update_text
        return container

    def _create_bilingual_button(self, parent, cn_text, en_text, command_func, bg_color=None, font_weight="normal"):
        btn_font = tkfont.Font(family=self.default_font_family, size=self.default_font_size, weight=font_weight)
        btn_frame = tk.Frame(parent, relief=tk.RAISED, borderwidth=2)
        effective_bg = bg_color if bg_color else parent.cget("bg")
        btn_frame.config(bg=effective_bg)
        lbl_cn = tk.Label(btn_frame, text=cn_text, fg=self.chinese_color, bg=effective_bg, font=btn_font, padx=3, pady=0); lbl_cn.pack(fill=tk.X)
        lbl_en = tk.Label(btn_frame, text=en_text, fg=self.english_color, bg=effective_bg, font=btn_font, padx=3, pady=0); lbl_en.pack(fill=tk.X)
        widgets_to_bind = [btn_frame, lbl_cn, lbl_en]
        hover_bg = "#e0e0e0" if effective_bg not in ["#e0e0e0", "#d0d0d0"] else "#c0c0c0"
        def release_action(event_widget):
            if event_widget.winfo_exists(): event_widget.config(relief=tk.RAISED)
        for w in widgets_to_bind:
            w.bind("<ButtonPress-1>", lambda e, f=command_func, bf=btn_frame: (bf.config(relief=tk.SUNKEN), self.root.after(50, f)))
            w.bind("<ButtonRelease-1>", lambda e, bf=btn_frame: self.root.after(1, lambda: release_action(bf)))
            w.bind("<Enter>", lambda e, bf=btn_frame: bf.config(bg=hover_bg) if str(bf.cget("relief")) != str(tk.SUNKEN) else None)
            w.bind("<Leave>", lambda e, bf=btn_frame: bf.config(bg=effective_bg) if str(bf.cget("relief")) != str(tk.SUNKEN) else None)
        return btn_frame

    def setup_bottom_panel_content(self, parent_frame):
        self.bottom_left_controls_frame = tk.Frame(parent_frame); self.bottom_left_controls_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), pady=5)


        mode_frame = tk.Frame(self.bottom_left_controls_frame)
        mode_frame.pack(anchor='w', pady=2)
        mode_label = self._create_bilingual_label_widget(mode_frame, "模式:", "Mode:")
        mode_label.pack(side=tk.LEFT, padx=(0,5))
        self.line_radio = tk.Radiobutton(mode_frame, text="直線測量 (Line)", variable=self.measurement_mode, value=MODE_LINE, command=self.redraw_points_a)
        self.line_radio.pack(side=tk.LEFT)
        self.circle_radio = tk.Radiobutton(mode_frame, text="直徑畫圓 (Circle)", variable=self.measurement_mode, value=MODE_CIRCLE, command=self.redraw_points_a)
        self.circle_radio.pack(side=tk.LEFT, padx=(5,0))
        self.coord_display_label = self._create_bilingual_label_widget(self.bottom_left_controls_frame, "鼠標坐標 (A): ---", "Mouse Coordinate (A): ---", relief=tk.SUNKEN, borderwidth=1); 
        self.coord_display_label.pack(fill=tk.X, pady=0, anchor=tk.W)
        
        author_reset_frame = tk.Frame(self.bottom_left_controls_frame, height=107)
        author_reset_frame.pack(fill=tk.X, pady=0)
        author_reset_frame.pack_propagate(False) 
        
        avatar_frame = tk.Frame(author_reset_frame, bg="white", height=107)
        avatar_frame.pack(side=tk.LEFT, pady=2, fill=tk.Y)
        
        try:
            avatar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "author_avatar.png")
            if os.path.exists(avatar_path):
                avatar_img_pil = Image.open(avatar_path)

                # --- 開始修改：保持圖片比例 ---
                original_width = avatar_img_pil.width
                original_height = avatar_img_pil.height
                
                max_display_width = 60  # 目標最大顯示寬度
                # avatar_frame 的高度是107，我們將其作為最大顯示高度
                max_display_height = 107 

                if original_width > 0 and original_height > 0: # 確保原始尺寸有效
                    # 計算寬度和高度的縮放比例
                    ratio_w = max_display_width / original_width
                    ratio_h = max_display_height / original_height
                    
                    # 選擇較小的縮放比例以確保圖片能完整放入目標框內且不變形
                    scale_ratio = min(ratio_w, ratio_h)
                    
                    # 計算新的寬度和高度
                    new_width = int(original_width * scale_ratio)
                    new_height = int(original_height * scale_ratio)
                    
                    # 確保調整後的尺寸至少為 1x1 像素
                    new_width = max(1, new_width)
                    new_height = max(1, new_height)
                else: # 如果原始尺寸無效，則使用預設或最大尺寸 (可選，或報錯)
                    # 這裡我們讓它盡可能大，但保持在60x107內
                    # 如果圖片本身就小於60x107，則使用原始尺寸
                    new_width = min(original_width if original_width > 0 else max_display_width, max_display_width)
                    new_height = min(original_height if original_height > 0 else max_display_height, max_display_height)


                if hasattr(Image, "Resampling"):
                    avatar_img_pil = avatar_img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
                else: 
                    avatar_img_pil = avatar_img_pil.resize((new_width, new_height), Image.LANCZOS)
                # --- 結束修改 ---
                
                self.avatar_photo = ImageTk.PhotoImage(avatar_img_pil)
                avatar_label_widget = tk.Label(avatar_frame, image=self.avatar_photo, bg="white")
                avatar_label_widget.pack(side=tk.LEFT, padx=5, pady=2)
                
                author_info_label = tk.Label(avatar_frame, text="作者: Wesley Chang, 2025-May", 
                                      font=(self.default_font_family, self.default_font_size), 
                                      fg="black", bg="white")
                author_info_label.pack(side=tk.LEFT, padx=5, pady=2)
            else:
                empty_author_label = tk.Label(avatar_frame, text="Author: Wesley Chang, May 2025", 
                                      font=(self.default_font_family, self.default_font_size), 
                                      fg="black", bg="white", height=2) 
                empty_author_label.pack(side=tk.LEFT, padx=5, pady=2)
                self.log_message("未找到作者頭像圖片。\nAuthor avatar image not found.")
        except Exception as e:
            empty_author_label_error = tk.Label(avatar_frame, text="作者: Wesley Chang, 2025-May", 
                                  font=(self.default_font_family, self.default_font_size), 
                                  fg="black", bg="white", height=2) 
            empty_author_label_error.pack(side=tk.LEFT, padx=5, pady=2)
            self.log_message(f"加載作者頭像時出錯: {str(e)}\nError loading author avatar: {str(e)}")
        
        self.reset_btn = self._create_bilingual_button(author_reset_frame, "重置所有", "Reset All", self.reset_all, bg_color="lightcoral")
        self.reset_btn.pack(side=tk.RIGHT, pady=2, padx=5)
      
        self.bottom_right_frame = tk.Frame(parent_frame); self.bottom_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        self.log_label_widget = self._create_bilingual_label_widget(self.bottom_right_frame, "操作日誌:", "Operation Log:"); self.log_label_widget.pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(self.bottom_right_frame, height=5, wrap=tk.WORD); self.log_text.pack(fill=tk.BOTH, expand=True); self.log_text.config(state=tk.DISABLED)

    def setup_image_panel_a(self, parent_panel): 
        top_controls_a = tk.Frame(parent_panel); top_controls_a.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5,2))

        self.load_image_a_btn = self._create_bilingual_button(top_controls_a, "加載待測圖片 (A)", "Load Image (A)", self.load_image_a); self.load_image_a_btn.pack(side=tk.LEFT, pady=(0,3), padx=(0,5))
        self.zoom_frame_a = tk.Frame(top_controls_a); self.zoom_frame_a.pack(side=tk.LEFT, pady=(0,3))
        self.zoom_in_btn_a = self._create_bilingual_button(self.zoom_frame_a, "放大 +", "Zoom In +", self.zoom_in_a); self.zoom_in_btn_a.pack(side=tk.LEFT, padx=1)
        self.zoom_out_btn_a = self._create_bilingual_button(self.zoom_frame_a, "縮小 -", "Zoom Out -", self.zoom_out_a); self.zoom_out_btn_a.pack(side=tk.LEFT, padx=1)
        self.zoom_reset_btn_a = self._create_bilingual_button(self.zoom_frame_a, "重置縮放", "Reset Zoom", self.zoom_reset_a); self.zoom_reset_btn_a.pack(side=tk.LEFT, padx=1)
        self.zoom_label_a = self._create_bilingual_label_widget(self.zoom_frame_a, "縮放: 100%", "Zoom: 100%"); self.zoom_label_a.pack(side=tk.LEFT, padx=2, pady=2)
        canvas_container_a = tk.Frame(parent_panel); canvas_container_a.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.scrollbar_x_a = tk.Scrollbar(canvas_container_a, orient=tk.HORIZONTAL); self.scrollbar_x_a.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas_a_subframe = tk.Frame(canvas_container_a); self.canvas_a_subframe.pack(fill=tk.BOTH, expand=True)
        self.canvas_a = tk.Canvas(self.canvas_a_subframe, bg="lightgray", cursor="crosshair", xscrollcommand=self.scrollbar_x_a.set)
        self.scrollbar_y_a = tk.Scrollbar(self.canvas_a_subframe, orient=tk.VERTICAL, command=self.canvas_a.yview); self.canvas_a.config(yscrollcommand=self.scrollbar_y_a.set)
        self.scrollbar_y_a.pack(side=tk.RIGHT, fill=tk.Y); self.canvas_a.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); self.scrollbar_x_a.config(command=self.canvas_a.xview)
        self.canvas_a.bind("<Button-1>", self.on_canvas_a_click); self.canvas_a.bind("<ButtonPress-2>", self.start_pan_a); self.canvas_a.bind("<ButtonPress-3>", self.start_pan_a)
        self.canvas_a.bind("<B2-Motion>", self.pan_image_a); self.canvas_a.bind("<B3-Motion>", self.pan_image_a); 
        self.canvas_a.bind("<Motion>", self.update_coordinate_display); self.canvas_a.bind("<Leave>", self.clear_coordinate_display)
        self._build_panel_a_controls(parent_panel) 

    def _build_panel_a_controls(self, parent_frame): 
        bottom_controls_a = tk.Frame(parent_frame)
        bottom_controls_a.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(2,5))
        
        self.points_label_a = self._create_bilingual_label_widget(bottom_controls_a, "已選點 (A): 0", "Selected Points (A): 0")
        self.points_label_a.pack(side=tk.LEFT, padx=(0,5), pady=2)
        
        self.dist_x_label_a = self._create_bilingual_label_widget(bottom_controls_a, "水平距離: ---", "Horiz Dist: ---")
        self.dist_x_label_a.pack(side=tk.LEFT, padx=(0, 5), pady=2)
        
        self.dist_y_label_a = self._create_bilingual_label_widget(bottom_controls_a, "垂直距離: ---", "Vert Dist: ---")
        self.dist_y_label_a.pack(side=tk.LEFT, padx=(0, 10), pady=2)
        
        appearance_frame_a = tk.Frame(bottom_controls_a)
        appearance_frame_a.pack(side=tk.LEFT, padx=(0,5), pady=2)
        
        self.point_a_color_choose_btn = self._create_bilingual_button(appearance_frame_a, "點顏色(A)", "Pt Color(A)", lambda: self.choose_color(self.point_a_color_var, "A"))
        self.point_a_color_choose_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.point_a_radius_label = self._create_bilingual_label_widget(appearance_frame_a, "點半徑(A):", "Pt Radius(A):")
        self.point_a_radius_label.pack(side=tk.LEFT, padx=(0,1))
        
        self.point_a_radius_spinbox = tk.Spinbox(appearance_frame_a, from_=1, to=20, textvariable=self.point_a_radius_var, width=3, command=self.apply_appearance_a, font=(self.default_font_family, self.default_font_size))
        self.point_a_radius_spinbox.pack(side=tk.LEFT, padx=1)
        
        self.clear_points_a_btn = self._create_bilingual_button(bottom_controls_a, "清除點 (A)", "Clear Pts (A)", self.clear_points_a)
        self.clear_points_a_btn.pack(side=tk.LEFT, pady=2, padx=(5,0))
        
        self.point_a_radius_var.trace_add("write", lambda *args: self.apply_appearance_a())
        self.point_a_color_var.trace_add("write", lambda *args: self.apply_appearance_a())

    def setup_image_panel_b(self, parent_panel): 
        top_controls_b = tk.Frame(parent_panel); top_controls_b.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5,2))
        self.load_image_b_btn = self._create_bilingual_button(top_controls_b, "加載尺規圖片 (B)", "Load Ruler Image (B)", self.load_image_b); self.load_image_b_btn.pack(side=tk.LEFT, pady=(0,3), padx=(0,5))
        self.zoom_frame_b = tk.Frame(top_controls_b); self.zoom_frame_b.pack(side=tk.LEFT, pady=(0,3))
        self.zoom_in_btn_b = self._create_bilingual_button(self.zoom_frame_b, "放大 +", "Zoom In +", self.zoom_in_b); self.zoom_in_btn_b.pack(side=tk.LEFT, padx=1)
        self.zoom_out_btn_b = self._create_bilingual_button(self.zoom_frame_b, "縮小 -", "Zoom Out -", self.zoom_out_b); self.zoom_out_btn_b.pack(side=tk.LEFT, padx=1)
        self.zoom_reset_btn_b = self._create_bilingual_button(self.zoom_frame_b, "重置縮放", "Reset Zoom", self.zoom_reset_b); self.zoom_reset_btn_b.pack(side=tk.LEFT, padx=1)
        self.zoom_label_b = self._create_bilingual_label_widget(self.zoom_frame_b, "縮放: 100%", "Zoom: 100%"); self.zoom_label_b.pack(side=tk.LEFT, padx=2, pady=2)
        self.help_btn_new_location = self._create_bilingual_button(top_controls_b, "使用說明", "Instructions", self.show_help_window); 
        self.help_btn_new_location.pack(side=tk.RIGHT, padx=5, pady=(0,3))
        canvas_container_b = tk.Frame(parent_panel); canvas_container_b.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.scrollbar_x_b = tk.Scrollbar(canvas_container_b, orient=tk.HORIZONTAL); self.scrollbar_x_b.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas_b_subframe = tk.Frame(canvas_container_b); self.canvas_b_subframe.pack(fill=tk.BOTH, expand=True)
        self.canvas_b = tk.Canvas(self.canvas_b_subframe, bg="lightgray", cursor="crosshair", xscrollcommand=self.scrollbar_x_b.set)
        self.scrollbar_y_b = tk.Scrollbar(self.canvas_b_subframe, orient=tk.VERTICAL, command=self.canvas_b.yview); self.canvas_b.config(yscrollcommand=self.scrollbar_y_b.set)
        self.scrollbar_y_b.pack(side=tk.RIGHT, fill=tk.Y); self.canvas_b.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); self.scrollbar_x_b.config(command=self.canvas_b.xview)
        self.canvas_b.bind("<Button-1>", self.on_canvas_b_click); self.canvas_b.bind("<ButtonPress-2>", self.start_pan_b); self.canvas_b.bind("<ButtonPress-3>", self.start_pan_b)
        self.canvas_b.bind("<B2-Motion>", self.pan_image_b); self.canvas_b.bind("<B3-Motion>", self.pan_image_b)
        self._build_panel_b_controls(parent_panel) 

    def _build_panel_b_controls(self, parent_frame): 
        bottom_controls_b = tk.Frame(parent_frame); 
        bottom_controls_b.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(2,5))
        self.points_label_b = self._create_bilingual_label_widget(bottom_controls_b, "已選點 (B): 0", "Selected Points (B): 0"); self.points_label_b.pack(side=tk.LEFT, padx=(0,10), pady=2)
        appearance_frame_b = tk.Frame(bottom_controls_b); 
        appearance_frame_b.pack(side=tk.LEFT, padx=(0,5), pady=2) 
        self.point_b_color_choose_btn = self._create_bilingual_button(appearance_frame_b, "點顏色(B)", "Pt Color(B)", lambda: self.choose_color(self.point_b_color_var, "B")); 
        self.point_b_color_choose_btn.pack(side=tk.LEFT, padx=(0, 5)) 
        self.point_b_radius_label = self._create_bilingual_label_widget(appearance_frame_b, "點半徑(B):", "Pt Radius(B):"); self.point_b_radius_label.pack(side=tk.LEFT, padx=(0,1))
        self.point_b_radius_spinbox = tk.Spinbox(appearance_frame_b, from_=1, to=20, textvariable=self.point_b_radius_var, width=3, command=self.apply_appearance_b, font=(self.default_font_family, self.default_font_size)); self.point_b_radius_spinbox.pack(side=tk.LEFT, padx=1)
        self.clear_points_b_btn = self._create_bilingual_button(appearance_frame_b, "清除點", "Clear Pts", self.clear_points_b)
        self.clear_points_b_btn.pack(side=tk.LEFT, padx=(5,0)) 
        self.point_b_radius_var.trace_add("write", lambda *args: self.apply_appearance_b()); self.point_b_color_var.trace_add("write", lambda *args: self.apply_appearance_b())
        scale_input_frame = tk.Frame(bottom_controls_b); scale_input_frame.pack(side=tk.LEFT, padx=(0,5), pady=2)
        self.scale_label = self._create_bilingual_label_widget(scale_input_frame, "實際距離:", "Actual Dist:"); self.scale_label.pack(side=tk.LEFT, padx=(0,1))
        self.scale_entry = tk.Entry(scale_input_frame, width=7, font=(self.default_font_family, self.default_font_size)); self.scale_entry.pack(side=tk.LEFT, padx=1)
        self.unit_var = tk.StringVar(value="mm"); self.unit_options = ["mm", "cm", "m", "inch", "µm", "pixel"]
        self.unit_dropdown = tk.OptionMenu(scale_input_frame, self.unit_var, *self.unit_options); self.unit_dropdown.config(font=(self.default_font_family, self.default_font_size), relief=tk.RAISED, borderwidth=1, width=4, padx=1, pady=0); self.unit_dropdown.pack(side=tk.LEFT, padx=1)
        self.set_scale_btn = self._create_bilingual_button(bottom_controls_b, "設比例尺", "Set Scale", self.set_scale) 
        self.set_scale_btn.pack(side=tk.LEFT, pady=2, padx=(0,5)) 
        self.scale_display_label = self._create_bilingual_label_widget(bottom_controls_b, "比例尺: 未設定", "Scale: Not Set"); self.scale_display_label.pack(side=tk.LEFT, pady=2)

    def show_help_window(self):
        help_win = tk.Toplevel(self.root)
        help_win.title("使用說明 - 圖像距離與圓直徑工具 v3.0\nInstructions - Image Distance & Circle Tool v3.0") 
        help_win.geometry("750x700"); 
        help_win.resizable(True, True)
        help_text_widget = scrolledtext.ScrolledText(help_win, wrap=tk.WORD, padx=10, pady=10, font=(self.default_font_family, self.default_font_size + 1))
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        help_text_widget.tag_configure("chinese_help", foreground=self.chinese_color)
        help_text_widget.tag_configure("english_help", foreground=self.english_color)
        help_text_widget.tag_configure("header_help", font=(self.default_font_family, self.default_font_size + 2, "bold"), foreground="black")
        help_text_widget.tag_configure("author_info", foreground="gray", font=(self.default_font_family, self.default_font_size - 1)) 
        help_content_raw = """
<H>圖像距離與圓直徑測量工具 v3.0 - 功能與使用方法</H>
<H>Image Distance & Circle Tool v3.0 - Features and Usage</H>

<H>【功能簡介】【Introduction】</H>

<CH>本工具提供兩種主要測量模式：</CH>
<EN>This tool provides two main measurement modes:</EN>

<CH>1. 直線測量： 計算圖像中兩點之間的直線距離（包括總長度、水平和垂直分量）。</CH>
<EN>   Line Measurement: Calculate the linear distance between two points in the image (including total length, horizontal, and vertical components).</EN>

<CH>2. 直徑畫圓： 以選定的兩點作為直徑，繪製一個圓形，並顯示其直徑。</CH>
<EN>   Draw Circle by Diameter: Draw a circle using the two selected points as its diameter and display the diameter value.</EN>

<CH>3. 您可以透過右側的尺規圖片設定比例尺，以獲得實際物理單位（如 mm, cm）的測量結果。</CH>
<EN>   You can set a scale using the ruler image on the right to obtain measurement results in actual physical units (e.g., mm, cm).</EN>

<H>【主要操作區域】【Main Operation Areas】</H>

<CH>1. 左側面板 (圖片 A): 加載和操作「待測圖片」，進行點選、測量或畫圓。</CH>
<EN>   Left Panel (Image A): Load and operate the "Target Image" for selecting points, measuring, or drawing circles.</EN>

<CH>2. 右側面板 (圖片 B): 加載和操作「尺規圖片」，用於設定比例尺。</CH>
<EN>   Right Panel (Image B): Load and operate the "Ruler Image" used for setting the scale.</EN>

<CH>3. 底部面板:</CH>
<EN>   Bottom Panel:</EN>

<CH>   - 左下方：模式選擇（直線/畫圓）、滑鼠座標顯示、重置按鈕。</CH>
<EN>   - Bottom-Left: Mode selection (Line/Circle), mouse coordinate display, reset button.</EN>

<CH>   - 右下方：操作日誌。</CH>
<EN>   - Bottom-Right: Operation log.</EN>

<CH>4. 圖片面板上方: 加載圖片按鈕、縮放控制項。「使用說明」按鈕位於圖片 B 的縮放控制項右側。</CH>
<EN>   Above Image Panels: Load image buttons, zoom controls. The "Instructions" button is located to the right of the zoom controls for Image B.</EN>

<H>【使用步驟】【Usage Steps】</H>

<H>1. 設定比例尺 (若需實際單位測量) Set Scale (If actual unit measurement is needed)</H>

<CH>   - 點擊右側面板的「加載尺規圖片 (B)」按鈕。</CH>
<EN>   - Click the "Load Ruler Image (B)" button on the right panel.</EN>

<CH>   - 選擇包含已知尺寸物體（例如尺子）的參考圖片。</CH>
<EN>   - Select the reference image containing an object of known size (e.g., a ruler).</EN>

<CH>   - 在右側圖片 (B) 上用**滑鼠左鍵**點選參考物體的兩個端點 (點擊第二點後會自動清除舊點重新選擇)。</CH>
<EN>   - On the right image (B), **left-click** on the two endpoints of the reference object (clicking the second point will clear previous points if re-selecting).</EN>

<CH>   - 在圖片 B 下方的「實際距離」欄位輸入該參考物體的**實際物理長度**。</CH>
<EN>   - Enter the **actual physical length** of the reference object in the "Actual Dist" field below Image B.</EN>

<CH>   - 選擇對應的「單位」。</CH>
<EN>   - Select the corresponding "Unit".</EN>

<CH>   - 點擊「設比例尺」按鈕。成功後，比例尺資訊會顯示在按鈕下方。</CH>
<EN>   - Click the "Set Scale" button. If successful, the scale information will be displayed below the button.</EN>

<H>2. 加載待測圖片 (A) Load Target Image (A)</H>

<CH>   - 點擊左側面板的「加載待測圖片 (A)」按鈕。</CH>
<EN>   - Click the "Load Image (A)" button on the left panel.</EN>

<CH>   - 選擇您想要測量或畫圓的圖片。</CH>
<EN>   - Select the image you want to measure or draw on.</EN>

<H>3. 選擇測量模式 Select Measurement Mode</H>

<CH>   - 在視窗底部左側，點選「直線測量」或「直徑畫圓」。</CH>
<EN>   - In the bottom-left area of the window, select either "Line" or "Circle".</EN>

<H>4. 在圖片 A 上選取兩點 Select Two Points on Image A</H>
<CH>   - 使用**滑鼠左鍵**在圖片 A 上點擊兩個點。</CH>
<EN>   - Use the left mouse button** to click two points on Image A.</EN>

<CH>   - 直線模式： 這兩點定義線段的起點和終點。</CH>
<EN>   - Line Mode: These two points define the start and end of the line segment.</EN>

<CH>   - 畫圓模式： 這兩點定義圓的直徑。</CH>
<EN>   - Circle Mode: These two points define the diameter of the circle.</EN>

<CH>   - 選定第二點後，對應的圖形（直線或圓）會自動繪製，測量結果也會自動計算並顯示。</CH>
<EN>   - After selecting the second point, the corresponding shape (line or circle) will be drawn automatically, and the measurement results will be calculated and displayed.</EN>

<H>5. 查看結果 View Results</H>

<CH>   - 直線模式： 總長度顯示在線段旁邊；水平和垂直分量顯示在圖片 A 下方。</CH>
<EN>   - Line Mode: Total length is shown next to the line segment; horizontal and vertical components are shown below Image A.</EN>

<CH>   - 畫圓模式： 直徑顯示在圓心附近；水平和垂直分量（基於直徑兩端點）顯示在圖片 A 下方。</CH>
<EN>   - Circle Mode: Diameter is shown near the circle center; horizontal and vertical components (based on diameter endpoints) are shown below Image A.</EN>

<CH>   - 如果比例尺未設定，則所有結果均以像素 (px) 為單位。</CH>
<EN>   - If the scale is not set, all results will be in pixels (px).</EN>

<H>【其他輔助功能】【Other Features】</H>

<CH>- 縮放： 使用各面板上方的 +/-/重置按鈕。</CH>
<EN>  Zoom: Use the + / - / Reset buttons above each panel.</EN>

<CH>- 拖動： 在圖片上按住滑鼠中鍵 (或右鍵) 並拖動。</CH>
<EN>  Pan: Press and hold the middle (or right) mouse button on the image and drag.</EN>

<CH>- 清除點： 使用圖片 A 或 B 下方的「清除點」按鈕清除對應面板上的點和圖形。</CH>
<EN>  Clear Points: Use the "Clear Pts (A/B)" button below each image panel to clear points and drawings on that panel.</EN>

<CH>- 外觀： 使用圖片 A 或 B 下方的「顏色」按鈕和「半徑」輸入框調整標記點/線條/圓形的外觀。</CH>
<EN>  Appearance: Use the "Color(A/B)" button and "Radius(A/B)" spinbox below each panel to adjust the appearance of points/lines/circles.</EN>

<CH>- 坐標顯示： 視窗底部左側顯示滑鼠在圖片 A 上的即時坐標。</CH>
<EN>  Coordinate Display: The bottom-left area shows real-time mouse coordinates over Image A.</EN>

<CH>- 日誌： 視窗底部右側記錄主要操作。</CH>
<EN>  Log: The bottom-right area logs major operations.</EN>

<CH>- 重置所有： 底部左側的按鈕，清除所有資料並恢復初始狀態。</CH>
<EN>  Reset All: Button in the bottom-left area to clear all data and restore the initial state.</EN>

<H>【注意事項】【Notes】</H>

<CH>- 測量精度依賴於尺規圖片清晰度、比例尺設定準確性及選點精確度。</CH>
<EN>- Measurement accuracy depends on ruler image clarity, scale setting accuracy, and point selection precision.</EN>

<CH>- 確保尺規物體與待測物體在拍攝時處於相似焦平面和角度，以減少透視誤差。(重要！)</CH>
<EN>- Ensure the ruler object and target object were in similar focal planes and at similar angles during photography to minimize perspective errors.(Important！)</EN>

<CH>- 輸入數字或小數點時，請確保使用英文輸入模式。</CH>
<EN>- Ensure you are in English input mode when entering numbers or decimals.</EN>
"""
        lines = help_content_raw.strip().split('\n')
        for line_content in lines:
            stripped_line = line_content.strip()
            tag_to_apply = None
            text_to_insert = line_content 
            if not stripped_line: help_text_widget.insert(tk.END, "\n"); continue
            if stripped_line.startswith("<CH>"): tag_to_apply = "chinese_help"; text_to_insert = line_content.replace("<CH>", "", 1).replace("</CH>", "", 1) 
            elif stripped_line.startswith("<EN>"): tag_to_apply = "english_help"; text_to_insert = line_content.replace("<EN>", "", 1).replace("</EN>", "", 1)
            elif stripped_line.startswith("<H>"): tag_to_apply = "header_help"; text_to_insert = line_content.replace("<H>", "", 1).replace("</H>", "", 1)
            if tag_to_apply: help_text_widget.insert(tk.END, text_to_insert + "\n", tag_to_apply)
            else: help_text_widget.insert(tk.END, text_to_insert + "\n")
        help_text_widget.insert(tk.END, "\n\n\n") 
        help_text_widget.insert(tk.END, "Created by Wesley Chang\n", "author_info")
        help_text_widget.config(state=tk.DISABLED)
        help_win.transient(self.root); help_win.grab_set(); self.root.wait_window(help_win)

    def choose_color(self, color_var, image_suffix):
        color_code = colorchooser.askcolor(title=f"選擇點顏色 ({image_suffix})\nChoose Point Color ({image_suffix})")
        if color_code and color_code[1]: color_var.set(color_code[1])

    def apply_appearance_a(self):
        if self.image_a: self.redraw_points_a()

    def apply_appearance_b(self):
        if self.image_b: self.redraw_points_b()

    def log_message(self, message):
        try:
            if self.log_text.winfo_exists():
                self.log_text.config(state=tk.NORMAL); self.log_text.insert(tk.END, f"{message}\n"); self.log_text.see(tk.END); self.log_text.config(state=tk.DISABLED)
        except tk.TclError: pass

    def reset_all(self):
        if messagebox.askyesno(self.common_titles["confirm"], "確定要重置所有設置和數據嗎？\nThis will clear all images, points, and scale.\n\nAre you sure you want to reset all settings and data?"):
            self.clear_points_a(); self.clear_points_b()
            self.image_a=None; self.image_b=None; self.photo_a=None; self.photo_b=None; self.image_a_path=""; self.image_b_path=""
            self.image_a_display={}; self.image_b_display={}; self.canvas_a.delete("all"); self.canvas_b.delete("all")
            self.canvas_a.config(scrollregion=(0,0,1,1)); self.canvas_b.config(scrollregion=(0,0,1,1))
            self.scale_value=0.0; 
            if hasattr(self, 'scale_entry'): self.scale_entry.delete(0, tk.END)
            if hasattr(self, 'unit_var'): self.unit_var.set("mm")
            if hasattr(self, 'points_label_a'): self.points_label_a.update_text("已選點 (A): 0", "Selected Points (A): 0")
            if hasattr(self, 'points_label_b'): self.points_label_b.update_text("已選點 (B): 0", "Selected Points (B): 0")
            if hasattr(self, 'scale_display_label'): self.scale_display_label.update_text("比例尺: 未設定", "Scale: Not Set")
            if hasattr(self, 'coord_display_label'): self.coord_display_label.update_text("鼠標坐標 (A): ---", "Mouse Coordinates (A): ---")
            if hasattr(self, 'dist_x_label_a'): self.dist_x_label_a.update_text("水平距離: ---", "Horiz Dist: ---")
            if hasattr(self, 'dist_y_label_a'): self.dist_y_label_a.update_text("垂直距離: ---", "Vert Dist: ---")
            self.zoom_factor_a=1.0; self.zoom_factor_b=1.0
            if hasattr(self, 'zoom_label_a'): self.zoom_label_a.update_text("縮放: 100%", "Zoom: 100%")
            if hasattr(self, 'zoom_label_b'): self.zoom_label_b.update_text("縮放: 100%", "Zoom: 100%")
            if hasattr(self, 'measurement_mode'): self.measurement_mode.set(MODE_LINE)
            self.log_message("--- 已重置所有 --- / --- All reset ---")

    def load_image_generic(self, image_attr, path_attr, zoom_factor_attr, zoom_label, clear_points_func, redisplay_func, panel_id, title_cn, title_en):
        try:
            file_path = filedialog.askopenfilename(title=f"{title_cn}\n{title_en}", filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tif *.tiff")])
            if not file_path: self.log_message(f"取消選擇圖片 ({panel_id})\nCancelled image ({panel_id}) selection"); return
            new_image_pil = Image.open(file_path)
            try:
                o_tag = None 
                if hasattr(new_image_pil, '_getexif') and new_image_pil._getexif() is not None:
                    for temp_o_tag in ExifTags.TAGS.keys(): 
                        if ExifTags.TAGS[temp_o_tag]=='Orientation': o_tag = temp_o_tag; break
                    if o_tag is not None:
                        exif_data=dict(new_image_pil._getexif().items())
                        orientation_val = exif_data.get(o_tag)
                        if orientation_val==3:new_image_pil=new_image_pil.rotate(180,expand=True)
                        elif orientation_val==6:new_image_pil=new_image_pil.rotate(270,expand=True)
                        elif orientation_val==8:new_image_pil=new_image_pil.rotate(90,expand=True)
            except Exception as exif_e: self.log_message(f"EXIF處理錯誤 ({panel_id}): {exif_e}")
            setattr(self, image_attr, new_image_pil); setattr(self, path_attr, file_path); setattr(self, zoom_factor_attr, 1.0)
            zoom_label.update_text("縮放: 100%", "Zoom: 100%")
            clear_points_func(); redisplay_func()
            base_name = os.path.basename(file_path)
            self.log_message(f"已加載圖片 ({panel_id}): {base_name}\nLoaded image ({panel_id}): {base_name}")
        except Exception as e:
            messagebox.showerror(self.common_titles["error"], f"無法加載圖片 ({panel_id}): {e}\nCannot load image ({panel_id}): {e}")
            self.log_message(f"錯誤: 加載圖片 ({panel_id}): {e}\n{traceback.format_exc()}")

    def load_image_a(self):
        self.load_image_generic("image_a", "image_a_path", "zoom_factor_a", self.zoom_label_a, self.clear_points_a, self.redisplay_image_a, "A", "選擇待測圖片 (A)", "Select Image (A)")
    def load_image_b(self):
        self.load_image_generic("image_b", "image_b_path", "zoom_factor_b", self.zoom_label_b, self.clear_points_b, self.redisplay_image_b, "B", "選擇尺規圖片 (B)", "Select Ruler Image (B)")

    def canvas_to_image_coords(self, canvas, event_x, event_y, image_display_dict):
        if not image_display_dict or 'ratio' not in image_display_dict or image_display_dict['ratio'] == 0: return None, None
        try:
            content_x = canvas.canvasx(event_x); content_y = canvas.canvasy(event_y)
            ratio = image_display_dict['ratio']
            original_x = content_x / ratio; original_y = content_y / ratio
            return original_x, original_y
        except Exception: return None, None

    def image_to_canvas_coords(self, canvas, original_x, original_y, image_display_dict):
        if not image_display_dict or 'ratio' not in image_display_dict: return None, None
        try: return original_x * image_display_dict['ratio'], original_y * image_display_dict['ratio']
        except Exception: return None, None

    def on_canvas_a_click(self, event):
        if not self.image_a or not self.image_a_display: messagebox.showinfo(self.common_titles["info"], "請先加載待測圖片 (A)\nPlease load Image A first."); return
        if len(self.points_a) >= 2: self.clear_points_a()
        original_x, original_y = self.canvas_to_image_coords(self.canvas_a, event.x, event.y, self.image_a_display)
        if original_x is None: return
        original_x=max(0,min(original_x,self.image_a.width)); original_y=max(0,min(original_y,self.image_a.height))
        self.points_a.append({'original_x':original_x, 'original_y':original_y}); self.redraw_points_a()
        num_points = len(self.points_a)
        if num_points == 1: 
            self.points_label_a.update_text("已選點 (A): 1", "Selected Points (A): 1"); self.log_message(f"選點1(A)@({original_x:.1f},{original_y:.1f})")
            if hasattr(self, 'dist_x_label_a'): self.dist_x_label_a.update_text("水平距離: ---", "Horiz Dist: ---")
            if hasattr(self, 'dist_y_label_a'): self.dist_y_label_a.update_text("垂直距離: ---", "Vert Dist: ---")
        elif num_points == 2: 
            self.points_label_a.update_text("已選點 (A): 2", "Selected Points (A): 2"); self.log_message(f"選點2(A)@({original_x:.1f},{original_y:.1f})")
            if self.scale_value > 0: self.calculate_distance()
            else:
                dx_orig = abs(self.points_a[1]['original_x'] - self.points_a[0]['original_x'])
                dy_orig = abs(self.points_a[1]['original_y'] - self.points_a[0]['original_y'])
                if hasattr(self, 'dist_x_label_a'): self.dist_x_label_a.update_text(f"水平距離: {dx_orig:.1f} px", f"Horiz Dist: {dx_orig:.1f} px")
                if hasattr(self, 'dist_y_label_a'): self.dist_y_label_a.update_text(f"垂直距離: {dy_orig:.1f} px", f"Vert Dist: {dy_orig:.1f} px")
                self.redraw_points_a() 
                self.log_message("提示: 請先設定比例尺以計算實際距離。\nTip: Set scale first to calculate actual distance.")

    def on_canvas_b_click(self, event):
        if not self.image_b or not self.image_b_display: messagebox.showinfo(self.common_titles["info"], "請先加載尺規圖片 (B)\nPlease load Ruler Image B first."); return
        if len(self.points_b) >= 2: self.clear_points_b()
        original_x, original_y = self.canvas_to_image_coords(self.canvas_b, event.x, event.y, self.image_b_display)
        if original_x is None: return
        original_x=max(0,min(original_x,self.image_b.width)); original_y=max(0,min(original_y,self.image_b.height))
        self.points_b.append({'original_x':original_x, 'original_y':original_y}); self.redraw_points_b()
        if len(self.points_b) == 1: self.points_label_b.update_text("已選點 (B): 1", "Selected Points (B): 1"); self.log_message(f"選點1(B)@({original_x:.1f},{original_y:.1f})")
        elif len(self.points_b) == 2: self.points_label_b.update_text("已選點 (B): 2", "Selected Points (B): 2"); self.log_message(f"選點2(B)@({original_x:.1f},{original_y:.1f}) - 請輸入實際距離並設定比例尺。")

    def clear_points_a(self):
        self.canvas_a.delete("point_a","line_a","text_a_dist","text_a_dist_bg", "circle_a", "text_a_diameter","text_a_diameter_bg") 
        self.points_a=[]
        if hasattr(self, 'points_label_a'): self.points_label_a.update_text("已選點 (A): 0", "Selected Points (A): 0")
        if hasattr(self, 'dist_x_label_a'): self.dist_x_label_a.update_text("水平距離: ---", "Horiz Dist: ---")
        if hasattr(self, 'dist_y_label_a'): self.dist_y_label_a.update_text("垂直距離: ---", "Vert Dist: ---")
        if self.image_a: self.log_message("清除點 (A)\nCleared points (A)")
        
    def clear_points_b(self):
        self.canvas_b.delete("point_b","line_b","text_b_dist","text_b_dist_bg"); self.points_b=[]
        if hasattr(self, 'points_label_b'): self.points_label_b.update_text("已選點 (B): 0", "Selected Points (B): 0")
        if self.image_b: self.log_message("清除點 (B)\nCleared points (B)")

    def set_scale(self):
        if len(self.points_b)!=2: messagebox.showwarning(self.common_titles["warning"], "請在尺規圖片(B)上選兩點。\nSelect 2 points on Ruler Img(B)."); return
        try:
            actual_dist_str=self.scale_entry.get().strip()
            if not actual_dist_str: messagebox.showwarning(self.common_titles["warning"], "請輸入尺規實際距離。\nEnter actual ruler distance."); return
            actual_d=float(actual_dist_str)
            if actual_d<=0: raise ValueError("距離 > 0")
            p1,p2=self.points_b[0],self.points_b[1]; dx,dy=p2['original_x']-p1['original_x'],p2['original_y']-p1['original_y']
            pix_d=math.hypot(dx, dy)
            if pix_d<1e-6: messagebox.showerror(self.common_titles["error"],"尺規點重合。\nRuler points overlap."); self.scale_value=0.0; self.scale_display_label.update_text("比例尺: 無效","Scale: Invalid"); return
            self.scale_value=actual_d/pix_d; unit=self.unit_var.get()
            self.scale_display_label.update_text(f"比例尺: {self.scale_value:.6f} {unit}/px", f"Scale: {self.scale_value:.6f} {unit}/px")
            messagebox.showinfo(self.common_titles["success"], f"比例尺已設: 1px ≈ {self.scale_value:.4f}{unit}\nScale set: 1px ≈ {self.scale_value:.4f}{unit}")
            self.log_message(f"比例尺已設: {self.scale_value:.6f} {unit}/px ({pix_d:.2f}px -> {actual_d}{unit})")
            self.update_coordinate_display(); self.redraw_points_a()
            if len(self.points_a) == 2: self.calculate_distance()
        except ValueError: messagebox.showerror(self.common_titles["input_error"],"無效距離。\nInvalid distance."); self.scale_value=0.0; self.scale_display_label.update_text("比例尺: 輸入錯誤","Scale: Input Error")
        except Exception as e: messagebox.showerror(self.common_titles["error"],f"設比例尺錯誤: {e}\nSet scale error: {e}"); self.scale_value=0.0; self.scale_display_label.update_text("比例尺: 計算錯誤","Scale: Calc Error")

    def calculate_distance(self): 
        if len(self.points_a)!=2 or self.scale_value<=0: 
             if len(self.points_a) == 2 and self.scale_value <= 0 : 
                 pass 
             if hasattr(self, 'dist_x_label_a'): self.dist_x_label_a.update_text("水平距離: ---", "Horiz Dist: ---")
             if hasattr(self, 'dist_y_label_a'): self.dist_y_label_a.update_text("垂直距離: ---", "Vert Dist: ---")
             return 
        try:
            p1,p2=self.points_a[0],self.points_a[1]
            dx_orig = abs(p2['original_x']-p1['original_x'])
            dy_orig = abs(p2['original_y']-p1['original_y'])
            pix_d=math.hypot(p2['original_x']-p1['original_x'], p2['original_y']-p1['original_y']) 
            actual_d = pix_d * self.scale_value
            actual_dx = dx_orig * self.scale_value
            actual_dy = dy_orig * self.scale_value
            unit = self.unit_var.get()
            if hasattr(self, 'dist_x_label_a'): self.dist_x_label_a.update_text(f"水平距離: {actual_dx:.4f} {unit}", f"Horiz Dist: {actual_dx:.4f} {unit}")
            if hasattr(self, 'dist_y_label_a'): self.dist_y_label_a.update_text(f"垂直距離: {actual_dy:.4f} {unit}", f"Vert Dist: {actual_dy:.4f} {unit}")
            self.log_message(f"--- 計算結果 ({self.measurement_mode.get()}): {actual_d:.4f} {unit} (dx={actual_dx:.4f}, dy={actual_dy:.4f}) ---")
            self.redraw_points_a() 
        except Exception as e: 
            messagebox.showerror(self.common_titles["calc_error"], f"計算距離錯誤: {e}\nError calculating distance: {e}")
            if hasattr(self, 'dist_x_label_a'): self.dist_x_label_a.update_text("水平距離: 錯誤", "Horiz Dist: Error")
            if hasattr(self, 'dist_y_label_a'): self.dist_y_label_a.update_text("垂直距離: 錯誤", "Vert Dist: Error")

    def _redisplay_image_generic(self, canvas, image_obj_pil, photo_attr, image_display_dict, zoom_factor, points_redraw_func, image_tag_str):
        log_prefix = "(A)" if image_tag_str == "image_a" else "(B)"
        if not image_obj_pil: self.log_message(f"Debug {log_prefix}: _redisplay_image_generic - image_obj_pil is None. Skipping."); return
        
        try:
            img_w,img_h=image_obj_pil.size
            new_w=max(1,int(img_w*zoom_factor))
            new_h=max(1,int(img_h*zoom_factor))
            
            if new_w == 0 or new_h == 0:
                self.log_message(f"Error {log_prefix}: _redisplay_image_generic - Calculated new_width or new_height is 0. new_w={new_w}, new_h={new_h}, zoom_factor={zoom_factor}")
                if image_display_dict is not None: image_display_dict.clear()
                return
            
            if hasattr(Image, "Resampling"):
                resample_method = Image.Resampling.LANCZOS
            else:
                resample_method = Image.LANCZOS

            rs_img_pil = image_obj_pil.resize((new_w,new_h), resample_method)
            setattr(self, photo_attr, ImageTk.PhotoImage(rs_img_pil))
            canvas.delete(image_tag_str)
            img_item_id = canvas.create_image(0,0,image=getattr(self,photo_attr),anchor=tk.NW,tags=image_tag_str)
            canvas.tag_lower(img_item_id) # Ensure image is at the bottom of the display stack
            canvas.config(scrollregion=canvas.bbox(tk.ALL))
            image_display_dict.clear()
            image_display_dict.update({'width':new_w,'height':new_h,'ratio':zoom_factor})
            points_redraw_func()
        except Exception as e: 
            self.log_message(f"ERROR {log_prefix} in _redisplay_image_generic: {e}\n{traceback.format_exc()}")
            if image_display_dict is not None: 
                image_display_dict.clear()
                self.log_message(f"Debug {log_prefix}: image_display_dict cleared due to error in _redisplay_image_generic.")

    def redisplay_image_a(self): self._redisplay_image_generic(self.canvas_a, self.image_a, "photo_a", self.image_a_display, self.zoom_factor_a, self.redraw_points_a, "image_a")
    def redisplay_image_b(self): self._redisplay_image_generic(self.canvas_b, self.image_b, "photo_b", self.image_b_display, self.zoom_factor_b, self.redraw_points_b, "image_b")

    def _zoom_generic(self, image_obj, zoom_factor_attr, zoom_label_widget, redisplay_func, direction, panel_id):
        if not image_obj: return
        current_zoom = getattr(self, zoom_factor_attr)
        if direction == "in": new_zoom = current_zoom * 1.2
        elif direction == "out": new_zoom = current_zoom / 1.2
        else: new_zoom = 1.0 # reset
        if direction == "out" and new_zoom < 0.05: self.log_message(f"Min zoom reached ({panel_id})"); return
        setattr(self, zoom_factor_attr, new_zoom)
        zoom_label_widget.update_text(f"縮放: {int(new_zoom*100)}%", f"Zoom: {int(new_zoom*100)}%")
        redisplay_func()
        op_str = "放大" if direction=="in" else "縮小" if direction=="out" else "重置縮放"
        self.log_message(f"圖片 {panel_id} {op_str} 至 {int(new_zoom*100)}%")

    def zoom_in_a(self): self._zoom_generic(self.image_a, "zoom_factor_a", self.zoom_label_a, self.redisplay_image_a, "in", "A")
    def zoom_out_a(self): self._zoom_generic(self.image_a, "zoom_factor_a", self.zoom_label_a, self.redisplay_image_a, "out", "A")
    def zoom_reset_a(self): self._zoom_generic(self.image_a, "zoom_factor_a", self.zoom_label_a, self.redisplay_image_a, "reset", "A")
    def zoom_in_b(self): self._zoom_generic(self.image_b, "zoom_factor_b", self.zoom_label_b, self.redisplay_image_b, "in", "B")
    def zoom_out_b(self): self._zoom_generic(self.image_b, "zoom_factor_b", self.zoom_label_b, self.redisplay_image_b, "out", "B")
    def zoom_reset_b(self): self._zoom_generic(self.image_b, "zoom_factor_b", self.zoom_label_b, self.redisplay_image_b, "reset", "B")

    def _get_contrasting_background(self, text_color_str):
        try:
            rgb_16bit = self.root.winfo_rgb(text_color_str) 
            r8, g8, b8 = rgb_16bit[0] / 256.0, rgb_16bit[1] / 256.0, rgb_16bit[2] / 256.0
            r_norm, g_norm, b_norm = r8 / 255.0, g8 / 255.0, b8 / 255.0
            luminance = 0.2126 * r_norm + 0.7152 * g_norm + 0.0722 * b_norm
            return "black" if luminance > 0.5 else "white"
        except tk.TclError: return "lightyellow" 

    def _redraw_points_generic(self, canvas, points_list, image_display_dict, color_var, radius_var, p_tag, l_tag, t_tag, is_image_a_panel):
        bg_tag_suffix = "_bg" 
        circle_item_tag = "circle_a" 
        diameter_text_item_tag = "text_a_diameter" 
        
        canvas.delete(p_tag, l_tag, t_tag, t_tag + bg_tag_suffix, 
                      circle_item_tag, diameter_text_item_tag, diameter_text_item_tag + bg_tag_suffix) 

        if not points_list or not image_display_dict or 'ratio' not in image_display_dict: return
        
        point_canvas_coords=[]; current_color=color_var.get()
        try: point_radius=int(radius_var.get())
        except ValueError: point_radius=2; radius_var.set(2) # Default if invalid
        
        line_thickness=max(1, point_radius // 2) 
        font_size_val=max(8, point_radius + 2) 
        
        for i, point_data in enumerate(points_list):
            canvas_x,canvas_y = self.image_to_canvas_coords(canvas, point_data['original_x'], point_data['original_y'], image_display_dict)
            if canvas_x is not None and canvas_y is not None: 
                point_canvas_coords.append((canvas_x, canvas_y))
                canvas.create_oval(canvas_x - point_radius, canvas_y - point_radius, 
                                   canvas_x + point_radius, canvas_y + point_radius,
                                   fill=current_color, outline="white", width=1, tags=(p_tag, f"{p_tag}_{i}"))
        
        if len(point_canvas_coords) == 2:
            p1_canvas, p2_canvas = point_canvas_coords
            p1_orig, p2_orig = points_list[0], points_list[1]
            
            delta_x_orig = p2_orig['original_x'] - p1_orig['original_x']
            delta_y_orig = p2_orig['original_y'] - p1_orig['original_y']
            pixel_distance_orig = math.hypot(delta_x_orig, delta_y_orig) 
            
            current_unit_str = self.unit_var.get()
            active_mode = self.measurement_mode.get() if is_image_a_panel else MODE_LINE 
            
            mid_x_canvas = (p1_canvas[0] + p2_canvas[0]) / 2
            mid_y_canvas = (p1_canvas[1] + p2_canvas[1]) / 2 
            
            delta_x_canvas = p2_canvas[0] - p1_canvas[0]
            delta_y_canvas = p2_canvas[1] - p1_canvas[1]     
            line_len_sq_canvas = delta_x_canvas**2 + delta_y_canvas**2
            angle_rad = math.atan2(delta_y_canvas, delta_x_canvas) if line_len_sq_canvas > 1e-9 else 0 # Avoid division by zero for very short lines
            
            text_offset = max(line_thickness, 4) + 8 + font_size_val * 0.5 
            display_text = ""; text_item_tag_to_use = t_tag; bg_item_tag_to_use = t_tag + bg_tag_suffix

            if not is_image_a_panel or active_mode == MODE_LINE:
                canvas.create_line(p1_canvas[0],p1_canvas[1],p2_canvas[0],p2_canvas[1],
                                   fill=current_color,width=line_thickness,tags=l_tag)
                if is_image_a_panel: 
                    if self.scale_value > 0: display_text=f"長度: {pixel_distance_orig * self.scale_value:.2f} {current_unit_str}" 
                    else: display_text = f"長度: {pixel_distance_orig:.1f} px"
                else: # Ruler panel (Image B)
                    display_text=f"像素: {pixel_distance_orig:.1f} px"
                
                text_x_pos = mid_x_canvas + text_offset * math.sin(angle_rad)
                text_y_pos = mid_y_canvas - text_offset * math.cos(angle_rad)

            elif is_image_a_panel and active_mode == MODE_CIRCLE:
                radius_on_canvas = math.hypot(delta_x_canvas, delta_y_canvas) / 2.0
                if radius_on_canvas > 0.5: # Draw circle if radius is reasonably large
                     canvas.create_oval(mid_x_canvas - radius_on_canvas, mid_y_canvas - radius_on_canvas, 
                                        mid_x_canvas + radius_on_canvas, mid_y_canvas + radius_on_canvas, 
                                        outline=current_color, width=line_thickness, tags=circle_item_tag)
                if self.scale_value > 0: display_text=f"直徑: {pixel_distance_orig * self.scale_value:.2f} {current_unit_str}"
                else: display_text = f"直徑: {pixel_distance_orig:.1f} px"
                
                text_x_pos = mid_x_canvas 
                text_y_pos = mid_y_canvas 
                text_item_tag_to_use = diameter_text_item_tag 
                bg_item_tag_to_use = diameter_text_item_tag + bg_tag_suffix
            else:
                display_text = "錯誤模式" # Should not happen with radio buttons
                text_x_pos, text_y_pos = mid_x_canvas, mid_y_canvas


            if display_text: 
                text_background_color = self._get_contrasting_background(current_color) 
                text_foreground_color = "white" if text_background_color == "black" else "black" 

                created_text_id = canvas.create_text(text_x_pos, text_y_pos, text=display_text, 
                                                     fill=text_foreground_color, font=("Arial", font_size_val), 
                                                     tags=text_item_tag_to_use, anchor=tk.CENTER)
                try:
                    text_bbox = canvas.bbox(created_text_id)
                    if text_bbox:
                        bg_padding_val = 2 
                        created_rect_id = canvas.create_rectangle(
                            text_bbox[0]-bg_padding_val, text_bbox[1]-bg_padding_val, 
                            text_bbox[2]+bg_padding_val, text_bbox[3]+bg_padding_val, 
                            fill=text_background_color, outline=text_background_color, tags=bg_item_tag_to_use)
                        canvas.tag_lower(created_rect_id, created_text_id) # Place background behind text
                    else: # If bbox fails (e.g., text off-screen), delete the orphaned text
                        canvas.delete(created_text_id)
                except tk.TclError: # Catch if item deleted before bbox
                     if canvas.winfo_exists() and created_text_id in canvas.find_all():
                        canvas.delete(created_text_id)

    def redraw_points_a(self):
        if self.image_a: self._redraw_points_generic(self.canvas_a,self.points_a,self.image_a_display,self.point_a_color_var,self.point_a_radius_var,"point_a","line_a","text_a_dist",True)
    def redraw_points_b(self):
        if self.image_b: self._redraw_points_generic(self.canvas_b,self.points_b,self.image_b_display,self.point_b_color_var,self.point_b_radius_var,"point_b","line_b","text_b_dist",False)

    def start_pan_a(self,event):
        if self.image_a: self.canvas_a.scan_mark(event.x,event.y)
    def pan_image_a(self,event):
        if self.image_a: self.canvas_a.scan_dragto(event.x,event.y,gain=1); self.redraw_points_a()
    def start_pan_b(self,event):
        if self.image_b: self.canvas_b.scan_mark(event.x,event.y)
    def pan_image_b(self,event):
        if self.image_b: self.canvas_b.scan_dragto(event.x,event.y,gain=1); self.redraw_points_b()
        
    def update_coordinate_display(self, event=None):
        if not hasattr(self, 'coord_display_label') or not self.coord_display_label.winfo_exists(): return 
        
        if hasattr(self, 'crosshair_line_h_a') and self.crosshair_line_h_a:
            if self.canvas_a.winfo_exists(): self.canvas_a.delete(self.crosshair_line_h_a)
            self.crosshair_line_h_a = None
        if hasattr(self, 'crosshair_line_v_a') and self.crosshair_line_v_a:
            if self.canvas_a.winfo_exists(): self.canvas_a.delete(self.crosshair_line_v_a)
            self.crosshair_line_v_a = None

        if not self.image_a or not self.image_a_display: 
            self.coord_display_label.update_text("鼠標坐標 (A): 未加載", "Mouse Coords (A): Not loaded")
            return

        if event is None: 
            unit_str_cn = f"(單位: {self.unit_var.get()})" if self.scale_value > 0 else "(單位: px)"
            unit_str_en = f"(Unit: {self.unit_var.get()})" if self.scale_value > 0 else "(Unit: px)"
            self.coord_display_label.update_text(f"鼠標坐標 (A): [移入畫布] {unit_str_cn}", f"Mouse Coords (A): [Enter canvas] {unit_str_en}")
            return

        if hasattr(self, 'canvas_a') and self.canvas_a.winfo_exists(): 
            widget_w = self.canvas_a.winfo_width()
            widget_h = self.canvas_a.winfo_height()

            if widget_w > 1 and widget_h > 1: 
                mouse_content_x = self.canvas_a.canvasx(event.x)
                mouse_content_y = self.canvas_a.canvasy(event.y)
                visible_area_x_start = self.canvas_a.canvasx(0)
                visible_area_y_start = self.canvas_a.canvasy(0)
                visible_area_x_end = self.canvas_a.canvasx(widget_w)
                visible_area_y_end = self.canvas_a.canvasy(widget_h)
                
                self.crosshair_line_h_a = self.canvas_a.create_line(
                    visible_area_x_start, mouse_content_y, visible_area_x_end, mouse_content_y,
                    fill=self.crosshair_color, tags="crosshair_a", dash=(2, 2))
                self.crosshair_line_v_a = self.canvas_a.create_line(
                    mouse_content_x, visible_area_y_start, mouse_content_x, visible_area_y_end,
                    fill=self.crosshair_color, tags="crosshair_a", dash=(2, 2))
                
                self.canvas_a.tag_raise("crosshair_a") 

                # Ensure image is under the crosshair. Image is added with tag_lower.
                # No need to explicitly lower crosshair relative to image, as image is already lowest.
                # Then, ensure drawing elements are above the crosshair.
                drawing_elements_tags = ["point_a", "line_a", "text_a_dist", "text_a_dist_bg", 
                                         "circle_a", "text_a_diameter", "text_a_diameter_bg"]
                for elem_tag in drawing_elements_tags:
                    if self.canvas_a.find_withtag(elem_tag):
                         self.canvas_a.tag_raise(elem_tag, "crosshair_a")

        orig_x_coord, orig_y_coord = self.canvas_to_image_coords(self.canvas_a, event.x, event.y, self.image_a_display)
        if orig_x_coord is None:
            if (0 <= event.x < self.canvas_a.winfo_width() and 0 <= event.y < self.canvas_a.winfo_height()):
                self.coord_display_label.update_text("鼠標坐標 (A): 圖像內容外", "Mouse Coords (A): Outside image content")
            else: self.coord_display_label.update_text("鼠標坐標 (A): ---", "Mouse Coords (A): ---")
            return
        
        clamped_orig_x=max(0, min(orig_x_coord, self.image_a.width if self.image_a else 0))
        clamped_orig_y=max(0, min(orig_y_coord, self.image_a.height if self.image_a else 0))
        
        is_within_image_bounds=(0 <= orig_x_coord < (self.image_a.width if self.image_a else float('inf'))) and \
                               (0 <= orig_y_coord < (self.image_a.height if self.image_a else float('inf')))
        
        prefix_cn="坐標(A): " if is_within_image_bounds else "坐標(A)(外): "
        prefix_en="Coords(A): " if is_within_image_bounds else "Coords(A)(Out): "
        
        if self.scale_value > 0:
            current_unit = self.unit_var.get()
            real_x = clamped_orig_x * self.scale_value
            real_y = clamped_orig_y * self.scale_value
            self.coord_display_label.update_text(
                f"{prefix_cn}X={real_x:.2f}{current_unit},Y={real_y:.2f}{current_unit} (原:{orig_x_coord:.1f},{orig_y_coord:.1f}px)",
                f"{prefix_en}X={real_x:.2f}{current_unit},Y={real_y:.2f}{current_unit} (Orig:{orig_x_coord:.1f},{orig_y_coord:.1f}px)"
            )
        else:
            self.coord_display_label.update_text(
                f"{prefix_cn}X={orig_x_coord:.1f}px,Y={orig_y_coord:.1f}px (未設比例尺)",
                f"{prefix_en}X={orig_x_coord:.1f}px,Y={orig_y_coord:.1f}px (No Scale)"
            )
            
    def clear_coordinate_display(self, event=None): 
        if hasattr(self, 'crosshair_line_h_a') and self.crosshair_line_h_a:
            if self.canvas_a.winfo_exists(): self.canvas_a.delete(self.crosshair_line_h_a)
            self.crosshair_line_h_a = None
        if hasattr(self, 'crosshair_line_v_a') and self.crosshair_line_v_a:
            if self.canvas_a.winfo_exists(): self.canvas_a.delete(self.crosshair_line_v_a)
            self.crosshair_line_v_a = None
        self.update_coordinate_display() 


if __name__ == "__main__":
    common_titles_main = { "error": "錯誤\nError", "library_missing": "缺少庫\nLibrary Missing" }
    try: from PIL import Image, ImageTk, ExifTags
    except ImportError:
        try:
            root_tk_temp = tk.Tk(); root_tk_temp.withdraw()
            messagebox.showerror(common_titles_main["library_missing"],"需 Pillow 庫: pip install Pillow\nNeed Pillow: pip install Pillow")
            root_tk_temp.destroy()
        except tk.TclError: 
            print("Tkinter TclError occurred, possibly no display environment.")
        print("Pillow 庫未安裝 (pip install Pillow)\nPillow not installed (pip install Pillow)"); exit(1)
    
    root = tk.Tk()
    app = ImageDistanceMeasurementTool(root)
    root.mainloop()
# --- END OF FILE image_distance_measurement.py ---