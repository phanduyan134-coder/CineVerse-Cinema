-- ====================================================================
-- KỊCH BẢN KHỞI TẠO CƠ SỞ DỮ LIỆU CINEVERSE (MICROSOFT SQL SERVER)
-- Đồ Án Chuyên Đề Python & Cơ Sở Dữ Liệu SQL Server
-- Hệ Thống Quản Lý & Đặt Vé Xem Phim CineVerse
-- ====================================================================

USE master;
GO

-- 1. XÓA CƠ SỞ DỮ LIỆU CŨ NẾU ĐÃ TỒN TẠI VÀ TẠO MỚI
IF EXISTS (SELECT name FROM sys.databases WHERE name = N'CineVerse')
BEGIN
    ALTER DATABASE CineVerse SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE CineVerse;
END
GO

CREATE DATABASE CineVerse COLLATE Vietnamese_CI_AS;
GO

USE CineVerse;
GO

-- ====================================================================
-- 2. TẠO CẤU TRÚC CÁC BẢNG DỮ LIỆU (DDL)
-- ====================================================================

-- 2.1. Bảng Người dùng (Users): Phân quyền Admin, Staff (Nhân viên), Customer (Khách hàng)
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) UNIQUE NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    fullname NVARCHAR(100) NOT NULL,
    email NVARCHAR(100),
    phone NVARCHAR(20),
    role NVARCHAR(20) NOT NULL DEFAULT 'customer', -- 'admin', 'staff', 'customer'
    created_at DATETIME DEFAULT GETDATE(),
    CONSTRAINT CK_users_role CHECK (role IN ('admin', 'staff', 'customer'))
);
GO

-- 2.2. Bảng Danh mục Phim (Movies)
CREATE TABLE movies (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(255) NOT NULL,
    genre NVARCHAR(100) NOT NULL,
    duration INT NOT NULL, -- Thời lượng tính bằng phút
    director NVARCHAR(100),
    description NVARCHAR(MAX),
    release_date NVARCHAR(20),
    poster_path NVARCHAR(255) DEFAULT '',
    trailer_url NVARCHAR(255) DEFAULT '',
    is_active INT DEFAULT 1, -- 1: Đang chiếu, 0: Ngừng chiếu
    CONSTRAINT CK_movies_duration CHECK (duration > 0)
);
GO

-- 2.3. Bảng Phòng chiếu (Rooms)
CREATE TABLE rooms (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    total_rows INT NOT NULL, -- Số hàng (ví dụ: 6 hàng A -> F)
    total_cols INT NOT NULL,  -- Số ghế mỗi hàng (ví dụ: 8)
    CONSTRAINT CK_rooms_dimensions CHECK (total_rows > 0 AND total_cols > 0)
);
GO

-- 2.4. Bảng Ghế ngồi (Seats)
CREATE TABLE seats (
    id INT IDENTITY(1,1) PRIMARY KEY,
    room_id INT NOT NULL FOREIGN KEY REFERENCES rooms(id) ON DELETE CASCADE,
    row_label NVARCHAR(10) NOT NULL,  -- A, B, C, ...
    seat_num INT NOT NULL,            -- 1, 2, 3, ...
    seat_code NVARCHAR(10) NOT NULL,  -- A1, A2, B3...
    seat_type NVARCHAR(50) NOT NULL DEFAULT 'Standard', -- 'Standard', 'VIP', 'Nebula', 'Galaxy VIP', 'Supernova'
    CONSTRAINT UQ_room_seat UNIQUE (room_id, seat_code),
    CONSTRAINT CK_seats_num CHECK (seat_num > 0)
);
GO

-- 2.5. Bảng Suất chiếu (Showtimes)
CREATE TABLE showtimes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    movie_id INT NOT NULL FOREIGN KEY REFERENCES movies(id) ON DELETE CASCADE,
    room_id INT NOT NULL FOREIGN KEY REFERENCES rooms(id) ON DELETE CASCADE,
    show_date NVARCHAR(20) NOT NULL,  -- Định dạng YYYY-MM-DD
    show_time NVARCHAR(20) NOT NULL,  -- Định dạng HH:MM (vd: 19:30)
    base_price FLOAT NOT NULL,         -- Giá vé cơ bản (VNĐ)
    CONSTRAINT CK_showtimes_price CHECK (base_price >= 0)
);
GO

-- 2.6. Bảng Đơn Đặt Vé (Bookings)
CREATE TABLE bookings (
    id INT IDENTITY(1,1) PRIMARY KEY,
    booking_code NVARCHAR(50) UNIQUE NOT NULL, -- Mã vé duy nhất (vd: VE202609081234)
    user_id INT NOT NULL FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE,
    showtime_id INT NOT NULL FOREIGN KEY REFERENCES showtimes(id) ON DELETE CASCADE,
    total_amount FLOAT NOT NULL,
    booking_date DATETIME DEFAULT GETDATE(),
    payment_method NVARCHAR(100) DEFAULT N'Tiền mặt / Trực tuyến',
    status NVARCHAR(50) DEFAULT 'Confirmed',   -- 'Confirmed', 'Checked-in', 'Cancelled'
    CONSTRAINT CK_bookings_amount CHECK (total_amount >= 0),
    CONSTRAINT CK_bookings_status CHECK (status IN ('Confirmed', 'Checked-in', 'Cancelled'))
);
GO

-- 2.7. Bảng Chi tiết Ghế Đã Đặt (Booking Details)
CREATE TABLE booking_details (
    id INT IDENTITY(1,1) PRIMARY KEY,
    booking_id INT NOT NULL FOREIGN KEY REFERENCES bookings(id) ON DELETE CASCADE,
    seat_id INT NOT NULL FOREIGN KEY REFERENCES seats(id),
    seat_code NVARCHAR(10) NOT NULL,
    price FLOAT NOT NULL,
    CONSTRAINT CK_booking_details_price CHECK (price >= 0)
);
GO

-- 2.8. Bảng Sản phẩm Bắp Nước (Concessions / F&B)
CREATE TABLE concessions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    category NVARCHAR(50) NOT NULL, -- 'Combo', 'Bắp', 'Nước'
    price FLOAT NOT NULL,
    description NVARCHAR(255),
    icon NVARCHAR(20) DEFAULT N'🍿',
    is_active INT DEFAULT 1,        -- 1: Đang bán, 0: Tạm ngưng
    CONSTRAINT CK_concessions_price CHECK (price >= 0)
);
GO

-- 2.9. Bảng Bắp Nước của Đơn Đặt (Booking Concessions)
CREATE TABLE booking_concessions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    booking_id INT NOT NULL FOREIGN KEY REFERENCES bookings(id) ON DELETE CASCADE,
    concession_id INT NOT NULL FOREIGN KEY REFERENCES concessions(id),
    concession_name NVARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    price FLOAT NOT NULL,
    CONSTRAINT CK_booking_concessions_qty CHECK (quantity > 0 AND price >= 0)
);
GO

-- 2.10. Bảng Nhật Ký Thay Đổi Trạng Thái Vé (Audit Log - Phục vụ Trigger)
CREATE TABLE booking_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    booking_id INT NOT NULL FOREIGN KEY REFERENCES bookings(id) ON DELETE CASCADE,
    old_status NVARCHAR(50),
    new_status NVARCHAR(50),
    changed_at DATETIME DEFAULT GETDATE(),
    action_note NVARCHAR(255)
);
GO

-- 2.11. Chỉ Mục Tối Ưu Hóa Truy Vấn (Non-Clustered Indexes - Tối ưu O(log N))
CREATE NONCLUSTERED INDEX IX_bookings_user_id ON bookings(user_id);
CREATE NONCLUSTERED INDEX IX_bookings_showtime_id ON bookings(showtime_id);
CREATE NONCLUSTERED INDEX IX_bookings_code ON bookings(booking_code);
CREATE NONCLUSTERED INDEX IX_booking_details_booking_id ON booking_details(booking_id);
CREATE NONCLUSTERED INDEX IX_showtimes_movie_date ON showtimes(movie_id, show_date);
CREATE NONCLUSTERED INDEX IX_seats_room_id ON seats(room_id);
GO

-- ====================================================================
-- 3. NẠP DỮ LIỆU MẪU BAN ĐẦU (SEED DATA - DML)
-- ====================================================================

-- 3.1. Người dùng mẫu (Mật khẩu đã mã hóa SHA-256)
-- admin / admin123  -> 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
-- nhanvien / nv123456 -> a5d21a2fa99d15d6c13d848008559574fd222b2a51415c72abf3bae221c41f71
-- khach1, khach2 / 123456 -> 8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92
INSERT INTO users (username, password_hash, fullname, email, phone, role)
VALUES 
(N'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', N'Quản Trị Viên CineVerse', N'admin@cineverse.vn', N'0901234567', N'admin'),
(N'nhanvien', 'a5d21a2fa99d15d6c13d848008559574fd222b2a51415c72abf3bae221c41f71', N'Nguyễn Văn Thu Ngân', N'staff@cineverse.vn', N'0933445566', N'staff'),
(N'khach1', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', N'Nguyễn Văn An', N'an.nguyen@gmail.com', N'0912345678', N'customer'),
(N'khach2', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', N'Trần Thị Bình', N'binh.tran@gmail.com', N'0987654321', N'customer');
GO

-- 3.2. Phòng chiếu mẫu CINEVERSE
INSERT INTO rooms (name, total_rows, total_cols)
VALUES 
(N'Hall 01 - Quantum IMAX (CineVerse)', 6, 8),
(N'Hall 02 - Nebula 4DX (CineVerse)', 5, 8);
GO

-- 3.3. Ghế ngồi cho từng phòng (Hàng cuối Supernova, giữa VIP/Galaxy, đầu Nebula/Standard)
DECLARE @room1_id INT = (SELECT TOP 1 id FROM rooms WHERE name LIKE N'%Hall 01%');
DECLARE @room2_id INT = (SELECT TOP 1 id FROM rooms WHERE name LIKE N'%Hall 02%');

-- Phòng 1: 6 hàng A -> F, 8 ghế mỗi hàng
DECLARE @rows1 VARCHAR(6) = 'ABCDEF';
DECLARE @r INT = 1;
WHILE @r <= 6
BEGIN
    DECLARE @letter CHAR(1) = SUBSTRING(@rows1, @r, 1);
    DECLARE @c INT = 1;
    DECLARE @stype NVARCHAR(50) = CASE 
        WHEN @r = 6 THEN N'Supernova'
        WHEN @r >= 3 THEN N'Galaxy VIP'
        ELSE N'Nebula'
    END;

    WHILE @c <= 8
    BEGIN
        INSERT INTO seats (room_id, row_label, seat_num, seat_code, seat_type)
        VALUES (@room1_id, @letter, @c, @letter + CAST(@c AS VARCHAR(2)), @stype);
        SET @c = @c + 1;
    END
    SET @r = @r + 1;
END

-- Phòng 2: 5 hàng A -> E, 8 ghế mỗi hàng
DECLARE @rows2 VARCHAR(5) = 'ABCDE';
SET @r = 1;
WHILE @r <= 5
BEGIN
    DECLARE @letter2 CHAR(1) = SUBSTRING(@rows2, @r, 1);
    DECLARE @c2 INT = 1;
    DECLARE @stype2 NVARCHAR(50) = CASE 
        WHEN @r = 5 THEN N'Supernova'
        WHEN @r >= 3 THEN N'Galaxy VIP'
        ELSE N'Nebula'
    END;

    WHILE @c2 <= 8
    BEGIN
        INSERT INTO seats (room_id, row_label, seat_num, seat_code, seat_type)
        VALUES (@room2_id, @letter2, @c2, @letter2 + CAST(@c2 AS VARCHAR(2)), @stype2);
        SET @c2 = @c2 + 1;
    END
    SET @r = @r + 1;
END
GO

-- 3.4. Danh sách phim mẫu CINEVERSE kèm Poster và Trailer YouTube
INSERT INTO movies (title, genre, duration, director, description, release_date, poster_path, trailer_url, is_active)
VALUES 
(
    N'[T18] Mai',
    N'Tâm lý, Tình cảm (18+)',
    131,
    N'Trấn Thành',
    N'Một câu chuyện tình cảm sâu sắc, đầy trắc trở giữa Mai và Dương tại khu chung cư cũ.',
    N'2024-02-10',
    N'assets/posters/mai.png',
    N'https://www.youtube.com/watch?v=kY3P988Fw-M',
    1
),
(
    N'[T16] Dune: Hành Tinh Cát 2',
    N'Khoa học viễn tưởng, IMAX',
    166,
    N'Denis Villeneuve',
    N'Paul Atreides gia nhập cùng người Fremen để giải phóng hành tinh Arrakis và báo thù cho gia tộc.',
    N'2024-03-01',
    N'assets/posters/dune2.png',
    N'https://www.youtube.com/watch?v=Way9Dexny3w',
    1
),
(
    N'[P] Kung Fu Panda 4',
    N'Hoạt hình, Gia đình',
    94,
    N'Mike Mitchell',
    N'Po bước vào hành trình mới để trở thành Thủ Lĩnh Tinh Thần và tìm kiếm một Thần Long Đại Hiệp kế nhiệm.',
    N'2024-03-08',
    N'assets/posters/kungfupanda4.png',
    N'https://www.youtube.com/watch?v=_inKs4eeHiI',
    1
),
(
    N'[T13] Godzilla x Kong: Đế Chế Mới',
    N'Hành động, Viễn tưởng, 3D',
    115,
    N'Adam Wingard',
    N'Hai quái thú huyền thoại Godzilla và Kong bắt tay chống lại một mối đe dọa khổng lồ bí ẩn từ Trái Đất rỗng.',
    N'2024-04-12',
    N'assets/posters/godzillaxkong.png',
    N'https://www.youtube.com/watch?v=lV1OOlGwExg',
    1
),
(
    N'[P] Lật Mặt 7: Một Điều Ước',
    N'Gia đình, Tâm lý',
    138,
    N'Lý Hải',
    N'Câu chuyện xúc động về tình mẫu tử của người mẹ già cùng nỗi trăn trở của những người con.',
    N'2024-04-26',
    N'assets/posters/latmat7.png',
    N'https://www.youtube.com/watch?v=0hC-U7x_d5o',
    1
);
GO

-- 3.5. Sản phẩm Bắp Nước (F&B Concessions)
INSERT INTO concessions (name, category, price, description, icon, is_active)
VALUES 
(N'Combo Solo CineVerse', N'Combo', 89000, N'1 Bắp ngọt lớn (L) + 1 Nước ngọt có gas (L)', N'🍿', 1),
(N'Combo Couple Galaxy', N'Combo', 119000, N'1 Bắp khổng lồ (tự chọn vị) + 2 Nước ngọt (L)', N'🍿', 1),
(N'Combo Party Supernova', N'Combo', 179000, N'2 Bắp lớn (Phô mai + Caramel) + 3 Nước ngọt + 1 Khoai tây', N'🎉', 1),
(N'Bắp Rang Bơ Phô Mai (L)', N'Bắp', 55000, N'Bắp nổ nóng giòn lắc bột phô mai Pháp béo ngậy thơm lừng', N'🧀', 1),
(N'Bắp Rang Bơ Caramel (L)', N'Bắp', 55000, N'Bắp nổ phủ lớp đường caramel vàng óng thơm ngọt', N'🍯', 1),
(N'Nước Ngọt Có Gas Pepsi/Coke (L)', N'Nước', 35000, N'Cốc lớn mát lạnh sảng khoái đánh tan cơn khát', N'🥤', 1);
GO

-- 3.6. Tạo Suất Chiếu mẫu (Hôm nay, Ngày mai, Ngày kia)
DECLARE @m1 INT = (SELECT TOP 1 id FROM movies WHERE title LIKE N'%Mai%');
DECLARE @m2 INT = (SELECT TOP 1 id FROM movies WHERE title LIKE N'%Dune%');
DECLARE @m3 INT = (SELECT TOP 1 id FROM movies WHERE title LIKE N'%Kung Fu%');
DECLARE @m4 INT = (SELECT TOP 1 id FROM movies WHERE title LIKE N'%Godzilla%');
DECLARE @m5 INT = (SELECT TOP 1 id FROM movies WHERE title LIKE N'%Lật Mặt%');

DECLARE @r1 INT = (SELECT TOP 1 id FROM rooms WHERE name LIKE N'%Hall 01%');
DECLARE @r2 INT = (SELECT TOP 1 id FROM rooms WHERE name LIKE N'%Hall 02%');

DECLARE @d0 NVARCHAR(20) = CONVERT(VARCHAR(10), GETDATE(), 120);
DECLARE @d1 NVARCHAR(20) = CONVERT(VARCHAR(10), DATEADD(day, 1, GETDATE()), 120);
DECLARE @d2 NVARCHAR(20) = CONVERT(VARCHAR(10), DATEADD(day, 2, GETDATE()), 120);

INSERT INTO showtimes (movie_id, room_id, show_date, show_time, base_price)
VALUES 
(@m1, @r1, @d0, N'09:30', 75000.0),
(@m1, @r2, @d0, N'18:30', 110000.0),
(@m2, @r1, @d0, N'13:45', 75000.0),
(@m2, @r2, @d0, N'20:45', 110000.0),
(@m3, @r2, @d0, N'16:15', 95000.0),
(@m4, @r1, @d1, N'13:45', 75000.0),
(@m4, @r2, @d1, N'20:45', 110000.0),
(@m5, @r2, @d1, N'16:15', 95000.0),
(@m5, @r1, @d2, N'18:30', 85000.0);
GO

-- 3.7. Tạo đơn vé mẫu đã đặt kiểm tra ghế khóa
DECLARE @st_first INT = (SELECT TOP 1 id FROM showtimes);
DECLARE @u_cust INT = (SELECT TOP 1 id FROM users WHERE username = N'khach1');
DECLARE @room_of_st INT = (SELECT room_id FROM showtimes WHERE id = @st_first);

DECLARE @s1 INT = (SELECT TOP 1 id FROM seats WHERE room_id = @room_of_st AND seat_code = N'C3');
DECLARE @s2 INT = (SELECT TOP 1 id FROM seats WHERE room_id = @room_of_st AND seat_code = N'C4');

INSERT INTO bookings (booking_code, user_id, showtime_id, total_amount, payment_method, status)
VALUES (N'VE2026MOCK001', @u_cust, @st_first, 190000.0, N'Chuyển khoản Online', N'Confirmed');

DECLARE @bk_id INT = SCOPE_IDENTITY();

INSERT INTO booking_details (booking_id, seat_id, seat_code, price)
VALUES 
(@bk_id, @s1, N'C3', 95000.0),
(@bk_id, @s2, N'C4', 95000.0);
GO

-- ====================================================================
-- 4. KHUNG NHÌN (VIEWS) - PHỤC VỤ TRUY VẤN VÀ BÁO CÁO NHANH
-- ====================================================================

-- 4.1. View xem thông tin chi tiết đơn vé điện tử (Join 5 bảng liên quan)
CREATE OR ALTER VIEW v_TicketDetails AS
SELECT 
    b.id AS booking_id,
    b.booking_code,
    u.fullname AS customer_name,
    u.phone AS customer_phone,
    m.title AS movie_title,
    m.genre AS movie_genre,
    r.name AS room_name,
    st.show_date,
    st.show_time,
    b.total_amount,
    b.booking_date,
    b.payment_method,
    b.status
FROM bookings b
JOIN users u ON b.user_id = u.id
JOIN showtimes st ON b.showtime_id = st.id
JOIN movies m ON st.movie_id = m.id
JOIN rooms r ON st.room_id = r.id;
GO

-- 4.2. View báo cáo tổng hợp doanh thu và số vé bán ra theo từng phim
CREATE OR ALTER VIEW v_MovieRevenueStatistics AS
SELECT 
    m.id AS movie_id,
    m.title AS movie_title,
    m.genre AS movie_genre,
    COUNT(bd.id) AS total_tickets_sold,
    COALESCE(SUM(bd.price), 0) AS total_ticket_revenue,
    CASE 
        WHEN COUNT(bd.id) > 0 THEN ROUND(COALESCE(SUM(bd.price), 0) / COUNT(bd.id), 0)
        ELSE 0 
    END AS avg_ticket_price
FROM movies m
LEFT JOIN showtimes st ON m.id = st.movie_id
LEFT JOIN bookings b ON st.id = b.showtime_id AND b.status IN ('Confirmed', 'Checked-in')
LEFT JOIN booking_details bd ON b.id = bd.booking_id
GROUP BY m.id, m.title, m.genre;
GO

-- 4.3. View thống kê các món bắp nước F&B bán chạy nhất
CREATE OR ALTER VIEW v_TopSellingConcessions AS
SELECT 
    c.id AS concession_id,
    c.name AS item_name,
    c.category,
    COALESCE(SUM(bc.quantity), 0) AS total_quantity_sold,
    COALESCE(SUM(bc.quantity * bc.price), 0) AS total_fnb_revenue
FROM concessions c
LEFT JOIN booking_concessions bc ON c.id = bc.concession_id
GROUP BY c.id, c.name, c.category;
GO

-- 4.4. Hàm Vô Hướng (Scalar Function) tính giá vé theo loại ghế
CREATE OR ALTER FUNCTION fn_CalculateSeatPrice
(
    @BasePrice FLOAT,
    @SeatType NVARCHAR(50)
)
RETURNS FLOAT
AS
BEGIN
    DECLARE @FinalPrice FLOAT;
    IF @SeatType = N'Supernova'
        SET @FinalPrice = @BasePrice + 50000.0;
    ELSE IF @SeatType LIKE N'%VIP%'
        SET @FinalPrice = @BasePrice + 20000.0;
    ELSE
        SET @FinalPrice = @BasePrice;
    RETURN @FinalPrice;
END;
GO

-- 4.5. Hàm Trả Về Bảng (Inline Table-Valued Function) lấy danh sách ghế trống của một suất chiếu
CREATE OR ALTER FUNCTION fn_GetAvailableSeats
(
    @ShowtimeID INT
)
RETURNS TABLE
AS
RETURN
(
    SELECT s.id AS seat_id, s.room_id, s.row_label, s.seat_num, s.seat_code, s.seat_type
    FROM seats s
    JOIN showtimes st ON s.room_id = st.room_id
    WHERE st.id = @ShowtimeID
      AND s.seat_code NOT IN (
          SELECT bd.seat_code
          FROM booking_details bd
          JOIN bookings b ON bd.booking_id = b.id
          WHERE b.showtime_id = @ShowtimeID
            AND b.status IN ('Confirmed', 'Checked-in')
      )
);
GO

-- ====================================================================
-- 5. THỦ TỤC LƯU TRỮ (STORED PROCEDURES)
-- ====================================================================

-- 5.1. Procedure lấy các chỉ số KPI Dashboard nhanh chóng (Tổng doanh thu, vé, phim, khách)
CREATE OR ALTER PROCEDURE sp_GetDashboardKPIs
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @TotalRevenue FLOAT = 0;
    DECLARE @TotalTickets INT = 0;
    DECLARE @TotalMovies INT = 0;
    DECLARE @TotalCustomers INT = 0;
    DECLARE @TotalFnBRevenue FLOAT = 0;

    -- Tổng doanh thu vé
    SELECT @TotalRevenue = COALESCE(SUM(total_amount), 0)
    FROM bookings 
    WHERE status IN ('Confirmed', 'Checked-in');

    -- Tổng số vé đã bán
    SELECT @TotalTickets = COUNT(bd.id)
    FROM booking_details bd
    JOIN bookings b ON bd.booking_id = b.id
    WHERE b.status IN ('Confirmed', 'Checked-in');

    -- Tổng số phim đang chiếu
    SELECT @TotalMovies = COUNT(*) 
    FROM movies 
    WHERE is_active = 1;

    -- Tổng số khách hàng
    SELECT @TotalCustomers = COUNT(*) 
    FROM users 
    WHERE role = 'customer';

    -- Doanh thu bắp nước
    SELECT @TotalFnBRevenue = COALESCE(SUM(quantity * price), 0)
    FROM booking_concessions;

    -- Trả về bảng kết quả
    SELECT 
        @TotalRevenue AS TotalRevenue,
        @TotalTickets AS TotalTickets,
        @TotalMovies AS TotalMovies,
        @TotalCustomers AS TotalCustomers,
        @TotalFnBRevenue AS TotalFnBRevenue;
END;
GO

-- 5.2. Procedure nghiệp vụ Soát Vé tại Cổng (Check-in Ticket) có tham số OUTPUT
CREATE OR ALTER PROCEDURE sp_CheckInTicket
    @BookingCode NVARCHAR(50),
    @ResultCode INT OUTPUT,          -- 1: Hợp lệ, 0: Vé đã soát, -1: Vé bị hủy, -2: Không tìm thấy
    @ResultMessage NVARCHAR(255) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @BookingID INT;
    DECLARE @CurrentStatus NVARCHAR(50);
    DECLARE @RoomName NVARCHAR(100);

    SELECT 
        @BookingID = b.id,
        @CurrentStatus = b.status,
        @RoomName = r.name
    FROM bookings b
    JOIN showtimes st ON b.showtime_id = st.id
    JOIN rooms r ON st.room_id = r.id
    WHERE UPPER(b.booking_code) = UPPER(@BookingCode);

    IF @BookingID IS NULL
    BEGIN
        SET @ResultCode = -2;
        SET @ResultMessage = N'Mã vé không tồn tại trên hệ thống CineVerse!';
        RETURN;
    END

    IF @CurrentStatus = 'Checked-in'
    BEGIN
        SET @ResultCode = 0;
        SET @ResultMessage = N'CẢNH BÁO: Vé này đã được soát vào rạp trước đó!';
        RETURN;
    END

    IF @CurrentStatus = 'Cancelled'
    BEGIN
        SET @ResultCode = -1;
        SET @ResultMessage = N'TỪ CHỐI: Vé này đã bị hủy hoặc hoàn tiền!';
        RETURN;
    END

    -- Cập nhật trạng thái sang Checked-in
    UPDATE bookings 
    SET status = 'Checked-in' 
    WHERE id = @BookingID;

    SET @ResultCode = 1;
    SET @ResultMessage = N'SOÁT VÉ HỢP LỆ! Mời quý khách vào ' + @RoomName;
END;
GO

-- 5.3. Procedure tra cứu suất chiếu theo phim và ngày
CREATE OR ALTER PROCEDURE sp_SearchShowtimes
    @MovieID INT = NULL,
    @ShowDate NVARCHAR(20) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        st.id,
        st.movie_id,
        st.room_id,
        m.title AS movie_title,
        r.name AS room_name,
        st.show_date,
        st.show_time,
        st.base_price
    FROM showtimes st
    JOIN movies m ON st.movie_id = m.id
    JOIN rooms r ON st.room_id = r.id
    WHERE (@MovieID IS NULL OR st.movie_id = @MovieID)
      AND (@ShowDate IS NULL OR st.show_date = @ShowDate)
    ORDER BY st.show_date ASC, st.show_time ASC;
END;
GO

-- 5.4. Procedure Hủy Vé Có Quản Lý Giao Dịch ACID (Transaction & TRY...CATCH)
CREATE OR ALTER PROCEDURE sp_CancelBookingWithTransaction
    @BookingID INT,
    @ResultCode INT OUTPUT,          -- 1: Thành công, 0: Đã hủy trước đó, -1: Không tìm thấy, -99: Lỗi hệ thống
    @ResultMessage NVARCHAR(255) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- 1. Kiểm tra sự tồn tại của đơn vé
        IF NOT EXISTS (SELECT 1 FROM bookings WHERE id = @BookingID)
        BEGIN
            SET @ResultCode = -1;
            SET @ResultMessage = N'Không tìm thấy đơn vé với ID này!';
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- 2. Kiểm tra nếu vé đã bị hủy trước đó
        DECLARE @OldStatus NVARCHAR(50);
        SELECT @OldStatus = status FROM bookings WHERE id = @BookingID;

        IF @OldStatus = 'Cancelled'
        BEGIN
            SET @ResultCode = 0;
            SET @ResultMessage = N'Vé này đã bị hủy trước đó!';
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- 3. Cập nhật trạng thái thành Cancelled (Kích hoạt Trigger ghi Audit Log)
        UPDATE bookings 
        SET status = 'Cancelled' 
        WHERE id = @BookingID;

        COMMIT TRANSACTION;

        SET @ResultCode = 1;
        SET @ResultMessage = N'Hủy vé và cập nhật trạng thái thành công!';
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        SET @ResultCode = -99;
        SET @ResultMessage = ERROR_MESSAGE();
    END CATCH
END;
GO

-- ====================================================================
-- 6. BỘ KÍCH HOẠT TỰ ĐỘNG (TRIGGERS)
-- ====================================================================

-- 6.1. Trigger tự động ghi vết thay đổi trạng thái vé (Audit Log)
CREATE OR ALTER TRIGGER trg_AuditBookingStatus
ON bookings
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Chỉ kích hoạt ghi nhận log khi có thay đổi trường trạng thái status
    IF UPDATE(status)
    BEGIN
        INSERT INTO booking_logs (booking_id, old_status, new_status, changed_at, action_note)
        SELECT 
            i.id,
            d.status AS old_status,
            i.status AS new_status,
            GETDATE(),
            CASE 
                WHEN i.status = 'Checked-in' THEN N'Khách hàng đã quét mã soát vé tại cổng'
                WHEN i.status = 'Cancelled' THEN N'Đơn vé đã bị hủy hoặc hoàn tiền'
                ELSE N'Cập nhật trạng thái vé'
            END
        FROM inserted i
        JOIN deleted d ON i.id = d.id
        WHERE i.status <> d.status;
    END
END;
GO

-- 6.2. Trigger kiểm tra và ngăn chặn đặt trùng ghế ở tầng CSDL
CREATE OR ALTER TRIGGER trg_PreventDuplicateSeat
ON booking_details
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- Kiểm tra xem ghế vừa chèn có trùng với bất kỳ vé Confirmed/Checked-in nào khác của cùng suất chiếu không
    IF EXISTS (
        SELECT 1
        FROM inserted i
        JOIN bookings b_new ON i.booking_id = b_new.id
        JOIN booking_details bd_old ON i.seat_id = bd_old.seat_id AND i.booking_id <> bd_old.booking_id
        JOIN bookings b_old ON bd_old.booking_id = b_old.id
        WHERE b_new.showtime_id = b_old.showtime_id
          AND b_old.status IN ('Confirmed', 'Checked-in')
    )
    BEGIN
        RAISERROR(N'Lỗi ràng buộc: Ghế này đã được khách hàng khác đặt trong cùng suất chiếu!', 16, 1);
        ROLLBACK TRANSACTION;
        RETURN;
    END
END;
GO

-- ====================================================================
-- 7. CÂU LỆNH KIỂM THỬ MẪU (DÀNH CHO THUYẾT TRÌNH TRÊN SSMS)
-- Quét chọn từng khối lệnh dưới đây và bấm F5 để demo cho Giảng viên:
-- ====================================================================
/*
-- 1. Xem dữ liệu Khung nhìn (Views):
SELECT * FROM v_TicketDetails;
SELECT * FROM v_MovieRevenueStatistics ORDER BY total_ticket_revenue DESC;
SELECT * FROM v_TopSellingConcessions ORDER BY total_quantity_sold DESC;

-- 2. Thực thi Hàm do người dùng định nghĩa (User-Defined Functions - UDFs):
-- - Hàm vô hướng (Scalar): Tính giá ghế VIP / Supernova
SELECT dbo.fn_CalculateSeatPrice(100000, N'Galaxy VIP') AS GiaGheVIP,
       dbo.fn_CalculateSeatPrice(100000, N'Supernova') AS GiaGheDoi;
-- - Hàm trả về bảng (Table-Valued): Lấy toàn bộ ghế còn trống của suất chiếu số 1
SELECT * FROM dbo.fn_GetAvailableSeats(1);

-- 3. Thực thi Thủ tục lưu trữ (Stored Procedures):
-- - Lấy KPI Dashboard quản trị:
EXEC sp_GetDashboardKPIs;
-- - Tra cứu lịch chiếu phim:
EXEC sp_SearchShowtimes @MovieID = 1;
-- - Nghiệp vụ soát vé tại quầy (Có tham số OUTPUT):
DECLARE @code INT, @msg NVARCHAR(255);
EXEC sp_CheckInTicket @BookingCode = N'VE2026MOCK001', @ResultCode = @code OUTPUT, @ResultMessage = @msg OUTPUT;
SELECT @code AS [Mã Kết Quả], @msg AS [Thông Điệp];
-- - Nghiệp vụ hủy vé an toàn với Transaction ACID:
DECLARE @cancel_code INT, @cancel_msg NVARCHAR(255);
EXEC sp_CancelBookingWithTransaction @BookingID = 1, @ResultCode = @cancel_code OUTPUT, @ResultMessage = @cancel_msg OUTPUT;
SELECT @cancel_code AS [Mã Hủy Vé], @cancel_msg AS [Thông Điệp Hủy];

-- 4. Xem Trigger đã tự động ghi vết Nhật Ký (Audit Log):
SELECT * FROM booking_logs;

-- 5. Lệnh sao lưu Cơ sở dữ liệu (Database Backup):
-- BACKUP DATABASE CineVerse TO DISK = 'C:\Backup\CineVerse_Backup.bak' WITH FORMAT, INIT, NAME = 'Full Backup CineVerse';
*/

PRINT N'>>> HOÀN TẤT KHỞI TẠO CƠ SỞ DỮ LIỆU CINEVERSE (TABLES, CONSTRAINTS, INDEXES, VIEWS, FUNCTIONS, PROCEDURES, TRIGGERS) <<<';
GO
