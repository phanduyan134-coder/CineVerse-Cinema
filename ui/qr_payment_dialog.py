"""
File: ui/qr_payment_dialog.py
Mô tả: Hộp thoại Quét Mã QR Thanh Toán VietQR 24/7 (CineVerse Secure Pay)
- Sinh mã QR động bằng thư viện qrcode và Pillow
- Hiển thị đầy đủ: Logo ngân hàng, Số tài khoản, Chủ tài khoản, Số tiền, Nội dung CK
- Đồng hồ đếm ngược giao dịch thời gian thực (Live Countdown Timer)
- Nút xác nhận thanh toán trực quan
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont
import os
import sys
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

from ui.styles import (
    COLOR_BG_DARK, COLOR_BG_CARD, COLOR_BG_LIGHT, COLOR_ACCENT,
    COLOR_GOLD, COLOR_SUCCESS, COLOR_DANGER, COLOR_BORDER, COLOR_TEXT_MUTED,
    center_window
)

class QRPaymentDialog:
    """Cửa sổ Modal Thanh Toán Chuyển Khoản Ngân Hàng VietQR 24/7"""
    def __init__(self, parent, booking_code: str, amount: float, on_success_callback=None):
        self.parent = parent
        self.booking_code = booking_code
        self.amount = amount
        self.on_success_callback = on_success_callback
        self.is_confirmed = False

        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("CineVerse - Thanh Toán Chuyển Khoản VietQR 24/7")
        self.dialog.geometry("490x690")
        self.dialog.resizable(False, False)
        self.dialog.configure(fg_color=COLOR_BG_DARK)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        center_window(self.dialog, 490, 690)

        self.remaining_seconds = 600  # 10 phút đếm ngược
        self._build_ui()
        self._start_countdown()

    def _generate_qr_image(self) -> ctk.CTkImage:
        """Tạo ảnh mã QR ngân hàng chuẩn VietQR sắc nét (có fallback nếu thiếu thư viện)"""
        if HAS_QRCODE:
            # Payload chuẩn mô phỏng chuyển khoản VietQR
            qr_payload = f"00020101021238540010A000000727012400069704220110090123456789530370454{int(self.amount)}5802VN62180814{self.booking_code}6304ABCD"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=6,
                border=2
            )
            qr.add_data(qr_payload)
            qr.make(fit=True)
            pil_qr = qr.make_image(fill_color="#0b132b", back_color="#ffffff").convert("RGB")
        else:
            # Fallback tạo ảnh QR đồ họa đẹp mắt bằng Pillow
            pil_qr = Image.new("RGB", (200, 200), "#ffffff")
            draw = ImageDraw.Draw(pil_qr)
            draw.rectangle([10, 10, 190, 190], outline="#0b132b", width=4)
            draw.rectangle([25, 25, 65, 65], fill="#0b132b")
            draw.rectangle([135, 25, 175, 65], fill="#0b132b")
            draw.rectangle([25, 135, 65, 175], fill="#0b132b")
            draw.rectangle([85, 85, 115, 115], fill="#003b7a")
            draw.text((38, 100), "VIETQR 24/7", fill="#0b132b")
        return ctk.CTkImage(light_image=pil_qr, dark_image=pil_qr, size=(200, 200))

    def _build_ui(self):
        # 1. Header Bar
        header = ctk.CTkFrame(self.dialog, corner_radius=0, fg_color=COLOR_BG_CARD, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="📱 THANH TOÁN VIETQR 24/7",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color=COLOR_GOLD
        ).pack(side="left", padx=20, pady=16)

        ctk.CTkLabel(
            header,
            text="⚡ CINEVERSE PAY",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color=COLOR_ACCENT
        ).pack(side="right", padx=20, pady=16)

        # 2. Main Content Container
        content = ctk.CTkFrame(self.dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=15)

        # Thẻ trắng chứa mã QR (Tạo độ tương phản cao để camera quét chuẩn 100%)
        qr_card = ctk.CTkFrame(content, corner_radius=16, fg_color="#ffffff", border_width=2, border_color=COLOR_GOLD)
        qr_card.pack(fill="x", pady=(0, 10), ipady=8)

        # Header ngân hàng trong thẻ QR
        bank_header = ctk.CTkFrame(qr_card, fg_color="#003b7a", corner_radius=8, height=36)
        bank_header.pack(fill="x", padx=12, pady=(10, 8))
        bank_header.pack_propagate(False)

        ctk.CTkLabel(
            bank_header,
            text="🏦 MB BANK • NGÂN HÀNG QUÂN ĐỘI (NAPAS 247)",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#ffffff"
        ).pack(expand=True)

        # Ảnh QR Code
        qr_img = self._generate_qr_image()
        lbl_qr = ctk.CTkLabel(qr_card, image=qr_img, text="")
        lbl_qr.pack(pady=4)

        ctk.CTkLabel(
            qr_card,
            text="Quét bằng ứng dụng Ngân hàng hoặc Ví điện tử bất kỳ",
            font=ctk.CTkFont(family="Inter", size=10),
            text_color="#555555"
        ).pack(pady=(0, 6))

        # 3. Thẻ Thông Tin Chuyển Khoản Chi Tiết
        info_card = ctk.CTkFrame(content, corner_radius=14, fg_color=COLOR_BG_CARD, border_width=1, border_color=COLOR_BORDER)
        info_card.pack(fill="x", pady=(0, 10), ipady=6)

        # Grid thông tin
        grid = ctk.CTkFrame(info_card, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=8)

        def add_row(r, label, value, is_highlight=False, color=None):
            ctk.CTkLabel(
                grid, text=label,
                font=ctk.CTkFont(family="Inter", size=11),
                text_color=COLOR_TEXT_MUTED
            ).grid(row=r, column=0, sticky="w", pady=2)

            val_color = color if color else ("#ffffff" if not is_highlight else COLOR_GOLD)
            val_font = ctk.CTkFont(family="Inter", size=12, weight="bold") if is_highlight else ctk.CTkFont(family="Inter", size=11)

            ctk.CTkLabel(
                grid, text=value,
                font=val_font,
                text_color=val_color
            ).grid(row=r, column=1, sticky="e", pady=2)

        add_row(0, "Chủ tài khoản:", "CINEVERSE CINEMA VN")
        add_row(1, "Số tài khoản:", "090123456789 (MB)")
        add_row(2, "Số tiền thanh toán:", f"{self.amount:,.0f} VNĐ", is_highlight=True, color=COLOR_GOLD)
        add_row(3, "Nội dung chuyển khoản:", self.booking_code, is_highlight=True, color=COLOR_ACCENT)

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        # 4. Đồng hồ đếm ngược (Live Countdown)
        self.lbl_timer = ctk.CTkLabel(
            content,
            text="⏱️ Giao dịch hết hạn trong: 10:00",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color=COLOR_GOLD
        )
        self.lbl_timer.pack(pady=(0, 10))

        # 5. Nút Bấm Thao Tác
        btn_box = ctk.CTkFrame(content, fg_color="transparent")
        btn_box.pack(fill="x")

        btn_confirm = ctk.CTkButton(
            btn_box,
            text="✅ TÔI ĐÃ CHUYỂN KHOẢN THÀNH CÔNG",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            corner_radius=12,
            height=42,
            fg_color=COLOR_SUCCESS,
            hover_color="#05b386",
            text_color="#000000",
            cursor="hand2",
            command=self._confirm_payment
        )
        btn_confirm.pack(fill="x", pady=(0, 8))

        btn_cancel = ctk.CTkButton(
            btn_box,
            text="❌ Hủy giao dịch",
            font=ctk.CTkFont(family="Inter", size=12),
            corner_radius=10,
            height=32,
            fg_color=COLOR_BG_CARD,
            hover_color=COLOR_BORDER,
            text_color=COLOR_DANGER,
            cursor="hand2",
            command=self._cancel
        )
        btn_cancel.pack(fill="x")

    def _start_countdown(self):
        """Cập nhật đồng hồ đếm ngược mỗi giây"""
        if self.is_confirmed:
            return

        if self.remaining_seconds <= 0:
            messagebox.showwarning("Hết hạn", "Giao dịch đã hết thời gian chờ thanh toán (10 phút)!")
            self._cancel()
            return

        mins = self.remaining_seconds // 60
        secs = self.remaining_seconds % 60
        self.lbl_timer.configure(text=f"⏱️ Giao dịch hết hạn trong: {mins:02d}:{secs:02d}")
        self.remaining_seconds -= 1
        self.dialog.after(1000, self._start_countdown)

    def _confirm_payment(self):
        """Xác nhận thanh toán thành công"""
        self.is_confirmed = True
        self.dialog.destroy()
        if self.on_success_callback:
            self.on_success_callback()

    def _cancel(self):
        self.is_confirmed = True
        self.dialog.destroy()

