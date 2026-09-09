"""
Module: services.py
Mô tả: Tầng xử lý nghiệp vụ (Business Logic Layer)
- Tương tác với CSDL qua database.py
- Chuyển đổi dữ liệu thành các Object OOP trong models.py
- Xử lý các logic: Đăng nhập, Đăng ký, Đặt vé (chống trùng ghế), Thống kê doanh thu
"""

import sqlite3
import random
from datetime import datetime
from database import get_connection, hash_password
from models import (
    User, Customer, Staff, Admin, Movie, Room, Seat, Showtime, Booking, Concession,
    UserFactory, PricingStrategy, StandardPricingStrategy, StudentPricingStrategy, 
    VIPGoldPricingStrategy, VIPDiamondPricingStrategy, PricingContext
)

class AuthService:
    """Nghiệp vụ Xác thực & Phân quyền"""

    @staticmethod
    def login(username: str, password: str):
        """Kiểm tra thông tin đăng nhập, trả về đối tượng Customer, Staff hoặc Admin tương ứng"""
        conn = get_connection()
        cursor = conn.cursor()
        pwd_hash = hash_password(password)

        cursor.execute("""
        SELECT id, username, fullname, email, phone, role 
        FROM users 
        WHERE username = ? AND password_hash = ?
        """, (username.strip(), pwd_hash))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        # Áp dụng Factory Method Pattern: Khởi tạo đối tượng User đa hình sạch sẽ
        return UserFactory.create_user(
            row['role'], row['id'], row['username'], row['fullname'], row['email'], row['phone']
        )

    @staticmethod
    def register(username: str, password: str, fullname: str, email: str = "", phone: str = ""):
        """Đăng ký tài khoản khách hàng mới"""
        if not username or not password or not fullname:
            return False, "Tên đăng nhập, mật khẩu và họ tên không được để trống!"

        if len(password) < 6:
            return False, "Mật khẩu phải có ít nhất 6 ký tự!"

        conn = get_connection()
        cursor = conn.cursor()
        try:
            pwd_hash = hash_password(password)
            cursor.execute("""
            INSERT INTO users (username, password_hash, fullname, email, phone, role)
            VALUES (?, ?, ?, ?, ?, 'customer')
            """, (username.strip(), pwd_hash, fullname.strip(), email.strip(), phone.strip()))
            conn.commit()
            return True, "Đăng ký tài khoản thành công! Bạn có thể đăng nhập ngay."
        except sqlite3.IntegrityError:
            return False, f"Tên tài khoản '{username}' đã tồn tại! Vui lòng chọn tên khác."
        except Exception as e:
            return False, f"Lỗi hệ thống: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def get_all_users() -> list[User]:
        """Lấy danh sách tất cả tài khoản người dùng phục vụ Admin"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, fullname, email, phone, role FROM users ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        res = []
        for row in rows:
            res.append(UserFactory.create_user(
                row['role'], row['id'], row['username'], row['fullname'], row['email'], row['phone']
            ))
        return res

    @staticmethod
    def create_user(username: str, password: str, fullname: str, role: str = 'staff', email: str = "", phone: str = ""):
        """Admin tạo tài khoản mới (Staff hoặc Admin hoặc Customer)"""
        if not username or not password or not fullname:
            return False, "Tên đăng nhập, mật khẩu và họ tên không được để trống!"
        if len(password) < 6:
            return False, "Mật khẩu phải có ít nhất 6 ký tự!"
        conn = get_connection()
        cursor = conn.cursor()
        try:
            pwd_hash = hash_password(password)
            cursor.execute("""
            INSERT INTO users (username, password_hash, fullname, email, phone, role)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (username.strip(), pwd_hash, fullname.strip(), email.strip(), phone.strip(), role.strip()))
            conn.commit()
            return True, f"Tạo tài khoản {role.upper()} '{username}' thành công!"
        except sqlite3.IntegrityError:
            return False, f"Tên tài khoản '{username}' đã tồn tại!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def delete_user(user_id: int):
        """Admin xóa tài khoản người dùng"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT role, username FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return False, "Không tìm thấy người dùng!"
            if row['role'] == 'admin':
                return False, "Không thể xóa tài khoản Quản trị viên (Admin)!"
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return True, f"Đã xóa tài khoản '{row['username']}' thành công!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
        finally:
            conn.close()


class CinemaService:
    """Nghiệp vụ Phim, Suất chiếu & Đặt vé"""

    @staticmethod
    def get_movies(only_active: bool = True, keyword: str = "") -> list[Movie]:
        """Lấy danh sách phim có lọc theo từ khóa tìm kiếm"""
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM movies WHERE 1=1"
        params = []
        if only_active:
            query += " AND is_active = 1"
        if keyword:
            query += " AND (title LIKE ? OR genre LIKE ? OR director LIKE ?)"
            p = f"%{keyword.strip()}%"
            params.extend([p, p, p])

        query += " ORDER BY id DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [Movie(
            r['id'], r['title'], r['genre'], r['duration'], 
            r['director'], r['description'], r['release_date'],
            r['poster_path'] if 'poster_path' in r.keys() else '',
            r['trailer_url'] if 'trailer_url' in r.keys() else '',
            r['is_active']
        ) for r in rows]

    @staticmethod
    def add_movie(title: str, genre: str, duration: int, director: str, description: str, release_date: str, poster_path: str = "", trailer_url: str = ""):
        if not title or duration <= 0:
            return False, "Tên phim không được để trống và thời lượng phải lớn hơn 0!"
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO movies (title, genre, duration, director, description, release_date, poster_path, trailer_url, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (title.strip(), genre.strip(), duration, director.strip(), description.strip(), release_date.strip(), poster_path.strip(), trailer_url.strip()))
            conn.commit()
            return True, "Thêm phim mới thành công!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def update_movie(movie_id: int, title: str, genre: str, duration: int, director: str, description: str, release_date: str, is_active: int, poster_path: str = "", trailer_url: str = ""):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            UPDATE movies 
            SET title = ?, genre = ?, duration = ?, director = ?, description = ?, release_date = ?, is_active = ?, poster_path = ?, trailer_url = ?
            WHERE id = ?
            """, (title.strip(), genre.strip(), duration, director.strip(), description.strip(), release_date.strip(), is_active, poster_path.strip(), trailer_url.strip(), movie_id))
            conn.commit()
            return True, "Cập nhật thông tin phim thành công!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def delete_movie(movie_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
            conn.commit()
            return True, "Đã xóa phim thành công!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def get_rooms() -> list[Room]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rooms ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        return [Room(r['id'], r['name'], r['total_rows'], r['total_cols']) for r in rows]

    @staticmethod
    def get_showtimes(movie_id: int = None, show_date: str = None) -> list[Showtime]:
        """Lấy danh sách suất chiếu theo phim hoặc theo ngày"""
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        SELECT st.*, m.title as movie_title, r.name as room_name
        FROM showtimes st
        JOIN movies m ON st.movie_id = m.id
        JOIN rooms r ON st.room_id = r.id
        WHERE 1=1
        """
        params = []
        if movie_id:
            query += " AND st.movie_id = ?"
            params.append(movie_id)
        if show_date:
            query += " AND st.show_date = ?"
            params.append(show_date)

        query += " ORDER BY st.show_date ASC, st.show_time ASC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [Showtime(r['id'], r['movie_id'], r['room_id'], r['show_date'], 
                         r['show_time'], r['base_price'], r['movie_title'], r['room_name']) for r in rows]

    @staticmethod
    def add_showtime(movie_id: int, room_id: int, show_date: str, show_time: str, base_price: float):
        if base_price <= 0:
            return False, "Giá vé cơ bản phải lớn hơn 0!"
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO showtimes (movie_id, room_id, show_date, show_time, base_price)
            VALUES (?, ?, ?, ?, ?)
            """, (movie_id, room_id, show_date.strip(), show_time.strip(), base_price))
            conn.commit()
            return True, "Tạo suất chiếu mới thành công!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def delete_showtime(showtime_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM showtimes WHERE id = ?", (showtime_id,))
            conn.commit()
            return True, "Đã xóa suất chiếu thành công!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def get_room_seats(room_id: int) -> list[Seat]:
        """Lấy tất cả các ghế của một phòng chiếu"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM seats 
        WHERE room_id = ? 
        ORDER BY row_label ASC, seat_num ASC
        """, (room_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Seat(r['id'], r['room_id'], r['row_label'], r['seat_num'], r['seat_code'], r['seat_type']) for r in rows]

    @staticmethod
    def get_booked_seats(showtime_id: int) -> set[str]:
        """Lấy tập hợp các mã ghế (seat_code) đã được đặt trong một suất chiếu"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT bd.seat_code 
        FROM booking_details bd
        JOIN bookings b ON bd.booking_id = b.id
        WHERE b.showtime_id = ? AND b.status = 'Confirmed'
        """, (showtime_id,))
        booked_codes = {r['seat_code'] for r in cursor.fetchall()}
        conn.close()
        return booked_codes

    @staticmethod
    def book_tickets(user_id: int, showtime_id: int, selected_seats: list[Seat], base_price: float, 
                     payment_method: str = "Trực tuyến", selected_concessions: list = None,
                     pricing_strategy: PricingStrategy = None):
        """
        Nghiệp vụ Đặt vé cốt lõi:
        - Kiểm tra đồng thời chống trùng ghế (Transaction Isolation)
        - Áp dụng Strategy Pattern (PricingStrategy, PricingContext) tính giá vé & chiết khấu ưu đãi linh hoạt
        - Tính tổng tiền vé + bắp nước F&B
        - Tạo mã vé ngẫu nhiên duy nhất
        - Lưu vào bookings, booking_details và booking_concessions
        """
        if not selected_seats:
            return False, "Bạn chưa chọn ghế nào!", None

        conn = get_connection()
        cursor = conn.cursor()
        try:
            # 1. Kiểm tra lại lần nữa xem có ghế nào vừa bị người khác đặt không
            cursor.execute("""
            SELECT bd.seat_code 
            FROM booking_details bd
            JOIN bookings b ON bd.booking_id = b.id
            WHERE b.showtime_id = ? AND b.status = 'Confirmed'
            """, (showtime_id,))
            already_booked = {r['seat_code'] for r in cursor.fetchall()}

            for seat in selected_seats:
                if seat.seat_code in already_booked:
                    conn.rollback()
                    return False, f"Rất tiếc! Ghế {seat.seat_code} vừa có khách khác đặt trước. Vui lòng chọn ghế khác.", None

            # 2. Xử lý bắp nước F&B
            fnb_amount = 0.0
            concessions_to_save = []
            if selected_concessions:
                for c_item, qty in selected_concessions:
                    if qty > 0:
                        fnb_amount += (c_item.price * qty)
                        concessions_to_save.append((c_item, qty))

            # 3. Áp dụng Mẫu Thiết Kế Strategy (Strategy Pattern) để tính toán giá vé & ưu đãi
            pricing_ctx = PricingContext(pricing_strategy or StandardPricingStrategy())
            grand_raw, total_amount, discount_note = pricing_ctx.calculate_total(
                selected_seats, base_price, fnb_amount
            )

            # 4. Tạo mã vé duy nhất: VE + YYYYMMDD + 4 chữ số ngẫu nhiên
            now = datetime.now()
            booking_code = f"VE{now.strftime('%Y%m%d')}{random.randint(1000, 9999)}"

            # 5. Lưu đơn đặt vé vào bảng bookings
            cursor.execute("""
            INSERT INTO bookings (booking_code, user_id, showtime_id, total_amount, payment_method, status)
            VALUES (?, ?, ?, ?, ?, 'Confirmed')
            """, (booking_code, user_id, showtime_id, total_amount, payment_method))
            booking_id = cursor.lastrowid

            # 5. Lưu chi tiết từng ghế vào booking_details
            for seat in selected_seats:
                seat_price = seat.calculate_price(base_price)
                cursor.execute("""
                INSERT INTO booking_details (booking_id, seat_id, seat_code, price)
                VALUES (?, ?, ?, ?)
                """, (booking_id, seat.id, seat.seat_code, seat_price))

            # 6. Lưu chi tiết bắp nước vào booking_concessions
            for c_item, qty in concessions_to_save:
                cursor.execute("""
                INSERT INTO booking_concessions (booking_id, concession_id, concession_name, quantity, price)
                VALUES (?, ?, ?, ?, ?)
                """, (booking_id, c_item.id, c_item.name, qty, c_item.price))

            conn.commit()

            # Trả về thông tin vé đã đặt thành công
            seats_str = ", ".join(s.seat_code for s in selected_seats)
            concessions_str = ", ".join(f"{qty}x {c.name}" for c, qty in concessions_to_save)
            booking_obj = Booking(
                booking_id=booking_id,
                booking_code=booking_code,
                user_id=user_id,
                showtime_id=showtime_id,
                total_amount=total_amount,
                booking_date=now.strftime("%Y-%m-%d %H:%M:%S"),
                payment_method=payment_method,
                status="Confirmed",
                seats_str=seats_str,
                concessions_str=concessions_str
            )
            return True, "Đặt vé thành công!", booking_obj

        except Exception as e:
            conn.rollback()
            return False, f"Lỗi khi đặt vé: {str(e)}", None
        finally:
            conn.close()

    @staticmethod
    def calculate_booking_summary(selected_seats: list[Seat], base_price: float, fnb_items: list = None, pricing_strategy: PricingStrategy = None):
        """
        Phương thức tiện ích: Tính toán tóm tắt giá vé sử dụng Strategy Pattern
        Trả về (tổng_gốc_chưa_giảm, tổng_sau_chiết_khấu, mô_tả_chiết_khấu)
        """
        fnb_total = sum(item.price * qty for item, qty in (fnb_items or [])) if fnb_items else 0.0
        pricing_ctx = PricingContext(pricing_strategy or StandardPricingStrategy())
        return pricing_ctx.calculate_total(selected_seats, base_price, fnb_total)

    @staticmethod
    def get_user_bookings(user_id: int) -> list[Booking]:
        """Lấy lịch sử các vé đã đặt của 1 khách hàng (kèm bắp nước F&B)"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT b.*, m.title as movie_title, r.name as room_name,
               (st.show_date || ' lúc ' || st.show_time) as show_schedule,
               GROUP_CONCAT(bd.seat_code, ', ') as seats_str
        FROM bookings b
        JOIN showtimes st ON b.showtime_id = st.id
        JOIN movies m ON st.movie_id = m.id
        JOIN rooms r ON st.room_id = r.id
        LEFT JOIN booking_details bd ON b.id = bd.booking_id
        WHERE b.user_id = ?
        GROUP BY b.id
        ORDER BY b.id DESC
        """, (user_id,))
        rows = cursor.fetchall()

        bookings = []
        for r in rows:
            cursor.execute("SELECT quantity, concession_name FROM booking_concessions WHERE booking_id = ?", (r['id'],))
            fnb_rows = cursor.fetchall()
            fnb_str = ", ".join(f"{it['quantity']}x {it['concession_name']}" for it in fnb_rows)

            b = Booking(
                r['id'], r['booking_code'], r['user_id'], r['showtime_id'],
                r['total_amount'], r['booking_date'], r['payment_method'],
                r['status'], r['movie_title'], r['room_name'],
                r['show_schedule'], r['seats_str'] or "",
                concessions_str=fnb_str
            )
            bookings.append(b)
        conn.close()
        return bookings

    @staticmethod
    def get_all_bookings() -> list[dict]:
        """Lấy danh sách tất cả các vé trong hệ thống phục vụ Quản trị viên (kèm bắp nước F&B)"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT b.id, b.booking_code, u.fullname as customer_name, u.phone as customer_phone,
               m.title as movie_title, r.name as room_name,
               (st.show_date || ' ' || st.show_time) as show_time,
               b.total_amount, b.booking_date, b.payment_method, b.status,
               GROUP_CONCAT(bd.seat_code, ', ') as seats_str
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN showtimes st ON b.showtime_id = st.id
        JOIN movies m ON st.movie_id = m.id
        JOIN rooms r ON st.room_id = r.id
        LEFT JOIN booking_details bd ON b.id = bd.booking_id
        GROUP BY b.id
        ORDER BY b.id DESC
        """)
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            cursor.execute("SELECT quantity, concession_name FROM booking_concessions WHERE booking_id = ?", (r['id'],))
            fnb_rows = cursor.fetchall()
            d['concessions_str'] = ", ".join(f"{it['quantity']}x {it['concession_name']}" for it in fnb_rows)
            results.append(d)
        conn.close()
        return results

    @staticmethod
    def get_statistics():
        """Thống kê tổng quan cho Admin Dashboard"""
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Tổng doanh thu (Vé Đã Xác Nhận hoặc Đã Vào Rạp)
        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM bookings WHERE status IN ('Confirmed', 'Checked-in')")
        total_revenue = cursor.fetchone()[0]

        # 2. Tổng số vé đã bán (tổng số ghế)
        cursor.execute("""
        SELECT COUNT(bd.id) 
        FROM booking_details bd
        JOIN bookings b ON bd.booking_id = b.id
        WHERE b.status IN ('Confirmed', 'Checked-in')
        """)
        total_tickets = cursor.fetchone()[0]

        # 3. Tổng số phim đang chiếu
        cursor.execute("SELECT COUNT(*) FROM movies WHERE is_active = 1")
        total_movies = cursor.fetchone()[0]

        # 4. Tổng số khách hàng
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'customer'")
        total_customers = cursor.fetchone()[0]

        # 5. Doanh thu theo từng phim
        cursor.execute("""
        SELECT m.title, COUNT(bd.id) as ticket_count, COALESCE(SUM(bd.price), 0) as movie_revenue
        FROM movies m
        LEFT JOIN showtimes st ON m.id = st.movie_id
        LEFT JOIN bookings b ON st.id = b.showtime_id AND b.status IN ('Confirmed', 'Checked-in')
        LEFT JOIN booking_details bd ON b.id = bd.booking_id
        GROUP BY m.id
        ORDER BY movie_revenue DESC
        """)
        movie_stats = [dict(r) for r in cursor.fetchall()]

        # 6. Doanh thu bắp nước & combo F&B
        cursor.execute("SELECT COALESCE(SUM(quantity * price), 0) FROM booking_concessions")
        total_fnb_revenue = cursor.fetchone()[0]

        # 7. Thống kê món F&B bán chạy nhất
        cursor.execute("""
        SELECT concession_name, SUM(quantity) as total_qty, SUM(quantity * price) as item_revenue
        FROM booking_concessions
        GROUP BY concession_id, concession_name
        ORDER BY total_qty DESC
        LIMIT 5
        """)
        fnb_stats = [dict(r) for r in cursor.fetchall()]

        conn.close()
        return {
            "total_revenue": total_revenue,
            "total_tickets": total_tickets,
            "total_movies": total_movies,
            "total_customers": total_customers,
            "total_fnb_revenue": total_fnb_revenue,
            "movie_stats": movie_stats,
            "fnb_stats": fnb_stats
        }

    @staticmethod
    def check_in_ticket(booking_code: str) -> tuple[bool, str, dict | None]:
        """
        Nghiệp vụ Soát Vé dành cho Nhân Viên (Staff):
        - Quét/Nhập mã vé
        - Đổi trạng thái vé sang 'Checked-in' (Đã vào rạp)
        - Ngăn chặn vé giả, vé đã dùng hoặc vé đã hủy
        """
        code = booking_code.strip().upper()
        if not code:
            return False, "Vui lòng nhập mã vé cần soát!", None

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT b.*, u.fullname as customer_name, u.phone as customer_phone,
               m.title as movie_title, r.name as room_name,
               (st.show_date || ' ' || st.show_time) as show_time,
               GROUP_CONCAT(bd.seat_code, ', ') as seats_str
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN showtimes st ON b.showtime_id = st.id
        JOIN movies m ON st.movie_id = m.id
        JOIN rooms r ON st.room_id = r.id
        LEFT JOIN booking_details bd ON b.id = bd.booking_id
        WHERE UPPER(b.booking_code) = ?
        GROUP BY b.id
        """, (code,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, f"Mã vé '{code}' KHÔNG TỒN TẠI trên hệ thống CINEVERSE!", None

        ticket_info = dict(row)
        cursor.execute("SELECT quantity, concession_name FROM booking_concessions WHERE booking_id = ?", (row['id'],))
        fnb_rows = cursor.fetchall()
        ticket_info['concessions_str'] = ", ".join(f"{it['quantity']}x {it['concession_name']}" for it in fnb_rows)

        if row['status'] == 'Checked-in':
            conn.close()
            return False, f"CẢNH BÁO: Vé '{code}' ĐÃ ĐƯỢC SOÁT VÀO RẠP TRƯỚC ĐÓ!", ticket_info

        if row['status'] == 'Cancelled':
            conn.close()
            return False, f"TỪ CHỐI: Vé '{code}' ĐÃ BỊ HỦY HOẶC HOÀN TIỀN!", ticket_info

        # Cập nhật trạng thái thành Checked-in
        cursor.execute("UPDATE bookings SET status = 'Checked-in' WHERE id = ?", (row['id'],))
        conn.commit()
        conn.close()
        ticket_info['status'] = 'Checked-in'
        return True, f"SOÁT VÉ HỢP LỆ! Mời quý khách vào {row['room_name']}.", ticket_info

    @staticmethod
    def cancel_booking(booking_id: int) -> tuple[bool, str]:
        """Hủy vé (chuyển trạng thái sang Cancelled)"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE bookings SET status = 'Cancelled' WHERE id = ?", (booking_id,))
            conn.commit()
            return True, "Đã hủy đơn vé thành công!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def search_bookings(keyword: str = "") -> list[dict]:
        """Tra cứu vé theo mã vé, tên khách hoặc số điện thoại (kèm bắp nước F&B)"""
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        SELECT b.id, b.booking_code, u.fullname as customer_name, u.phone as customer_phone,
               m.title as movie_title, r.name as room_name,
               (st.show_date || ' ' || st.show_time) as show_time,
               b.total_amount, b.booking_date, b.payment_method, b.status,
               GROUP_CONCAT(bd.seat_code, ', ') as seats_str
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN showtimes st ON b.showtime_id = st.id
        JOIN movies m ON st.movie_id = m.id
        JOIN rooms r ON st.room_id = r.id
        LEFT JOIN booking_details bd ON b.id = bd.booking_id
        WHERE 1=1
        """
        params = []
        if keyword:
            kw = f"%{keyword.strip()}%"
            query += " AND (b.booking_code LIKE ? OR u.fullname LIKE ? OR u.phone LIKE ? OR m.title LIKE ?)"
            params.extend([kw, kw, kw, kw])

        query += " GROUP BY b.id ORDER BY b.id DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            cursor.execute("SELECT quantity, concession_name FROM booking_concessions WHERE booking_id = ?", (r['id'],))
            fnb_rows = cursor.fetchall()
            d['concessions_str'] = ", ".join(f"{it['quantity']}x {it['concession_name']}" for it in fnb_rows)
            results.append(d)
        conn.close()
        return results

    # ================= QUẢN LÝ BẮP NƯỚC (F&B CONCESSIONS) =================
    @staticmethod
    def get_concessions(only_active: bool = True) -> list[Concession]:
        """Lấy danh sách sản phẩm bắp nước & combo"""
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM concessions"
        if only_active:
            query += " WHERE is_active = 1"
        query += " ORDER BY category DESC, price ASC"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [Concession(r['id'], r['name'], r['category'], r['price'], r['description'] or '', r['icon'] or '🍿', bool(r['is_active'])) for r in rows]

    @staticmethod
    def add_concession(name: str, category: str, price: float, description: str = "", icon: str = "🍿") -> tuple[bool, str]:
        if not name.strip() or price <= 0:
            return False, "Tên sản phẩm không được để trống và giá phải lớn hơn 0!"
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO concessions (name, category, price, description, icon, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
            """, (name.strip(), category.strip(), price, description.strip(), icon.strip() or '🍿'))
            conn.commit()
            return True, "Thêm sản phẩm bắp nước thành công!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def update_concession(concession_id: int, name: str, category: str, price: float, description: str, is_active: int, icon: str = "🍿") -> tuple[bool, str]:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            UPDATE concessions 
            SET name = ?, category = ?, price = ?, description = ?, is_active = ?, icon = ?
            WHERE id = ?
            """, (name.strip(), category.strip(), price, description.strip(), is_active, icon.strip() or '🍿', concession_id))
            conn.commit()
            return True, "Cập nhật sản phẩm bắp nước thành công!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def delete_concession(concession_id: int) -> tuple[bool, str]:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM concessions WHERE id = ?", (concession_id,))
            conn.commit()
            return True, "Đã xóa sản phẩm bắp nước thành công!"
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
        finally:
            conn.close()

