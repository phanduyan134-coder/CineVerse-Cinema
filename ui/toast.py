"""
Module: ui/toast.py
Mô tả: Hệ thống thông báo nổi (Floating Toast Notification) hiện đại cho CINEVERSE.
Thay thế các hộp thoại messagebox pop-up gián đoạn bằng thanh thông báo trượt nhẹ góc trên.
"""

import tkinter as tk
import customtkinter as ctk
from typing import Optional

# Bảng màu chuẩn cho các trạng thái Toast
TOAST_THEMES = {
    "success": {
        "border": "#10b981",       # Emerald Green
        "bg_tint": "#0d281e",
        "icon": "✓",
        "icon_color": "#10b981",
        "default_title": "Thành Công",
        "progress_color": "#10b981"
    },
    "error": {
        "border": "#ef4444",       # Ruby Red
        "bg_tint": "#2a1115",
        "icon": "✕",
        "icon_color": "#ef4444",
        "default_title": "Có Lỗi Xảy Ra",
        "progress_color": "#ef4444"
    },
    "warning": {
        "border": "#f59e0b",       # Amber Gold
        "bg_tint": "#2b1f0c",
        "icon": "!",
        "icon_color": "#f59e0b",
        "default_title": "Cảnh Báo",
        "progress_color": "#f59e0b"
    },
    "info": {
        "border": "#3b82f6",       # Sapphire Blue
        "bg_tint": "#111f38",
        "icon": "i",
        "icon_color": "#60a5fa",
        "default_title": "Thông Báo",
        "progress_color": "#3b82f6"
    }
}

_active_toasts = []

class ToastNotification(ctk.CTkFrame):
    """Component Toast nổi với hiệu ứng trượt êm ái và thanh thời gian tự tắt"""
    def __init__(
        self,
        parent,
        message: str,
        title: Optional[str] = None,
        toast_type: str = "success",
        duration_ms: int = 3200
    ):
        # Lấy cửa sổ toplevel chứa widget
        self.top = parent.winfo_toplevel() if hasattr(parent, "winfo_toplevel") else parent
        theme = TOAST_THEMES.get(toast_type.lower(), TOAST_THEMES["info"])
        self.theme = theme
        self.duration_ms = duration_ms
        self.step_interval = 40  # ms mỗi lần cập nhật progress bar
        self._title = title or theme["default_title"]
        self.remaining_ms = duration_ms
        self._is_destroyed = False

        # Quản lý hàng đợi: nếu có toast cũ, hạ vị trí hoặc dọn dẹp
        global _active_toasts
        # Xóa các toast đã bị destroy khỏi danh sách
        _active_toasts = [t for t in _active_toasts if not t._is_destroyed and t.winfo_exists()]
        
        # Nếu cửa sổ lớn có header (Customer, Staff, Admin >= 900px), neo toast dưới header (y=95)
        top_w = self.top.winfo_width() if hasattr(self.top, "winfo_width") else 1000
        base_y = 95 if top_w >= 900 else 20
        offset_y = base_y + len(_active_toasts) * 82

        super().__init__(
            self.top,
            fg_color="#141419",
            border_width=1,
            border_color=theme["border"],
            corner_radius=14,
            width=360,
            height=68
        )

        _active_toasts.append(self)

        # Content layout
        self._build_content(self._title, message, theme)

        # Animation slide in
        self.target_y = offset_y
        self.current_y = offset_y - 20
        self.place(relx=0.98, y=self.current_y, anchor="ne")
        try:
            self.lift()
        except Exception:
            pass
        self._slide_id = None
        self._timer_id = None
        self._slide_in()

        # Bắt đầu đếm ngược thanh tiến trình
        self._timer_id = self.after(self.step_interval, self._update_timer)

    def _build_content(self, title: str, message: str, theme: dict):
        self.grid_columnconfigure(1, weight=1)

        # Icon tròn vector vẽ bằng Canvas - căn giữa tuyệt đối 100%, không bị che lẹm viền
        icon_canvas = tk.Canvas(self, width=34, height=34, bg="#141419", highlightthickness=0)
        icon_canvas.grid(row=0, column=0, rowspan=2, padx=(14, 10), pady=(10, 8), sticky="w")
        icon_canvas.create_oval(2, 2, 32, 32, outline=theme["border"], width=1.5, fill=theme.get("bg_tint", "#111f38"))
        icon_canvas.create_text(17, 17, text=theme["icon"], font=("Inter", 13, "bold"), fill=theme["icon_color"])

        # Text: Title & Message
        lbl_title = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color="#ffffff",
            anchor="w"
        )
        lbl_title.grid(row=0, column=1, padx=(0, 6), pady=(8, 0), sticky="w")

        lbl_msg = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#9ca3af",
            anchor="w",
            wraplength=250,
            justify="left"
        )
        lbl_msg.grid(row=1, column=1, padx=(0, 6), pady=(0, 8), sticky="w")

        # Close Button (✕)
        btn_close = ctk.CTkButton(
            self,
            text="✕",
            width=22,
            height=22,
            corner_radius=11,
            fg_color="transparent",
            hover_color="#2a2a35",
            text_color="#9ca3af",
            font=ctk.CTkFont(size=11),
            cursor="hand2",
            command=self.dismiss
        )
        btn_close.grid(row=0, column=2, padx=(0, 10), pady=(8, 0), sticky="ne")

        # Mini Progress countdown bar ở cạnh dưới cùng
        self.progress_bar = ctk.CTkProgressBar(
            self,
            height=3,
            corner_radius=0,
            fg_color="#1f1f28",
            progress_color=theme["progress_color"]
        )
        self.progress_bar.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 4))
        self.progress_bar.set(1.0)

    def _slide_in(self):
        if self._is_destroyed or not self.winfo_exists():
            return
        try:
            self.lift()
        except Exception:
            pass
        if self.current_y < self.target_y:
            self.current_y += 4
            self.place_configure(y=self.current_y)
            self._slide_id = self.after(15, self._slide_in)
        else:
            self.place_configure(y=self.target_y)

    def _update_timer(self):
        if self._is_destroyed or not self.winfo_exists():
            return
        self.remaining_ms -= self.step_interval
        if self.remaining_ms <= 0:
            self.dismiss()
        else:
            pct = max(0.0, self.remaining_ms / self.duration_ms)
            self.progress_bar.set(pct)
            self._timer_id = self.after(self.step_interval, self._update_timer)

    def dismiss(self):
        """Đóng toast êm dịu và tự hủy"""
        if self._is_destroyed:
            return
        self._is_destroyed = True
        if self._slide_id:
            try:
                self.after_cancel(self._slide_id)
            except Exception:
                pass
        if self._timer_id:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
        global _active_toasts
        if self in _active_toasts:
            _active_toasts.remove(self)
        try:
            self.destroy()
        except Exception:
            pass


def show_toast(
    parent, 
    message: str, 
    title: Optional[str] = None, 
    toast_type: str = "success", 
    duration_ms: int = 3200
) -> ToastNotification:
    """Hàm tiện ích toàn cục để gọi hiển thị Toast thông báo nhanh chóng"""
    return ToastNotification(parent, message, title=title, toast_type=toast_type, duration_ms=duration_ms)
