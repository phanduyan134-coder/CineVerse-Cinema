"""
Script kiểm thử toàn bộ luồng nghiệp vụ của hệ thống (Automated Verification)
"""

import sys
from database import init_database, seed_data, DatabaseManager
from services import AuthService, CinemaService
from models import (
    UserFactory, Admin, Staff, Customer,
    PricingStrategy, StandardPricingStrategy, StudentPricingStrategy,
    VIPGoldPricingStrategy, VIPDiamondPricingStrategy, PricingContext
)

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_tests():
    print("=== BẮT ĐẦU KIỂM THỬ HỆ THỐNG ===")
    init_database()
    seed_data()

    # 1. Test Đăng nhập Admin
    admin = AuthService.login("admin", "admin123")
    assert admin is not None, "Lỗi đăng nhập Admin"
    assert admin.is_admin() is True, "Admin role không chính xác"
    assert admin.is_staff() is True, "Admin phải có quyền nhân viên"
    print(" 1. Đăng nhập Admin: Thành công (Role: Admin)")

    # 2. Test Đăng nhập Nhân viên (Staff)
    staff = AuthService.login("nhanvien", "nv123456")
    assert staff is not None, "Lỗi đăng nhập Nhân viên"
    assert staff.is_staff() is True, "Staff role không chính xác"
    assert staff.is_admin() is False, "Staff không được có quyền admin"
    print(" 2. Đăng nhập Nhân viên (Staff): Thành công (Role: Staff)")

    # 3. Test Đăng nhập Khách hàng
    cust = AuthService.login("khach1", "123456")
    assert cust is not None, "Lỗi đăng nhập Khách hàng"
    assert cust.is_customer() is True, "Customer role không chính xác"
    assert cust.is_staff() is False, "Customer không được có quyền staff"
    print(" 3. Đăng nhập Khách hàng: Thành công (Role: Customer)")

    # 4. Test Đăng ký tài khoản mới
    test_user = "testuser_99"
    succ, msg = AuthService.register(test_user, "password123", "Người Dùng Thử", "test@gmail.com", "0123456789")
    print(f" 4. Đăng ký khách hàng mới: {msg}")

    # 5. Test Lấy danh sách phim & Tìm kiếm
    movies = CinemaService.get_movies(only_active=True)
    assert len(movies) > 0, "Không có phim nào trong CSDL"
    print(f" 5. Lấy danh sách phim: Tìm thấy {len(movies)} phim")

    search_res = CinemaService.get_movies(keyword="Dune")
    assert len(search_res) >= 1, "Tìm kiếm phim 'Dune' thất bại"
    assert search_res[0].poster_path != "", "Phim chưa có đường dẫn poster"
    assert "youtube.com" in (search_res[0].trailer_url or ""), "Phim chưa có link trailer YouTube"
    print(f" 6. Tìm kiếm phim theo từ khóa: Tìm thấy '{search_res[0].title}' (Poster: {search_res[0].poster_path}, Trailer: {search_res[0].trailer_url})")

    # 6. Test Lấy suất chiếu & Ghế phòng chiếu
    showtimes = CinemaService.get_showtimes(movie_id=search_res[0].id)
    assert len(showtimes) > 0, "Không tìm thấy suất chiếu cho phim"
    first_st = showtimes[0]
    print(f" 7. Lấy suất chiếu: Suất lúc {first_st.show_time} ({first_st.show_date}) tại {first_st.room_name}")

    seats = CinemaService.get_room_seats(first_st.room_id)
    booked_codes = CinemaService.get_booked_seats(first_st.id)
    print(f" 8. Kiểm tra sơ đồ phòng: Tổng {len(seats)} ghế, đã bán {len(booked_codes)} ghế")

    # 7. Test Đặt vé (POS / Khách)
    available_seats = [s for s in seats if s.seat_code not in booked_codes]
    assert len(available_seats) >= 2, "Không đủ ghế trống để test đặt vé"
    selected_to_book = available_seats[:2]

    succ, msg, booking = CinemaService.book_tickets(
        user_id=cust.id,
        showtime_id=first_st.id,
        selected_seats=selected_to_book,
        base_price=first_st.base_price,
        payment_method="Chuyển khoản QR"
    )
    assert succ is True, f"Đặt vé thất bại: {msg}"
    print(f" 9. Đặt vé thành công: Mã vé #{booking.booking_code}, Tổng tiền: {booking.total_amount:,.0f} VNĐ")

    # 8. Test kiểm tra ghế vừa đặt không cho đặt lại (Chống trùng ghế)
    succ_dup, msg_dup, _ = CinemaService.book_tickets(
        user_id=cust.id,
        showtime_id=first_st.id,
        selected_seats=selected_to_book,
        base_price=first_st.base_price
    )
    assert succ_dup is False, "Lỗi bảo mật: Ghế đã bán vẫn cho đặt lại!"
    print(f" 10. Chống trùng ghế hoạt động chính xác: {msg_dup}")

    # 9. Test Nghiệp vụ Soát Vé của Nhân viên (Gate Check-in)
    succ_chk, msg_chk, info_chk = CinemaService.check_in_ticket(booking.booking_code)
    assert succ_chk is True, f"Soát vé thất bại: {msg_chk}"
    print(f" 11. Nghiệp vụ Soát vé (Staff Check-in): Thành công - {msg_chk}")

    # Soát lại lần 2 phải bị từ chối
    succ_chk2, msg_chk2, _ = CinemaService.check_in_ticket(booking.booking_code)
    assert succ_chk2 is False, "Lỗi: Vé đã soát vẫn cho soát lần 2!"
    print(f" 12. Cảnh báo vé đã soát hoạt động chuẩn: {msg_chk2}")

    # 10. Test Lịch sử vé của khách hàng
    my_bookings = CinemaService.get_user_bookings(cust.id)
    assert len(my_bookings) >= 1, "Không tìm thấy lịch sử vé của khách"
    print(f" 13. Lịch sử vé khách hàng: Có {len(my_bookings)} đơn vé")

    # 11. Test Báo cáo thống kê Admin & Quản lý User
    stats = CinemaService.get_statistics()
    assert stats['total_revenue'] > 0, "Doanh thu không được cộng dồn"
    users_list = AuthService.get_all_users()
    assert len(users_list) >= 3, "Danh sách người dùng không đủ 3 phân quyền"
    print(f" 14. Báo cáo thống kê Admin: Doanh thu {stats['total_revenue']:,.0f} VNĐ, Quản lý {len(users_list)} tài khoản (Admin, Staff, Customer)")

    # 12. Test Quản lý Bắp Nước & Combo (F&B Concessions CRUD)
    concessions = CinemaService.get_concessions(only_active=True)
    assert len(concessions) >= 6, "Chưa nạp đủ seed data bắp nước"
    first_fnb = concessions[0]
    print(f" 15. Quản lý Bắp Nước & Combo: Tìm thấy {len(concessions)} món (Top: {first_fnb.icon} {first_fnb.name} - {first_fnb.get_formatted_price()})")

    # Thêm món thử nghiệm
    succ_add, msg_add = CinemaService.add_concession("Bắp Phô Mai Cay Đặc Biệt", "Bắp", 59000, "Bắp cay phô mai 64oz", "🍿")
    assert succ_add is True, f"Thêm món F&B thất bại: {msg_add}"
    all_fnb_after = CinemaService.get_concessions(only_active=False)
    added_item = next(i for i in all_fnb_after if i.name == "Bắp Phô Mai Cay Đặc Biệt")
    # Cập nhật & xóa dọn dẹp
    succ_upd, _ = CinemaService.update_concession(added_item.id, "Bắp Phô Mai Cay Đặc Biệt (Upgraded)", "Bắp", 65000, "Bắp cay phô mai", 1, "🍿")
    assert succ_upd is True
    succ_del, _ = CinemaService.delete_concession(added_item.id)
    assert succ_del is True
    print(" 16. CRUD Bắp Nước (Add / Update / Delete Concession): Thành công tuyệt đối")

    # 13. Test Đặt vé kèm Bắp Nước & Thanh toán VietQR
    avail2 = [s for s in seats if s.seat_code not in CinemaService.get_booked_seats(first_st.id)]
    assert len(avail2) >= 1, "Hết ghế trống để test F&B booking"
    fnb_order = [(concessions[0], 2), (concessions[1], 1)] # 2 x Solo, 1 x Couple
    expected_fnb_cost = concessions[0].price * 2 + concessions[1].price * 1
    expected_seat_cost = avail2[0].calculate_price(first_st.base_price)
    expected_grand_total = expected_seat_cost + expected_fnb_cost

    succ_fnb_bk, msg_fnb, bk_fnb_obj = CinemaService.book_tickets(
        user_id=cust.id,
        showtime_id=first_st.id,
        selected_seats=[avail2[0]],
        base_price=first_st.base_price,
        payment_method="Chuyển khoản VietQR 24/7",
        selected_concessions=fnb_order
    )
    assert succ_fnb_bk is True, f"Đặt vé kèm F&B thất bại: {msg_fnb}"
    assert bk_fnb_obj.total_amount == expected_grand_total, f"Tổng tiền không khớp: {bk_fnb_obj.total_amount} != {expected_grand_total}"
    assert bk_fnb_obj.concessions_str != "", "Chuỗi bắp nước concessions_str rỗng"
    print(f" 17. Đặt vé kèm Bắp Nước (F&B) & VietQR: Mã #{bk_fnb_obj.booking_code}, Tổng tiền: {bk_fnb_obj.total_amount:,.0f} đ (Bắp nước: {bk_fnb_obj.concessions_str})")

    # 18. Test Mẫu thiết kế Singleton (DatabaseManager)
    db1 = DatabaseManager()
    db2 = DatabaseManager()
    assert db1 is db2, "Singleton thất bại: Hai thể hiện DatabaseManager khác nhau"
    conn = db1.get_connection()
    assert conn is not None, "Không lấy được kết nối từ Singleton DatabaseManager"
    conn.close()
    print(" 18. Mẫu thiết kế Singleton (DatabaseManager): Đảm bảo duy nhất 1 thể hiện quản lý CSDL (Thread-Safe)")

    # 19. Test Mẫu thiết kế Factory Method (UserFactory)
    user_a = UserFactory.create_user("admin", 1, "test_admin", "Quản trị viên")
    user_s = UserFactory.create_user("staff", 2, "test_staff", "Nhân viên quầy")
    user_c = UserFactory.create_user("customer", 3, "test_cust", "Khách hàng")
    assert isinstance(user_a, Admin), "UserFactory không tạo đúng đối tượng Admin"
    assert isinstance(user_s, Staff), "UserFactory không tạo đúng đối tượng Staff"
    assert isinstance(user_c, Customer), "UserFactory không tạo đúng đối tượng Customer"
    print(" 19. Mẫu thiết kế Factory Method (UserFactory): Khởi tạo đối tượng User đa hình chính xác 100%")

    # 20. Test Mẫu thiết kế Strategy (PricingStrategy & PricingContext)
    raw_total, std_total, desc_std = CinemaService.calculate_booking_summary([avail2[0]], first_st.base_price, fnb_order, StandardPricingStrategy())
    assert std_total == expected_grand_total, f"Strategy Standard tính sai: {std_total} != {expected_grand_total}"

    raw_total, stu_total, desc_stu = CinemaService.calculate_booking_summary([avail2[0]], first_st.base_price, fnb_order, StudentPricingStrategy())
    assert stu_total == expected_grand_total * 0.9, f"Strategy Student (-10%) tính sai: {stu_total}"

    raw_total, dia_total, desc_dia = CinemaService.calculate_booking_summary([avail2[0]], first_st.base_price, fnb_order, VIPDiamondPricingStrategy())
    assert dia_total == expected_grand_total * 0.9, f"Strategy Diamond (-10%) tính sai: {dia_total}"

    print(f" 20. Mẫu thiết kế Strategy (PricingStrategy & Context): Hoán đổi chiến lược giá linh hoạt (Standard: {std_total:,.0f}đ, HSSV -10%: {stu_total:,.0f}đ, VIP Kim Cương -10%: {dia_total:,.0f}đ)")

    print("\n TOÀN BỘ 20/20 BƯỚC KIỂM THỬ HỆ THỐNG & MẪU THIẾT KẾ ĐÃ VƯỢT QUA XUẤT SẮC!")

if __name__ == "__main__":
    run_tests()
