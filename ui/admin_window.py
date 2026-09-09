"""
Module: ui/admin_window.py
Mô tả: Giao diện Quản trị viên CINEVERSE nâng cấp Bo Góc Hiện Đại bằng CustomTkinter.
"""

import os
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from services import CinemaService, AuthService
from models import Admin, Concession
from ui.styles import (
    COLOR_BG_DARK, COLOR_BG_CARD, COLOR_BG_LIGHT, COLOR_ACCENT, COLOR_ACCENT_HOVER,
    COLOR_GOLD, COLOR_GOLD_HOVER, COLOR_TEXT, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED,
    COLOR_SUCCESS, COLOR_DANGER, COLOR_BORDER,
    setup_styles, center_window
)

class AdminWindow:
    """Giao diện Quản trị viên CINEVERSE Bo Góc Hiện Đại"""
    def __init__(self, root, admin: Admin, on_logout):
        self.root = root
        self.admin = admin
        self.on_logout = on_logout

        self.root.title(f"CINEVERSE - Trung Tâm Điều Hành: {admin.fullname}")
        self.root.configure(fg_color=COLOR_BG_DARK)
        setup_styles()
        center_window(self.root, 1180, 740)

        self._build_ui()

    def _build_ui(self):
        # Header bar Bo Tròn
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
            text="🌌 CINEVERSE - TRUNG TÂM QUẢN TRỊ", 
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color=COLOR_ACCENT
        )
        lbl_brand.pack(side="left")

        # Right nav
        right_nav = ctk.CTkFrame(header, fg_color="transparent")
        right_nav.pack(side="right", padx=15, pady=12)

        lbl_user = ctk.CTkLabel(
            right_nav, 
            text=f"👑 Admin: {self.admin.fullname}", 
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

        # Tabview Bo Góc
        self.tabview = ctk.CTkTabview(
            self.root, 
            corner_radius=18,
            fg_color=COLOR_BG_CARD,
            segmented_button_selected_color=COLOR_ACCENT,
            segmented_button_selected_hover_color=COLOR_ACCENT_HOVER,
            segmented_button_unselected_color=COLOR_BG_LIGHT
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.tab_stats = self.tabview.add("  📊 DOANH THU  ")
        self.tab_movies = self.tabview.add("  🎬 PHIM  ")
        self.tab_showtimes = self.tabview.add("  🕒 LỊCH CHIẾU  ")
        self.tab_concessions = self.tabview.add("  🍿 BẮP NƯỚC & COMBO  ")
        self.tab_bookings = self.tabview.add("  📋 ĐẶT VÉ  ")
        self.tab_users = self.tabview.add("  👥 TÀI KHOẢN  ")

        self._build_stats_tab()
        self._build_movies_tab()
        self._build_showtimes_tab()
        self._build_concessions_tab()
        self._build_bookings_tab()
        self._build_users_tab()

    # ================= TAB 1: THỐNG KÊ DOANH THU (BENTO GRID DASHBOARD) =================
    def _build_stats_tab(self):
        # 1. BENTO ROW 1: 4 Thẻ KPI Bo Góc Đẳng Cấp
        bento_top = ctk.CTkFrame(self.tab_stats, fg_color="transparent")
        bento_top.pack(fill="x", pady=(2, 10))

        self.card_revenue, self.sub_revenue = self._create_bento_kpi_card(
            bento_top, "💰 TỔNG DOANH THU TOÀN RẠP", "0 đ", "✦ Vé: 0 đ • F&B: 0 đ", COLOR_GOLD
        )
        self.card_tickets, self.sub_tickets = self._create_bento_kpi_card(
            bento_top, "🎟️ TỔNG VÉ ĐÃ BÁN", "0 vé", "✦ Tỉ lệ lấp đầy rạp ước tính: ~0%", COLOR_SUCCESS
        )
        self.card_fnb, self.sub_fnb = self._create_bento_kpi_card(
            bento_top, "🍿 DOANH SỐ BẮP NƯỚC (F&B)", "0 đ", "✦ Đóng góp: ~0% tổng doanh thu", "#f39c12"
        )
        self.card_users, self.sub_users = self._create_bento_kpi_card(
            bento_top, "👥 TÀI KHOẢN HỆ THỐNG", "0 tài khoản", "✦ Quản trị • Nhân viên • Khách", "#9d4edd"
        )

        # 2. BENTO ROW 2: Chia 2 Khối Bento (Trái: Biểu Đồ Canvas 60%, Phải: Top F&B 40%)
        bento_mid = ctk.CTkFrame(self.tab_stats, fg_color="transparent")
        bento_mid.pack(fill="x", pady=(0, 10))

        # Khối Bento Trái: Biểu Đồ Cột Doanh Thu Phim Bằng Tkinter Canvas
        self.bento_chart_card = ctk.CTkFrame(bento_mid, corner_radius=16, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER)
        self.bento_chart_card.pack(side="left", fill="both", expand=True, padx=(0, 6))

        chart_head = ctk.CTkFrame(self.bento_chart_card, fg_color="transparent")
        chart_head.pack(fill="x", padx=15, pady=(10, 4))
        ctk.CTkLabel(
            chart_head, 
            text="📊 BIỂU ĐỒ DOANH THU THEO PHIM (REVENUE ANALYTICS)", 
            font=ctk.CTkFont(family="Anton", size=14), 
            text_color=COLOR_GOLD
        ).pack(side="left")

        btn_refresh = ctk.CTkButton(
            chart_head, 
            text="🔄 Làm Mới", 
            font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
            corner_radius=8, 
            height=26, 
            width=75,
            fg_color=COLOR_BG_LIGHT, 
            hover_color=COLOR_BORDER,
            cursor="hand2", 
            command=self._load_statistics
        )
        btn_refresh.pack(side="right")

        self.chart_canvas = tk.Canvas(self.bento_chart_card, height=140, bg=COLOR_BG_CARD, highlightthickness=0, bd=0)
        self.chart_canvas.pack(fill="x", padx=15, pady=(0, 8))
        self.chart_canvas.bind("<Configure>", lambda e: self._draw_revenue_chart())

        # Khối Bento Phải: Top Bắp Nước F&B Bán Chạy Nhất
        self.bento_fnb_card = ctk.CTkFrame(bento_mid, corner_radius=16, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER, width=420)
        self.bento_fnb_card.pack(side="right", fill="both", padx=(6, 0))
        self.bento_fnb_card.pack_propagate(False)

        fnb_head = ctk.CTkFrame(self.bento_fnb_card, fg_color="transparent")
        fnb_head.pack(fill="x", padx=15, pady=(10, 4))
        ctk.CTkLabel(
            fnb_head, 
            text="🍿 TOP BẮP NƯỚC & COMBO BÁN CHẠY", 
            font=ctk.CTkFont(family="Anton", size=14), 
            text_color=COLOR_GOLD
        ).pack(side="left")

        self.fnb_list_container = ctk.CTkFrame(self.bento_fnb_card, fg_color="transparent")
        self.fnb_list_container.pack(fill="both", expand=True, padx=15, pady=(0, 8))

        # 3. BENTO ROW 3: Bảng Doanh Thu Chi Tiết Theo Phim
        table_card = ctk.CTkFrame(self.tab_stats, corner_radius=16, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER)
        table_card.pack(fill="both", expand=True, pady=(0, 4))

        ctk.CTkLabel(
            table_card, 
            text="📈 BẢNG TỔNG HỢP CHI TIẾT DOANH THU & LƯỢT VÉ TỪNG PHIM", 
            font=ctk.CTkFont(family="Anton", size=13),
            text_color=COLOR_GOLD
        ).pack(anchor="w", padx=15, pady=(8, 4))

        tbl_container = tk.Frame(table_card, bg=COLOR_BG_CARD)
        tbl_container.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        cols = ("title", "tickets", "rate", "revenue")
        self.tree_movie_stats = ttk.Treeview(tbl_container, columns=cols, show="headings", style="Dark.Treeview", height=6)
        self.tree_movie_stats.heading("title", text="Tên Phim Điện Ảnh")
        self.tree_movie_stats.heading("tickets", text="Số Vé Đã Bán")
        self.tree_movie_stats.heading("rate", text="Tỉ Lệ Đóng Góp")
        self.tree_movie_stats.heading("revenue", text="Tổng Doanh Thu Vé (VNĐ)")

        self.tree_movie_stats.column("title", width=340, anchor="w")
        self.tree_movie_stats.column("tickets", width=110, anchor="center")
        self.tree_movie_stats.column("rate", width=120, anchor="center")
        self.tree_movie_stats.column("revenue", width=170, anchor="e")

        scroll_s = ttk.Scrollbar(tbl_container, orient="vertical", command=self.tree_movie_stats.yview)
        self.tree_movie_stats.configure(yscrollcommand=scroll_s.set)
        self.tree_movie_stats.pack(side="left", fill="both", expand=True)
        scroll_s.pack(side="right", fill="y")

        self.current_stats_data = None
        self._load_statistics()

    def _create_bento_kpi_card(self, parent, title, initial_val, initial_sub, color):
        card = ctk.CTkFrame(parent, corner_radius=16, fg_color=COLOR_BG_CARD, border_width=1, border_color=color)
        card.pack(side="left", fill="both", expand=True, padx=5)

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(family="Inter", size=10, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=14, pady=(10, 0))
        lbl_val = ctk.CTkLabel(card, text=initial_val, font=ctk.CTkFont(family="Anton", size=20), text_color=color)
        lbl_val.pack(anchor="w", padx=14, pady=(2, 0))
        lbl_sub = ctk.CTkLabel(card, text=initial_sub, font=ctk.CTkFont(family="Inter", size=9), text_color=COLOR_TEXT_MUTED)
        lbl_sub.pack(anchor="w", padx=14, pady=(0, 10))
        return lbl_val, lbl_sub

    def _draw_revenue_chart(self):
        if not getattr(self, "current_stats_data", None):
            return
        w = self.chart_canvas.winfo_width()
        h = self.chart_canvas.winfo_height()
        if w <= 50:
            return
        self.chart_canvas.delete("all")

        movies = self.current_stats_data.get('movie_stats', [])[:4]
        if not movies:
            self.chart_canvas.create_text(w / 2, h / 2, text="Chưa có dữ liệu doanh thu", fill=COLOR_TEXT_MUTED, font=("Inter", 11))
            return

        max_rev = max((m['movie_revenue'] for m in movies), default=1)
        if max_rev <= 0:
            max_rev = 1

        bar_h = 18
        spacing = 30
        start_y = 12
        left_pad = 135
        right_pad = 160
        max_bar_w = max(50, w - left_pad - right_pad)

        colors = [COLOR_ACCENT, COLOR_GOLD, COLOR_SUCCESS, "#9d4edd"]

        for idx, m in enumerate(movies):
            y = start_y + idx * spacing
            color = colors[idx % len(colors)]
            rev = m['movie_revenue']
            bar_len = int((rev / max_rev) * max_bar_w)

            # Tên phim bên trái (rút gọn nếu dài)
            title = m['title']
            if len(title) > 17:
                title = title[:16] + "…"
            self.chart_canvas.create_text(left_pad - 10, y + bar_h / 2, text=title, anchor="e", fill=COLOR_TEXT_WHITE, font=("Inter", 9, "bold"))

            # Nền thanh rỗng mờ
            self.chart_canvas.create_rectangle(left_pad, y, left_pad + max_bar_w, y + bar_h, fill="#131c33", outline="")

            # Thanh doanh thu màu sắc
            if bar_len > 0:
                self.chart_canvas.create_rectangle(left_pad, y, left_pad + bar_len, y + bar_h, fill=color, outline="")

            # Số tiền và tỉ lệ bên phải
            pct = (rev / self.current_stats_data['total_revenue'] * 100) if self.current_stats_data['total_revenue'] > 0 else 0
            val_txt = f"{rev:,.0f} đ ({pct:.1f}%)"
            self.chart_canvas.create_text(left_pad + bar_len + 8, y + bar_h / 2, text=val_txt, anchor="w", fill=color, font=("Inter", 9, "bold"))

    def _load_statistics(self):
        stats = CinemaService.get_statistics()
        self.current_stats_data = stats

        total_rev = stats['total_revenue']
        fnb_rev = stats.get('total_fnb_revenue', 0)
        ticket_rev = total_rev - fnb_rev
        tickets = stats['total_tickets']
        fnb_pct = (fnb_rev / total_rev * 100) if total_rev > 0 else 0

        self.card_revenue.configure(text=f"{total_rev:,.0f} đ")
        self.sub_revenue.configure(text=f"✦ Vé: {ticket_rev:,.0f} đ • F&B: {fnb_rev:,.0f} đ")

        self.card_tickets.configure(text=f"{tickets} vé")
        self.sub_tickets.configure(text=f"✦ Phục vụ {stats['total_customers']} khách hàng")

        self.card_fnb.configure(text=f"{fnb_rev:,.0f} đ")
        self.sub_fnb.configure(text=f"✦ Chiếm {fnb_pct:.1f}% tổng doanh thu rạp")

        total_accs = stats['total_customers'] + 2
        self.card_users.configure(text=f"{total_accs} tài khoản")
        self.sub_users.configure(text=f"✦ {stats['total_customers']} Khách • 1 Staff • 1 Admin")

        # Vẽ biểu đồ Canvas
        self._draw_revenue_chart()

        # Hiển thị Top F&B Items
        for widget in self.fnb_list_container.winfo_children():
            widget.destroy()

        fnb_items = stats.get('fnb_stats', [])
        if not fnb_items:
            ctk.CTkLabel(self.fnb_list_container, text="Chưa có giao dịch bắp nước nào", font=ctk.CTkFont(family="Inter", size=10, slant="italic"), text_color=COLOR_TEXT_MUTED).pack(pady=20)
        else:
            max_qty = max((it['total_qty'] for it in fnb_items), default=1)
            for it in fnb_items[:4]:
                row = ctk.CTkFrame(self.fnb_list_container, fg_color="transparent")
                row.pack(fill="x", pady=2)

                top_f = ctk.CTkFrame(row, fg_color="transparent")
                top_f.pack(fill="x")

                name = it['concession_name']
                if len(name) > 28:
                    name = name[:27] + "…"
                ctk.CTkLabel(top_f, text=name, font=ctk.CTkFont(family="Inter", size=10, weight="bold"), text_color=COLOR_TEXT_WHITE).pack(side="left")
                ctk.CTkLabel(top_f, text=f"{it['total_qty']} phần • {it['item_revenue']:,.0f} đ", font=ctk.CTkFont(family="Inter", size=9, weight="bold"), text_color=COLOR_GOLD).pack(side="right")

                # Progress bar nhỏ
                ratio = min(1.0, it['total_qty'] / max_qty) if max_qty > 0 else 0
                pb = ctk.CTkProgressBar(row, height=5, corner_radius=3, fg_color="#131c33", progress_color="#f39c12")
                pb.set(ratio)
                pb.pack(fill="x", pady=(2, 0))

        # Cập nhật Bảng Doanh Thu Chi Tiết (Xếp Hạng Huy Chương Top 1, 2, 3)
        for row in self.tree_movie_stats.get_children():
            self.tree_movie_stats.delete(row)

        for rank, m in enumerate(stats['movie_stats'], 1):
            rev = m['movie_revenue']
            rate_str = f"{(rev / total_rev * 100):.1f}%" if total_rev > 0 else "0.0%"
            medal = "🥇 " if rank == 1 else ("🥈 " if rank == 2 else ("🥉 " if rank == 3 else f"#{rank} "))
            title_display = f"{medal}{m['title']}"
            self.tree_movie_stats.insert("", "end", values=(
                title_display, f"{m['ticket_count']} vé", rate_str, f"{rev:,.0f} đ"
            ))

    # ================= TAB 2: QUẢN LÝ PHIM =================
    def _build_movies_tab(self):
        # Bảng phim
        table_card = ctk.CTkFrame(self.tab_movies, corner_radius=14, fg_color=COLOR_BG_LIGHT, border_width=1, border_color=COLOR_BORDER)
        table_card.pack(fill="both", expand=True, pady=(5, 10))

        tbl_f = tk.Frame(table_card, bg=COLOR_BG_LIGHT)
        tbl_f.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("id", "title", "genre", "duration", "director", "release", "status")
        self.tree_admin_movies = ttk.Treeview(tbl_f, columns=cols, show="headings", style="Dark.Treeview", height=6, selectmode="browse")
        self.tree_admin_movies.heading("id", text="Mã")
        self.tree_admin_movies.heading("title", text="Tên Phim")
        self.tree_admin_movies.heading("genre", text="Thể Loại")
        self.tree_admin_movies.heading("duration", text="Thời Lượng")
        self.tree_admin_movies.heading("director", text="Đạo Diễn")
        self.tree_admin_movies.heading("release", text="Khởi Chiếu")
        self.tree_admin_movies.heading("status", text="Trạng Thái")

        self.tree_admin_movies.column("id", width=40, anchor="center")
        self.tree_admin_movies.column("title", width=200, anchor="w")
        self.tree_admin_movies.column("genre", width=130, anchor="w")
        self.tree_admin_movies.column("duration", width=90, anchor="center")
        self.tree_admin_movies.column("director", width=130, anchor="w")
        self.tree_admin_movies.column("release", width=100, anchor="center")
        self.tree_admin_movies.column("status", width=115, anchor="center")

        scroll_m = ttk.Scrollbar(tbl_f, orient="vertical", command=self.tree_admin_movies.yview)
        self.tree_admin_movies.configure(yscrollcommand=scroll_m.set)
        self.tree_admin_movies.pack(side="left", fill="both", expand=True)
        scroll_m.pack(side="right", fill="y")
        self.tree_admin_movies.bind("<<TreeviewSelect>>", self._on_admin_movie_selected)

        # Form Nhập Liệu Bo Tròn
        form_card = ctk.CTkFrame(self.tab_movies, corner_radius=16, fg_color=COLOR_BG_LIGHT, border_width=1, border_color=COLOR_BORDER)
        form_card.pack(fill="x", pady=(0, 5), padx=2, ipady=4)

        ctk.CTkLabel(form_card, text="📝 THÔNG TIN BỘ PHIM", font=ctk.CTkFont(family="Inter", size=12, weight="bold"), text_color=COLOR_GOLD).grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(8, 6))

        # Row 1
        ctk.CTkLabel(form_card, text="Tên phim (*):", font=ctk.CTkFont(family="Inter", size=11)).grid(row=1, column=0, sticky="w", padx=15, pady=3)
        self.txt_m_title = ctk.CTkEntry(form_card, corner_radius=8, height=32, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.txt_m_title.grid(row=1, column=1, sticky="ew", padx=10, pady=3)

        ctk.CTkLabel(form_card, text="Thể loại:", font=ctk.CTkFont(family="Inter", size=11)).grid(row=1, column=2, sticky="w", padx=15, pady=3)
        self.txt_m_genre = ctk.CTkEntry(form_card, corner_radius=8, height=32, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.txt_m_genre.grid(row=1, column=3, sticky="ew", padx=10, pady=3)

        # Row 2
        ctk.CTkLabel(form_card, text="Thời lượng (phút):", font=ctk.CTkFont(family="Inter", size=11)).grid(row=2, column=0, sticky="w", padx=15, pady=3)
        self.txt_m_duration = ctk.CTkEntry(form_card, corner_radius=8, height=32, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.txt_m_duration.grid(row=2, column=1, sticky="ew", padx=10, pady=3)

        ctk.CTkLabel(form_card, text="Đạo diễn:", font=ctk.CTkFont(family="Inter", size=11)).grid(row=2, column=2, sticky="w", padx=15, pady=3)
        self.txt_m_director = ctk.CTkEntry(form_card, corner_radius=8, height=32, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.txt_m_director.grid(row=2, column=3, sticky="ew", padx=10, pady=3)

        # Row 3
        ctk.CTkLabel(form_card, text="Ngày khởi chiếu:", font=ctk.CTkFont(family="Inter", size=11)).grid(row=3, column=0, sticky="w", padx=15, pady=3)
        self.txt_m_release = ctk.CTkEntry(form_card, corner_radius=8, height=32, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.txt_m_release.grid(row=3, column=1, sticky="ew", padx=10, pady=3)
        self.txt_m_release.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ctk.CTkLabel(form_card, text="Trạng thái:", font=ctk.CTkFont(family="Inter", size=11)).grid(row=3, column=2, sticky="w", padx=15, pady=3)
        self.combo_m_active = ctk.CTkComboBox(form_card, values=["Đang chiếu", "Ngừng chiếu"], corner_radius=8, state="readonly")
        self.combo_m_active.set("Đang chiếu")
        self.combo_m_active.grid(row=3, column=3, sticky="ew", padx=10, pady=3)

        # Row 4: Mô tả
        ctk.CTkLabel(form_card, text="Tóm tắt:", font=ctk.CTkFont(family="Inter", size=11)).grid(row=4, column=0, sticky="w", padx=15, pady=3)
        self.txt_m_desc = ctk.CTkEntry(form_card, corner_radius=8, height=32, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.txt_m_desc.grid(row=4, column=1, columnspan=3, sticky="ew", padx=10, pady=3)

        # Row 5: Poster & Trailer
        ctk.CTkLabel(form_card, text="Đường dẫn Poster:", font=ctk.CTkFont(family="Inter", size=11)).grid(row=5, column=0, sticky="w", padx=15, pady=3)
        
        poster_box = ctk.CTkFrame(form_card, fg_color="transparent")
        poster_box.grid(row=5, column=1, sticky="ew", padx=10, pady=3)

        self.txt_m_poster = ctk.CTkEntry(poster_box, corner_radius=8, height=32, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER, placeholder_text="assets/posters/ten_phim.png")
        self.txt_m_poster.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_browse_p = ctk.CTkButton(poster_box, text="📂 Duyệt...", width=70, height=32, corner_radius=8, fg_color=COLOR_BG_LIGHT, hover_color=COLOR_BORDER, cursor="hand2", command=self._browse_poster_file)
        btn_browse_p.pack(side="right")

        ctk.CTkLabel(form_card, text="Trailer YouTube URL:", font=ctk.CTkFont(family="Inter", size=11)).grid(row=5, column=2, sticky="w", padx=15, pady=3)
        self.txt_m_trailer = ctk.CTkEntry(form_card, corner_radius=8, height=32, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER, placeholder_text="https://www.youtube.com/watch?v=...")
        self.txt_m_trailer.grid(row=5, column=3, sticky="ew", padx=10, pady=3)

        form_card.columnconfigure(1, weight=1)
        form_card.columnconfigure(3, weight=1)

        # Buttons Bo Tròn
        btn_bar = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_bar.grid(row=6, column=0, columnspan=4, sticky="e", padx=10, pady=(8, 8))

        btn_clear = ctk.CTkButton(btn_bar, text="🧹 Làm Mới", corner_radius=10, height=32, width=90, fg_color=COLOR_BG_CARD, hover_color=COLOR_BORDER, cursor="hand2", command=self._clear_movie_form)
        btn_clear.pack(side="left", padx=4)

        btn_add = ctk.CTkButton(btn_bar, text="➕ Thêm Phim", corner_radius=10, height=32, width=100, fg_color="#06d6a0", hover_color="#05b386", text_color="black", font=ctk.CTkFont(weight="bold"), cursor="hand2", command=self._handle_add_movie)
        btn_add.pack(side="left", padx=4)

        btn_update = ctk.CTkButton(btn_bar, text="✏️ Cập Nhật", corner_radius=10, height=32, width=100, fg_color="#2980b9", hover_color="#1f618d", font=ctk.CTkFont(weight="bold"), cursor="hand2", command=self._handle_update_movie)
        btn_update.pack(side="left", padx=4)

        btn_del = ctk.CTkButton(btn_bar, text="🗑️ Xóa Phim", corner_radius=10, height=32, width=90, fg_color=COLOR_DANGER, hover_color="#c92a2a", font=ctk.CTkFont(weight="bold"), cursor="hand2", command=self._handle_delete_movie)
        btn_del.pack(side="left", padx=4)

        self.current_movie_id = None
        self._load_admin_movies()

    def _load_admin_movies(self):
        for row in self.tree_admin_movies.get_children():
            self.tree_admin_movies.delete(row)

        self.admin_movies_list = CinemaService.get_movies(only_active=False)
        for m in self.admin_movies_list:
            status_str = "● ĐANG CHIẾU" if m.is_active else "○ NGỪNG CHIẾU"
            self.tree_admin_movies.insert("", "end", values=(
                m.id, m.title, m.genre, f"{m.duration} phút", m.director, m.release_date, status_str
            ))

    def _on_admin_movie_selected(self, event):
        selected_item = self.tree_admin_movies.focus()
        if not selected_item:
            return

        values = self.tree_admin_movies.item(selected_item, "values")
        m_id = int(values[0])
        movie = next((m for m in self.admin_movies_list if m.id == m_id), None)
        if movie:
            self.current_movie_id = movie.id
            self.txt_m_title.delete(0, "end")
            self.txt_m_title.insert(0, movie.title)

            self.txt_m_genre.delete(0, "end")
            self.txt_m_genre.insert(0, movie.genre)

            self.txt_m_duration.delete(0, "end")
            self.txt_m_duration.insert(0, str(movie.duration))

            self.txt_m_director.delete(0, "end")
            self.txt_m_director.insert(0, movie.director or "")

            self.txt_m_release.delete(0, "end")
            self.txt_m_release.insert(0, movie.release_date or "")

            self.combo_m_active.set("Đang chiếu" if movie.is_active else "Ngừng chiếu")

            self.txt_m_desc.delete(0, "end")
            self.txt_m_desc.insert(0, movie.description or "")

            self.txt_m_poster.delete(0, "end")
            self.txt_m_poster.insert(0, movie.poster_path or "")

            self.txt_m_trailer.delete(0, "end")
            self.txt_m_trailer.insert(0, movie.trailer_url or "")

    def _browse_poster_file(self):
        fpath = filedialog.askopenfilename(
            title="Chọn ảnh Poster Phim",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.webp"), ("All files", "*.*")]
        )
        if fpath:
            try:
                rel = os.path.relpath(fpath, os.getcwd())
                clean_path = rel.replace("\\", "/")
            except Exception:
                clean_path = fpath.replace("\\", "/")
            self.txt_m_poster.delete(0, "end")
            self.txt_m_poster.insert(0, clean_path)

    def _clear_movie_form(self):
        self.current_movie_id = None
        self.txt_m_title.delete(0, "end")
        self.txt_m_genre.delete(0, "end")
        self.txt_m_duration.delete(0, "end")
        self.txt_m_director.delete(0, "end")
        self.txt_m_release.delete(0, "end")
        self.txt_m_release.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.txt_m_desc.delete(0, "end")
        self.txt_m_poster.delete(0, "end")
        self.txt_m_trailer.delete(0, "end")
        self.combo_m_active.set("Đang chiếu")

    def _handle_add_movie(self):
        title = self.txt_m_title.get().strip()
        genre = self.txt_m_genre.get().strip()
        director = self.txt_m_director.get().strip()
        release_date = self.txt_m_release.get().strip()
        description = self.txt_m_desc.get().strip()
        poster_path = self.txt_m_poster.get().strip()
        trailer_url = self.txt_m_trailer.get().strip()

        try:
            duration = int(self.txt_m_duration.get().strip())
        except ValueError:
            messagebox.showwarning("Lỗi", "Thời lượng phim phải là số nguyên (phút)!")
            return

        success, msg = CinemaService.add_movie(title, genre, duration, director, description, release_date, poster_path, trailer_url)
        if success:
            messagebox.showinfo("Thành công", msg)
            self._clear_movie_form()
            self._load_admin_movies()
            self._load_showtimes_combo_data()
        else:
            messagebox.showerror("Lỗi", msg)

    def _handle_update_movie(self):
        if not self.current_movie_id:
            messagebox.showwarning("Thông báo", "Vui lòng chọn 1 phim từ bảng để cập nhật!")
            return

        title = self.txt_m_title.get().strip()
        genre = self.txt_m_genre.get().strip()
        director = self.txt_m_director.get().strip()
        release_date = self.txt_m_release.get().strip()
        description = self.txt_m_desc.get().strip()
        poster_path = self.txt_m_poster.get().strip()
        trailer_url = self.txt_m_trailer.get().strip()
        is_active = 1 if self.combo_m_active.get() == "Đang chiếu" else 0

        try:
            duration = int(self.txt_m_duration.get().strip())
        except ValueError:
            messagebox.showwarning("Lỗi", "Thời lượng phim phải là số nguyên (phút)!")
            return

        success, msg = CinemaService.update_movie(self.current_movie_id, title, genre, duration, director, description, release_date, is_active, poster_path, trailer_url)
        if success:
            messagebox.showinfo("Thành công", msg)
            self._load_admin_movies()
            self._load_showtimes_combo_data()
        else:
            messagebox.showerror("Lỗi", msg)

    def _handle_delete_movie(self):
        if not self.current_movie_id:
            messagebox.showwarning("Thông báo", "Vui lòng chọn 1 phim từ bảng để xóa!")
            return

        confirm = messagebox.askyesno("Xác nhận xóa", "Bạn có chắc chắn muốn xóa phim này và tất cả các suất chiếu liên quan?")
        if confirm:
            success, msg = CinemaService.delete_movie(self.current_movie_id)
            if success:
                messagebox.showinfo("Thành công", msg)
                self._clear_movie_form()
                self._load_admin_movies()
                self._load_showtimes_combo_data()
            else:
                messagebox.showerror("Lỗi", msg)

    # ================= TAB 3: QUẢN LÝ LỊCH CHIẾU =================
    def _build_showtimes_tab(self):
        table_card = ctk.CTkFrame(self.tab_showtimes, corner_radius=14, fg_color=COLOR_BG_LIGHT, border_width=1, border_color=COLOR_BORDER)
        table_card.pack(fill="both", expand=True, pady=(5, 10))

        tbl_f = tk.Frame(table_card, bg=COLOR_BG_LIGHT)
        tbl_f.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("id", "movie", "room", "date", "time", "price")
        self.tree_admin_st = ttk.Treeview(tbl_f, columns=cols, show="headings", style="Dark.Treeview", height=7, selectmode="browse")
        self.tree_admin_st.heading("id", text="Mã SC")
        self.tree_admin_st.heading("movie", text="Phim")
        self.tree_admin_st.heading("room", text="Phòng Chiếu")
        self.tree_admin_st.heading("date", text="Ngày Chiếu")
        self.tree_admin_st.heading("time", text="Giờ Chiếu")
        self.tree_admin_st.heading("price", text="Giá Vé Gốc")

        self.tree_admin_st.column("id", width=50, anchor="center")
        self.tree_admin_st.column("movie", width=220, anchor="w")
        self.tree_admin_st.column("room", width=180, anchor="w")
        self.tree_admin_st.column("date", width=110, anchor="center")
        self.tree_admin_st.column("time", width=90, anchor="center")
        self.tree_admin_st.column("price", width=110, anchor="e")

        scroll_st = ttk.Scrollbar(tbl_f, orient="vertical", command=self.tree_admin_st.yview)
        self.tree_admin_st.configure(yscrollcommand=scroll_st.set)
        self.tree_admin_st.pack(side="left", fill="both", expand=True)
        scroll_st.pack(side="right", fill="y")

        # Form Tạo Suất Chiếu Bo Tròn
        form_card = ctk.CTkFrame(self.tab_showtimes, corner_radius=16, fg_color=COLOR_BG_LIGHT, border_width=1, border_color=COLOR_BORDER)
        form_card.pack(fill="x", pady=(0, 5), padx=2, ipady=4)

        ctk.CTkLabel(form_card, text="🕒 TẠO SUẤT CHIẾU VŨ TRỤ MỚI", font=ctk.CTkFont(family="Inter", size=12, weight="bold"), text_color=COLOR_GOLD).grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(8, 6))

        ctk.CTkLabel(form_card, text="Chọn phim:", font=ctk.CTkFont(family="Inter", size=11)).grid(row=1, column=0, sticky="w", padx=15, pady=3)
        self.combo_st_movie = ctk.CTkComboBox(form_card, corner_radius=8, width=260, state="readonly")
        self.combo_st_movie.grid(row=1, column=1, sticky="w", padx=10, pady=3)

        ctk.CTkLabel(form_card, text="Chọn phòng:", font=ctk.CTkFont(family="Inter", size=11)).grid(row=1, column=2, sticky="w", padx=15, pady=3)
        self.combo_st_room = ctk.CTkComboBox(form_card, corner_radius=8, width=240, state="readonly")
        self.combo_st_room.grid(row=1, column=3, sticky="w", padx=10, pady=3)

        ctk.CTkLabel(form_card, text="Ngày chiếu (YYYY-MM-DD):", font=ctk.CTkFont(family="Inter", size=11)).grid(row=2, column=0, sticky="w", padx=15, pady=3)
        self.txt_st_date = ctk.CTkEntry(form_card, corner_radius=8, width=260, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.txt_st_date.grid(row=2, column=1, sticky="w", padx=10, pady=3)
        self.txt_st_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ctk.CTkLabel(form_card, text="Giờ chiếu:", font=ctk.CTkFont(family="Inter", size=11)).grid(row=2, column=2, sticky="w", padx=15, pady=3)
        self.combo_st_time = ctk.CTkComboBox(form_card, values=["09:30", "11:45", "14:15", "16:45", "19:15", "21:45"], corner_radius=8, width=240)
        self.combo_st_time.set("19:15")
        self.combo_st_time.grid(row=2, column=3, sticky="w", padx=10, pady=3)

        ctk.CTkLabel(form_card, text="Giá vé gốc (VNĐ):", font=ctk.CTkFont(family="Inter", size=11)).grid(row=3, column=0, sticky="w", padx=15, pady=3)
        self.txt_st_price = ctk.CTkEntry(form_card, corner_radius=8, width=260, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.txt_st_price.grid(row=3, column=1, sticky="w", padx=10, pady=3)
        self.txt_st_price.insert(0, "85000")

        # Nút Thêm / Xóa Suất chiếu Bo Tròn
        btn_bar = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_bar.grid(row=4, column=0, columnspan=4, sticky="e", padx=10, pady=(8, 8))

        btn_add_st = ctk.CTkButton(btn_bar, text="➕ Tạo Suất Chiếu", corner_radius=10, height=32, width=130, fg_color="#06d6a0", hover_color="#05b386", text_color="black", font=ctk.CTkFont(weight="bold"), cursor="hand2", command=self._handle_add_showtime)
        btn_add_st.pack(side="left", padx=5)

        btn_del_st = ctk.CTkButton(btn_bar, text="🗑️ Xóa Suất Chiếu", corner_radius=10, height=32, width=130, fg_color=COLOR_DANGER, hover_color="#c92a2a", font=ctk.CTkFont(weight="bold"), cursor="hand2", command=self._handle_delete_showtime)
        btn_del_st.pack(side="left", padx=5)

        self._load_showtimes_combo_data()
        self._load_admin_showtimes()

    def _load_showtimes_combo_data(self):
        movies = CinemaService.get_movies(only_active=True)
        self.movie_map = {f"{m.id} - {m.title}": m.id for m in movies}
        self.combo_st_movie.configure(values=list(self.movie_map.keys()))
        if self.movie_map:
            self.combo_st_movie.set(list(self.movie_map.keys())[0])

        rooms = CinemaService.get_rooms()
        self.room_map = {f"{r.id} - {r.name}": r.id for r in rooms}
        self.combo_st_room.configure(values=list(self.room_map.keys()))
        if self.room_map:
            self.combo_st_room.set(list(self.room_map.keys())[0])

    def _load_admin_showtimes(self):
        for row in self.tree_admin_st.get_children():
            self.tree_admin_st.delete(row)

        st_list = CinemaService.get_showtimes()
        for st in st_list:
            self.tree_admin_st.insert("", "end", values=(
                st.id, st.movie_title, st.room_name, st.show_date, st.show_time, f"{st.base_price:,.0f} đ"
            ))

    def _handle_add_showtime(self):
        selected_m = self.combo_st_movie.get()
        selected_r = self.combo_st_room.get()
        if not selected_m or not selected_r:
            messagebox.showwarning("Lỗi", "Vui lòng chọn phim và phòng chiếu!")
            return

        movie_id = self.movie_map[selected_m]
        room_id = self.room_map[selected_r]
        show_date = self.txt_st_date.get().strip()
        show_time = self.combo_st_time.get().strip()

        try:
            base_price = float(self.txt_st_price.get().strip().replace(",", ""))
        except ValueError:
            messagebox.showwarning("Lỗi", "Giá vé cơ bản phải là số hợp lệ!")
            return

        success, msg = CinemaService.add_showtime(movie_id, room_id, show_date, show_time, base_price)
        if success:
            messagebox.showinfo("Thành công", msg)
            self._load_admin_showtimes()
        else:
            messagebox.showerror("Lỗi", msg)

    def _handle_delete_showtime(self):
        selected_item = self.tree_admin_st.focus()
        if not selected_item:
            messagebox.showwarning("Thông báo", "Vui lòng chọn 1 suất chiếu từ bảng để xóa!")
            return

        values = self.tree_admin_st.item(selected_item, "values")
        st_id = int(values[0])

        confirm = messagebox.askyesno("Xác nhận xóa", "Bạn có chắc chắn muốn xóa suất chiếu này? Các vé liên quan cũng sẽ bị xóa.")
        if confirm:
            success, msg = CinemaService.delete_showtime(st_id)
            if success:
                messagebox.showinfo("Thành công", msg)
                self._load_admin_showtimes()
            else:
                messagebox.showerror("Lỗi", msg)

    # ================= TAB 4: QUẢN LÝ BẮP NƯỚC (F&B CONCESSIONS) =================
    def _build_concessions_tab(self):
        content = ctk.CTkFrame(self.tab_concessions, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=10, pady=10)

        # Cột Trái: Bảng danh sách Bắp Nước & Combo
        left_col = ctk.CTkFrame(content, corner_radius=16, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        top_bar = ctk.CTkFrame(left_col, fg_color="transparent")
        top_bar.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            top_bar,
            text="🍿 MENU BẮP NƯỚC & COMBO RẠP PHIM",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color=COLOR_GOLD
        ).pack(side="left")

        # Lọc danh mục
        self.combo_fnb_filter = ctk.CTkComboBox(
            top_bar,
            values=["Tất cả", "Combo", "Bắp", "Nước", "Snack"],
            width=110,
            height=30,
            corner_radius=8,
            state="readonly",
            command=lambda val: self._load_admin_concessions()
        )
        self.combo_fnb_filter.set("Tất cả")
        self.combo_fnb_filter.pack(side="right", padx=(5, 0))

        ctk.CTkLabel(top_bar, text="Lọc:", font=ctk.CTkFont(size=11), text_color=COLOR_TEXT_MUTED).pack(side="right", padx=(10, 2))

        btn_ref_fnb = ctk.CTkButton(
            top_bar,
            text="🔄 Làm Mới",
            width=80,
            height=30,
            corner_radius=8,
            fg_color=COLOR_BG_LIGHT,
            hover_color=COLOR_BORDER,
            cursor="hand2",
            command=self._load_admin_concessions
        )
        btn_ref_fnb.pack(side="right", padx=(0, 5))

        # Table Treeview
        tbl_frame = tk.Frame(left_col, bg=COLOR_BG_CARD)
        tbl_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        fnb_cols = ("id", "icon", "name", "category", "price", "desc", "status")
        self.tree_admin_fnb = ttk.Treeview(tbl_frame, columns=fnb_cols, show="headings", style="Dark.Treeview", selectmode="browse")
        self.tree_admin_fnb.heading("id", text="ID")
        self.tree_admin_fnb.heading("icon", text="Icon")
        self.tree_admin_fnb.heading("name", text="Tên Món / Combo")
        self.tree_admin_fnb.heading("category", text="Phân Loại")
        self.tree_admin_fnb.heading("price", text="Đơn Giá")
        self.tree_admin_fnb.heading("desc", text="Mô Tả Chi Tiết")
        self.tree_admin_fnb.heading("status", text="Trạng Thái")

        self.tree_admin_fnb.column("id", width=35, anchor="center")
        self.tree_admin_fnb.column("icon", width=45, anchor="center")
        self.tree_admin_fnb.column("name", width=170, anchor="w")
        self.tree_admin_fnb.column("category", width=75, anchor="center")
        self.tree_admin_fnb.column("price", width=85, anchor="e")
        self.tree_admin_fnb.column("desc", width=180, anchor="w")
        self.tree_admin_fnb.column("status", width=110, anchor="center")

        scroll_fnb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree_admin_fnb.yview)
        self.tree_admin_fnb.configure(yscrollcommand=scroll_fnb.set)
        self.tree_admin_fnb.pack(side="left", fill="both", expand=True)
        scroll_fnb.pack(side="right", fill="y")
        self.tree_admin_fnb.bind("<<TreeviewSelect>>", self._on_admin_concession_selected)

        # Cột Phải: Form Thêm / Sửa Bắp Nước
        right_form = ctk.CTkFrame(content, corner_radius=16, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER, width=340)
        right_form.pack(side="right", fill="y")
        right_form.pack_propagate(False)

        ctk.CTkLabel(
            right_form,
            text="📝 THÔNG TIN SẢN PHẨM",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color=COLOR_ACCENT
        ).pack(anchor="w", padx=16, pady=(15, 10))

        # Fields
        form_inner = ctk.CTkFrame(right_form, fg_color="transparent")
        form_inner.pack(fill="x", padx=16)

        ctk.CTkLabel(form_inner, text="Tên món / Combo:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", pady=(2, 2))
        self.txt_fnb_name = ctk.CTkEntry(form_inner, corner_radius=8, height=32, placeholder_text="Ví dụ: Combo Sweet Solo")
        self.txt_fnb_name.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        row_cat_price = ctk.CTkFrame(form_inner, fg_color="transparent")
        row_cat_price.grid(row=2, column=0, sticky="ew", pady=(0, 6))
        row_cat_price.columnconfigure(0, weight=1)
        row_cat_price.columnconfigure(1, weight=1)

        ctk.CTkLabel(row_cat_price, text="Phân loại:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w")
        self.combo_fnb_cat = ctk.CTkComboBox(row_cat_price, values=["Combo", "Bắp", "Nước", "Snack"], corner_radius=8, height=32, state="readonly")
        self.combo_fnb_cat.set("Combo")
        self.combo_fnb_cat.grid(row=1, column=0, sticky="ew", padx=(0, 3))

        ctk.CTkLabel(row_cat_price, text="Đơn giá (VNĐ):", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, sticky="w", padx=(3, 0))
        self.txt_fnb_price = ctk.CTkEntry(row_cat_price, corner_radius=8, height=32, placeholder_text="Ví dụ: 85000")
        self.txt_fnb_price.grid(row=1, column=1, sticky="ew", padx=(3, 0))

        row_icon_status = ctk.CTkFrame(form_inner, fg_color="transparent")
        row_icon_status.grid(row=3, column=0, sticky="ew", pady=(0, 6))
        row_icon_status.columnconfigure(0, weight=1)
        row_icon_status.columnconfigure(1, weight=1)

        ctk.CTkLabel(row_icon_status, text="Icon biểu tượng:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w")
        self.combo_fnb_icon = ctk.CTkComboBox(row_icon_status, values=["🍿", "🥤", "🍿🥤", "🌭", "🥨", "🍫", "🍹"], corner_radius=8, height=32)
        self.combo_fnb_icon.set("🍿🥤")
        self.combo_fnb_icon.grid(row=1, column=0, sticky="ew", padx=(0, 3))

        ctk.CTkLabel(row_icon_status, text="Trạng thái:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, sticky="w", padx=(3, 0))
        self.combo_fnb_status = ctk.CTkComboBox(row_icon_status, values=["Đang bán", "Ngừng bán"], corner_radius=8, height=32, state="readonly")
        self.combo_fnb_status.set("Đang bán")
        self.combo_fnb_status.grid(row=1, column=1, sticky="ew", padx=(3, 0))

        ctk.CTkLabel(form_inner, text="Mô tả thành phần:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=4, column=0, sticky="w", pady=(2, 2))
        self.txt_fnb_desc = ctk.CTkEntry(form_inner, corner_radius=8, height=32, placeholder_text="1 bắp rang bơ + 1 pepsi")
        self.txt_fnb_desc.grid(row=5, column=0, sticky="ew", pady=(0, 8))

        form_inner.columnconfigure(0, weight=1)

        # Action Buttons
        btn_box = ctk.CTkFrame(right_form, fg_color="transparent")
        btn_box.pack(fill="x", padx=16, pady=(2, 10))

        btn_add = ctk.CTkButton(
            btn_box, text="➕ Thêm Món Mới", corner_radius=10, height=34,
            fg_color="#06d6a0", hover_color="#05b386", text_color="black", font=ctk.CTkFont(weight="bold"),
            cursor="hand2", command=self._handle_add_concession
        )
        btn_add.pack(fill="x", pady=3)

        row_actions = ctk.CTkFrame(btn_box, fg_color="transparent")
        row_actions.pack(fill="x", pady=3)
        row_actions.columnconfigure(0, weight=1)
        row_actions.columnconfigure(1, weight=1)

        btn_update = ctk.CTkButton(
            row_actions, text="✏️ Cập Nhật", corner_radius=10, height=34,
            fg_color="#2980b9", hover_color="#1f618d", font=ctk.CTkFont(weight="bold"),
            cursor="hand2", command=self._handle_update_concession
        )
        btn_update.grid(row=0, column=0, sticky="ew", padx=(0, 3))

        btn_del = ctk.CTkButton(
            row_actions, text="🗑️ Xóa Món", corner_radius=10, height=34,
            fg_color=COLOR_DANGER, hover_color="#c92a2a", font=ctk.CTkFont(weight="bold"),
            cursor="hand2", command=self._handle_delete_concession
        )
        btn_del.grid(row=0, column=1, sticky="ew", padx=(3, 0))

        btn_clear = ctk.CTkButton(
            btn_box, text="🧹 Xóa Trắng Form", corner_radius=10, height=30,
            fg_color=COLOR_BG_LIGHT, hover_color=COLOR_BORDER,
            cursor="hand2", command=self._clear_concession_form
        )
        btn_clear.pack(fill="x", pady=(3, 0))

        self.current_concession_id = None
        self._load_admin_concessions()

    def _load_admin_concessions(self):
        for row in self.tree_admin_fnb.get_children():
            self.tree_admin_fnb.delete(row)

        category_filter = self.combo_fnb_filter.get() if hasattr(self, 'combo_fnb_filter') else "Tất cả"
        items = CinemaService.get_concessions(only_active=False)
        self.admin_concessions_list = items

        for item in items:
            if category_filter != "Tất cả" and item.category != category_filter:
                continue
            stt = "● ĐANG BÁN" if item.is_active else "○ TẠM NGƯNG"
            self.tree_admin_fnb.insert("", "end", values=(
                item.id, item.icon, item.name, item.category, f"{item.price:,.0f} đ", item.description, stt
            ))

    def _on_admin_concession_selected(self, event):
        selected = self.tree_admin_fnb.focus()
        if not selected:
            return
        vals = self.tree_admin_fnb.item(selected, "values")
        c_id = int(vals[0])
        item = next((i for i in self.admin_concessions_list if i.id == c_id), None)
        if item:
            self.current_concession_id = item.id
            self.txt_fnb_name.delete(0, "end")
            self.txt_fnb_name.insert(0, item.name)
            self.combo_fnb_cat.set(item.category)
            self.txt_fnb_price.delete(0, "end")
            self.txt_fnb_price.insert(0, f"{item.price:.0f}")
            self.combo_fnb_icon.set(item.icon)
            self.combo_fnb_status.set("Đang bán" if item.is_active else "Ngừng bán")
            self.txt_fnb_desc.delete(0, "end")
            self.txt_fnb_desc.insert(0, item.description or "")

    def _clear_concession_form(self):
        self.current_concession_id = None
        self.txt_fnb_name.delete(0, "end")
        self.combo_fnb_cat.set("Combo")
        self.txt_fnb_price.delete(0, "end")
        self.combo_fnb_icon.set("🍿🥤")
        self.combo_fnb_status.set("Đang bán")
        self.txt_fnb_desc.delete(0, "end")

    def _handle_add_concession(self):
        name = self.txt_fnb_name.get().strip()
        cat = self.combo_fnb_cat.get().strip()
        icon = self.combo_fnb_icon.get().strip() or "🍿"
        desc = self.txt_fnb_desc.get().strip()

        try:
            price = float(self.txt_fnb_price.get().strip().replace(",", "").replace(".", ""))
        except ValueError:
            messagebox.showwarning("Lỗi", "Đơn giá phải là số hợp lệ!")
            return

        succ, msg = CinemaService.add_concession(name, cat, price, desc, icon)
        if succ:
            messagebox.showinfo("Thành công", msg)
            self._clear_concession_form()
            self._load_admin_concessions()
        else:
            messagebox.showerror("Lỗi", msg)

    def _handle_update_concession(self):
        if not self.current_concession_id:
            messagebox.showwarning("Thông báo", "Vui lòng click chọn 1 món từ bảng để cập nhật!")
            return

        name = self.txt_fnb_name.get().strip()
        cat = self.combo_fnb_cat.get().strip()
        icon = self.combo_fnb_icon.get().strip() or "🍿"
        desc = self.txt_fnb_desc.get().strip()
        is_active = 1 if self.combo_fnb_status.get() == "Đang bán" else 0

        try:
            price = float(self.txt_fnb_price.get().strip().replace(",", "").replace(".", ""))
        except ValueError:
            messagebox.showwarning("Lỗi", "Đơn giá phải là số hợp lệ!")
            return

        succ, msg = CinemaService.update_concession(self.current_concession_id, name, cat, price, desc, is_active, icon)
        if succ:
            messagebox.showinfo("Thành công", msg)
            self._load_admin_concessions()
        else:
            messagebox.showerror("Lỗi", msg)

    def _handle_delete_concession(self):
        if not self.current_concession_id:
            messagebox.showwarning("Thông báo", "Vui lòng chọn 1 món từ bảng để xóa!")
            return

        confirm = messagebox.askyesno("Xác nhận xóa", "Bạn có chắc muốn xóa món bắp nước này khỏi hệ thống?")
        if confirm:
            succ, msg = CinemaService.delete_concession(self.current_concession_id)
            if succ:
                messagebox.showinfo("Thành công", msg)
                self._clear_concession_form()
                self._load_admin_concessions()
            else:
                messagebox.showerror("Lỗi", msg)

    # ================= TAB 5: QUẢN LÝ ĐẶT VÉ =================
    def _build_bookings_tab(self):
        top_bar = ctk.CTkFrame(self.tab_bookings, fg_color="transparent")
        top_bar.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(
            top_bar, 
            text="📋 DANH SÁCH TOÀN BỘ VÉ ĐÃ ĐẶT TRÊN HỆ THỐNG", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color=COLOR_GOLD
        ).pack(side="left")

        btn_refresh = ctk.CTkButton(
            top_bar, 
            text="🔄 Làm Mới Danh Sách", 
            corner_radius=10, 
            height=32, 
            width=130,
            fg_color=COLOR_BG_LIGHT, 
            hover_color=COLOR_BORDER,
            cursor="hand2", 
            command=self._load_admin_bookings
        )
        btn_refresh.pack(side="right")

        table_card = ctk.CTkFrame(self.tab_bookings, corner_radius=16, fg_color=COLOR_BG_LIGHT, border_width=1, border_color=COLOR_BORDER)
        table_card.pack(fill="both", expand=True, pady=(0, 5))

        tbl_f = tk.Frame(table_card, bg=COLOR_BG_LIGHT)
        tbl_f.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("code", "customer", "phone", "movie", "room", "schedule", "seats", "concessions", "total", "date", "status")
        self.tree_admin_bookings = ttk.Treeview(tbl_f, columns=cols, show="headings", style="Dark.Treeview")
        self.tree_admin_bookings.heading("code", text="Mã Vé")
        self.tree_admin_bookings.heading("customer", text="Khách Hàng")
        self.tree_admin_bookings.heading("phone", text="SĐT")
        self.tree_admin_bookings.heading("movie", text="Phim")
        self.tree_admin_bookings.heading("room", text="Phòng")
        self.tree_admin_bookings.heading("schedule", text="Suất Chiếu")
        self.tree_admin_bookings.heading("seats", text="Ghế")
        self.tree_admin_bookings.heading("concessions", text="Bắp Nước / Combo")
        self.tree_admin_bookings.heading("total", text="Tổng Tiền")
        self.tree_admin_bookings.heading("date", text="Ngày Đặt")
        self.tree_admin_bookings.heading("status", text="Trạng Thái")

        self.tree_admin_bookings.column("code", width=105, anchor="center")
        self.tree_admin_bookings.column("customer", width=120, anchor="w")
        self.tree_admin_bookings.column("phone", width=90, anchor="center")
        self.tree_admin_bookings.column("movie", width=150, anchor="w")
        self.tree_admin_bookings.column("room", width=120, anchor="w")
        self.tree_admin_bookings.column("schedule", width=110, anchor="center")
        self.tree_admin_bookings.column("seats", width=75, anchor="center")
        self.tree_admin_bookings.column("concessions", width=140, anchor="w")
        self.tree_admin_bookings.column("total", width=90, anchor="e")
        self.tree_admin_bookings.column("date", width=120, anchor="center")
        self.tree_admin_bookings.column("status", width=115, anchor="center")

        scroll_b = ttk.Scrollbar(tbl_f, orient="vertical", command=self.tree_admin_bookings.yview)
        self.tree_admin_bookings.configure(yscrollcommand=scroll_b.set)
        self.tree_admin_bookings.pack(side="left", fill="both", expand=True)
        scroll_b.pack(side="right", fill="y")

        self._load_admin_bookings()

    def _load_admin_bookings(self):
        for row in self.tree_admin_bookings.get_children():
            self.tree_admin_bookings.delete(row)

        bookings = CinemaService.get_all_bookings()
        for b in bookings:
            stt_raw = str(b.get('status') or '').upper()
            if "CONFIRM" in stt_raw:
                stt_display = "● ĐÃ XÁC NHẬN"
            elif "CHECK" in stt_raw:
                stt_display = "● ĐÃ CHECK-IN"
            elif "CANCEL" in stt_raw:
                stt_display = "● ĐÃ HỦY"
            else:
                stt_display = f"● {stt_raw}"

            self.tree_admin_bookings.insert("", "end", values=(
                b['booking_code'], b['customer_name'], b['customer_phone'] or "",
                b['movie_title'], b['room_name'], b['show_time'],
                b['seats_str'] or "", b.get('concessions_str') or "Không có",
                f"{b['total_amount']:,.0f} đ",
                b['booking_date'], stt_display
            ))

    # ================= TAB 6: QUẢN LÝ TÀI KHOẢN & NHÂN VIÊN =================
    def _build_users_tab(self):
        content = ctk.CTkFrame(self.tab_users, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=10, pady=10)

        # Cột Trái: Bảng Danh Sách Tài Khoản
        tbl_card = ctk.CTkFrame(content, corner_radius=14, fg_color=COLOR_BG_LIGHT, border_width=1, border_color=COLOR_BORDER)
        tbl_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        top_bar = ctk.CTkFrame(tbl_card, fg_color="transparent")
        top_bar.pack(fill="x", padx=12, pady=(10, 8))

        ctk.CTkLabel(
            top_bar, 
            text="👥 DANH SÁCH TÀI KHOẢN HỆ THỐNG", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color=COLOR_GOLD
        ).pack(side="left")

        btn_refresh = ctk.CTkButton(
            top_bar, text="🔄 Làm Mới", corner_radius=8, height=30, width=80,
            fg_color=COLOR_BG_CARD, hover_color=COLOR_BORDER, cursor="hand2",
            command=self._load_admin_users
        )
        btn_refresh.pack(side="right")

        self.txt_search_users = ctk.CTkEntry(
            top_bar, placeholder_text="🔍 Tìm username, họ tên...", corner_radius=8, height=30, width=180,
            fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER
        )
        self.txt_search_users.pack(side="right", padx=(0, 8))
        self.txt_search_users.bind("<KeyRelease>", lambda e: self._load_admin_users())

        tbl_f = tk.Frame(tbl_card, bg=COLOR_BG_LIGHT)
        tbl_f.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        cols = ("id", "username", "fullname", "phone", "email", "role")
        self.tree_admin_users = ttk.Treeview(tbl_f, columns=cols, show="headings", style="Dark.Treeview", selectmode="browse")
        self.tree_admin_users.heading("id", text="ID")
        self.tree_admin_users.heading("username", text="Tên Đăng Nhập")
        self.tree_admin_users.heading("fullname", text="Họ Và Tên")
        self.tree_admin_users.heading("phone", text="Số Điện Thoại")
        self.tree_admin_users.heading("email", text="Email")
        self.tree_admin_users.heading("role", text="Vai Trò (Phân Quyền)")

        self.tree_admin_users.column("id", width=35, anchor="center")
        self.tree_admin_users.column("username", width=120, anchor="w")
        self.tree_admin_users.column("fullname", width=160, anchor="w")
        self.tree_admin_users.column("phone", width=100, anchor="center")
        self.tree_admin_users.column("email", width=160, anchor="w")
        self.tree_admin_users.column("role", width=140, anchor="center")

        scroll = ttk.Scrollbar(tbl_f, orient="vertical", command=self.tree_admin_users.yview)
        self.tree_admin_users.configure(yscrollcommand=scroll.set)
        self.tree_admin_users.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree_admin_users.bind("<<TreeviewSelect>>", self._on_admin_user_selected)

        # Cột Phải: Form Thêm Nhân Viên / Người Dùng
        form_card = ctk.CTkFrame(content, corner_radius=14, fg_color=COLOR_BG_LIGHT, border_width=1, border_color=COLOR_BORDER, width=380)
        form_card.pack(side="right", fill="both", padx=(0, 0))
        form_card.pack_propagate(False)

        ctk.CTkLabel(
            form_card, 
            text="➕ THÊM / CẤP TÀI KHOẢN MỚI", 
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color=COLOR_ACCENT
        ).pack(anchor="w", padx=15, pady=(12, 10))

        # Fields
        ctk.CTkLabel(form_card, text="Tên đăng nhập:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15, pady=(2, 1))
        self.txt_u_username = ctk.CTkEntry(form_card, corner_radius=8, height=32, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.txt_u_username.pack(fill="x", padx=15, pady=(0, 6))

        ctk.CTkLabel(form_card, text="Mật khẩu khởi tạo:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15, pady=(2, 1))
        self.txt_u_password = ctk.CTkEntry(form_card, corner_radius=8, height=32, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER, show="*")
        self.txt_u_password.pack(fill="x", padx=15, pady=(0, 6))

        ctk.CTkLabel(form_card, text="Họ và tên:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15, pady=(2, 1))
        self.txt_u_fullname = ctk.CTkEntry(form_card, corner_radius=8, height=32, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.txt_u_fullname.pack(fill="x", padx=15, pady=(0, 6))

        ctk.CTkLabel(form_card, text="Số điện thoại:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15, pady=(2, 1))
        self.txt_u_phone = ctk.CTkEntry(form_card, corner_radius=8, height=32, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.txt_u_phone.pack(fill="x", padx=15, pady=(0, 6))

        ctk.CTkLabel(form_card, text="Email:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15, pady=(2, 1))
        self.txt_u_email = ctk.CTkEntry(form_card, corner_radius=8, height=32, fg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
        self.txt_u_email.pack(fill="x", padx=15, pady=(0, 6))

        ctk.CTkLabel(form_card, text="Phân quyền (Role):", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15, pady=(2, 1))
        self.combo_u_role = ctk.CTkComboBox(form_card, values=["staff (Nhân viên)", "customer (Khách hàng)", "admin (Quản trị viên)"], corner_radius=8, height=32, state="readonly")
        self.combo_u_role.set("staff (Nhân viên)")
        self.combo_u_role.pack(fill="x", padx=15, pady=(0, 15))

        # Buttons
        btn_box = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_box.pack(fill="x", padx=15, pady=(0, 10))

        btn_add = ctk.CTkButton(
            btn_box, text="➕ Cấp Tài Khoản", corner_radius=10, height=34,
            fg_color="#06d6a0", hover_color="#05b386", text_color="black", font=ctk.CTkFont(weight="bold"),
            cursor="hand2", command=self._handle_create_user
        )
        btn_add.pack(fill="x", pady=4)

        btn_del = ctk.CTkButton(
            btn_box, text="🗑️ Xóa Tài Khoản Đã Chọn", corner_radius=10, height=34,
            fg_color=COLOR_DANGER, hover_color="#c92a2a", font=ctk.CTkFont(weight="bold"),
            cursor="hand2", command=self._handle_delete_user
        )
        btn_del.pack(fill="x", pady=4)

        self.selected_user_id = None
        self._load_admin_users()

    def _load_admin_users(self):
        for row in self.tree_admin_users.get_children():
            self.tree_admin_users.delete(row)

        kw = self.txt_search_users.get().strip().lower() if hasattr(self, 'txt_search_users') else ""
        users = AuthService.get_all_users()
        for u in users:
            if kw and (kw not in u.username.lower() and kw not in u.fullname.lower() and kw not in u.role.lower()):
                continue
            role_label = "👑 Admin" if u.is_admin() else ("👔 Nhân viên" if u.is_staff() else "👤 Khách hàng")
            self.tree_admin_users.insert("", "end", values=(
                u.id, u.username, u.fullname, u.phone or "", u.email or "", role_label
            ))

    def _on_admin_user_selected(self, event):
        selected = self.tree_admin_users.focus()
        if not selected:
            return
        values = self.tree_admin_users.item(selected, "values")
        self.selected_user_id = int(values[0])

    def _handle_create_user(self):
        username = self.txt_u_username.get().strip()
        pwd = self.txt_u_password.get().strip()
        fullname = self.txt_u_fullname.get().strip()
        phone = self.txt_u_phone.get().strip()
        email = self.txt_u_email.get().strip()
        role_val = self.combo_u_role.get().split()[0]  # 'staff', 'customer', or 'admin'

        succ, msg = AuthService.create_user(username, pwd, fullname, role=role_val, email=email, phone=phone)
        if succ:
            messagebox.showinfo("Thành công", msg)
            self.txt_u_username.delete(0, "end")
            self.txt_u_password.delete(0, "end")
            self.txt_u_fullname.delete(0, "end")
            self.txt_u_phone.delete(0, "end")
            self.txt_u_email.delete(0, "end")
            self._load_admin_users()
        else:
            messagebox.showerror("Lỗi", msg)

    def _handle_delete_user(self):
        if not self.selected_user_id:
            messagebox.showwarning("Thông báo", "Vui lòng chọn 1 tài khoản từ bảng để xóa!")
            return

        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa tài khoản này?")
        if confirm:
            succ, msg = AuthService.delete_user(self.selected_user_id)
            if succ:
                messagebox.showinfo("Thành công", msg)
                self.selected_user_id = None
                self._load_admin_users()
            else:
                messagebox.showerror("Lỗi", msg)
