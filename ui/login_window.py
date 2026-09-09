"""
Module: ui/login_window.py
Mô tả: Cửa sổ Đăng nhập và Đăng ký tài khoản phong cách CINEVERSE bo góc hiện đại (CustomTkinter).
"""

import customtkinter as ctk
from tkinter import messagebox
from services import AuthService
from ui.toast import show_toast
from ui.styles import (
    COLOR_BG_DARK, COLOR_BG_CARD, COLOR_BG_LIGHT, COLOR_ACCENT, COLOR_ACCENT_HOVER,
    COLOR_GOLD, COLOR_TEXT, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED, COLOR_BORDER,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADING, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL,
    setup_styles, center_window
)

class LoginWindow:
    """Cửa sổ Đăng nhập & Đăng ký Bo Góc Hiện Đại"""
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success

        self.root.title("CINEVERSE - Đa Vũ Trụ Điện Ảnh")
        self.root.configure(fg_color=COLOR_BG_DARK)
        self.root.resizable(False, False)
        setup_styles()
        center_window(self.root, 530, 800)

        self._build_ui()

    def _build_ui(self):
        # Card chứa toàn bộ giao diện bo tròn với viền Neon Crimson phát sáng rực rỡ
        main_card = ctk.CTkFrame(
            self.root, 
            corner_radius=24, 
            fg_color=COLOR_BG_CARD, 
            border_width=2, 
            border_color="#e50914"
        )
        main_card.pack(fill="both", expand=True, padx=22, pady=16)

        # Header Logo & Typography Điện Ảnh Chuẩn Rạp Chiếu
        lbl_logo = ctk.CTkLabel(
            main_card, 
            text="🌌 CINEVERSE", 
            font=ctk.CTkFont(family="Anton", size=28), 
            text_color=COLOR_ACCENT
        )
        lbl_logo.pack(pady=(12, 4))

        badge_sub = ctk.CTkFrame(main_card, corner_radius=10, fg_color="#220c10", border_width=1, border_color="#551119")
        badge_sub.pack(pady=(0, 10))
        lbl_sub = ctk.CTkLabel(
            badge_sub, 
            text="✦ MULTIVERSE CINEMA EXPERIENCE ✦", 
            font=ctk.CTkFont(family="Inter", size=9, weight="bold"),
            text_color=COLOR_GOLD
        )
        lbl_sub.pack(padx=14, pady=3)

        # Footer Gợi ý tài khoản test & Phím tắt đăng nhập nhanh (pack bottom trước để không bao giờ bị che khuất)
        hint_card = ctk.CTkFrame(main_card, corner_radius=14, fg_color=COLOR_BG_DARK, border_width=1, border_color=COLOR_BORDER)
        hint_card.pack(side="bottom", fill="x", padx=20, pady=(6, 14))

        lbl_hint = ctk.CTkLabel(
            hint_card,
            text="⚡ ĐĂNG NHẬP NHANH (CLICK CHỌN VAI TRÒ DEMO):",
            font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
            text_color=COLOR_GOLD,
            justify="center"
        )
        lbl_hint.pack(pady=(6, 4))

        quick_btns = ctk.CTkFrame(hint_card, fg_color="transparent")
        quick_btns.pack(fill="x", padx=10, pady=(0, 8))

        def fill_account(u, p):
            self.txt_login_user.delete(0, "end")
            self.txt_login_user.insert(0, u)
            self.txt_login_pwd.delete(0, "end")
            self.txt_login_pwd.insert(0, p)

        btn_q_admin = ctk.CTkButton(
            quick_btns, text="👑 Admin", height=28, width=85, corner_radius=8,
            fg_color="#e50914", hover_color="#b80710", text_color=COLOR_TEXT_WHITE, font=ctk.CTkFont(size=11, weight="bold"), cursor="hand2",
            command=lambda: fill_account("admin", "admin123")
        )
        btn_q_admin.pack(side="left", expand=True, padx=2)

        btn_q_staff = ctk.CTkButton(
            quick_btns, text="👔 Nhân Viên", height=28, width=95, corner_radius=8,
            fg_color="#2563eb", hover_color="#1d4ed8", text_color=COLOR_TEXT_WHITE, font=ctk.CTkFont(size=11, weight="bold"), cursor="hand2",
            command=lambda: fill_account("nhanvien", "nv123456")
        )
        btn_q_staff.pack(side="left", expand=True, padx=2)

        btn_q_cust = ctk.CTkButton(
            quick_btns, text="👤 Khách Hàng", height=28, width=95, corner_radius=8,
            fg_color="#374151", hover_color="#4b5563", text_color=COLOR_TEXT_WHITE, font=ctk.CTkFont(size=11, weight="bold"), cursor="hand2",
            command=lambda: fill_account("khach1", "123456")
        )
        btn_q_cust.pack(side="left", expand=True, padx=2)

        # Tabview Bo Góc: ĐĂNG NHẬP / ĐĂNG KÝ
        self.tabview = ctk.CTkTabview(
            main_card, 
            corner_radius=16,
            fg_color=COLOR_BG_LIGHT,
            segmented_button_selected_color=COLOR_ACCENT,
            segmented_button_selected_hover_color=COLOR_ACCENT_HOVER,
            segmented_button_unselected_color=COLOR_BG_DARK
        )
        self.tabview.pack(side="top", fill="both", expand=True, padx=20, pady=(0, 6))

        self.tab_login = self.tabview.add("  ĐĂNG NHẬP  ")
        self.tab_register = self.tabview.add("  ĐĂNG KÝ MỚI  ")

        self._build_login_tab()
        self._build_register_tab()

    def _build_login_tab(self):
        # Tên đăng nhập
        lbl_u = ctk.CTkLabel(self.tab_login, text="Tên đăng nhập:", font=ctk.CTkFont(family="Inter", size=12, weight="bold"), text_color=COLOR_TEXT_WHITE)
        lbl_u.pack(anchor="w", pady=(10, 2), padx=5)

        self.txt_login_user = ctk.CTkEntry(
            self.tab_login, 
            corner_radius=12, 
            height=40,
            fg_color=COLOR_BG_CARD,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_WHITE,
            placeholder_text="Nhập username..."
        )
        self.txt_login_user.pack(fill="x", pady=(0, 12), padx=5)
        self.txt_login_user.insert(0, "khach1")

        # Mật khẩu
        lbl_p = ctk.CTkLabel(self.tab_login, text="Mật khẩu:", font=ctk.CTkFont(family="Inter", size=12, weight="bold"), text_color=COLOR_TEXT_WHITE)
        lbl_p.pack(anchor="w", pady=(0, 2), padx=5)

        self.txt_login_pwd = ctk.CTkEntry(
            self.tab_login, 
            corner_radius=12, 
            height=40,
            show="•",
            fg_color=COLOR_BG_CARD,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_WHITE,
            placeholder_text="Nhập mật khẩu..."
        )
        self.txt_login_pwd.pack(fill="x", pady=(0, 20), padx=5)
        self.txt_login_pwd.insert(0, "123456")

        # Nút Đăng nhập bo tròn
        btn_login = ctk.CTkButton(
            self.tab_login, 
            text="ĐĂNG NHẬP VÀO CINEVERSE", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            corner_radius=14, 
            height=42,
            fg_color=COLOR_ACCENT, 
            hover_color=COLOR_ACCENT_HOVER,
            text_color=COLOR_TEXT_WHITE,
            cursor="hand2",
            command=self._handle_login
        )
        btn_login.pack(fill="x", pady=5, padx=5)

        self.txt_login_pwd.bind("<Return>", lambda event: self._handle_login())
        self.txt_login_user.bind("<Return>", lambda event: self._handle_login())

    def _build_register_tab(self):
        # Họ và tên
        lbl_name = ctk.CTkLabel(self.tab_register, text="Họ và tên (*):", font=ctk.CTkFont(family="Inter", size=11), text_color=COLOR_TEXT_WHITE)
        lbl_name.pack(anchor="w", padx=5)
        self.txt_reg_name = ctk.CTkEntry(self.tab_register, corner_radius=10, height=30, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER, text_color="white", placeholder_text="Ví dụ: Nguyễn Văn An")
        self.txt_reg_name.pack(fill="x", pady=(1, 3), padx=5)

        # Tên đăng nhập
        lbl_user = ctk.CTkLabel(self.tab_register, text="Tên đăng nhập (chữ & số, không dấu) (*):", font=ctk.CTkFont(family="Inter", size=11), text_color=COLOR_TEXT_WHITE)
        lbl_user.pack(anchor="w", padx=5)
        self.txt_reg_user = ctk.CTkEntry(self.tab_register, corner_radius=10, height=30, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER, text_color="white", placeholder_text="Ví dụ: nguyenvana123")
        self.txt_reg_user.pack(fill="x", pady=(1, 3), padx=5)

        # Mật khẩu
        lbl_pwd = ctk.CTkLabel(self.tab_register, text="Mật khẩu (≥ 6 ký tự) (*):", font=ctk.CTkFont(family="Inter", size=11), text_color=COLOR_TEXT_WHITE)
        lbl_pwd.pack(anchor="w", padx=5)
        self.txt_reg_pwd = ctk.CTkEntry(self.tab_register, corner_radius=10, height=30, show="•", fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER, text_color="white", placeholder_text="Nhập mật khẩu...")
        self.txt_reg_pwd.pack(fill="x", pady=(1, 3), padx=5)
        self.txt_reg_pwd.bind("<KeyRelease>", lambda e: self._check_password_match())

        # Nhập lại Mật khẩu lần 2 (Xác nhận)
        lbl_pwd_confirm = ctk.CTkLabel(self.tab_register, text="Xác nhận lại mật khẩu (*):", font=ctk.CTkFont(family="Inter", size=11), text_color=COLOR_TEXT_WHITE)
        lbl_pwd_confirm.pack(anchor="w", padx=5)
        self.txt_reg_pwd_confirm = ctk.CTkEntry(self.tab_register, corner_radius=10, height=30, show="•", fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER, text_color="white", placeholder_text="Nhập lại mật khẩu để xác nhận...")
        self.txt_reg_pwd_confirm.pack(fill="x", pady=(1, 2), padx=5)
        self.txt_reg_pwd_confirm.bind("<KeyRelease>", lambda e: self._check_password_match())

        # Match Status & Hiện/Ẩn mật khẩu
        match_frame = ctk.CTkFrame(self.tab_register, fg_color="transparent")
        match_frame.pack(fill="x", padx=5, pady=(0, 2))

        self.lbl_pwd_status = ctk.CTkLabel(match_frame, text="", font=ctk.CTkFont(family="Inter", size=10, weight="bold"))
        self.lbl_pwd_status.pack(side="left")

        self.show_pwd_var = ctk.BooleanVar(value=False)
        self.chk_show_pwd = ctk.CTkCheckBox(
            match_frame, 
            text="Hiện mật khẩu", 
            variable=self.show_pwd_var,
            font=ctk.CTkFont(size=10),
            checkbox_width=16,
            checkbox_height=16,
            command=self._toggle_show_passwords
        )
        self.chk_show_pwd.pack(side="right")

        # Số điện thoại
        lbl_phone = ctk.CTkLabel(self.tab_register, text="Số điện thoại (10 chữ số):", font=ctk.CTkFont(family="Inter", size=11), text_color=COLOR_TEXT_WHITE)
        lbl_phone.pack(anchor="w", padx=5)
        self.txt_reg_phone = ctk.CTkEntry(self.tab_register, corner_radius=10, height=30, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER, text_color="white", placeholder_text="09xxxxxxxx")
        self.txt_reg_phone.pack(fill="x", pady=(1, 3), padx=5)

        # Nút Đăng ký bo góc
        btn_reg = ctk.CTkButton(
            self.tab_register, 
            text="TẠO TÀI KHOẢN MỚI", 
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            corner_radius=12, 
            height=36,
            fg_color="#06d6a0", 
            hover_color="#05b386", 
            text_color="#000000",
            cursor="hand2", 
            command=self._handle_register
        )
        btn_reg.pack(fill="x", pady=(3, 2), padx=5)

    def _toggle_show_passwords(self):
        show_char = "" if self.show_pwd_var.get() else "•"
        self.txt_reg_pwd.configure(show=show_char)
        self.txt_reg_pwd_confirm.configure(show=show_char)

    def _check_password_match(self):
        p1 = self.txt_reg_pwd.get()
        p2 = self.txt_reg_pwd_confirm.get()
        if not p2:
            self.lbl_pwd_status.configure(text="")
            return

        if p1 == p2:
            self.lbl_pwd_status.configure(text="✓ Mật khẩu trùng khớp", text_color="#06d6a0")
        else:
            self.lbl_pwd_status.configure(text="✕ Mật khẩu chưa khớp", text_color=COLOR_DANGER)

    def _handle_login(self):
        username = self.txt_login_user.get().strip()
        password = self.txt_login_pwd.get().strip()

        if not username or not password:
            show_toast(self.root, "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!", title="Thiếu Thông Tin", toast_type="warning")
            return

        user = AuthService.login(username, password)
        if user:
            self.on_login_success(user)
        else:
            show_toast(self.root, "Sai tên đăng nhập hoặc mật khẩu! Vui lòng thử lại.", title="Đăng Nhập Thất Bại", toast_type="error")

    def _handle_register(self):
        fullname = self.txt_reg_name.get().strip()
        username = self.txt_reg_user.get().strip()
        password = self.txt_reg_pwd.get().strip()
        confirm_pwd = self.txt_reg_pwd_confirm.get().strip()
        phone = self.txt_reg_phone.get().strip()

        # 1. Kiểm tra các trường bắt buộc
        if not fullname or not username or not password or not confirm_pwd:
            show_toast(self.root, "Vui lòng điền đủ: Họ tên, Tên đăng nhập, Mật khẩu!", title="Thiếu Thông Tin", toast_type="warning")
            return

        # 2. Kiểm tra tên đăng nhập hợp lệ (chữ, số, gạch dưới, không dấu cách)
        if " " in username or not (username.isalnum() or "_" in username):
            show_toast(self.root, "Tên đăng nhập chỉ được chứa chữ cái, chữ số hoặc gạch dưới (_)", title="Tên Không Hợp Lệ", toast_type="warning")
            self.txt_reg_user.focus()
            return

        # 3. Kiểm tra độ dài mật khẩu
        if len(password) < 6:
            show_toast(self.root, "Mật khẩu bảo mật phải có độ dài từ 6 ký tự trở lên!", title="Mật Khẩu Yếu", toast_type="warning")
            self.txt_reg_pwd.focus()
            return

        # 4. Kiểm tra xác nhận mật khẩu 2 lần
        if password != confirm_pwd:
            show_toast(self.root, "Mật khẩu và xác nhận mật khẩu không trùng khớp!", title="Mật Khẩu Chưa Khớp", toast_type="error")
            self.txt_reg_pwd_confirm.focus()
            return

        # 5. Kiểm tra định dạng số điện thoại (nếu có nhập)
        if phone:
            digits = "".join(ch for ch in phone if ch.isdigit())
            if len(digits) != 10 or not digits.startswith("0"):
                show_toast(self.root, "Số điện thoại phải gồm 10 chữ số bắt đầu bằng số 0!", title="SĐT Không Hợp Lệ", toast_type="warning")
                self.txt_reg_phone.focus()
                return
            phone = digits

        success, msg = AuthService.register(username, password, fullname, "", phone)
        if success:
            show_toast(self.root, f"🎉 {msg.rstrip('.!')}! Chào mừng bạn đến với CINEVERSE.", title="Đăng Ký Thành Công", toast_type="success")
            self.tabview.set("  ĐĂNG NHẬP  ")
            self.txt_login_user.delete(0, "end")
            self.txt_login_user.insert(0, username)
            self.txt_login_pwd.delete(0, "end")
            self.txt_login_pwd.insert(0, password)
            # Dọn dẹp form đăng ký
            self.txt_reg_name.delete(0, "end")
            self.txt_reg_user.delete(0, "end")
            self.txt_reg_pwd.delete(0, "end")
            self.txt_reg_pwd_confirm.delete(0, "end")
            self.txt_reg_phone.delete(0, "end")
            self.lbl_pwd_status.configure(text="")
        else:
            show_toast(self.root, msg, title="Đăng Ký Thất Bại", toast_type="error")
