"""
Module: models.py
Mô tả: Định nghĩa các lớp Đối tượng (OOP Classes) theo mô hình hướng đối tượng:
- Kế thừa (Inheritance): User -> Customer, Staff, Admin
- Đóng gói (Encapsulation): Các thuộc tính và phương thức nghiệp vụ của từng thực thể
- Đa hình (Polymorphism): Các hành vi đặc trưng cho từng loại đối tượng
- Mẫu thiết kế (Design Patterns): Factory Method (UserFactory), Strategy Pattern (PricingStrategy, PricingContext)
"""

from abc import ABC, abstractmethod

class User:
    """Lớp cơ sở Người dùng (Base Class)"""
    def __init__(self, user_id: int, username: str, fullname: str, email: str = "", phone: str = "", role: str = "customer"):
        self.id = user_id
        self.username = username
        self.fullname = fullname
        self.email = email
        self.phone = phone
        self.role = role

    def is_admin(self) -> bool:
        """Đa hình: kiểm tra quyền admin"""
        return self.role == "admin"

    def is_staff(self) -> bool:
        """Đa hình: kiểm tra quyền nhân viên (Staff hoặc Admin)"""
        return self.role in ("staff", "admin")

    def is_customer(self) -> bool:
        """Đa hình: kiểm tra khách hàng thông thường"""
        return self.role == "customer"

    def get_role_display(self) -> str:
        if self.role == "admin":
            return "👑 Quản Trị Viên (Admin)"
        elif self.role == "staff":
            return "👔 Nhân Viên Rạp (Staff)"
        return "👤 Khách Hàng (Customer)"

    def get_display_name(self) -> str:
        return f"{self.fullname} (@{self.username})"

    def __str__(self):
        return f"User({self.username}, Role: {self.role})"


class Customer(User):
    """Lớp Khách hàng (Kế thừa từ User)"""
    def __init__(self, user_id: int, username: str, fullname: str, email: str = "", phone: str = ""):
        super().__init__(user_id, username, fullname, email, phone, role="customer")
        self.membership_points = 0

    def is_admin(self) -> bool:
        return False

    def is_staff(self) -> bool:
        return False

    def is_customer(self) -> bool:
        return True

    def __str__(self):
        return f"Customer({self.fullname} - {self.phone})"


class Staff(User):
    """Lớp Nhân viên rạp (Kế thừa từ User - Bán vé tại quầy & Soát vé)"""
    def __init__(self, user_id: int, username: str, fullname: str, email: str = "", phone: str = ""):
        super().__init__(user_id, username, fullname, email, phone, role="staff")

    def is_admin(self) -> bool:
        return False

    def is_staff(self) -> bool:
        return True

    def is_customer(self) -> bool:
        return False

    def __str__(self):
        return f"Staff({self.fullname} - Nhân viên quầy & soát vé)"


class Admin(User):
    """Lớp Quản trị viên (Kế thừa từ User - Toàn quyền hệ thống)"""
    def __init__(self, user_id: int, username: str, fullname: str, email: str = "", phone: str = ""):
        super().__init__(user_id, username, fullname, email, phone, role="admin")

    def is_admin(self) -> bool:
        return True

    def is_staff(self) -> bool:
        return True

    def is_customer(self) -> bool:
        return False

    def __str__(self):
        return f"Admin({self.fullname} - Toàn quyền quản trị)"


class UserFactory:
    """
    Mẫu thiết kế Factory Method (Factory Method Pattern):
    Đóng gói logic tạo lập các đối tượng con của User (Customer, Staff, Admin)
    dựa vào vai trò (role) được truyền vào, tách biệt hoàn toàn tầng khởi tạo khỏi tầng nghiệp vụ.
    """
    @staticmethod
    def create_user(role: str, user_id: int, username: str, fullname: str, email: str = "", phone: str = "") -> User:
        role_key = (role or "").strip().lower()
        if role_key == "admin":
            return Admin(user_id, username, fullname, email, phone)
        elif role_key == "staff":
            return Staff(user_id, username, fullname, email, phone)
        else:
            return Customer(user_id, username, fullname, email, phone)


class Movie:
    """Lớp Phim"""
    def __init__(self, movie_id: int, title: str, genre: str, duration: int, 
                 director: str = "", description: str = "", release_date: str = "", 
                 poster_path: str = "", trailer_url: str = "", is_active: int = 1):
        self.id = movie_id
        self.title = title
        self.genre = genre
        self.duration = duration  # Phút
        self.director = director
        self.description = description
        self.release_date = release_date
        self.poster_path = poster_path
        self.trailer_url = trailer_url
        self.is_active = bool(is_active)

    def get_duration_formatted(self) -> str:
        hours = self.duration // 60
        mins = self.duration % 60
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"

    def __str__(self):
        return f"{self.title} ({self.genre} - {self.get_duration_formatted()})"


class Room:
    """Lớp Phòng chiếu"""
    def __init__(self, room_id: int, name: str, total_rows: int, total_cols: int):
        self.id = room_id
        self.name = name
        self.total_rows = total_rows
        self.total_cols = total_cols

    @property
    def capacity(self) -> int:
        """Tổng số ghế trong phòng"""
        return self.total_rows * self.total_cols

    def __str__(self):
        return f"{self.name} (Sức chứa: {self.capacity} ghế)"


class Seat:
    """Lớp Ghế ngồi trong hệ thống rạp CINEVERSE (Đa Vũ Trụ Điện Ảnh)"""
    def __init__(self, seat_id: int, room_id: int, row_label: str, seat_num: int, 
                 seat_code: str, seat_type: str = "Nebula"):
        self.id = seat_id
        self.room_id = room_id
        self.row_label = row_label
        self.seat_num = seat_num
        self.seat_code = seat_code
        self.seat_type = seat_type  # 'Nebula' (Chuẩn), 'Galaxy VIP', 'Supernova' (Ghế đôi)

    def is_vip(self) -> bool:
        return "VIP" in self.seat_type.upper() or self.seat_type.upper() == "GALAXY VIP"

    def is_sweetbox(self) -> bool:
        """Ghế Cặp đôi Supernova (Tím hồng vũ trụ ở hàng cuối cùng)"""
        return "SUPERNOVA" in self.seat_type.upper() or "SWEETBOX" in self.seat_type.upper()

    def calculate_price(self, base_price: float) -> float:
        """
        Tính giá vé theo chuẩn CINEVERSE:
        - Ghế Nebula (Thường): Giá gốc
        - Ghế Galaxy VIP: Phụ thu 25.000đ
        - Ghế Cặp đôi Supernova: Phụ thu 50.000đ
        """
        if self.is_sweetbox():
            return base_price + 50000.0
        elif self.is_vip():
            return base_price + 25000.0
        return base_price

    def __str__(self):
        return f"Ghế {self.seat_code} [{self.seat_type}]"


class Showtime:
    """Lớp Suất chiếu"""
    def __init__(self, showtime_id: int, movie_id: int, room_id: int, 
                 show_date: str, show_time: str, base_price: float,
                 movie_title: str = "", room_name: str = ""):
        self.id = showtime_id
        self.movie_id = movie_id
        self.room_id = room_id
        self.show_date = show_date
        self.show_time = show_time
        self.base_price = base_price
        self.movie_title = movie_title
        self.room_name = room_name

    def get_full_schedule(self) -> str:
        return f"{self.show_date} lúc {self.show_time}"

    def __str__(self):
        return f"Suất: {self.movie_title} | {self.room_name} | {self.get_full_schedule()} | {self.base_price:,.0f} VNĐ"


class Booking:
    """Lớp Đơn đặt vé"""
    def __init__(self, booking_id: int, booking_code: str, user_id: int, showtime_id: int,
                 total_amount: float, booking_date: str = "", payment_method: str = "Trực tuyến",
                 status: str = "Confirmed", movie_title: str = "", room_name: str = "", 
                 show_schedule: str = "", seats_str: str = "", concessions_str: str = ""):
        self.id = booking_id
        self.booking_code = booking_code
        self.user_id = user_id
        self.showtime_id = showtime_id
        self.total_amount = total_amount
        self.booking_date = booking_date
        self.payment_method = payment_method
        self.status = status
        # Thông tin bổ sung phục vụ hiển thị
        self.movie_title = movie_title
        self.room_name = room_name
        self.show_schedule = show_schedule
        self.seats_str = seats_str
        self.concessions_str = concessions_str

    def __str__(self):
        fnb_part = f" | Bắp nước: {self.concessions_str}" if self.concessions_str else ""
        return f"Vé #{self.booking_code} - {self.movie_title} - {self.total_amount:,.0f}đ{fnb_part}"


class Concession:
    """Lớp Sản phẩm Bắp Nước & Combo Rạp Phim (OOP Entity)"""
    def __init__(self, item_id: int, name: str, category: str, price: float, 
                 description: str = "", icon: str = "🍿", is_active: bool = True):
        self.id = item_id
        self.name = name
        self.category = category
        self.price = float(price)
        self.description = description
        self.icon = icon
        self.is_active = bool(is_active)

    def get_formatted_price(self) -> str:
        return f"{self.price:,.0f} đ"

    def __str__(self):
        return f"{self.icon} {self.name} ({self.get_formatted_price()})"


# ==============================================================================
# DESIGN PATTERN: STRATEGY PATTERN (Chiến Lược Tính Giá & Chiết Khấu Ưu Đãi)
# ==============================================================================

class PricingStrategy(ABC):
    """
    Mẫu thiết kế Chiến lược (Strategy Pattern) - Lớp cơ sở trừu tượng:
    Định nghĩa thuật toán tính giá vé và chính sách ưu đãi chiết khấu linh hoạt.
    Tuân thủ nguyên lý Open/Closed (Mở rộng thêm chiến lược mới mà không cần sửa code cũ).
    """
    @abstractmethod
    def calculate_seat_price(self, seat: Seat, base_price: float) -> float:
        """Tính giá cho từng vị trí ghế"""
        pass

    @abstractmethod
    def apply_discount(self, subtotal: float) -> tuple[float, str]:
        """Áp dụng chính sách chiết khấu, trả về (tổng_tiền_sau_giảm, mô_tả)"""
        pass


class StandardPricingStrategy(PricingStrategy):
    """Chiến lược giá vé tiêu chuẩn (Khách thông thường)"""
    def calculate_seat_price(self, seat: Seat, base_price: float) -> float:
        return seat.calculate_price(base_price)

    def apply_discount(self, subtotal: float) -> tuple[float, str]:
        return subtotal, "Giá vé tiêu chuẩn (Không áp dụng ưu đãi)"


class StudentPricingStrategy(PricingStrategy):
    """Chiến lược giá Học sinh / Sinh viên: Giảm 10% tiền vé"""
    def calculate_seat_price(self, seat: Seat, base_price: float) -> float:
        return seat.calculate_price(base_price)

    def apply_discount(self, subtotal: float) -> tuple[float, str]:
        discount = subtotal * 0.10
        return subtotal - discount, f"Ưu đãi Học sinh / Sinh viên (-10%: -{discount:,.0f} đ)"


class VIPGoldPricingStrategy(PricingStrategy):
    """Chiến lược giá Hội viên Vàng (Gold Member): Giảm 5% toàn đơn"""
    def calculate_seat_price(self, seat: Seat, base_price: float) -> float:
        return seat.calculate_price(base_price)

    def apply_discount(self, subtotal: float) -> tuple[float, str]:
        discount = subtotal * 0.05
        return subtotal - discount, f"Đặc quyền Hội viên Vàng (-5%: -{discount:,.0f} đ)"


class VIPDiamondPricingStrategy(PricingStrategy):
    """Chiến lược giá Hội viên Kim Cương (Diamond Member): Giảm 10% toàn đơn"""
    def calculate_seat_price(self, seat: Seat, base_price: float) -> float:
        return seat.calculate_price(base_price)

    def apply_discount(self, subtotal: float) -> tuple[float, str]:
        discount = subtotal * 0.10
        return subtotal - discount, f"Đặc quyền Hội viên Kim Cương (-10%: -{discount:,.0f} đ)"


class PricingContext:
    """
    Lớp Ngữ cảnh (Context) trong Strategy Pattern:
    Duy trì tham chiếu đến một đối tượng Strategy và thực hiện tính giá tổng hợp.
    Cho phép hoán đổi chiến lược tính giá linh hoạt ngay trong lúc chương trình đang chạy (Runtime).
    """
    def __init__(self, strategy: PricingStrategy = None):
        self._strategy = strategy or StandardPricingStrategy()

    @property
    def strategy(self) -> PricingStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: PricingStrategy):
        self._strategy = strategy

    def calculate_total(self, seats: list[Seat], base_price: float, fnb_subtotal: float = 0.0) -> tuple[float, float, str]:
        """
        Tính toán tổng thanh toán:
        Trả về (tổng_gốc_chưa_giảm, tổng_sau_khi_áp_dụng_chiến_lược, mô_tả_chiết_khấu)
        """
        seats_subtotal = sum(self._strategy.calculate_seat_price(s, base_price) for s in seats)
        grand_raw = seats_subtotal + fnb_subtotal
        final_total, discount_desc = self._strategy.apply_discount(grand_raw)
        return grand_raw, final_total, discount_desc



