# 🌌 ĐỒ ÁN MÔN: KỸ THUẬT LẬP TRÌNH PYTHON
## HỆ THỐNG ĐẶT VÉ XEM PHIM CINEVERSE (MULTIVERSE CINEMA)
> **Slogan:** *"Khám phá đa vũ trụ qua từng khung hình"*

---

### 📌 1. Giới thiệu Đề tài
Dự án là phần mềm Desktop hoàn chỉnh hỗ trợ quy trình đặt vé xem phim và quản lý rạp chiếu phim mang thương hiệu sáng tạo **CINEVERSE (Đa Vũ Trụ Điện Ảnh)** theo phong cách **Sci-Fi / IMAX High-Tech**. 

Hệ thống được thiết kế với **Mô hình Phân quyền 3 Cấp (Role-Based Access Control - RBAC)** hoàn chỉnh:
1. **👑 Quản trị viên (Admin):** Dashboard doanh thu, Quản lý phim, Quản lý suất chiếu, Quản lý toàn bộ vé và **Quản lý phân quyền tài khoản & nhân viên**.
2. **👔 Nhân viên rạp (Staff):** Quầy bán vé tại chỗ (**POS Counter**), Soát vé & Check-in cửa phòng chiếu (**Gate Scanner/Check-in**), Tra cứu & Hủy vé.
3. **👤 Khách hàng (Customer):** Khám phá phim, xem Poster sắc nét & xem Trailer chính thức trên YouTube, tự chọn ghế trên **Màn hình lượng tử (Quantum Screen)**, đặt vé online và xuất vé điện tử **Quantum E-Ticket**.

---

### 🧠 2. Các Kỹ thuật Lập trình Python & OOP Áp dụng (Điểm cộng thuyết trình)

1. **Lập trình Hướng đối tượng & 3 Mẫu thiết kế kinh điển (Design Patterns):**
   - **Kế thừa (Inheritance):** Lớp cơ sở `User` được kế thừa bởi 3 lớp con phân quyền chuyên biệt: `Customer`, `Staff` và `Admin`.
   - **Đóng gói (Encapsulation):** Các thuộc tính của `Movie`, `Room`, `Showtime`, `Seat`, `Booking`, `Concession` được đóng gói an toàn; mật khẩu người dùng được mã hóa bằng thuật toán băm SHA-256 (`hashlib`).
   - **Đa hình (Polymorphism):** Nhận diện đa hình đối tượng người dùng qua `UserFactory` và điều phối giao diện tự động (`AdminWindow`, `StaffWindow`, `CustomerWindow`).
   - **Mẫu Singleton (Creational Pattern):** Đảm bảo duy nhất một đối tượng `DatabaseManager` quản lý kết nối SQLite thread-safe xuyên suốt vòng đời ứng dụng.
   - **Mẫu Factory Method (Creational Pattern):** Lớp `UserFactory` tạo đối tượng người dùng dựa trên trường `role` trong CSDL, mở rộng linh hoạt không làm sửa đổi code hiện tại (Open/Closed Principle).
   - **Mẫu Strategy Pattern (Behavioral Pattern):** Hoán đổi linh hoạt thuật toán tính giá vé (`StandardPricingStrategy`, `StudentDiscountStrategy -10%`, `VipDiamondDiscountStrategy -10%`) thông qua lớp ngữ cảnh `PricingContext`.
2. **Cấu trúc Dữ liệu & Nghiệp vụ Nâng cao:**
   - Sử dụng `Set` (Tập hợp) để kiểm tra va chạm ghế đã đặt trong thời gian thực với độ phức tạp $O(1)$.
   - Giao dịch an toàn (`Transaction Rollback/Commit`) ngăn chặn triệt để tình trạng 2 khách đặt trùng ghế cùng lúc.
   - Nghiệp vụ F&B (Bắp nước & Combo) tích hợp vào đơn đặt vé và hóa đơn POS.
   - Tích hợp cổng thanh toán mã động chuẩn quốc gia **VietQR Napas 24/7**.
   - Thẻ thành viên kỹ thuật số **CineVerse Metallic VIP Pass** tự động tính điểm thưởng, thăng hạng (Bạc, Vàng, Kim Cương) và mã QR cá nhân hóa.
3. **Thiết kế Giao diện Bo Góc Điện Ảnh Cao Cấp (CustomTkinter):**
   - Phong cách **Dark Cinematic Obsidian** (`#0d0d12`), viền Neon Crimson Red (`#ff2a4b`) và Vàng hoàng gia (`#ffd700`).
   - Bố cục **Bento Grid** hiện đại tại Dashboard Admin, biểu đồ doanh thu vẽ thuần Vector Canvas.
   - Thẻ phim **Movie Poster Cards** kèm thumbnail sắc nét và badge độ tuổi điện ảnh chuẩn Việt Nam (`[P]`, `[T13]`, `[T16]`, `[T18]`).
   - Sơ đồ phòng chiếu chia rõ **Lối đi trung tâm (Central Aisle)** và ghế đôi **Sweetbox Cặp Đôi (💑)**.
   - Hệ thống thông báo nổi **Floating Toast Notification** bo góc, vector canvas đếm ngược tự tắt.

---

### 📂 3. Cấu trúc Thư mục Dự án

```text
Cinema/
│
├── assets/
│   └── posters/        # Thư mục chứa ảnh poster phim độ phân giải cao (.png)
│       ├── dune2.png
│       ├── mai.png
│       ├── kungfupanda4.png
│       ├── godzillaxkong.png
│       └── latmat7.png
│
├── database.py         # Quản lý kết nối SQLite, tạo bảng và nạp dữ liệu mẫu ban đầu
├── models.py           # Định nghĩa các lớp Đối tượng OOP (User, Customer, Staff, Admin, Movie, Seat,...)
├── services.py         # Tầng xử lý nghiệp vụ (Đăng nhập, Đặt vé, Soát vé, Thống kê, Quản lý tài khoản)
├── main.py             # Điểm khởi chạy chính & Điều phối luồng giao diện 3 phân quyền
├── test_system.py      # Kịch bản kiểm thử tự động toàn bộ 14 chức năng nghiệp vụ & phân quyền
├── cinema.db           # File Cơ sở dữ liệu SQLite tự động sinh ra khi chạy
│
└── ui/                 # Giao diện đồ họa người dùng (CustomTkinter Bo Góc)
    ├── __init__.py
    ├── styles.py       # Cấu hình bảng màu CINEVERSE Dark Mode, font chữ và kiểu dáng
    ├── login_window.py # Màn hình Đăng nhập & Đăng ký tài khoản bo góc
    ├── customer_window.py # Giao diện Khách hàng: Poster, Trailer, Sơ đồ chọn ghế, Đặt vé, Lịch sử vé
    ├── staff_window.py    # Giao diện Nhân viên: Quầy bán vé POS, Soát vé Check-in, Tra cứu & Hủy vé
    └── admin_window.py    # Giao diện Quản trị viên: Dashboard Thống kê, Quản lý phim, Suất chiếu, Vé, Quản lý tài khoản
```

---

### 🔑 4. Danh sách Tài khoản Thử nghiệm (Sẵn có trong CSDL)

Khi khởi chạy, phần mềm đã tự động nạp sẵn dữ liệu mẫu cho cả 3 nhóm phân quyền:

| Vai trò (Role) | Tên đăng nhập | Mật khẩu | Chức năng & Quyền hạn chính |
| :--- | :--- | :--- | :--- |
| **👑 Quản trị viên (Admin)** | `admin` | `admin123` | Toàn quyền hệ thống: Dashboard Doanh thu, Quản lý phim (Poster/Trailer), Lên lịch chiếu, Quản lý đặt vé, **Cấp tài khoản Nhân viên mới** |
| **👔 Nhân viên (Staff)** | `nhanvien` | `nv123456` | **Quầy POS bán vé tại chỗ**, **Soát vé & Check-in cửa rạp**, Tra cứu vé khách hàng, Hủy/hoàn vé |
| **👤 Khách hàng 1** | `khach1` | `123456` | Đặt vé online, xem Poster & Trailer YouTube, chọn ghế lượng tử, xem lịch sử vé và xuất Quantum E-Ticket |
| **👤 Khách hàng 2** | `khach2` | `123456` | Tài khoản khách hàng mẫu thứ 2 |

*(Bạn cũng có thể tạo thêm tài khoản khách hàng mới trên tab "ĐĂNG KÝ MỚI", hoặc dùng tài khoản `admin` để cấp thêm tài khoản nhân viên `staff`).*

---

### 🚀 5. Hướng dẫn Khởi chạy Phần mềm

Mở cửa sổ dòng lệnh (Terminal / Command Prompt / PowerShell) tại thư mục dự án:

```bash
# 1. Cài đặt các thư viện hỗ trợ giao diện bo góc & ảnh (chỉ cần chạy 1 lần duy nhất):
pip install customtkinter pillow

# 2. Khởi chạy phần mềm CINEVERSE:
python main.py

# 3. Chạy kiểm thử tự động toàn bộ 20 kịch bản hệ thống & Mẫu thiết kế OOP:
python test_system.py
```

---

### 🎯 6. Chi Tiết Các Phân Hệ Chức Năng

#### A. Phân hệ Khách hàng (Customer - `CustomerWindow`)
1. **Đăng nhập & Đăng ký:** Tạo tài khoản bảo mật bằng hàm băm mật khẩu SHA-256.
2. **Khám phá Phim & Xem Poster/Trailer:**
   - Xem danh sách phim đang chiếu, tìm kiếm phim theo tên/thể loại theo thời gian thực.
   - Xem ảnh poster độ nét cao ngay trong bảng chi tiết phim.
   - Nút **`▶️ XEM TRAILER`** click để mở trực tiếp video trailer chính thức trên YouTube.
3. **Lựa chọn Suất chiếu:** Xem danh sách giờ chiếu theo từng phòng chiếu đặc biệt (Nebula 4DX, Galaxy IMAX Laser, Supernova VIP Lounge).
4. **Sơ đồ Ghế tương tác Trực quan:**
   - Màn hình lượng tử (Quantum Screen) uốn lượn phong cách rạp chiếu cao cấp.
   - Click chọn/hủy nhiều ghế cùng lúc, phân loại màu sắc 3 hạng ghế: Nebula, Galaxy VIP, Supernova Sweetbox.
   - Tự động cộng tổng tiền theo hạng ghế được chọn.
5. **Thanh toán & Vé điện tử:** Xuất biên nhận **Quantum E-Ticket** kèm mã vạch bảo mật và mã đặt vé duy nhất.
6. **Lịch sử Đặt vé:** Xem lại toàn bộ danh sách vé đã đặt và mở lại vé điện tử bất kỳ lúc nào.

#### B. Phân hệ Nhân viên (Staff - `StaffWindow`)
1. **Quầy Bán Vé Tại Chỗ (POS Counter):**
   - Giúp nhân viên bán vé trực tiếp cho khách vãng lai mua tại quầy.
   - Chọn phim, chọn suất chiếu, mở sơ đồ ghế trực quan và thu tiền (Tiền mặt, Chuyển khoản QR POS, Thẻ ngân hàng).
2. **Soát Vé & Check-in Cửa Rạp (Gate Check-in):**
   - Ô nhập/quét mã vé (Ví dụ: `VE2026...`) với thẻ kết quả trực quan:
     - 🟢 **Hợp lệ:** Chuyển trạng thái vé sang `Checked-in` (Đã vào rạp), hiển thị tên khách, phòng, suất chiếu, số ghế.
     - 🟡 **Cảnh báo:** Báo động nếu vé này đã được soát vào rạp trước đó.
     - 🔴 **Từ chối:** Báo động nếu mã vé không tồn tại hoặc đã bị hủy.
   - Danh sách vé gần đây với tính năng click đúp soát vé siêu tốc.
3. **Tra cứu & Quản lý Vé:** Tìm kiếm vé theo mã vé/sđt/tên khách, in lại hóa đơn và xử lý hủy/hoàn vé.

#### C. Phân hệ Quản trị viên (Admin - `AdminWindow`)
1. **Dashboard Thống kê Doanh thu:**
   - 4 Thẻ KPI: Tổng Doanh Thu (VNĐ), Tổng Số Vé Đã Bán, Số Lượng Phim Đang Chiếu, Số Lượng Khách Hàng.
   - Bảng báo cáo phân tích doanh thu chi tiết và số vé bán ra của từng bộ phim.
2. **Quản lý Phim Toàn diện:** Thêm phim mới, cập nhật tên phim, thể loại, thời lượng, đạo diễn, tóm tắt, đường dẫn poster và link trailer YouTube.
3. **Quản lý Suất chiếu:** Lên lịch chiếu phim vào từng phòng chiếu với ngày, giờ và giá vé cơ bản.
4. **Quản lý Đơn vé Toàn hệ thống:** Theo dõi toàn bộ các giao dịch đặt vé của khách hàng trong rạp.
5. **Quản lý Tài khoản & Phân quyền (Mới):**
   - Xem danh sách toàn bộ người dùng trong hệ thống (Admin, Staff, Customer).
   - Cấp tài khoản mới cho Nhân viên hoặc Quản trị viên.
   - Xóa tài khoản người dùng vi phạm.
