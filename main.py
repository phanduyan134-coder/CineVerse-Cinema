"""
File: main.py
Mô tả: Điểm khởi chạy chính của Hệ Thống Đặt Vé Xem Phim (Cinema Booking System)
- Đồ án môn: Kỹ thuật lập trình Python
- 100% Python thuần túy (Sử dụng Tkinter & SQLite có sẵn)
"""

import sys
import os
import ctypes

# Khóa thư mục làm việc và đường dẫn import luôn trỏ chính xác vào thư mục chứa project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Kích hoạt chế độ High-DPI chuẩn xác trên Windows để toàn bộ cửa sổ, font chữ và viền bo góc sắc nét 100% (Crisp / HiDPI)
if os.name == 'nt':
    try:
        # Per-Monitor DPI Awareness v2 (Windows 10 v1703+ và Windows 11)
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            # Fallback Windows 8.1 / 10
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                # Fallback Windows Vista / 7 / 8
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

# Cấu hình UTF-8 cho console
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import customtkinter as ctk
import tkinter as tk
from database import init_database, seed_data
from models import User
from ui.login_window import LoginWindow
from ui.customer_window import CustomerWindow
from ui.admin_window import AdminWindow
from ui.staff_window import StaffWindow
from ui.styles import enable_high_dpi

class CinemaApp:
    """Bộ điều phối luồng ứng dụng chính (CineVerse Controller)"""
    def __init__(self):
        # 1. Tự động kiểm tra và khởi tạo CSDL + Dữ liệu mẫu
        print("[HỆ THỐNG] Đang khởi động cơ sở dữ liệu CINEVERSE...")
        init_database()
        seed_data()

        # 2. Khởi tạo cửa sổ CustomTkinter gốc bo góc hiện đại
        self.root = ctk.CTk()
        self.current_user = None

        # 3. Mở màn hình đăng nhập đầu tiên
        self.show_login_screen()

    def show_login_screen(self):
        """Hiển thị màn hình Đăng nhập"""
        self._clear_root()
        self.current_user = None
        self.login_view = LoginWindow(self.root, on_login_success=self.handle_login_success)

    def handle_login_success(self, user: User):
        """Xử lý sau khi đăng nhập thành công: Phân quyền điều hướng màn hình (RBAC 3 Cấp)"""
        self.current_user = user
        self._clear_root()

        # Áp dụng tính Đa hình (Polymorphism) của OOP:
        # Kiểm tra vai trò của người dùng để mở giao diện tương ứng
        if user.is_admin():
            print(f"[ĐĂNG NHẬP] Quản trị viên '{user.fullname}' đã đăng nhập thành công.")
            self.admin_view = AdminWindow(self.root, admin=user, on_logout=self.show_login_screen)
        elif user.is_staff():
            print(f"[ĐĂNG NHẬP] Nhân viên quầy & soát vé '{user.fullname}' đã đăng nhập thành công.")
            self.staff_view = StaffWindow(self.root, staff=user, on_logout=self.show_login_screen)
        else:
            print(f"[ĐĂNG NHẬP] Khách hàng '{user.fullname}' đã đăng nhập thành công.")
            self.customer_view = CustomerWindow(self.root, customer=user, on_logout=self.show_login_screen)

    def _clear_root(self):
        """Dọn dẹp các widget trên cửa sổ chính trước khi chuyển view"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        """Bắt đầu vòng lặp sự kiện chính của ứng dụng đồ họa"""
        print("[HỆ THỐNG] Khởi chạy giao diện thành công! Chúc bạn làm đồ án đạt điểm cao.")
        self.root.mainloop()

if __name__ == "__main__":
    app = CinemaApp()
    app.run()

