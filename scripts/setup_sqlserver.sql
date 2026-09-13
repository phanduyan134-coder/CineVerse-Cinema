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
    created_at DATETIME DEFAULT GETDATE()
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
    is_active INT DEFAULT 1 -- 1: Đang chiếu, 0: Ngừng chiếu
);
GO

-- 2.3. Bảng Phòng chiếu (Rooms)
CREATE TABLE rooms (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    total_rows INT NOT NULL, -- Số hàng (ví dụ: 6 hàng A -> F)
    total_cols INT NOT NULL  -- Số ghế mỗi hàng (ví dụ: 8)
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
    CONSTRAINT UQ_room_seat UNIQUE (room_id, seat_code)
);
GO

-- 2.5. Bảng Suất chiếu (Showtimes)
CREATE TABLE showtimes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    movie_id INT NOT NULL FOREIGN KEY REFERENCES movies(id) ON DELETE CASCADE,
    room_id INT NOT NULL FOREIGN KEY REFERENCES rooms(id) ON DELETE CASCADE,
    show_date NVARCHAR(20) NOT NULL,  -- Định dạng YYYY-MM-DD
    show_time NVARCHAR(20) NOT NULL,  -- Định dạng HH:MM (vd: 19:30)
    base_price FLOAT NOT NULL          -- Giá vé cơ bản (VNĐ)
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
    status NVARCHAR(50) DEFAULT 'Confirmed'    -- 'Confirmed', 'Checked-in', 'Cancelled'
);
GO

-- 2.7. Bảng Chi tiết Ghế Đã Đặt (Booking Details)
CREATE TABLE booking_details (
    id INT IDENTITY(1,1) PRIMARY KEY,
    booking_id INT NOT NULL FOREIGN KEY REFERENCES bookings(id) ON DELETE CASCADE,
    seat_id INT NOT NULL FOREIGN KEY REFERENCES seats(id),
    seat_code NVARCHAR(10) NOT NULL,
    price FLOAT NOT NULL
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
    is_active INT DEFAULT 1         -- 1: Đang bán, 0: Tạm ngưng
);
GO

-- 2.9. Bảng Bắp Nước của Đơn Đặt (Booking Concessions)
CREATE TABLE booking_concessions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    booking_id INT NOT NULL FOREIGN KEY REFERENCES bookings(id) ON DELETE CASCADE,
    concession_id INT NOT NULL FOREIGN KEY REFERENCES concessions(id),
    concession_name NVARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    price FLOAT NOT NULL
);
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

PRINT N'>>> HOÀN TẤT KHỞI TẠO CƠ SỞ DỮ LIỆU CINEVERSE TRÊN MICROSOFT SQL SERVER <<<';
GO
