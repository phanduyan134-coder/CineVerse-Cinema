"""
Module: database.py
Mô tả: Quản lý kết nối CSDL SQLite, tạo các bảng và nạp dữ liệu mẫu ban đầu.
Sử dụng thư viện sqlite3 có sẵn trong Python chuẩn.
"""

import sqlite3
import os
import sys
import hashlib
import threading
from datetime import datetime, timedelta

# Thiết lập encoding UTF-8 cho stdout trên Windows
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "cinema.db")

class DatabaseManager:
    """
    Mẫu thiết kế Singleton (Singleton Pattern):
    Đảm bảo chỉ có một thể hiện duy nhất quản lý kết nối CSDL trong toàn bộ ứng dụng,
    bảo đảm an toàn đa luồng (Thread-safe) bằng threading.Lock.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.db_path = DB_NAME
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        """Tạo và trả về kết nối tới SQLite Database kèm PRAGMA foreign_keys"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Cho phép truy cập cột theo tên (dict-like)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

def get_connection():
    """Hàm bao tương thích ngược: Lấy kết nối CSDL từ Singleton DatabaseManager"""
    return DatabaseManager().get_connection()

def hash_password(password: str) -> str:
    """Mã hóa mật khẩu bằng thuật toán SHA-256 (bảo mật chuẩn)"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_database():
    """Khởi tạo toàn bộ cấu trúc bảng cho hệ thống"""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Bảng Người dùng (Users)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        fullname TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        role TEXT NOT NULL DEFAULT 'customer', -- 'admin' hoặc 'customer'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Bảng Phim (Movies)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        genre TEXT NOT NULL,
        duration INTEGER NOT NULL, -- Thời lượng tính bằng phút
        director TEXT,
        description TEXT,
        release_date TEXT,
        poster_path TEXT DEFAULT '',
        trailer_url TEXT DEFAULT '',
        is_active INTEGER DEFAULT 1 -- 1: Đang chiếu, 0: Ngừng chiếu
    )
    """)

    # 3. Bảng Phòng chiếu (Rooms)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        total_rows INTEGER NOT NULL, -- Số hàng (ví dụ: 6 hàng A, B, C, D, E, F)
        total_cols INTEGER NOT NULL  -- Số ghế mỗi hàng (ví dụ: 8)
    )
    """)

    # 4. Bảng Ghế ngồi (Seats)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        row_label TEXT NOT NULL,  -- A, B, C, ...
        seat_num INTEGER NOT NULL, -- 1, 2, 3, ...
        seat_code TEXT NOT NULL,  -- A1, A2, B3...
        seat_type TEXT NOT NULL DEFAULT 'Standard', -- 'Standard' hoặc 'VIP'
        FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
        UNIQUE(room_id, seat_code)
    )
    """)

    # 5. Bảng Suất chiếu (Showtimes)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS showtimes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        show_date TEXT NOT NULL,  -- Định dạng YYYY-MM-DD
        show_time TEXT NOT NULL,  -- Định dạng HH:MM (vd: 19:30)
        base_price REAL NOT NULL, -- Giá vé cơ bản (VNĐ)
        FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
        FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
    )
    """)

    # 6. Bảng Đặt vé (Bookings)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_code TEXT UNIQUE NOT NULL, -- Mã vé duy nhất (vd: VE20260908001)
        user_id INTEGER NOT NULL,
        showtime_id INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        payment_method TEXT DEFAULT 'Tiền mặt / Trực tuyến',
        status TEXT DEFAULT 'Confirmed', -- 'Confirmed', 'Cancelled'
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (showtime_id) REFERENCES showtimes(id) ON DELETE CASCADE
    )
    """)

    # 7. Bảng Chi tiết đặt vé (Booking Details - lưu từng ghế của 1 đơn đặt)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS booking_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        seat_id INTEGER NOT NULL,
        seat_code TEXT NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
        FOREIGN KEY (seat_id) REFERENCES seats(id) ON DELETE CASCADE
    )
    """)

    # 8. Bảng Sản phẩm Bắp Nước (Concessions / F&B)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS concessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL, -- 'Combo', 'Bắp', 'Nước'
        price REAL NOT NULL,
        description TEXT,
        icon TEXT DEFAULT '🍿',
        is_active INTEGER DEFAULT 1 -- 1: Đang bán, 0: Tạm ngưng
    )
    """)

    # 9. Bảng Bắp Nước của Đơn Đặt (Booking Concessions)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS booking_concessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        concession_id INTEGER NOT NULL,
        concession_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
        FOREIGN KEY (concession_id) REFERENCES concessions(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

def seed_data():
    """Nạp dữ liệu mẫu ban đầu để phần mềm sẵn sàng sử dụng ngay"""
    conn = get_connection()
    cursor = conn.cursor()

    # Đảm bảo tài khoản nhanvien (Staff) luôn tồn tại
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'nhanvien'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO users (username, password_hash, fullname, email, phone, role)
        VALUES (?, ?, ?, ?, ?, ?)
        """, ('nhanvien', hash_password('nv123456'), 'Nguyễn Văn Thu Ngân', 'staff@cinema.com', '0933445566', 'staff'))
        conn.commit()

    # Đảm bảo bảng bắp nước (Concessions / F&B) luôn có dữ liệu phong phú
    cursor.execute("SELECT COUNT(*) FROM concessions")
    if cursor.fetchone()[0] == 0:
        concessions_data = [
            ('Combo Solo CineVerse', 'Combo', 89000, '1 Bắp ngọt lớn (L) + 1 Nước ngọt có gas (L)', '🍿', 1),
            ('Combo Couple Galaxy', 'Combo', 119000, '1 Bắp khổng lồ (tự chọn vị) + 2 Nước ngọt (L)', '🍿', 1),
            ('Combo Party Supernova', 'Combo', 179000, '2 Bắp lớn (Phô mai + Caramel) + 3 Nước ngọt + 1 Khoai tây', '🎉', 1),
            ('Bắp Rang Bơ Phô Mai (L)', 'Bắp', 55000, 'Bắp nổ nóng giòn lắc bột phô mai Pháp béo ngậy thơm lừng', '🧀', 1),
            ('Bắp Rang Bơ Caramel (L)', 'Bắp', 55000, 'Bắp nổ phủ lớp đường caramel vàng óng thơm ngọt', '🍯', 1),
            ('Nước Ngọt Có Gas Pepsi/Coke (L)', 'Nước', 35000, 'Cốc lớn mát lạnh sảng khoái đánh tan cơn khát', '🥤', 1)
        ]
        cursor.executemany("""
        INSERT INTO concessions (name, category, price, description, icon, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
        """, concessions_data)
        conn.commit()

    # Kiểm tra nếu đã có tài khoản admin thì không seed lại các bảng khác
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    print("[INFO] Đang nạp dữ liệu mẫu ban đầu...")

    # 1. Thêm tài khoản mẫu
    users = [
        ('admin', hash_password('admin123'), 'Quản Trị Viên', 'admin@cinema.com', '0901234567', 'admin'),
        ('nhanvien', hash_password('nv123456'), 'Nguyễn Văn Thu Ngân', 'staff@cinema.com', '0933445566', 'staff'),
        ('khach1', hash_password('123456'), 'Nguyễn Văn An', 'an.nguyen@gmail.com', '0912345678', 'customer'),
        ('khach2', hash_password('123456'), 'Trần Thị Bình', 'binh.tran@gmail.com', '0987654321', 'customer')
    ]
    cursor.executemany("""
    INSERT INTO users (username, password_hash, fullname, email, phone, role)
    VALUES (?, ?, ?, ?, ?, ?)
    """, users)

    # 2. Thêm phòng chiếu mẫu CINEVERSE
    rooms = [
        ('Hall 01 - Quantum IMAX (CineVerse)', 6, 8),  # 6 hàng (A-F), mỗi hàng 8 ghế (Hàng F là Supernova)
        ('Hall 02 - Nebula 4DX (CineVerse)', 5, 8)    # 5 hàng (A-E), mỗi hàng 8 ghế (Hàng E là Supernova)
    ]
    cursor.executemany("INSERT INTO rooms (name, total_rows, total_cols) VALUES (?, ?, ?)", rooms)

    # Lấy ID của các phòng vừa tạo
    cursor.execute("SELECT id, total_rows, total_cols FROM rooms")
    room_records = cursor.fetchall()

    row_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for r in room_records:
        r_id = r['id']
        rows_count = r['total_rows']
        cols_count = r['total_cols']

        seat_list = []
        for row_idx in range(rows_count):
            letter = row_letters[row_idx]
            # Chuẩn CINEVERSE: Hàng cuối là Supernova (Ghế cặp đôi), các hàng giữa là Galaxy VIP, hàng đầu là Nebula
            if row_idx == rows_count - 1:
                seat_type = 'Supernova'
            elif row_idx >= 2:
                seat_type = 'Galaxy VIP'
            else:
                seat_type = 'Nebula'

            for col in range(1, cols_count + 1):
                seat_code = f"{letter}{col}"
                seat_list.append((r_id, letter, col, seat_code, seat_type))

        cursor.executemany("""
        INSERT INTO seats (room_id, row_label, seat_num, seat_code, seat_type)
        VALUES (?, ?, ?, ?, ?)
        """, seat_list)

    # 3. Thêm danh sách phim mẫu CINEVERSE kèm Poster và Trailer YouTube
    movies = [
        (
            '[T18] Mai',
            'Tâm lý, Tình cảm (18+)',
            131,
            'Trấn Thành',
            'Một câu chuyện tình cảm sâu sắc, đầy trắc trở giữa Mai và Dương tại khu chung cư cũ.',
            '2024-02-10',
            'assets/posters/mai.png',
            'https://www.youtube.com/watch?v=kY3P988Fw-M',
            1
        ),
        (
            '[T16] Dune: Hành Tinh Cát 2',
            'Khoa học viễn tưởng, IMAX',
            166,
            'Denis Villeneuve',
            'Paul Atreides gia nhập cùng người Fremen để giải phóng hành tinh Arrakis và báo thù cho gia tộc.',
            '2024-03-01',
            'assets/posters/dune2.png',
            'https://www.youtube.com/watch?v=Way9Dexny3w',
            1
        ),
        (
            '[P] Kung Fu Panda 4',
            'Hoạt hình, Gia đình',
            94,
            'Mike Mitchell',
            'Po bước vào hành trình mới để trở thành Thủ Lĩnh Tinh Thần và tìm kiếm một Thần Long Đại Hiệp kế nhiệm.',
            '2024-03-08',
            'assets/posters/kungfupanda4.png',
            'https://www.youtube.com/watch?v=_inKs4eeHiI',
            1
        ),
        (
            '[T13] Godzilla x Kong: Đế Chế Mới',
            'Hành động, Viễn tưởng, 3D',
            115,
            'Adam Wingard',
            'Hai quái thú huyền thoại Godzilla và Kong bắt tay chống lại một mối đe dọa khổng lồ bí ẩn từ Trái Đất rỗng.',
            '2024-04-12',
            'assets/posters/godzillaxkong.png',
            'https://www.youtube.com/watch?v=lV1OOlGwExg',
            1
        ),
        (
            '[P] Lật Mặt 7: Một Điều Ước',
            'Gia đình, Tâm lý',
            138,
            'Lý Hải',
            'Câu chuyện xúc động về tình mẫu tử của người mẹ già cùng nỗi trăn trở của những người con.',
            '2024-04-26',
            'assets/posters/latmat7.png',
            'https://www.youtube.com/watch?v=0hC-U7x_d5o',
            1
        )
    ]
    cursor.executemany("""
    INSERT INTO movies (title, genre, duration, director, description, release_date, poster_path, trailer_url, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, movies)

    # 4. Thêm các suất chiếu mẫu (hôm nay, ngày mai và ngày kia)
    today = datetime.now()
    dates = [
        today.strftime("%Y-%m-%d"),
        (today + timedelta(days=1)).strftime("%Y-%m-%d"),
        (today + timedelta(days=2)).strftime("%Y-%m-%d")
    ]

    cursor.execute("SELECT id FROM movies")
    movie_ids = [m['id'] for m in cursor.fetchall()]

    cursor.execute("SELECT id FROM rooms")
    room_ids = [r['id'] for r in cursor.fetchall()]

    time_slots_day = ["09:30", "13:45", "16:15"]
    time_slots_eve = ["18:30", "20:45", "22:15"]
    showtimes = []

    # Tạo các suất chiếu phong phú đa dạng khung giờ cho từng phim
    for day_idx, d in enumerate(dates):
        for m_idx, m_id in enumerate(movie_ids):
            # Suất ban ngày
            t1 = time_slots_day[(m_idx + day_idx) % len(time_slots_day)]
            r1 = room_ids[(m_idx + day_idx) % len(room_ids)]
            p1 = 75000.0 if r1 == room_ids[0] else 95000.0
            showtimes.append((m_id, r1, d, t1, p1))

            # Suất ban tối
            t2 = time_slots_eve[(m_idx + day_idx + 1) % len(time_slots_eve)]
            r2 = room_ids[(m_idx + day_idx + 1) % len(room_ids)]
            p2 = 85000.0 if r2 == room_ids[0] else 110000.0
            showtimes.append((m_id, r2, d, t2, p2))

    cursor.executemany("""
    INSERT INTO showtimes (movie_id, room_id, show_date, show_time, base_price)
    VALUES (?, ?, ?, ?, ?)
    """, showtimes)

    # 5. Tạo 1 vé mẫu đã đặt cho suất chiếu đầu tiên để kiểm tra ghế bị khóa
    cursor.execute("SELECT id, room_id, base_price FROM showtimes LIMIT 1")
    first_st = cursor.fetchone()
    if first_st:
        st_id = first_st['id']
        st_room_id = first_st['room_id']
        base_p = first_st['base_price']

        # Lấy ghế C3 và C4 của phòng đó làm ghế đã bán
        cursor.execute("SELECT id, seat_code, seat_type FROM seats WHERE room_id = ? AND seat_code IN ('C3', 'C4')", (st_room_id,))
        booked_seats = cursor.fetchall()
        if len(booked_seats) == 2:
            code = f"VE{today.strftime('%Y%m%d')}001"
            total = sum(base_p + (20000 if s['seat_type'] == 'VIP' else 0) for s in booked_seats)
            cursor.execute("""
            INSERT INTO bookings (booking_code, user_id, showtime_id, total_amount, payment_method, status)
            VALUES (?, 2, ?, ?, 'Chuyển khoản Online', 'Confirmed')
            """, (code, st_id, total))
            booking_id = cursor.lastrowid

            for s in booked_seats:
                price = base_p + (20000 if s['seat_type'] == 'VIP' else 0)
                cursor.execute("""
                INSERT INTO booking_details (booking_id, seat_id, seat_code, price)
                VALUES (?, ?, ?, ?)
                """, (booking_id, s['id'], s['seat_code'], price))

    conn.commit()
    conn.close()
    print("[INFO] Khởi tạo dữ liệu mẫu thành công!")

if __name__ == "__main__":
    init_database()
    seed_data()
