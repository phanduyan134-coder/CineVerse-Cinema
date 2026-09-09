# CINEVERSE — BÁO CÁO THIẾT KẾ KIẾN TRÚC PHẦN MỀM & HỒ SƠ UML HỌC THUẬT

> **Đồ Án**: Hệ Thống Quản Lý & Đặt Vé Xem Phim Đa Vũ Trụ Điện Ảnh (CINEVERSE)  
> **Ngôn ngữ**: Python 3.11+ | **GUI Framework**: CustomTkinter / Tkinter | **CSDL**: SQLite3  
> **Kiến trúc**: 3-Tier Layered Architecture | **Mẫu thiết kế (Design Patterns)**: Singleton, Factory Method, Strategy

---

## 1. TỔNG QUAN KIẾN TRÚC PHÂN TẦNG (3-TIER LAYERED ARCHITECTURE)

Hệ thống được thiết kế theo mô hình **Kiến trúc 3 tầng (3-Tier Architecture)** phân tách độc lập trách nhiệm (Separation of Concerns):
- **Tầng Giao Diện (Presentation Layer)**: Đảm nhận hiển thị, tương tác người dùng, animation, toast và đồ họa Canvas.
- **Tầng Nghiệp Vụ (Business Logic Layer)**: Đảm nhận xử lý thuật toán, kiểm tra nghiệp vụ, chống trùng ghế, xác thực phân quyền và tích lũy điểm thưởng.
- **Tầng Dữ Liệu & Mô Hình Đối Tượng (Data Access & Domain Model Layer)**: Chứa các lớp thực thể OOP thuần túy, mẫu thiết kế khởi tạo/tính giá và quản lý kết nối CSDL tập trung.

```mermaid
graph TD
    subgraph Tier1["TẦNG 1: TRÌNH DIỄN (PRESENTATION LAYER)"]
        UI_Login["ui/login_window.py<br/>(Đăng Nhập / Đăng Ký)"]
        UI_Cust["ui/customer_window.py<br/>(Chọn Suất, Sơ Đồ Ghế, E-Ticket, VIP Pass)"]
        UI_Staff["ui/staff_window.py<br/>(POS Quầy Bán Vé, Máy Tính Tiền, Soát Vé)"]
        UI_Admin["ui/admin_window.py<br/>(Bento KPI, Canvas Chart, CRUD Phim/Lịch/F&B/User)"]
        UI_QR["ui/qr_payment_dialog.py<br/>(VietQR 24/7 Napas Live Countdown)"]
        UI_Toast["ui/toast.py<br/>(Floating Animation Toast)"]
    end

    subgraph Tier2["TẦNG 2: NGHIỆP VỤ HỆ THỐNG (BUSINESS LOGIC LAYER)"]
        Srv_Auth["services.py - AuthService<br/>• login(), register(), create_user()<br/>• Mã hóa SHA-256, Kiểm tra tính hợp lệ"]
        Srv_Cinema["services.py - CinemaService<br/>• book_tickets() (Transaction Isolation, Chống trùng ghế)<br/>• check_in_ticket() (Soát vé 1 chiều)<br/>• get_statistics() (Doanh thu phim, F&B)"]
    end

    subgraph Tier3["TẦNG 3: DỮ LIỆU & MÔ HÌNH OOP (DATA & DOMAIN MODEL LAYER)"]
        Singleton_DB["database.py - DatabaseManager<br/>(Singleton Pattern: Thread-Safe SQLite Connection)"]
        Factory_User["models.py - UserFactory<br/>(Factory Method Pattern: Tạo User đa hình)"]
        Strategy_Price["models.py - PricingStrategy & PricingContext<br/>(Strategy Pattern: Chiết khấu Tiêu Chuẩn / HSSV / VIP)"]
        Entities["models.py - Domain Entities<br/>(User, Customer, Staff, Admin, Movie, Room, Seat, Showtime, Booking, Concession)"]
        DB_File[("cinema.db<br/>(SQLite Database)")]
    end

    Tier1 --> Tier2
    Tier2 --> Tier3
    Singleton_DB --> DB_File
```

---

## 2. SƠ ĐỒ CA SỬ DỤNG (UML USE CASE DIAGRAM)

Hệ thống phục vụ **3 Tác nhân (Actors)** chính trong một chu trình rạp phim khép kín:
1. **Khách Hàng (Customer)**: Đặt vé online, chọn ghế, chọn bắp nước, quét mã QR thanh toán, theo dõi thẻ hội viên VIP.
2. **Nhân Viên Rạp (Staff)**: Xuất vé tại quầy POS, tính tiền thừa, kiểm soát vé vào rạp tại cửa phòng chiếu, tra cứu/hủy vé.
3. **Quản Trị Viên (Admin)**: Toàn quyền quản trị hệ thống, giám sát doanh thu thời gian thực, quản lý phim, lịch chiếu, menu F&B và cấp phát tài khoản.

```mermaid
graph LR
    actor_cust["Khách Hàng (Customer)"]
    actor_staff["Nhân Viên (Staff)"]
    actor_admin["Quản Trị (Admin)"]

    subgraph System["HỆ THỐNG CINEVERSE MULTIVERSE CINEMA"]
        %% Use cases cho Khách hàng
        uc_login["Đăng nhập / Đăng ký tài khoản"]
        uc_search["Tìm kiếm & Xem chi tiết phim, Trailer"]
        uc_book["Chọn Suất chiếu & Sơ đồ ghế ngồi"]
        uc_fnb["Chọn Bắp nước & Combo F&B"]
        uc_pay["Thanh toán chuyển khoản VietQR 24/7"]
        uc_ticket["Xem Vé điện tử Quantum E-Ticket & Xuất file"]
        uc_vip["Theo dõi Thẻ VIP Metallic & Điểm thưởng"]

        %% Use cases cho Nhân viên
        uc_pos["Bán vé & In biên nhận POS tại quầy"]
        uc_cash["Tính tiền thừa nhanh cho khách"]
        uc_checkin["Soát vé cửa phòng chiếu (Barcode / QR)"]
        uc_manage_ticket["Tra cứu, In lại hoặc Hủy vé hoàn tiền"]

        %% Use cases cho Admin
        uc_kpi["Theo dõi Dashboard Bento KPI Doanh Thu"]
        uc_chart["Xem Biểu đồ Doanh thu & Tỉ lệ đóng góp"]
        uc_crud_movie["Quản lý Danh mục Phim (CRUD)"]
        uc_crud_st["Quản lý Suất Chiếu (CRUD)"]
        uc_crud_fnb["Quản lý Menu Bắp Nước & Combo (CRUD)"]
        uc_crud_user["Quản lý & Cấp tài khoản nhân viên (CRUD)"]
    end

    actor_cust --> uc_login
    actor_cust --> uc_search
    actor_cust --> uc_book
    uc_book -.->|<<include>>| uc_fnb
    uc_book -.->|<<include>>| uc_pay
    uc_pay -.->|<<include>>| uc_ticket
    actor_cust --> uc_vip

    actor_staff --> uc_login
    actor_staff --> uc_pos
    uc_pos -.->|<<include>>| uc_cash
    actor_staff --> uc_checkin
    actor_staff --> uc_manage_ticket

    actor_admin --> uc_login
    actor_admin --> uc_kpi
    actor_admin --> uc_chart
    actor_admin --> uc_crud_movie
    actor_admin --> uc_crud_st
    actor_admin --> uc_crud_fnb
    actor_admin --> uc_crud_user
```

---

## 3. SƠ ĐỒ LỚP TỔNG THỂ (UML CLASS DIAGRAM)

Sơ đồ lớp chi tiết dưới đây thể hiện trọn vẹn:
- Quan hệ **Kế thừa (Inheritance)** từ `User` sang `Customer`, `Staff`, `Admin`.
- Mẫu thiết kế **Factory Method**: `UserFactory` khởi tạo các đối tượng User đa hình.
- Mẫu thiết kế **Strategy**: `PricingStrategy` và các hiện thực hóa cụ thể (`StandardPricingStrategy`, `StudentPricingStrategy`, `VIPGoldPricingStrategy`, `VIPDiamondPricingStrategy`), được bao đóng bởi `PricingContext`.
- Mẫu thiết kế **Singleton**: `DatabaseManager` bảo đảm duy nhất một thể hiện kết nối an toàn đa luồng.
- Các quan hệ **Kết tập (Aggregation)** và **Thành phần (Composition)** giữa `Booking`, `Seat`, `Showtime`, `Movie`, `Room`, `Concession`.

```mermaid
classDiagram
    %% Singleton Database Manager
    class DatabaseManager {
        -static _instance: DatabaseManager
        -static _lock: Lock
        +db_path: str
        +__new__(cls) DatabaseManager
        +get_connection() Connection
    }

    %% User Hierarchy (Inheritance & Polymorphism)
    class User {
        <<abstract>>
        +id: int
        +username: str
        +fullname: str
        +email: str
        +phone: str
        +role: str
        +is_admin() bool
        +is_staff() bool
        +is_customer() bool
        +get_role_display() str
    }

    class Customer {
        +membership_points: int
        +is_customer() bool
    }

    class Staff {
        +is_staff() bool
    }

    class Admin {
        +is_admin() bool
        +is_staff() bool
    }

    User <|-- Customer : Kế thừa
    User <|-- Staff : Kế thừa
    User <|-- Admin : Kế thừa

    %% Factory Method Pattern
    class UserFactory {
        <<Factory>>
        +static create_user(role, user_id, username, fullname, email, phone) User
    }
    UserFactory ..> User : Khởi tạo (Creates)

    %% Strategy Pattern for Pricing & Discounts
    class PricingStrategy {
        <<abstract>>
        +calculate_seat_price(seat: Seat, base_price: float)* float
        +apply_discount(subtotal: float)* tuple[float, str]
    }

    class StandardPricingStrategy {
        +calculate_seat_price(seat, base_price) float
        +apply_discount(subtotal) tuple[float, str]
    }

    class StudentPricingStrategy {
        +calculate_seat_price(seat, base_price) float
        +apply_discount(subtotal) tuple[float, str]
    }

    class VIPGoldPricingStrategy {
        +calculate_seat_price(seat, base_price) float
        +apply_discount(subtotal) tuple[float, str]
    }

    class VIPDiamondPricingStrategy {
        +calculate_seat_price(seat, base_price) float
        +apply_discount(subtotal) tuple[float, str]
    }

    class PricingContext {
        <<Context>>
        -strategy: PricingStrategy
        +set_strategy(strategy: PricingStrategy)
        +calculate_total(seats, base_price, fnb_subtotal) tuple[float, float, str]
    }

    PricingStrategy <|-- StandardPricingStrategy : Hiện thực
    PricingStrategy <|-- StudentPricingStrategy : Hiện thực
    PricingStrategy <|-- VIPGoldPricingStrategy : Hiện thực
    PricingStrategy <|-- VIPDiamondPricingStrategy : Hiện thực
    PricingContext o-- PricingStrategy : Sử dụng (Aggregation)

    %% Domain Entities
    class Movie {
        +id: int
        +title: str
        +genre: str
        +duration: int
        +director: str
        +release_date: str
        +poster_path: str
        +trailer_url: str
        +is_active: bool
        +get_duration_formatted() str
    }

    class Room {
        +id: int
        +name: str
        +total_rows: int
        +total_cols: int
        +capacity int
    }

    class Seat {
        +id: int
        +room_id: int
        +row_label: str
        +seat_num: int
        +seat_code: str
        +seat_type: str
        +is_vip() bool
        +is_sweetbox() bool
        +calculate_price(base_price: float) float
    }

    class Showtime {
        +id: int
        +movie_id: int
        +room_id: int
        +show_date: str
        +show_time: str
        +base_price: float
        +get_full_schedule() str
    }

    class Booking {
        +id: int
        +booking_code: str
        +user_id: int
        +showtime_id: int
        +total_amount: float
        +booking_date: str
        +payment_method: str
        +status: str
        +movie_title: str
        +room_name: str
        +show_schedule: str
        +seats_str: str
        +concessions_str: str
    }

    class Concession {
        +id: int
        +name: str
        +category: str
        +price: float
        +description: str
        +icon: str
        +is_active: bool
        +get_formatted_price() str
    }

    %% Entity Relationships
    Showtime o-- Movie : Tham chiếu Phim
    Showtime o-- Room : Tham chiếu Phòng chiếu
    Room "1" *-- "many" Seat : Chứa các ghế
    Booking "1" *-- "many" Seat : Đặt các ghế
    Booking o-- Showtime : Thuộc suất chiếu
    Booking o-- Customer : Khách sở hữu
    Booking o-- Concession : Kèm bắp nước
```

---

## 4. SƠ ĐỒ TRÌNH TỰ (UML SEQUENCE DIAGRAMS)

### 4.1. Luồng 1: Quy Trình Đặt Vé, Tính Giá Chiến Lược (Strategy) & Thanh Toán VietQR

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Khách Hàng (User)
    participant UI as CustomerWindow (UI)
    participant Service as CinemaService
    participant Context as PricingContext
    participant Strategy as PricingStrategy
    participant DB as SQLite Database
    participant QR as QRPaymentDialog

    Customer ->> UI: Chọn ghế (C3, C4) & Bắp nước (Pepsi, Bắp Caramel)
    Customer ->> UI: Nhấn "💳 XÁC NHẬN THANH TOÁN"
    UI ->> QR: Mở Popup VietQR 24/7 (Live Countdown 10:00)
    Customer ->> QR: Quét App Ngân hàng & Bấm "TÔI ĐÃ CHUYỂN KHOẢN"
    QR -->> UI: Callback Xác Nhận Thanh Toán Thành Công
    UI ->> Service: book_tickets(user_id, showtime_id, seats, concessions, pricing_strategy)
    
    rect rgb(20, 25, 45)
        Note over Service, DB: TRANSACTION ISOLATION (CHỐNG TRÙNG GHẾ)
        Service ->> DB: BEGIN TRANSACTION
        Service ->> DB: SELECT seat_code FROM bookings WHERE status='Confirmed'
        DB -->> Service: Danh sách ghế đã bán
        Service ->> Context: calculate_total(seats, base_price, fnb_amount)
        Context ->> Strategy: calculate_seat_price(seat, base_price)
        Strategy -->> Context: Giá ghế theo phân loại (Standard/VIP/Sweetbox)
        Context ->> Strategy: apply_discount(subtotal)
        Strategy -->> Context: (tổng_sau_giảm, mô_tả_ưu_đãi)
        Context -->> Service: grand_total

        Service ->> DB: INSERT INTO bookings (booking_code, total_amount, payment_method, ...)
        Service ->> DB: INSERT INTO booking_details (booking_id, seat_id, ...)
        Service ->> DB: INSERT INTO booking_concessions (booking_id, concession_id, ...)
        Service ->> DB: COMMIT TRANSACTION
    end

    Service -->> UI: (True, "Đặt vé thành công!", booking_obj)
    UI ->> UI: show_toast("Đặt vé thành công!", "success")
    UI ->> Customer: Hiển thị Vé Điện Tử (Quantum E-Ticket) + Tùy chọn Xuất File .txt
```

---

### 4.2. Luồng 2: Quy Trình Soát Vé Cửa Rạp & Chống Vé Gian Lận Trùng Lặp

```mermaid
sequenceDiagram
    autonumber
    actor Staff as Nhân Viên Soát Vé
    participant UI as StaffWindow (Check-in Tab)
    participant Service as CinemaService
    participant DB as SQLite Database
    participant Toast as Floating Toast Notification

    Staff ->> UI: Quét hoặc nhập mã vé "VE20260908xxxx"
    Staff ->> UI: Nhấn "🚀 KIỂM TRA & SOÁT VÉ"
    UI ->> Service: check_in_ticket(booking_code)
    
    Service ->> DB: SELECT * FROM bookings WHERE booking_code = ?
    DB -->> Service: Bản ghi thông tin vé (status)

    alt Vé không tồn tại
        Service -->> UI: (False, "❌ TỪ CHỐI: MÃ VÉ KHÔNG TỒN TẠI!")
        UI ->> Toast: show_toast(msg, "error")
    else Vé đã bị hủy (Cancelled)
        Service -->> UI: (False, "❌ TỪ CHỐI: VÉ NÀY ĐÃ BỊ HỦY / HOÀN TIỀN!")
        UI ->> Toast: show_toast(msg, "error")
    else Vé đã check-in trước đó (Checked-in)
        Service -->> UI: (False, "⚠️ CẢNH BÁO: VÉ ĐÃ ĐƯỢC SOÁT VÀO RẠP TRƯỚC ĐÓ!")
        UI ->> Toast: show_toast(msg, "warning")
    else Vé hợp lệ lần đầu (Confirmed)
        Service ->> DB: UPDATE bookings SET status = 'Checked-in' WHERE id = ?
        DB -->> Service: Update OK
        Service -->> UI: (True, "✓ SOÁT VÉ HỢP LỆ! Mời khách vào phòng chiếu.")
        UI ->> Toast: show_toast(msg, "success")
        UI ->> UI: Cập nhật thẻ trạng thái xanh ngọc + Bảng lịch sử vé gần đây
    end
```

---

## 5. THUYẾT MINH CHUYÊN SÂU 3 MẪU THIẾT KẾ (DESIGN PATTERNS DEEP-DIVE)

### 5.1. Mẫu Thiết Kế Singleton (Singleton Pattern)
- **Vị trí**: [`database.py`](file:///d:/IT/Python/Cinema/database.py) — Lớp `DatabaseManager`.
- **Vấn đề giải quyết**: Tránh việc mở kết nối rải rác, gây tốn tài nguyên hệ điều hành hoặc xung đột file SQLite khi nhiều luồng truy cập đồng thời.
- **Cách thức hiện thực**:
  - Ghi đè phương thức `__new__` của Python.
  - Sử dụng biến tĩnh `_instance` lưu giữ thể hiện duy nhất.
  - Áp dụng `threading.Lock()` theo kỹ thuật **Double-Checked Locking** bảo đảm an toàn đa luồng tuyệt đối.
- **Đoạn code minh chứng**:
  ```python
  class DatabaseManager:
      _instance = None
      _lock = threading.Lock()

      def __new__(cls, *args, **kwargs):
          if not cls._instance:
              with cls._lock:
                  if not cls._instance:
                      cls._instance = super().__new__(cls)
                      cls._instance.db_path = DB_NAME
          return cls._instance
  ```

---

### 5.2. Mẫu Thiết Kế Factory Method (Factory Method Pattern)
- **Vị trí**: [`models.py`](file:///d:/IT/Python/Cinema/models.py) — Lớp `UserFactory`.
- **Vấn đề giải quyết**: Tách rời tầng khởi tạo người dùng khỏi tầng nghiệp vụ và tầng CSDL. Thay vì viết các câu lệnh `if-elif-else` phân nhánh rải rác ở khắp các tệp `services.py`, toàn bộ logic phân quyền đối tượng con được gom về một đầu mối tập trung.
- **Nguyên lý SOLID đáp ứng**: **Single Responsibility Principle (SRP)** — Chỉ có `UserFactory` chịu trách nhiệm quyết định khởi tạo lớp người dùng nào.
- **Đoạn code minh chứng**:
  ```python
  class UserFactory:
      @staticmethod
      def create_user(role: str, user_id: int, username: str, fullname: str, email: str = "", phone: str = "") -> User:
          role_key = (role or "").strip().lower()
          if role_key == "admin":
              return Admin(user_id, username, fullname, email, phone)
          elif role_key == "staff":
              return Staff(user_id, username, fullname, email, phone)
          else:
              return Customer(user_id, username, fullname, email, phone)
  ```

---

### 5.3. Mẫu Thiết Kế Chiến Lược (Strategy Pattern)
- **Vị trí**: [`models.py`](file:///d:/IT/Python/Cinema/models.py) — `PricingStrategy`, `PricingContext`.
- **Vấn đề giải quyết**: Rạp chiếu phim thường xuyên thay đổi chính sách giá vé và ưu đãi (Giá tiêu chuẩn, Giảm giá Học sinh/Sinh viên 10%, Chiết khấu Hội viên Vàng 5%, Hội viên Kim Cương 10%, hoặc các đợt flash sale). Nếu dùng các câu lệnh `if-else` lồng nhau trong hàm đặt vé thì code sẽ bị phình to, dễ phát sinh lỗi (Code Smell).
- **Nguyên lý SOLID đáp ứng**:
  - **Open/Closed Principle (OCP)**: Hệ thống mở để mở rộng thêm các chiến lược giá mới (như `CouponPricingStrategy`, `MidnightPricingStrategy`) nhưng đóng với việc sửa đổi mã nguồn nghiệp vụ `CinemaService.book_tickets`.
  - **Dependency Inversion Principle (DIP)**: `PricingContext` và `CinemaService` phụ thuộc vào lớp trừu tượng `PricingStrategy`, không phụ thuộc vào các lớp cụ thể.
- **Đoạn code minh chứng**:
  ```python
  class PricingStrategy(ABC):
      @abstractmethod
      def calculate_seat_price(self, seat: Seat, base_price: float) -> float:
          pass

      @abstractmethod
      def apply_discount(self, subtotal: float) -> tuple[float, str]:
          pass

  class PricingContext:
      def __init__(self, strategy: PricingStrategy = None):
          self._strategy = strategy or StandardPricingStrategy()

      def calculate_total(self, seats: list[Seat], base_price: float, fnb_subtotal: float = 0.0):
          seats_subtotal = sum(self._strategy.calculate_seat_price(s, base_price) for s in seats)
          grand_raw = seats_subtotal + fnb_subtotal
          final_total, discount_desc = self._strategy.apply_discount(grand_raw)
          return grand_raw, final_total, discount_desc
  ```

---

## 6. ĐỐI SOÁT CÁC NGUYÊN LÝ THIẾT KẾ SOLID

| Nguyên lý SOLID | Cách áp dụng trong kiến trúc CINEVERSE | Lợi ích thu được |
| :--- | :--- | :--- |
| **S - Single Responsibility** *(Đơn trách nhiệm)* | `models.py` chỉ chứa thực thể; `services.py` chỉ xử lý nghiệp vụ; `ui/` chỉ vẽ giao diện; `UserFactory` chỉ khởi tạo user; `DatabaseManager` chỉ kết nối CSDL. | Dễ đọc, dễ bảo trì, cô lập lỗi nhanh chóng. |
| **O - Open/Closed** *(Mở rộng / Đóng sửa đổi)* | Bổ sung thêm chiến lược giá vé mới (`SeniorPricingStrategy`, `VoucherStrategy`) chỉ cần tạo class mới kế thừa `PricingStrategy`, không sửa 1 dòng code nào trong `book_tickets`. | Mở rộng tính năng an toàn, không sinh lỗi hồi quy. |
| **L - Liskov Substitution** *(Thay thế Liskov)* | Mọi lớp con của `User` (`Customer`, `Staff`, `Admin`) đều có thể thay thế cho `User` mà không làm thay đổi tính đúng đắn của chương trình. | Tận dụng triệt để tính đa hình (Polymorphism). |
| **I - Interface Segregation** *(Phân tách giao diện)* | `PricingStrategy` chỉ có 2 phương thức tinh gọn (`calculate_seat_price`, `apply_discount`), không bắt các lớp con hiện thực các phương thức thừa thãi. | Các lớp con gọn gàng, rõ ràng. |
| **D - Dependency Inversion** *(Đảo ngược phụ thuộc)* | `CinemaService` và `PricingContext` phụ thuộc vào Interface trừu tượng `PricingStrategy` chứ không gắn chặt vào lớp cụ thể. | Giảm mức độ phụ thuộc (Decoupling) tối đa. |

