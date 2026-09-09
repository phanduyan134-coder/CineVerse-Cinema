"""
Module: ui/styles.py
Mô tả: Định nghĩa bảng màu Sci-Fi CINEVERSE, Font chữ và cấu hình CustomTkinter bo góc hiện đại.
"""

import os
import sys
import ctypes
import customtkinter as ctk
from tkinter import ttk

def enable_high_dpi():
    """Kích hoạt hỗ trợ High-DPI trên Windows để giao diện luôn sắc nét 100% (không bị mờ do Windows scaling)"""
    if os.name == 'nt':
        try:
            # Per-Monitor DPI Awareness v2 (Windows 10 1703+ / Windows 11)
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                # Per-Monitor DPI Awareness v1 (Windows 8.1 / 10)
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                try:
                    # System DPI Aware (Windows Vista / 7 / 8)
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    pass

# Tự động kích hoạt ngay khi nạp module
enable_high_dpi()

# Kích hoạt Dark Mode mặc định cho CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Bảng mã màu CINEVERSE - Phong Cách 1: Cinema Crimson Red (Chuẩn Rạp CGV / Netflix / Hollywood)
COLOR_BG_DARK = "#0a0a0d"        # Nền chính: Đen than chì OLED sâu thẳm
COLOR_BG_CARD = "#141419"        # Nền Card / Container: Xám đen điện ảnh sang trọng
COLOR_BG_LIGHT = "#1e1e26"       # Nền phụ / Header bảng / Input: Xám than elevated
COLOR_ACCENT = "#e50914"         # Đỏ Ruby rạp chiếu chuẩn Hollywood / Netflix / CGV
COLOR_ACCENT_HOVER = "#b80710"   # Đỏ sẫm sang trọng khi rê chuột
COLOR_GOLD = "#f59e0b"           # Vàng hoàng gia Amber ấm áp
COLOR_GOLD_HOVER = "#d97706"     # Vàng hổ phách sẫm khi hover
COLOR_TEXT = "#e2e8f0"           # Màu chữ bạc ngọc trai dịu mắt
COLOR_TEXT_WHITE = "#ffffff"     # Màu chữ trắng tinh thể
COLOR_TEXT_MUTED = "#8e8e96"     # Màu chữ phụ xám bạc kim loại
COLOR_SUCCESS = "#10b981"        # Xanh ngọc lục bảo thành công
COLOR_DANGER = "#ef4444"         # Đỏ cảnh báo tươi
COLOR_BORDER = "#2b2b36"         # Viền bo góc titan sắc sảo

# Màu phân khúc ghế ngồi theo phong cách Cinema Crimson Red
SEAT_AVAILABLE_STD = "#383846"       # Ghế Standard: Xám titan sang trọng
SEAT_AVAILABLE_VIP = "#b45309"       # Ghế VIP: Vàng hổ phách quý phái
SEAT_AVAILABLE_SWEETBOX = "#9d174d"  # Ghế Cặp Đôi Sweetbox: Đỏ nhung hoa hồng lãng mạn
SEAT_SELECTED = "#e50914"            # Ghế Đang Chọn: Đỏ Ruby phát sáng rực rỡ
SEAT_BOOKED = "#1e1e24"              # Ghế Đã Bán: Xám đen mờ không gian

def load_custom_fonts():
    """Tự động nạp font chữ điện ảnh cao cấp (Anton, Inter, Josefin Sans) từ assets/fonts vào Windows GDI Session"""
    loaded_fonts = []
    if os.name == 'nt':
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fonts_dir = os.path.join(base_dir, "assets", "fonts")
        if os.path.isdir(fonts_dir):
            for fname in os.listdir(fonts_dir):
                if fname.lower().endswith(('.ttf', '.otf')):
                    fpath = os.path.join(fonts_dir, fname)
                    try:
                        res = ctypes.windll.gdi32.AddFontResourceExW(fpath, 0x10, 0)
                        if res > 0:
                            loaded_fonts.append(fname)
                    except Exception:
                        pass
    return loaded_fonts

# Tự động nạp font khi nạp module
load_custom_fonts()

# Định nghĩa hệ thống Font chuẩn rạp chiếu phim (Lấy cảm hứng từ Cinestar / CGV)
FONT_FAMILY_TITLE = "Anton"          # Font tiêu đề điện ảnh hoành tráng (All-Caps, Condensed, High-Impact)
FONT_FAMILY_UI = "Inter"             # Font giao diện số 1 thế giới (Sắc nét, Kerning hoàn hảo trên màn hình)
FONT_FAMILY_LOGO = "Josefin Sans"    # Font logo thương hiệu tinh tế, hiện đại

# Font Cinema Display (Dành cho Tiêu đề hoành tráng phong cách poster rạp chiếu Cinestar)
FONT_CINEMA_HERO = (FONT_FAMILY_TITLE, 24)
FONT_CINEMA_TITLE = (FONT_FAMILY_TITLE, 18)
FONT_CINEMA_SECTION = (FONT_FAMILY_TITLE, 15)

# Font UI & Nội dung sắc nét (Chuẩn Inter Retina hiện đại)
FONT_TITLE = (FONT_FAMILY_UI, 17, "bold")
FONT_SUBTITLE = (FONT_FAMILY_UI, 13, "bold")
FONT_HEADING = (FONT_FAMILY_UI, 11, "bold")
FONT_BODY = (FONT_FAMILY_UI, 10)
FONT_BODY_BOLD = (FONT_FAMILY_UI, 10, "bold")
FONT_SMALL = (FONT_FAMILY_UI, 9)
FONT_SEAT = (FONT_FAMILY_UI, 9, "bold")
FONT_BUTTON = (FONT_FAMILY_UI, 11, "bold")

def setup_styles():
    """Cấu hình bổ trợ cho các widget Treeview của ttk hòa hợp với CustomTkinter"""
    style = ttk.Style()
    style.theme_use("clam")

    # Cấu hình Treeview Dark Sci-Fi sắc nét
    style.configure("Dark.Treeview", 
                    background=COLOR_BG_CARD, 
                    foreground=COLOR_TEXT_WHITE, 
                    fieldbackground=COLOR_BG_CARD, 
                    font=FONT_BODY, 
                    rowheight=34,
                    borderwidth=0)
    style.configure("Dark.Treeview.Heading", 
                    background=COLOR_BG_LIGHT, 
                    foreground=COLOR_GOLD, 
                    font=FONT_BODY_BOLD, 
                    relief="flat")
    style.map("Dark.Treeview", 
              background=[("selected", COLOR_ACCENT_HOVER)],
              foreground=[("selected", COLOR_TEXT_WHITE)])

def center_window(window, width: int, height: int):
    """Căn giữa cửa sổ ứng dụng trên màn hình máy tính"""
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = max(0, (screen_width // 2) - (width // 2))
    y = max(0, (screen_height // 2) - (height // 2))
    window.geometry(f"{width}x{height}+{x}+{y}")
