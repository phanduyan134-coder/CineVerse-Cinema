"""
Module: ui/staff_window.py
Mô tả: Giao diện Dành Riêng Cho Nhân Viên Rạp CINEVERSE (Staff / POS & Soát vé)
- Bán vé tại quầy (POS Counter)
- Soát vé & Check-in cửa rạp (Gate Scanner / Check-in)
- Tra cứu vé & In lại biên nhận Quantum E-Ticket
"""

import os
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image
from services import CinemaService
from models import Staff, Seat, Showtime, Movie, Concession
from ui.qr_payment_dialog import QRPaymentDialog
from ui.toast import show_toast
from ui.styles import (
    COLOR_BG_DARK, COLOR_BG_CARD, COLOR_BG_LIGHT, COLOR_ACCENT, COLOR_ACCENT_HOVER,
    COLOR_GOLD, COLOR_GOLD_HOVER, COLOR_TEXT, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED,
    COLOR_SUCCESS, COLOR_DANGER, COLOR_BORDER,
    SEAT_AVAILABLE_STD, SEAT_AVAILABLE_VIP, SEAT_AVAILABLE_SWEETBOX, SEAT_SELECTED, SEAT_BOOKED,
    setup_styles, center_window
)

class StaffWindow:
    """Giao diện Nhân viên Rạp CINEVERSE Bo Góc Hiện Đại (POS & Soát Vé)"""
    def __init__(self, root, staff: Staff, on_logout):
        self.root = root
        self.staff = staff
        self.on_logout = on_logout

        self.root.title(f"CINEVERSE - Quầy Nhân Viên & Soát Vé: {staff.fullname}")
        self.root.configure(fg_color=COLOR_BG_DARK)
        setup_styles()
        center_window(self.root, 1180, 750)

        self.selected_pos_movie = None
        self.selected_pos_showtime = None

        self._build_ui()

    def _build_ui(self):
        # 1. Header Bar Bo Tròn
        header = ctk.CTkFrame(
            self.root, 
            corner_radius=18, 
            fg_color=COLOR_BG_CARD, 
            border_width=1, 
            border_color=COLOR_BORDER,
            height=70
        )
        header.pack(fill="x", padx=15, pady=(15, 10))

        # Brand
        brand_frame = ctk.CTkFrame(header, fg_color="transparent")
        brand_frame.pack(side="left", padx=20, pady=12)

        lbl_brand = ctk.CTkLabel(
            brand_frame, 
            text="🌌 CINEVERSE - PHÂN HỆ NHÂN VIÊN (STAFF)", 
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color=COLOR_ACCENT
        )
        lbl_brand.pack(side="left")

        # Right nav
        right_nav = ctk.CTkFrame(header, fg_color="transparent")
        right_nav.pack(side="right", padx=15, pady=12)

        lbl_user = ctk.CTkLabel(
            right_nav, 
            text=f"👔 Thu ngân: {self.staff.fullname}", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color=COLOR_GOLD
        )
        lbl_user.pack(side="left", padx=15)

        btn_logout = ctk.CTkButton(
            right_nav, 
            text="🚪 Đăng Xuất", 
            corner_radius=12,
            height=34,
            fg_color=COLOR_DANGER, 
            hover_color="#c92a2a",
            cursor="hand2", 
            command=self.on_logout
        )
        btn_logout.pack(side="left")

        # Tabview Bo Góc Hiện Đại
        self.tabview = ctk.CTkTabview(
            self.root, 
            corner_radius=18,
            fg_color=COLOR_BG_CARD,
            segmented_button_selected_color=COLOR_ACCENT,
            segmented_button_selected_hover_color=COLOR_ACCENT_HOVER,
            segmented_button_unselected_color=COLOR_BG_LIGHT
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.tab_pos = self.tabview.add("  🎟️ BÁN VÉ TẠI QUẦY (POS)  ")
        self.tab_checkin = self.tabview.add("  🔍 SOÁT VÉ & CHECK-IN CỬA RẠP  ")
        self.tab_manage = self.tabview.add("  📋 TRA CỨU & QUẢN LÝ VÉ  ")

        self._build_pos_tab()
        self._build_checkin_tab()
        self._build_manage_tab()

    # ================= TAB 1: BÁN VÉ TẠI QUẦY (POS) =================
    def _build_pos_tab(self):
        container = ctk.CTkFrame(self.tab_pos, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Cột Trái: Chọn Phim & Suất Chiếu
        left_card = ctk.CTkFrame(container, corner_radius=16, fg_color=COLOR_BG_LIGHT, border_width=1, border_color=COLOR_BORDER, width=475)
        left_card.pack(side="left", fill="both", padx=(0, 10), pady=0)
        left_card.pack_propagate(False)

        # Header Mục 1: Badge số bo góc chuẩn CustomTkinter (Khắc phục triệt để lỗi lệch ô vuông của emoji)
        sec1_header = ctk.CTkFrame(left_card, fg_color="transparent")
        sec1_header.pack(anchor="w", padx=15, pady=(12, 6))

        ctk.CTkLabel(
            sec1_header, 
            text="1", 
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            fg_color=COLOR_GOLD,
            text_color="#0b132b",
            corner_radius=6,
            width=22,
            height=22
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            sec1_header, 
            text="CHỌN PHIM ĐANG CHIẾU", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color=COLOR_GOLD
        ).pack(side="left")

        # Search Phim
        search_box = ctk.CTkFrame(left_card, fg_color="transparent")
        search_box.pack(fill="x", padx=15, pady=(0, 8))

        self.txt_pos_search = ctk.CTkEntry(
            search_box, 
            placeholder_text="Tìm tên phim...", 
            corner_radius=8, 
            height=32, 
            fg_color=COLOR_BG_CARD, 
            border_color=COLOR_BORDER
        )
        self.txt_pos_search.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.txt_pos_search.bind("<KeyRelease>", lambda e: self._load_pos_movies())

        # Bảng Phim
        tree_frame = tk.Frame(left_card, bg=COLOR_BG_LIGHT)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 8))

        cols_m = ("id", "title", "duration")
        self.tree_pos_movies = ttk.Treeview(tree_frame, columns=cols_m, show="headings", style="Dark.Treeview", height=7, selectmode="browse")
        self.tree_pos_movies.heading("id", text="ID")
        self.tree_pos_movies.heading("title", text="Tên Phim")
        self.tree_pos_movies.heading("duration", text="Thời Lượng")
        self.tree_pos_movies.column("id", width=35, anchor="center")
        self.tree_pos_movies.column("title", width=270, anchor="w")
        self.tree_pos_movies.column("duration", width=95, anchor="center")

        scroll_m = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_pos_movies.yview)
        self.tree_pos_movies.configure(yscrollcommand=scroll_m.set)
        self.tree_pos_movies.pack(side="left", fill="both", expand=True)
        scroll_m.pack(side="right", fill="y")
        self.tree_pos_movies.bind("<<TreeviewSelect>>", self._on_pos_movie_selected)

        # Suất Chiếu
        # Header Mục 2: Badge số bo góc chuẩn CustomTkinter
        sec2_header = ctk.CTkFrame(left_card, fg_color="transparent")
        sec2_header.pack(anchor="w", padx=15, pady=(8, 4))

        ctk.CTkLabel(
            sec2_header, 
            text="2", 
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            fg_color=COLOR_GOLD,
            text_color="#0b132b",
            corner_radius=6,
            width=22,
            height=22
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            sec2_header, 
            text="CHỌN SUẤT CHIẾU", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color=COLOR_GOLD
        ).pack(side="left")

        st_frame = tk.Frame(left_card, bg=COLOR_BG_LIGHT)
        st_frame.pack(fill="both", expand=True, padx=15, pady=(0, 12))

        cols_st = ("id", "date", "time", "room", "price")
        self.tree_pos_showtimes = ttk.Treeview(st_frame, columns=cols_st, show="headings", style="Dark.Treeview", height=6, selectmode="browse")
        self.tree_pos_showtimes.heading("id", text="ID")
        self.tree_pos_showtimes.heading("date", text="Ngày")
        self.tree_pos_showtimes.heading("time", text="Giờ")
        self.tree_pos_showtimes.heading("room", text="Phòng Chiếu")
        self.tree_pos_showtimes.heading("price", text="Giá Gốc")

        self.tree_pos_showtimes.column("id", width=30, anchor="center")
        self.tree_pos_showtimes.column("date", width=85, anchor="center")
        self.tree_pos_showtimes.column("time", width=55, anchor="center")
        self.tree_pos_showtimes.column("room", width=155, anchor="w")
        self.tree_pos_showtimes.column("price", width=85, anchor="e")

        scroll_st = ttk.Scrollbar(st_frame, orient="vertical", command=self.tree_pos_showtimes.yview)
        self.tree_pos_showtimes.configure(yscrollcommand=scroll_st.set)
        self.tree_pos_showtimes.pack(side="left", fill="both", expand=True)
        scroll_st.pack(side="right", fill="y")
        self.tree_pos_showtimes.bind("<<TreeviewSelect>>", self._on_pos_showtime_selected)

        # Cột Phải: Thông tin Khách Vãng Lai & Nút Mở Sơ Đồ Ghế
        right_card = ctk.CTkFrame(container, corner_radius=16, fg_color=COLOR_BG_LIGHT, border_width=1, border_color=COLOR_BORDER)
        right_card.pack(side="right", fill="both", expand=True, padx=(0, 0), pady=0)

        # Header Mục 3: Badge số bo góc chuẩn CustomTkinter
        sec3_header = ctk.CTkFrame(right_card, fg_color="transparent")
        sec3_header.pack(anchor="w", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            sec3_header, 
            text="3", 
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            fg_color=COLOR_ACCENT,
            text_color="#0b132b",
            corner_radius=6,
            width=22,
            height=22
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            sec3_header, 
            text="THÔNG TIN XUẤT VÉ TẠI QUẦY", 
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color=COLOR_ACCENT
        ).pack(side="left")

        # Panel chi tiết suất chiếu đã chọn (Chia 2 cột: Poster nhỏ & Chi tiết)
        self.pos_info_card = ctk.CTkFrame(right_card, corner_radius=12, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER)
        self.pos_info_card.pack(fill="x", padx=20, pady=(0, 15), ipady=8)

        self.lbl_pos_poster = ctk.CTkLabel(self.pos_info_card, text="🎬", width=70, height=100, corner_radius=8, fg_color=COLOR_BG_LIGHT)
        self.lbl_pos_poster.pack(side="left", padx=12, pady=6)

        info_text_col = ctk.CTkFrame(self.pos_info_card, fg_color="transparent")
        info_text_col.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=6)

        self.lbl_pos_selected_movie = ctk.CTkLabel(
            info_text_col, 
            text="Vui lòng chọn Phim và Suất chiếu ở bảng bên trái", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color=COLOR_TEXT_WHITE
        )
        self.lbl_pos_selected_movie.pack(anchor="w", pady=(4, 2))

        self.lbl_pos_selected_st = ctk.CTkLabel(
            info_text_col, 
            text="", 
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=COLOR_GOLD
        )
        self.lbl_pos_selected_st.pack(anchor="w", pady=(0, 4))

        # Form Khách Vãng Lai
        form_frame = ctk.CTkFrame(right_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkLabel(form_frame, text="Tên khách hàng (tùy chọn):", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", pady=6)
        self.txt_pos_cust_name = ctk.CTkEntry(form_frame, corner_radius=8, height=34, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER, placeholder_text="Khách Mua Tại Quầy")
        self.txt_pos_cust_name.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=6)

        ctk.CTkLabel(form_frame, text="Số điện thoại khách (tùy chọn):", font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w", pady=6)
        self.txt_pos_cust_phone = ctk.CTkEntry(form_frame, corner_radius=8, height=34, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER, placeholder_text="0901234567")
        self.txt_pos_cust_phone.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=6)

        ctk.CTkLabel(form_frame, text="Phương thức thanh toán:", font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w", pady=6)
        self.combo_pos_payment = ctk.CTkComboBox(form_frame, values=["Tiền mặt tại quầy", "Chuyển khoản QR POS", "Thẻ ngân hàng POS"], corner_radius=8, height=34, state="readonly")
        self.combo_pos_payment.set("Tiền mặt tại quầy")
        self.combo_pos_payment.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=6)

        form_frame.columnconfigure(1, weight=1)

        # Nút Mở Sơ Đồ Chọn Ghế
        self.btn_pos_select_seat = ctk.CTkButton(
            right_card, 
            text="🎟️ MỞ SƠ ĐỒ CHỌN GHẾ & XUẤT VÉ", 
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            corner_radius=14, 
            height=46,
            fg_color=COLOR_GOLD, 
            hover_color=COLOR_GOLD_HOVER,
            text_color="#000000",
            cursor="hand2", 
            state="disabled",
            command=self._open_pos_seat_modal
        )
        self.btn_pos_select_seat.pack(fill="x", padx=20, pady=(10, 15))

        # Hướng dẫn thao tác nhanh cho thu ngân (Tạo đối xứng chiều cao với cột bên trái)
        guide_card = ctk.CTkFrame(right_card, corner_radius=12, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER)
        guide_card.pack(fill="x", padx=20, pady=(0, 15), ipady=6)

        ctk.CTkLabel(
            guide_card,
            text="💡 Quy trình bán vé nhanh tại quầy:",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color=COLOR_GOLD
        ).pack(anchor="w", padx=14, pady=(8, 4))

        guide_steps = (
            "• Bước 1 & 2: Click chọn Phim và Suất chiếu cần xem ở cột bên trái.\n"
            "• Bước 3: Nhập thông tin Khách hàng (hoặc để mặc định cho khách vãng lai).\n"
            "• Bước 4: Nhấn nút vàng 'Mở sơ đồ chọn ghế' để chọn vị trí, nhận tiền và in vé."
        )
        ctk.CTkLabel(
            guide_card,
            text=guide_steps,
            font=ctk.CTkFont(family="Inter", size=11),
            text_color=COLOR_TEXT_MUTED,
            justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 8))

        self._load_pos_movies()

    def _load_pos_movies(self):
        for row in self.tree_pos_movies.get_children():
            self.tree_pos_movies.delete(row)

        kw = self.txt_pos_search.get().strip()
        self.pos_movies = CinemaService.get_movies(only_active=True, keyword=kw)
        for m in self.pos_movies:
            self.tree_pos_movies.insert("", "end", values=(m.id, m.title, f"{m.duration} phút"))

        # Tự động chọn phim đầu tiên
        children = self.tree_pos_movies.get_children()
        if children:
            self.tree_pos_movies.focus(children[0])
            self.tree_pos_movies.selection_set(children[0])
            self._on_pos_movie_selected(None)

    def _on_pos_movie_selected(self, event):
        selected = self.tree_pos_movies.focus()
        if not selected:
            return
        m_id = int(self.tree_pos_movies.item(selected, "values")[0])
        self.selected_pos_movie = next((m for m in self.pos_movies if m.id == m_id), None)

        # Reset showtime
        self.selected_pos_showtime = None
        self.btn_pos_select_seat.configure(state="disabled")
        self.lbl_pos_selected_movie.configure(text=f"🎬 Phim: {self.selected_pos_movie.title}")
        self.lbl_pos_selected_st.configure(text="👉 Tiếp theo: Vui lòng click chọn 1 suất chiếu ở bên dưới")

        # Cập nhật ảnh Poster nhỏ
        if self.selected_pos_movie and self.selected_pos_movie.poster_path and os.path.exists(self.selected_pos_movie.poster_path):
            try:
                pil_img = Image.open(self.selected_pos_movie.poster_path)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(70, 100))
                self.lbl_pos_poster.configure(image=ctk_img, text="")
            except Exception:
                self.lbl_pos_poster.configure(image=None, text="🎬")
        else:
            self.lbl_pos_poster.configure(image=None, text="🎬")

        # Load showtimes
        for row in self.tree_pos_showtimes.get_children():
            self.tree_pos_showtimes.delete(row)

        self.pos_showtimes = CinemaService.get_showtimes(movie_id=self.selected_pos_movie.id)
        for st in self.pos_showtimes:
            self.tree_pos_showtimes.insert("", "end", values=(
                st.id, st.show_date, st.show_time, st.room_name, f"{st.base_price:,.0f} đ"
            ))

        # Tự động chọn suất chiếu đầu tiên
        st_children = self.tree_pos_showtimes.get_children()
        if st_children:
            self.tree_pos_showtimes.focus(st_children[0])
            self.tree_pos_showtimes.selection_set(st_children[0])
            self._on_pos_showtime_selected(None)

    def _on_pos_showtime_selected(self, event):
        selected = self.tree_pos_showtimes.focus()
        if not selected:
            return
        st_id = int(self.tree_pos_showtimes.item(selected, "values")[0])
        self.selected_pos_showtime = next((s for s in self.pos_showtimes if s.id == st_id), None)

        if self.selected_pos_showtime:
            st = self.selected_pos_showtime
            self.lbl_pos_selected_st.configure(
                text=f"🕒 Suất: {st.show_date} lúc {st.show_time} | {st.room_name} | Giá gốc: {st.base_price:,.0f} VNĐ"
            )
            self.btn_pos_select_seat.configure(state="normal")

    def _open_pos_seat_modal(self):
        if not self.selected_pos_showtime:
            return

        st = self.selected_pos_showtime
        dialog = ctk.CTkToplevel(self.root)
        self.pos_seat_dialog = dialog
        dialog.title(f"CINEVERSE POS - Sơ Đồ Chọn Ghế ({st.room_name})")
        dialog.transient(self.root)
        dialog.grab_set()
        center_window(dialog, 1020, 780)

        selected_seats = []

        # Header
        top = ctk.CTkFrame(dialog, corner_radius=14, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER)
        top.pack(fill="x", padx=15, pady=(15, 8), ipady=4)

        ctk.CTkLabel(
            top, 
            text=f"🎬 [QUẦY VÉ] Phim: {self.selected_pos_movie.title}", 
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(anchor="w", padx=15, pady=(4, 0))

        ctk.CTkLabel(
            top, 
            text=f"🕒 Suất: {st.show_date} lúc {st.show_time} | {st.room_name}", 
            font=ctk.CTkFont(size=12),
            text_color=COLOR_GOLD
        ).pack(anchor="w", padx=15, pady=(0, 4))

        # Màn hình cong IMAX Lượng Tử (Curved IMAX Screen with Projection Beam & Neon Glow)
        screen_canvas = tk.Canvas(
            dialog, 
            height=58, 
            bg=COLOR_BG_DARK, 
            highlightthickness=0, 
            bd=0
        )
        screen_canvas.pack(fill="x", padx=35, pady=(4, 8))

        def draw_pos_imax_screen(event=None):
            w = screen_canvas.winfo_width()
            h = screen_canvas.winfo_height()
            if w <= 50:
                return
            screen_canvas.delete("all")

            p1 = (w * 0.12, 14)
            p2 = (w * 0.88, 14)
            p3 = (w * 0.96, h - 2)
            p4 = (w * 0.04, h - 2)
            screen_canvas.create_polygon(
                p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1],
                fill="#220e12", outline=""
            )
            screen_canvas.create_arc(
                w * 0.07, -35, w * 0.93, 25,
                start=205, extent=130, style="arc", outline="#4a151e", width=5
            )
            screen_canvas.create_arc(
                w * 0.07, -35, w * 0.93, 24,
                start=205, extent=130, style="arc", outline=COLOR_ACCENT, width=3
            )
            screen_canvas.create_arc(
                w * 0.35, -30, w * 0.65, 24,
                start=235, extent=70, style="arc", outline="#ffffff", width=2
            )
            screen_canvas.create_text(
                w / 2, 34,
                text="⚡ MÀN HÌNH CHIẾU CONG IMAX LASER ⚡",
                font=("Anton", 11),
                fill=COLOR_ACCENT
            )
            screen_canvas.create_text(
                w / 2, 48,
                text="✦ CINEVERSE POS THEATER TERMINAL • DOLBY ATMOS ✦",
                font=("Inter", 8, "bold"),
                fill=COLOR_TEXT_MUTED
            )

        screen_canvas.bind("<Configure>", draw_pos_imax_screen)

        # Seats
        seat_box = ctk.CTkFrame(dialog, fg_color="transparent")
        seat_box.pack(expand=True, pady=5)

        all_seats = CinemaService.get_room_seats(st.room_id)
        booked = CinemaService.get_booked_seats(st.id)

        rows_dict = {}
        for s in all_seats:
            rows_dict.setdefault(s.row_label, []).append(s)

        def toggle_s(seat: Seat, btn: ctk.CTkButton):
            if seat.seat_code in booked:
                return
            if seat in selected_seats:
                selected_seats.remove(seat)
                color = SEAT_AVAILABLE_SWEETBOX if seat.is_sweetbox() else (SEAT_AVAILABLE_VIP if seat.is_vip() else SEAT_AVAILABLE_STD)
                btn.configure(fg_color=color, text_color="white")
            else:
                selected_seats.append(seat)
                btn.configure(fg_color=SEAT_SELECTED, text_color="black")
            update_sum()

        for row_lbl, row_seats in sorted(rows_dict.items()):
            rf = ctk.CTkFrame(seat_box, fg_color="transparent")
            rf.pack(pady=3)
            # Badge chữ cái hàng đầu bo tròn
            ctk.CTkLabel(
                rf, text=row_lbl, width=28, height=28, corner_radius=14,
                fg_color="#1e1e28", font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                text_color=COLOR_GOLD
            ).pack(side="left", padx=4)

            for s in sorted(row_seats, key=lambda x: x.seat_num):
                # Lối đi rạp chiếu trung tâm giữa ghế 4 và ghế 5
                if s.seat_num == 5:
                    aisle = ctk.CTkFrame(rf, width=28, height=1, fg_color="transparent")
                    aisle.pack(side="left")

                is_b = s.seat_code in booked
                is_sw = s.is_sweetbox()
                if is_b:
                    fg, txt, cur, stt = SEAT_BOOKED, f"✕ {s.seat_code}", "arrow", "disabled"
                elif is_sw:
                    fg, txt, cur, stt = SEAT_AVAILABLE_SWEETBOX, f"💑 {s.seat_code}", "hand2", "normal"
                elif s.is_vip():
                    fg, txt, cur, stt = SEAT_AVAILABLE_VIP, s.seat_code, "hand2", "normal"
                else:
                    fg, txt, cur, stt = SEAT_AVAILABLE_STD, s.seat_code, "hand2", "normal"

                # Đệm khoảng cách cho cặp ghế Sweetbox
                if is_sw:
                    btn_padx = (4, 1) if s.seat_num % 2 == 1 else (1, 4)
                else:
                    btn_padx = 3

                btn = ctk.CTkButton(
                    rf, text=txt, width=46, height=32, corner_radius=8,
                    fg_color=fg, hover_color=COLOR_ACCENT, state=stt, cursor=cur
                )
                btn.configure(command=lambda seat=s, b=btn: toggle_s(seat, b))
                btn.pack(side="left", padx=btn_padx)

            # Badge chữ cái hàng cuối bo tròn
            ctk.CTkLabel(
                rf, text=row_lbl, width=28, height=28, corner_radius=14,
                fg_color="#1e1e28", font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                text_color=COLOR_GOLD
            ).pack(side="left", padx=4)

        # Chú thích phân khúc ghế Bo Tròn (Legend)
        legend_frame = ctk.CTkFrame(dialog, corner_radius=12, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER)
        legend_frame.pack(fill="x", padx=15, pady=(4, 4), ipady=3)

        legends = [
            ("Ghế Nebula (Chuẩn)", SEAT_AVAILABLE_STD),
            ("Ghế Galaxy VIP (+25k)", SEAT_AVAILABLE_VIP),
            ("Ghế Cặp Đôi Supernova (+50k)", SEAT_AVAILABLE_SWEETBOX),
            ("Đang Chọn", SEAT_SELECTED),
            ("Đã Bán", SEAT_BOOKED)
        ]
        for text, color in legends:
            box = ctk.CTkFrame(legend_frame, width=14, height=14, corner_radius=4, fg_color=color)
            box.pack(side="left", padx=(10, 3), pady=4)
            ctk.CTkLabel(legend_frame, text=text, font=ctk.CTkFont(family="Inter", size=10), text_color=COLOR_TEXT).pack(side="left", padx=(0, 6))

        # Khung Chọn Bắp Nước POS (F&B Concessions)
        fnb_card = ctk.CTkFrame(dialog, corner_radius=12, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER)
        fnb_card.pack(fill="x", padx=15, pady=(2, 4))

        fnb_header_box = ctk.CTkFrame(fnb_card, fg_color="transparent")
        fnb_header_box.pack(fill="x", padx=12, pady=(4, 2))

        ctk.CTkLabel(
            fnb_header_box,
            text="🍿 BẮP NƯỚC & COMBO BÁN KÈM (TÙY CHỌN BÁN TẠI QUẦY):",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color=COLOR_GOLD
        ).pack(side="left")

        fnb_scroll = ctk.CTkScrollableFrame(fnb_card, orientation="horizontal", height=84, fg_color="transparent")
        fnb_scroll.pack(fill="x", padx=10, pady=(0, 4))

        all_concessions = CinemaService.get_concessions(only_active=True)
        concession_qty_map = {}
        concession_lbl_map = {}

        def change_concession_qty(item, delta):
            current = concession_qty_map.get(item, 0)
            new_qty = max(0, current + delta)
            concession_qty_map[item] = new_qty
            if item in concession_lbl_map:
                concession_lbl_map[item].configure(text=str(new_qty))
            update_sum()

        for item in all_concessions:
            concession_qty_map[item] = 0
            item_card = ctk.CTkFrame(fnb_scroll, corner_radius=10, fg_color=COLOR_BG_LIGHT, border_width=1, border_color=COLOR_BORDER, width=220, height=78)
            item_card.pack(side="left", padx=4, pady=2)
            item_card.pack_propagate(False)

            # Tiêu đề món đầy đủ không bị cắt chữ
            ctk.CTkLabel(
                item_card, 
                text=f"{item.icon} {item.name}", 
                font=ctk.CTkFont(family="Inter", size=10, weight="bold"), 
                text_color=COLOR_TEXT_WHITE,
                wraplength=205,
                justify="left",
                anchor="w"
            ).pack(anchor="w", padx=8, pady=(4, 0))

            # Hàng dưới: Đơn giá bên trái & Bộ chọn số lượng (Stepper) bên phải
            bot_row = ctk.CTkFrame(item_card, fg_color="transparent")
            bot_row.pack(fill="x", side="bottom", padx=8, pady=(0, 4))

            lbl_price = ctk.CTkLabel(
                bot_row, 
                text=f"{item.get_formatted_price()}", 
                font=ctk.CTkFont(family="Inter", size=10, weight="bold"), 
                text_color=COLOR_GOLD
            )
            lbl_price.pack(side="left")

            step_box = ctk.CTkFrame(bot_row, fg_color="transparent")
            step_box.pack(side="right")

            btn_sub = ctk.CTkButton(step_box, text="-", width=22, height=20, corner_radius=5, fg_color=COLOR_BG_CARD, hover_color=COLOR_BORDER, font=ctk.CTkFont(size=11, weight="bold"), command=lambda i=item: change_concession_qty(i, -1))
            btn_sub.pack(side="left", padx=2)

            lbl_q = ctk.CTkLabel(step_box, text="0", width=18, font=ctk.CTkFont(size=10, weight="bold"), text_color=COLOR_ACCENT)
            lbl_q.pack(side="left", padx=2)
            concession_lbl_map[item] = lbl_q

            btn_add = ctk.CTkButton(step_box, text="+", width=22, height=20, corner_radius=5, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color="black", font=ctk.CTkFont(size=11, weight="bold"), command=lambda i=item: change_concession_qty(i, 1))
            btn_add.pack(side="left", padx=2)

        # Bottom Bar: Có thêm Máy Tính Tiền Thối (Cash Change Calculator)
        bot = ctk.CTkFrame(dialog, corner_radius=14, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER)
        bot.pack(fill="x", padx=15, pady=(4, 10), ipady=6)

        # Cột trái: Thẻ Chip tóm tắt ghế đã chọn
        left_summary = ctk.CTkFrame(bot, fg_color="transparent")
        left_summary.pack(side="left", padx=10, pady=2)

        lbl_sum_title = ctk.CTkLabel(left_summary, text="Ghế đang chọn:", font=ctk.CTkFont(family="Inter", size=10, weight="bold"), text_color=COLOR_TEXT_MUTED)
        lbl_sum_title.pack(anchor="w", padx=2, pady=(0, 2))

        chips_box = ctk.CTkFrame(left_summary, fg_color="transparent")
        chips_box.pack(anchor="w")

        def get_total_price():
            seats_total = sum(s.calculate_price(st.base_price) for s in selected_seats)
            fnb_total = sum(item.price * qty for item, qty in concession_qty_map.items())
            return seats_total + fnb_total

        # Máy tính tiền thừa cho thu ngân với các nút mệnh giá nhanh
        calc_box = ctk.CTkFrame(bot, fg_color="transparent")
        calc_box.pack(side="left", padx=8)

        calc_top = ctk.CTkFrame(calc_box, fg_color="transparent")
        calc_top.pack(fill="x", pady=(0, 2))

        ctk.CTkLabel(calc_top, text="Khách đưa:", font=ctk.CTkFont(family="Inter", size=11, weight="bold")).pack(side="left", padx=(0, 4))
        txt_cash = ctk.CTkEntry(calc_top, width=100, height=28, corner_radius=6, placeholder_text="0 đ", font=ctk.CTkFont(family="Inter", size=11, weight="bold"))
        txt_cash.pack(side="left", padx=(0, 6))

        lbl_change = ctk.CTkLabel(calc_top, text="Tiền thừa: 0 đ", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color=COLOR_SUCCESS)
        lbl_change.pack(side="left", padx=(0, 4))

        # Dãy phím tiền tệ nhanh 1-chạm cho thu ngân
        denom_box = ctk.CTkFrame(calc_box, fg_color="transparent")
        denom_box.pack(anchor="w")

        def calc_change(*args):
            try:
                g_str = txt_cash.get().strip().replace(".", "").replace(",", "")
                if not g_str:
                    lbl_change.configure(text="Tiền thừa: 0 đ", text_color=COLOR_SUCCESS)
                    return 0, 0
                given = float(g_str)
                total = get_total_price()
                diff = given - total
                if diff >= 0:
                    lbl_change.configure(text=f"Tiền thừa: {diff:,.0f} đ", text_color=COLOR_SUCCESS)
                else:
                    lbl_change.configure(text=f"Thiếu: {abs(diff):,.0f} đ", text_color=COLOR_DANGER)
                return given, max(0, diff)
            except ValueError:
                lbl_change.configure(text="Số không hợp lệ", text_color=COLOR_DANGER)
                return 0, 0

        txt_cash.bind("<KeyRelease>", calc_change)

        def set_cash(amount):
            txt_cash.delete(0, "end")
            txt_cash.insert(0, f"{amount:,.0f}".replace(",", "."))
            calc_change()

        for d_lbl, d_val in [("50k", 50000), ("100k", 100000), ("200k", 200000), ("500k", 500000)]:
            ctk.CTkButton(
                denom_box, text=d_lbl, width=40, height=22, corner_radius=5,
                fg_color=COLOR_BG_LIGHT, hover_color=COLOR_BORDER,
                font=ctk.CTkFont(family="Inter", size=9, weight="bold"),
                command=lambda v=d_val: set_cash(v)
            ).pack(side="left", padx=2)

        btn_exact = ctk.CTkButton(
            denom_box, text="Đúng Tiền", width=68, height=22, corner_radius=5,
            fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color=COLOR_TEXT_WHITE,
            font=ctk.CTkFont(family="Inter", size=9, weight="bold"),
            command=lambda: set_cash(get_total_price())
        )
        btn_exact.pack(side="left", padx=2)

        # Tổng tiền góc phải
        right_pay = ctk.CTkFrame(bot, fg_color="transparent")
        right_pay.pack(side="right", padx=10)

        lbl_total_pos = ctk.CTkLabel(right_pay, text="Tổng: 0 đ", font=ctk.CTkFont(family="Anton", size=16), text_color=COLOR_GOLD)
        lbl_total_pos.pack(side="left", padx=10)

        def update_sum():
            for widget in chips_box.winfo_children():
                widget.destroy()

            if not selected_seats:
                ctk.CTkLabel(chips_box, text="Chưa chọn ghế (click sơ đồ)", font=ctk.CTkFont(family="Inter", size=10, slant="italic"), text_color=COLOR_TEXT_MUTED).pack(side="left")
                lbl_total_pos.configure(text="Tổng: 0 đ")
                btn_finish.configure(state="disabled")
            else:
                total = get_total_price()
                for s in selected_seats[:3]:
                    s_price = s.calculate_price(st.base_price)
                    chip_border = SEAT_AVAILABLE_SWEETBOX if s.is_sweetbox() else (COLOR_GOLD if s.is_vip() else COLOR_ACCENT)
                    chip_icon = "💑" if s.is_sweetbox() else ("👑" if s.is_vip() else "💺")
                    chip = ctk.CTkFrame(chips_box, fg_color=COLOR_BG_LIGHT, corner_radius=6, border_width=1, border_color=chip_border)
                    chip.pack(side="left", padx=2)
                    ctk.CTkLabel(chip, text=f"{chip_icon} {s.seat_code} • {s_price//1000:,.0f}k", font=ctk.CTkFont(family="Inter", size=9, weight="bold"), text_color=COLOR_TEXT_WHITE).pack(padx=5, pady=2)

                if len(selected_seats) > 3:
                    chip_m = ctk.CTkFrame(chips_box, fg_color=COLOR_BG_LIGHT, corner_radius=6, border_width=1, border_color=COLOR_GOLD)
                    chip_m.pack(side="left", padx=2)
                    ctk.CTkLabel(chip_m, text=f"+{len(selected_seats)-3}", font=ctk.CTkFont(family="Inter", size=9, weight="bold"), text_color=COLOR_GOLD).pack(padx=4, pady=2)

                fnb_items = [(i, q) for i, q in concession_qty_map.items() if q > 0]
                if fnb_items:
                    chip_f = ctk.CTkFrame(chips_box, fg_color=COLOR_BG_LIGHT, corner_radius=6, border_width=1, border_color="#f39c12")
                    chip_f.pack(side="left", padx=3)
                    ctk.CTkLabel(chip_f, text=f"🍿 {sum(q for _, q in fnb_items)} Bắp nước", font=ctk.CTkFont(family="Inter", size=9, weight="bold"), text_color="#f39c12").pack(padx=5, pady=2)

                lbl_total_pos.configure(text=f"Tổng: {total:,.0f} đ")
                btn_finish.configure(state="normal")
            calc_change()

        def handle_confirm():
            if not selected_seats:
                return
            cust_name = self.txt_pos_cust_name.get().strip() or "Khách Quầy"
            cust_phone = self.txt_pos_cust_phone.get().strip() or "Tại quầy"
            pay_method = self.combo_pos_payment.get()
            selected_fnb = [(item, qty) for item, qty in concession_qty_map.items() if qty > 0]
            total = get_total_price()
            given_cash, change_cash = calc_change()

            def do_save():
                succ, msg, booking = CinemaService.book_tickets(
                    user_id=self.staff.id,
                    showtime_id=st.id,
                    selected_seats=selected_seats,
                    base_price=st.base_price,
                    payment_method=pay_method,
                    selected_concessions=selected_fnb
                )

                if succ:
                    dialog.destroy()
                    booking.movie_title = self.selected_pos_movie.title
                    booking.room_name = st.room_name
                    booking.show_schedule = f"{st.show_date} lúc {st.show_time}"
                    self._show_pos_thermal_receipt(booking, cust_name, cust_phone, pay_method, total, given_cash, change_cash)
                    show_toast(self.root, f"Thanh toán POS thành công! Mã vé: #{booking.booking_code}", title="Thành Công", toast_type="success")
                    self._load_manage_bookings()
                    self._load_recent_checkin_list()
                else:
                    show_toast(self.root, msg, title="Lỗi POS", toast_type="error")

            if "QR" in pay_method:
                now_str = datetime.now().strftime('%Y%m%d%H%M%S')[-8:]
                temp_code = f"POS{now_str}"
                QRPaymentDialog(
                    parent=dialog,
                    booking_code=temp_code,
                    amount=total,
                    on_success_callback=do_save
                )
            else:
                do_save()

        btn_finish = ctk.CTkButton(
            bot, 
            text="💳 XUẤT VÉ & THU TIỀN", 
            corner_radius=10, 
            height=36,
            fg_color=COLOR_SUCCESS, 
            hover_color="#05b386",
            text_color="#000000",
            font=ctk.CTkFont(weight="bold"),
            state="disabled", 
            cursor="hand2",
            command=handle_confirm
        )
        btn_finish.pack(side="right", padx=15)

    # ================= HÓA ĐƠN VÉ NHIỆT POS 80MM (THERMAL POS RECEIPT) =================
    def _show_pos_thermal_receipt(self, booking, cust_name, cust_phone, pay_method, total, given_cash, change_cash):
        receipt_win = ctk.CTkToplevel(self.root)
        receipt_win.title(f"POS RECEIPT - #{booking.booking_code}")
        receipt_win.configure(fg_color=COLOR_BG_DARK)
        receipt_win.transient(self.root)
        receipt_win.grab_set()
        center_window(receipt_win, 450, 670)

        card = ctk.CTkFrame(receipt_win, corner_radius=20, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER)
        card.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(
            card, 
            text="🌌 CINEVERSE MULTIVERSE CINEMA", 
            font=ctk.CTkFont(family="Anton", size=17), 
            text_color=COLOR_ACCENT
        ).pack(pady=(14, 2))

        ctk.CTkLabel(
            card, 
            text="BIÊN NHẬN VÉ POS 80MM / QUẦY THU NGÂN", 
            font=ctk.CTkFont(family="Inter", size=10, weight="bold"), 
            text_color=COLOR_GOLD
        ).pack(pady=(0, 4))

        stamp = ctk.CTkFrame(card, corner_radius=8, fg_color="#0b291b", border_width=1, border_color=COLOR_SUCCESS)
        stamp.pack(pady=(2, 4))
        ctk.CTkLabel(stamp, text="✓ GIAO DỊCH THÀNH CÔNG • VÉ HỢP LỆ", font=ctk.CTkFont(family="Inter", size=9, weight="bold"), text_color=COLOR_SUCCESS).pack(padx=12, pady=2)

        ctk.CTkLabel(card, text="MÃ GIAO DỊCH POS", font=ctk.CTkFont(family="Inter", size=9), text_color=COLOR_TEXT_MUTED).pack(pady=(2, 0))
        ctk.CTkLabel(card, text=booking.booking_code, font=ctk.CTkFont(family="Consolas", size=20, weight="bold"), text_color=COLOR_GOLD).pack(pady=(1, 4))

        cut1 = ctk.CTkFrame(card, fg_color="transparent")
        cut1.pack(fill="x", padx=15, pady=(2, 4))
        ctk.CTkLabel(cut1, text="✂️  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -", font=ctk.CTkFont(family="Consolas", size=9), text_color=COLOR_BORDER).pack()

        info_box = ctk.CTkFrame(card, corner_radius=10, fg_color=COLOR_BG_LIGHT, border_width=1, border_color=COLOR_BORDER)
        info_box.pack(fill="x", padx=16, pady=4, ipady=4)

        rows = [
            ("Thu ngân:", self.staff.fullname),
            ("Khách hàng:", f"{cust_name} ({cust_phone})"),
            ("Phim:", booking.movie_title),
            ("Phòng chiếu:", booking.room_name),
            ("Suất chiếu:", booking.show_schedule),
            ("Ghế đặt:", booking.seats_str),
        ]
        if getattr(booking, "concessions_str", None):
            rows.append(("Bắp nước F&B:", booking.concessions_str))
        rows.extend([
            ("Thanh toán:", pay_method),
            ("Tổng cộng:", f"{total:,.0f} VNĐ"),
        ])
        if given_cash > 0:
            rows.append(("Tiền khách đưa:", f"{given_cash:,.0f} VNĐ"))
            rows.append(("Tiền thừa trả lại:", f"{change_cash:,.0f} VNĐ"))

        for l, v in rows:
            f = ctk.CTkFrame(info_box, fg_color="transparent")
            f.pack(fill="x", padx=12, pady=1)
            ctk.CTkLabel(f, text=l, font=ctk.CTkFont(family="Inter", size=10, weight="bold"), text_color=COLOR_TEXT).pack(side="left")
            c = COLOR_GOLD if "Tổng" in l else (COLOR_SUCCESS if ("thừa" in l or "thối" in l) else COLOR_TEXT_WHITE)
            ctk.CTkLabel(f, text=v, font=ctk.CTkFont(family="Inter", size=10, weight="bold"), text_color=c).pack(side="right")

        cut2 = ctk.CTkFrame(card, fg_color="transparent")
        cut2.pack(fill="x", padx=15, pady=(4, 2))
        ctk.CTkLabel(cut2, text="✂️  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -", font=ctk.CTkFont(family="Consolas", size=9), text_color=COLOR_BORDER).pack()

        barcode_canvas = tk.Canvas(card, height=30, width=280, bg=COLOR_BG_CARD, highlightthickness=0, bd=0)
        barcode_canvas.pack(pady=(2, 2))
        seed = hash(booking.booking_code)
        x = 10
        while x < 270:
            bar_w = 1 if (seed & 1) else (3 if (seed & 2) else 2)
            gap = 2 if (seed & 4) else 1
            color = COLOR_TEXT_WHITE if (seed & 8) else COLOR_ACCENT
            barcode_canvas.create_rectangle(x, 2, x + bar_w, 28, fill=color, outline="")
            x += bar_w + gap
            seed = (seed >> 1) | ((seed & 1) << 30)

        ctk.CTkLabel(card, text=f"*CV-{booking.booking_code}*", font=ctk.CTkFont(family="Consolas", size=9), text_color=COLOR_TEXT_MUTED).pack(pady=(0, 8))

        btn_f = ctk.CTkFrame(card, fg_color="transparent")
        btn_f.pack(fill="x", padx=16, pady=(0, 10))

        def export_pos_txt():
            try:
                fname = f"POS_Receipt_{booking.booking_code}.txt"
                fnb_l = f"BAP NUOC:     {booking.concessions_str}\n" if getattr(booking, "concessions_str", None) else ""
                cash_l = f"TIEN KHACH:   {given_cash:,.0f} VND\nTIEN THOI:    {change_cash:,.0f} VND\n" if given_cash > 0 else ""
                content = f"""========================================
       CINEVERSE MULTIVERSE CINEMA
       QUAY VE POS - HOA DON BAN LE
========================================
MA VE:        {booking.booking_code}
THU NGAN:     {self.staff.fullname}
KHACH HANG:   {cust_name} ({cust_phone})
PHIM:         {booking.movie_title}
PHONG CHIEU:  {booking.room_name}
SUAT CHIEU:   {booking.show_schedule}
GHE NGOI:     {booking.seats_str}
{fnb_l}THANH TOAN:   {pay_method}
TONG TIEN:    {total:,.0f} VND
{cash_l}========================================
Cam on quy khach! Chuc xem phim vui ve!
========================================"""
                with open(fname, "w", encoding="utf-8") as out_f:
                    out_f.write(content)
                show_toast(self.root, f"Đã xuất hóa đơn POS: {os.path.basename(fname)}", title="Xuất Vé", toast_type="success")
            except Exception as ex:
                show_toast(self.root, f"Không thể xuất file: {str(ex)}", title="Lỗi Xuất File", toast_type="error")

        btn_save = ctk.CTkButton(
            btn_f, text="🖨️ Xuất File Vé (.txt)", font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            corner_radius=10, height=36, fg_color="#2a9d8f", hover_color="#21867a", cursor="hand2", command=export_pos_txt
        )
        btn_save.pack(side="left", fill="x", expand=True, padx=(0, 4))

        btn_close = ctk.CTkButton(
            btn_f, text="Đóng / Hoàn Tất", font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            corner_radius=10, height=36, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color=COLOR_TEXT_WHITE,
            cursor="hand2", command=receipt_win.destroy
        )
        btn_close.pack(side="right", fill="x", expand=True, padx=(4, 0))

    # ================= TAB 2: SOÁT VÉ & CHECK-IN CỬA RẠP =================
    def _build_checkin_tab(self):
        container = ctk.CTkFrame(self.tab_checkin, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=10)

        # Top Card: Ô Quét / Nhập Mã Vé
        scan_card = ctk.CTkFrame(container, corner_radius=16, fg_color=COLOR_BG_LIGHT, border_width=1, border_color=COLOR_BORDER)
        scan_card.pack(fill="x", pady=(0, 15), ipady=8)

        ctk.CTkLabel(
            scan_card, 
            text="🎫 QUÉT HOẶC NHẬP MÃ VÉ ĐỂ SOÁT CỬA:", 
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color=COLOR_GOLD
        ).pack(anchor="w", padx=20, pady=(10, 8))

        input_box = ctk.CTkFrame(scan_card, fg_color="transparent")
        input_box.pack(fill="x", padx=20, pady=(0, 10))

        self.txt_checkin_code = ctk.CTkEntry(
            input_box, 
            corner_radius=12, 
            height=44, 
            fg_color=COLOR_BG_CARD, 
            border_color=COLOR_ACCENT,
            font=ctk.CTkFont(size=15, weight="bold"),
            placeholder_text="Nhập mã vé (Ví dụ: VE20260908...)"
        )
        self.txt_checkin_code.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.txt_checkin_code.bind("<Return>", lambda e: self._handle_check_in())

        btn_checkin = ctk.CTkButton(
            input_box, 
            text="🚀 KIỂM TRA & SOÁT VÉ", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            corner_radius=12, 
            height=44, 
            width=200,
            fg_color=COLOR_ACCENT, 
            hover_color=COLOR_ACCENT_HOVER,
            text_color=COLOR_TEXT_WHITE,
            cursor="hand2", 
            command=self._handle_check_in
        )
        btn_checkin.pack(side="right")

        # Result Card: Hiển thị kết quả kiểm tra trực quan
        self.result_card = ctk.CTkFrame(container, corner_radius=16, fg_color=COLOR_BG_CARD, border_width=2, border_color=COLOR_BORDER)
        self.result_card.pack(fill="x", pady=(0, 15), ipady=12)

        self.lbl_result_badge = ctk.CTkLabel(
            self.result_card, 
            text="SẴN SÀNG SOÁT VÉ - VUI LÒNG QUÉT MÃ", 
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        )
        self.lbl_result_badge.pack(pady=(12, 6))

        self.lbl_result_details = ctk.CTkLabel(
            self.result_card, 
            text="Thông tin vé sau khi kiểm tra sẽ hiển thị tại đây...", 
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=COLOR_TEXT
        )
        self.lbl_result_details.pack(pady=(0, 12))

        # Bottom: Danh sách vé vừa đặt gần đây để tiện test/soát nhanh
        ctk.CTkLabel(
            container, 
            text="⚡ DANH SÁCH VÉ GẦN ĐÂY (Click đúp để soát nhanh):", 
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(anchor="w", pady=(5, 4))

        tree_f = tk.Frame(container, bg=COLOR_BG_CARD)
        tree_f.pack(fill="both", expand=True)

        cols = ("code", "movie", "room", "time", "seats", "status")
        self.tree_quick_checkin = ttk.Treeview(tree_f, columns=cols, show="headings", style="Dark.Treeview", height=6, selectmode="browse")
        self.tree_quick_checkin.heading("code", text="Mã Vé")
        self.tree_quick_checkin.heading("movie", text="Phim")
        self.tree_quick_checkin.heading("room", text="Phòng")
        self.tree_quick_checkin.heading("time", text="Giờ Chiếu")
        self.tree_quick_checkin.heading("seats", text="Ghế")
        self.tree_quick_checkin.heading("status", text="Trạng Thái")

        self.tree_quick_checkin.column("code", width=140, anchor="center")
        self.tree_quick_checkin.column("movie", width=220, anchor="w")
        self.tree_quick_checkin.column("room", width=160, anchor="w")
        self.tree_quick_checkin.column("time", width=120, anchor="center")
        self.tree_quick_checkin.column("seats", width=80, anchor="center")
        self.tree_quick_checkin.column("status", width=110, anchor="center")

        scroll = ttk.Scrollbar(tree_f, orient="vertical", command=self.tree_quick_checkin.yview)
        self.tree_quick_checkin.configure(yscrollcommand=scroll.set)
        self.tree_quick_checkin.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree_quick_checkin.bind("<Double-1>", self._on_quick_ticket_double_click)

        self._load_recent_checkin_list()

    def _load_recent_checkin_list(self):
        for row in self.tree_quick_checkin.get_children():
            self.tree_quick_checkin.delete(row)

        bookings = CinemaService.get_all_bookings()
        for b in bookings[:15]:
            status_txt = "✅ Đã vào rạp" if b['status'] == 'Checked-in' else ("❌ Đã hủy" if b['status'] == 'Cancelled' else "Chờ vào rạp")
            self.tree_quick_checkin.insert("", "end", values=(
                b['booking_code'], b['movie_title'], b['room_name'], b['show_time'], b['seats_str'], status_txt
            ))

    def _on_quick_ticket_double_click(self, event):
        selected = self.tree_quick_checkin.focus()
        if not selected:
            return
        code = self.tree_quick_checkin.item(selected, "values")[0]
        self.txt_checkin_code.delete(0, "end")
        self.txt_checkin_code.insert(0, code)
        self._handle_check_in()

    def _handle_check_in(self):
        code = self.txt_checkin_code.get().strip()
        if not code:
            show_toast(self.root, "Vui lòng nhập mã vé cần soát!", title="Thông Báo", toast_type="warning")
            return

        succ, msg, info = CinemaService.check_in_ticket(code)
        if succ:
            self.result_card.configure(border_color=COLOR_SUCCESS, fg_color="#062e24")
            self.lbl_result_badge.configure(
                text="✓ SOÁT VÉ THÀNH CÔNG • MỜI VÀO PHÒNG CHIẾU", 
                font=ctk.CTkFont(family="Anton", size=18),
                text_color=COLOR_SUCCESS
            )
            fnb_warning = ""
            if info.get('concessions_str'):
                fnb_warning = f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🍿 LƯU Ý BẮP NƯỚC: {info['concessions_str']}\n👉 NHẮC KHÁCH NHẬN COMBO TẠI QUẦY BAR F&B!"

            details = (
                f"🎬 PHIM: {info['movie_title'].upper()}\n"
                f"🏛️ PHÒNG: {info['room_name']}   |   🕒 GIỜ CHIẾU: {info['show_time']}\n"
                f"💺 GHẾ ĐÃ ĐẶT: {info['seats_str']}\n"
                f"👤 KHÁCH HÀNG: {info['customer_name']} (SĐT: {info['customer_phone'] or 'N/A'})\n"
                f"💰 THANH TOÁN: {info['total_amount']:,.0f} VNĐ ({info['payment_method']})"
                f"{fnb_warning}"
            )
            self.lbl_result_details.configure(
                text=details, 
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                text_color=COLOR_TEXT_WHITE
            )
        else:
            if info and info.get('status') == 'Checked-in':
                self.result_card.configure(border_color=COLOR_GOLD, fg_color="#332600")
                self.lbl_result_badge.configure(
                    text="⚠️ CẢNH BÁO: VÉ ĐÃ ĐƯỢC SOÁT VÀO RẠP TRƯỚC ĐÓ!", 
                    font=ctk.CTkFont(family="Anton", size=18),
                    text_color=COLOR_GOLD
                )
            else:
                self.result_card.configure(border_color=COLOR_DANGER, fg_color="#330b0b")
                self.lbl_result_badge.configure(
                    text="❌ TỪ CHỐI: VÉ KHÔNG HỢP LỆ HOẶC ĐÃ BỊ HỦY!", 
                    font=ctk.CTkFont(family="Anton", size=18),
                    text_color=COLOR_DANGER
                )

            self.lbl_result_details.configure(
                text=msg, 
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                text_color=COLOR_TEXT
            )

        self._load_recent_checkin_list()
        self._load_manage_bookings()

    # ================= TAB 3: TRA CỨU & QUẢN LÝ VÉ =================
    def _build_manage_tab(self):
        top_bar = ctk.CTkFrame(self.tab_manage, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=(10, 8))

        ctk.CTkLabel(top_bar, text="🔍 Tra cứu vé:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(5, 6))

        self.txt_search_b = ctk.CTkEntry(
            top_bar, 
            placeholder_text="Nhập mã vé, tên khách, số điện thoại...", 
            corner_radius=8, 
            height=32, 
            width=260, 
            fg_color=COLOR_BG_LIGHT, 
            border_color=COLOR_BORDER
        )
        self.txt_search_b.pack(side="left", padx=(0, 6))
        self.txt_search_b.bind("<Return>", lambda e: self._load_manage_bookings())

        btn_s = ctk.CTkButton(top_bar, text="Tìm kiếm", corner_radius=8, height=32, width=75, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, cursor="hand2", command=self._load_manage_bookings)
        btn_s.pack(side="left", padx=3)

        btn_ref = ctk.CTkButton(top_bar, text="🔄 Làm mới", corner_radius=8, height=32, width=75, fg_color=COLOR_BG_CARD, hover_color=COLOR_BORDER, cursor="hand2", command=self._load_manage_bookings)
        btn_ref.pack(side="left", padx=3)

        # Status Filter Pills
        self.manage_status_filter = "ALL"
        self.filter_buttons = {}

        filter_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        filter_box.pack(side="right", padx=5)

        filters = [
            ("ALL", "Tất Cả", COLOR_ACCENT, "#000000"),
            ("WAITING", "⏳ Chờ Vào Rạp", "#f39c12", "#000000"),
            ("CHECKED_IN", "✅ Đã Vào Rạp", COLOR_SUCCESS, "#000000"),
            ("CANCELLED", "❌ Đã Hủy", COLOR_DANGER, "#ffffff"),
        ]

        for code, text, active_bg, active_fg in filters:
            btn = ctk.CTkButton(
                filter_box,
                text=text,
                corner_radius=8,
                height=32,
                font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                cursor="hand2",
                command=lambda c=code: self._set_manage_filter(c)
            )
            btn.pack(side="left", padx=3)
            self.filter_buttons[code] = (btn, text, active_bg, active_fg)

        self._update_filter_button_styles()

        # Table Card
        table_card = ctk.CTkFrame(self.tab_manage, corner_radius=14, fg_color=COLOR_BG_LIGHT, border_width=1, border_color=COLOR_BORDER)
        table_card.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cols = ("id", "code", "cust", "phone", "movie", "room", "time", "seats", "concessions", "total", "status")
        self.tree_manage = ttk.Treeview(table_card, columns=cols, show="headings", style="Dark.Treeview", selectmode="browse")
        self.tree_manage.heading("id", text="ID")
        self.tree_manage.heading("code", text="Mã Vé")
        self.tree_manage.heading("cust", text="Khách Hàng")
        self.tree_manage.heading("phone", text="SĐT")
        self.tree_manage.heading("movie", text="Phim")
        self.tree_manage.heading("room", text="Phòng Chiếu")
        self.tree_manage.heading("time", text="Giờ Chiếu")
        self.tree_manage.heading("seats", text="Ghế")
        self.tree_manage.heading("concessions", text="Bắp Nước / Combo")
        self.tree_manage.heading("total", text="Tổng Tiền")
        self.tree_manage.heading("status", text="Trạng Thái")

        self.tree_manage.column("id", width=35, anchor="center")
        self.tree_manage.column("code", width=110, anchor="center")
        self.tree_manage.column("cust", width=120, anchor="w")
        self.tree_manage.column("phone", width=90, anchor="center")
        self.tree_manage.column("movie", width=150, anchor="w")
        self.tree_manage.column("room", width=110, anchor="w")
        self.tree_manage.column("time", width=100, anchor="center")
        self.tree_manage.column("seats", width=75, anchor="center")
        self.tree_manage.column("concessions", width=140, anchor="w")
        self.tree_manage.column("total", width=85, anchor="e")
        self.tree_manage.column("status", width=120, anchor="center")

        scroll = ttk.Scrollbar(table_card, orient="vertical", command=self.tree_manage.yview)
        self.tree_manage.configure(yscrollcommand=scroll.set)
        self.tree_manage.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scroll.pack(side="right", fill="y", pady=10)

        # Action Buttons
        act_box = ctk.CTkFrame(self.tab_manage, fg_color="transparent")
        act_box.pack(fill="x", padx=10, pady=(0, 5))

        btn_view_receipt = ctk.CTkButton(
            act_box, text="🧾 Xem Chi Tiết & In Lại Vé POS", corner_radius=10, height=34,
            fg_color="#2980b9", hover_color="#1f618d", cursor="hand2",
            command=self._handle_view_ticket
        )
        btn_view_receipt.pack(side="right", padx=5)

        btn_cancel = ctk.CTkButton(
            act_box, text="🚫 Hủy Vé (Hoàn tiền)", corner_radius=10, height=34,
            fg_color=COLOR_DANGER, hover_color="#c92a2a", cursor="hand2",
            command=self._handle_cancel_booking
        )
        btn_cancel.pack(side="right", padx=5)

        self._load_manage_bookings()

    def _set_manage_filter(self, code: str):
        self.manage_status_filter = code
        self._update_filter_button_styles()
        self._load_manage_bookings()

    def _update_filter_button_styles(self):
        for code, (btn, text, active_bg, active_fg) in self.filter_buttons.items():
            if code == self.manage_status_filter:
                btn.configure(
                    fg_color=active_bg,
                    text_color=active_fg,
                    hover_color=active_bg,
                    border_width=0
                )
            else:
                btn.configure(
                    fg_color=COLOR_BG_CARD,
                    text_color=COLOR_TEXT_MUTED,
                    hover_color=COLOR_BORDER,
                    border_width=1,
                    border_color=COLOR_BORDER
                )

    def _load_manage_bookings(self):
        for row in self.tree_manage.get_children():
            self.tree_manage.delete(row)

        kw = self.txt_search_b.get().strip() if hasattr(self, 'txt_search_b') else ""
        bookings = CinemaService.search_bookings(kw) if kw else CinemaService.get_all_bookings()

        status_filter = getattr(self, "manage_status_filter", "ALL")
        for b in bookings:
            raw_stt = b.get('status', 'Confirmed')
            if status_filter == "WAITING" and raw_stt in ('Checked-in', 'Cancelled'):
                continue
            elif status_filter == "CHECKED_IN" and raw_stt != 'Checked-in':
                continue
            elif status_filter == "CANCELLED" and raw_stt != 'Cancelled':
                continue

            display_stt = "● ĐÃ CHECK-IN" if raw_stt == 'Checked-in' else ("● ĐÃ HỦY" if raw_stt == 'Cancelled' else "● ĐÃ XÁC NHẬN")
            self.tree_manage.insert("", "end", values=(
                b['id'], b['booking_code'], b['customer_name'], b['customer_phone'] or "N/A",
                b['movie_title'], b['room_name'], b['show_time'], b['seats_str'],
                b.get('concessions_str') or "Không có",
                f"{b['total_amount']:,.0f} đ", display_stt
            ))

    def _handle_view_ticket(self):
        selected = self.tree_manage.focus()
        if not selected:
            show_toast(self.root, "Vui lòng chọn 1 đơn vé từ bảng để in lại!", title="Thông Báo", toast_type="warning")
            return

        values = self.tree_manage.item(selected, "values")
        b_code = values[1]

        bookings = CinemaService.get_all_bookings()
        target = next((b for b in bookings if b['booking_code'] == b_code), None)
        if not target:
            show_toast(self.root, "Không tìm thấy thông tin đơn vé!", title="Lỗi", toast_type="error")
            return

        receipt_win = ctk.CTkToplevel(self.root)
        receipt_win.title(f"HÓA ĐƠN POS 80MM - #{target['booking_code']}")
        receipt_win.configure(fg_color=COLOR_BG_DARK)
        receipt_win.transient(self.root)
        receipt_win.grab_set()
        center_window(receipt_win, 420, 680)

        card = ctk.CTkFrame(receipt_win, corner_radius=18, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER)
        card.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(
            card, 
            text="🌌 CINEVERSE MULTIVERSE CINEMA", 
            font=ctk.CTkFont(family="Anton", size=17), 
            text_color=COLOR_ACCENT
        ).pack(pady=(14, 2))

        ctk.CTkLabel(
            card, 
            text="BIÊN NHẬN VÉ POS 80MM / QUẦY THU NGÂN", 
            font=ctk.CTkFont(family="Inter", size=10, weight="bold"), 
            text_color=COLOR_GOLD
        ).pack(pady=(0, 4))

        # Status stamp
        stt = target.get('status', 'Confirmed')
        if stt == 'Checked-in':
            stamp_text = "✓ VÉ ĐÃ CHECK-IN SOÁT CỬA VÀO RẠP"
            stamp_bg = "#332600"
            stamp_c = COLOR_GOLD
        elif stt == 'Cancelled':
            stamp_text = "❌ VÉ ĐÃ BỊ HỦY / HOÀN TIỀN"
            stamp_bg = "#330b0b"
            stamp_c = COLOR_DANGER
        else:
            stamp_text = "✓ VÉ HỢP LỆ • SẴN SÀNG VÀO RẠP"
            stamp_bg = "#0b291b"
            stamp_c = COLOR_SUCCESS

        stamp = ctk.CTkFrame(card, corner_radius=8, fg_color=stamp_bg, border_width=1, border_color=stamp_c)
        stamp.pack(pady=(2, 4))
        ctk.CTkLabel(stamp, text=stamp_text, font=ctk.CTkFont(family="Inter", size=9, weight="bold"), text_color=stamp_c).pack(padx=12, pady=2)

        ctk.CTkLabel(card, text="MÃ VÉ:", font=ctk.CTkFont(family="Inter", size=9), text_color=COLOR_TEXT_MUTED).pack(pady=(2, 0))
        ctk.CTkLabel(card, text=target['booking_code'], font=ctk.CTkFont(family="Consolas", size=20, weight="bold"), text_color=COLOR_GOLD).pack(pady=(1, 4))

        cut1 = ctk.CTkFrame(card, fg_color="transparent")
        cut1.pack(fill="x", padx=15, pady=(2, 4))
        ctk.CTkLabel(cut1, text="✂️  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -", font=ctk.CTkFont(family="Consolas", size=9), text_color=COLOR_BORDER).pack()

        info_rows = [
            ("Thu ngân:", self.staff.fullname),
            ("Khách hàng:", f"{target['customer_name']} ({target['customer_phone'] or 'N/A'})"),
            ("Phim:", target['movie_title']),
            ("Phòng chiếu:", target['room_name']),
            ("Suất chiếu:", target['show_time']),
            ("Ghế đặt:", target['seats_str']),
        ]
        if target.get('concessions_str'):
            info_rows.append(("Bắp nước kèm:", target['concessions_str']))

        stt_display = "✓ ĐÃ XÁC NHẬN" if target['status'] == 'Confirmed' else ("✓ ĐÃ SOÁT VÉ" if target['status'] == 'Checked-in' else "❌ ĐÃ HỦY")
        info_rows.extend([
            ("Thanh toán:", target.get('payment_method', 'Tại quầy POS')),
            ("Tổng tiền:", f"{target['total_amount']:,.0f} VNĐ"),
            ("Trạng thái:", stt_display)
        ])

        info_box = ctk.CTkFrame(card, corner_radius=10, fg_color=COLOR_BG_LIGHT, border_width=1, border_color=COLOR_BORDER)
        info_box.pack(fill="x", padx=16, pady=4, ipady=4)

        for label, val in info_rows:
            f = ctk.CTkFrame(info_box, fg_color="transparent")
            f.pack(fill="x", padx=12, pady=1)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(family="Inter", size=10, weight="bold"), text_color=COLOR_TEXT).pack(side="left")
            color = COLOR_GOLD if "Tổng" in label else (COLOR_SUCCESS if "Trạng" in label else COLOR_TEXT_WHITE)
            ctk.CTkLabel(f, text=val, font=ctk.CTkFont(family="Inter", size=10, weight="bold"), text_color=color).pack(side="right")

        cut2 = ctk.CTkFrame(card, fg_color="transparent")
        cut2.pack(fill="x", padx=15, pady=(4, 2))
        ctk.CTkLabel(cut2, text="✂️  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -", font=ctk.CTkFont(family="Consolas", size=9), text_color=COLOR_BORDER).pack()

        barcode_canvas = tk.Canvas(card, height=30, width=280, bg=COLOR_BG_CARD, highlightthickness=0, bd=0)
        barcode_canvas.pack(pady=(2, 2))
        seed = hash(target['booking_code'])
        x = 10
        while x < 270:
            bar_w = 1 if (seed & 1) else (3 if (seed & 2) else 2)
            gap = 2 if (seed & 4) else 1
            b_color = COLOR_TEXT_WHITE if (seed & 8) else COLOR_ACCENT
            barcode_canvas.create_rectangle(x, 2, x + bar_w, 28, fill=b_color, outline="")
            x += bar_w + gap
            seed = (seed >> 1) | ((seed & 1) << 30)

        ctk.CTkLabel(card, text=f"*CV-{target['booking_code']}*", font=ctk.CTkFont(family="Consolas", size=9), text_color=COLOR_TEXT_MUTED).pack(pady=(0, 8))

        def export_file():
            try:
                fname = f"Ve_POS_{target['booking_code']}.txt"
                fnb_line = f"BAP NUOC:     {target['concessions_str']}\n" if target.get('concessions_str') else ""
                content = f"""========================================
       CINEVERSE MULTIVERSE CINEMA
       QUAY VE POS - HOA DON BAN LE
========================================
MA VE:        {target['booking_code']}
THU NGAN:     {self.staff.fullname}
KHACH HANG:   {target['customer_name']} ({target['customer_phone'] or 'N/A'})
PHIM:         {target['movie_title']}
PHONG CHIEU:  {target['room_name']}
SUAT CHIEU:   {target['show_time']}
GHE NGOI:     {target['seats_str']}
{fnb_line}TONG TIEN:    {target['total_amount']:,.0f} VND
TRANG THAI:   {target['status']}
========================================
Cam on quy khach da lua chon CINEVERSE!
========================================"""
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(content)
                show_toast(self.root, f"Đã xuất hóa đơn POS: {os.path.basename(fname)}", title="Thành Công", toast_type="success")
            except Exception as e:
                show_toast(self.root, f"Không thể xuất file: {str(e)}", title="Lỗi", toast_type="error")

        btn_bar = ctk.CTkFrame(card, fg_color="transparent")
        btn_bar.pack(fill="x", padx=16, pady=(0, 10))

        btn_save = ctk.CTkButton(btn_bar, text="🖨️ Xuất File Vé (.txt)", corner_radius=10, height=36, fg_color="#2a9d8f", hover_color="#21867a", cursor="hand2", command=export_file)
        btn_save.pack(side="left", fill="x", expand=True, padx=(0, 4))

        btn_cls = ctk.CTkButton(btn_bar, text="Đóng", corner_radius=10, height=36, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color=COLOR_TEXT_WHITE, cursor="hand2", command=receipt_win.destroy)
        btn_cls.pack(side="right", fill="x", expand=True, padx=(4, 0))

    def _handle_cancel_booking(self):
        selected = self.tree_manage.focus()
        if not selected:
            show_toast(self.root, "Vui lòng chọn 1 đơn vé từ bảng để hủy!", title="Thông Báo", toast_type="warning")
            return

        values = self.tree_manage.item(selected, "values")
        b_id = int(values[0])
        code = values[1]

        confirm = messagebox.askyesno("Xác nhận hủy", f"Bạn có chắc chắn muốn hủy đơn vé #{code} và hoàn tiền?")
        if confirm:
            succ, msg = CinemaService.cancel_booking(b_id)
            if succ:
                show_toast(self.root, msg, title="Hủy Vé Thành Công", toast_type="success")
                self._load_manage_bookings()
                self._load_recent_checkin_list()
            else:
                show_toast(self.root, msg, title="Lỗi Hủy Vé", toast_type="error")

