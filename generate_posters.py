"""
File: generate_posters.py
Mô tả: Script tạo các poster phim nghệ thuật chuẩn Ultra-HD (440x620 - Độ nét cao Retina/HiDPI)
- Sử dụng TrueType Font hệ thống Windows (Segoe UI Bold / Regular)
- Hiệu ứng Gradient mượt mà, viền Neon công nghệ, huy hiệu độ tuổi (P, T13, T16, T18)
- Định dạng âm thanh hình ảnh chuẩn rạp: IMAX, Dolby Atmos, 4DX
"""

from PIL import Image, ImageDraw, ImageFont
import os
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

POSTER_DIR = "assets/posters"
os.makedirs(POSTER_DIR, exist_ok=True)

def load_font(size: int, bold: bool = False):
    """Tải Font Segoe UI chuẩn của Windows để chữ sắc nét tuyệt đối (ClearType Subpixel)"""
    candidate_paths = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

POSTER_DATA = [
    {
        "filename": "dune2.png",
        "title": "DUNE: PART TWO",
        "subtitle": "HÀNH TINH CÁT 2",
        "rating": "T16",
        "rating_color": (245, 158, 11),  # Amber
        "format": "QUANTUM IMAX 70MM",
        "bg_top": (135, 75, 15),
        "bg_bottom": (16, 10, 6),
        "accent": (255, 195, 18),
        "center_label": "D U N E",
        "tagline": "BẢN HÙNG CA CHIẾN TRANH VŨ TRỤ",
        "tech_spec": "DIRECTED BY DENIS VILLENEUVE • SOUND BY HANS ZIMMER",
        "stars": "★ ★ ★ ★ ★ (9.4/10)"
    },
    {
        "filename": "mai.png",
        "title": "MAI",
        "subtitle": "BỘ PHIM CỦA TRẤN THÀNH",
        "rating": "T18",
        "rating_color": (239, 71, 111),  # Crimson Rose
        "format": "GOLD CLASS VIP",
        "bg_top": (155, 25, 75),
        "bg_bottom": (25, 8, 18),
        "accent": (255, 110, 170),
        "center_label": "M A I",
        "tagline": "QUÁ KHỨ CHƯA NGỦ YÊN • HIỆN TẠI ĐẦY NƯỚC MẮT",
        "tech_spec": "PHƯƠNG ANH ĐÀO • TUẤN TRẦN • HỒNG ĐÀO",
        "stars": "★ ★ ★ ★ ★ (9.1/10)"
    },
    {
        "filename": "kungfupanda4.png",
        "title": "KUNG FU PANDA 4",
        "subtitle": "THẦN LONG ĐẠI HIỆP",
        "rating": "P",
        "rating_color": (6, 214, 160),  # Jade Green
        "format": "NEBULA 4DX D-BOX",
        "bg_top": (10, 105, 80),
        "bg_bottom": (8, 30, 22),
        "accent": (52, 211, 153),
        "center_label": "DRAGON",
        "tagline": "TRẬN CHIẾN TÂM LINH ĐỈNH CAO CHÂU Á",
        "tech_spec": "DREAMWORKS ANIMATION • JACK BLACK",
        "stars": "★ ★ ★ ★ ★ (8.8/10)"
    },
    {
        "filename": "godzillaxkong.png",
        "title": "GODZILLA x KONG",
        "subtitle": "THE NEW EMPIRE",
        "rating": "T13",
        "rating_color": (56, 189, 248),  # Electric Cyan
        "format": "QUANTUM 3D LASER",
        "bg_top": (25, 65, 150),
        "bg_bottom": (10, 15, 35),
        "accent": (72, 202, 228),
        "center_label": "TITANS",
        "tagline": "KHI HAI ĐẾ VƯƠNG VŨ TRỤ HỢP LỰC",
        "tech_spec": "WARNER BROS. & LEGENDARY PICTURES",
        "stars": "★ ★ ★ ★ ★ (9.0/10)"
    },
    {
        "filename": "latmat7.png",
        "title": "LẬT MẶT 7",
        "subtitle": "MỘT ĐIỀU ƯỚC (LÝ HẢI)",
        "rating": "P",
        "rating_color": (6, 214, 160),  # Jade Green
        "format": "CINEVERSE EXCLUSIVE",
        "bg_top": (175, 80, 15),
        "bg_bottom": (28, 16, 10),
        "accent": (251, 191, 36),
        "center_label": "GIA ĐÌNH",
        "tagline": "TÌNH MẸ BAO LA • GIA ĐÌNH LÀ ĐIỂM TỰA",
        "tech_spec": "KỊCH BẢN & ĐẠO DIỄN: LÝ HẢI PRODUCTION",
        "stars": "★ ★ ★ ★ ★ (9.3/10)"
    }
]

def render_ultra_hd_poster(data):
    w, h = 440, 620
    img = Image.new("RGB", (w, h), color=data["bg_bottom"])
    draw = ImageDraw.Draw(img)

    # 1. Gradient nền đa sắc mượt mà
    top_r, top_g, top_b = data["bg_top"]
    bot_r, bot_g, bot_b = data["bg_bottom"]

    for y in range(h):
        factor = y / float(h)
        # Đường cong sigmoid nhẹ để dải chuyển sắc mềm mại hơn
        factor = factor * factor * (3 - 2 * factor)
        r = int(top_r * (1 - factor) + bot_r * factor)
        g = int(top_g * (1 - factor) + bot_g * factor)
        b = int(top_b * (1 - factor) + bot_b * factor)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # 2. Khung viền kép kim loại công nghệ bo tròn
    accent = data["accent"]
    draw.rounded_rectangle([(10, 10), (w - 10, h - 10)], radius=14, outline=accent, width=2)
    draw.rounded_rectangle([(16, 16), (w - 16, h - 16)], radius=10, outline=(255, 255, 255, 50), width=1)

    # Chi tiết góc công nghệ (Sci-Fi Corner Brackets)
    corner_len = 25
    # Góc trên trái
    draw.line([(10, 10 + corner_len), (10, 10), (10 + corner_len, 10)], fill=(255, 255, 255), width=3)
    # Góc trên phải
    draw.line([(w - 10 - corner_len, 10), (w - 10, 10), (w - 10, 10 + corner_len)], fill=(255, 255, 255), width=3)
    # Góc dưới trái
    draw.line([(10, h - 10 - corner_len), (10, h - 10), (10 + corner_len, h - 10)], fill=(255, 255, 255), width=3)
    # Góc dưới phải
    draw.line([(w - 10 - corner_len, h - 10), (w - 10, h - 10), (w - 10, h - 10 - corner_len)], fill=(255, 255, 255), width=3)

    # 3. Tải Font TrueType chuẩn
    font_badge = load_font(13, bold=True)
    font_rating = load_font(14, bold=True)
    font_center = load_font(34, bold=True)
    font_title = load_font(26, bold=True)
    font_sub = load_font(16, bold=True)
    font_meta = load_font(12, bold=False)
    font_stars = load_font(16, bold=True)
    font_footer = load_font(11, bold=True)

    # 4. Badge Định dạng phòng chiếu (Header)
    fmt_text = f"🌌 {data['format']}"
    draw.rounded_rectangle([(w // 2 - 120, 24), (w // 2 + 120, 52)], radius=14, fill=(10, 16, 30), outline=accent, width=1)
    draw.text((w // 2, 38), fmt_text, fill=accent, font=font_badge, anchor="mm")

    # 5. Huy hiệu phân loại độ tuổi (Rating Badge) góc trên trái
    rate_w = 64
    rate_h = 30
    draw.rounded_rectangle([(26, 68), (26 + rate_w, 68 + rate_h)], radius=8, fill=data["rating_color"])
    draw.text((26 + rate_w // 2, 68 + rate_h // 2), data["rating"], fill=(10, 10, 15), font=font_rating, anchor="mm")

    # 6. Vòng tròn nghệ thuật cổng không gian (Portal Art Ring)
    cx, cy, radius = w // 2, 195, 85
    # Vòng hào quang mờ
    for i in range(4):
        draw.ellipse([(cx - radius - i*2, cy - radius - i*2), (cx + radius + i*2, cy + radius + i*2)], outline=accent)
    # Vòng trong sắc nét
    draw.ellipse([(cx - radius, cy - radius), (cx + radius, cy + radius)], outline=(255, 255, 255), width=2)
    draw.ellipse([(cx - radius + 12, cy - radius + 12), (cx + radius - 12, cy + radius - 12)], outline=accent, width=1)
    
    # Ký tự biểu tượng chính giữa vòng tròn
    draw.text((cx, cy), data["center_label"], fill=(255, 255, 255), font=font_center, anchor="mm")

    # 7. Tên phim chính (Large Title với hiệu ứng bóng đổ sắc nét)
    title = data["title"]
    # Bóng đổ
    draw.text((w // 2 + 2, 332), title, fill=(0, 0, 0), font=font_title, anchor="mm")
    # Chữ nổi
    draw.text((w // 2, 330), title, fill=(255, 255, 255), font=font_title, anchor="mm")

    # 8. Phụ đề tiếng Việt
    draw.text((w // 2, 370), data["subtitle"], fill=accent, font=font_sub, anchor="mm")

    # 9. Tagline
    draw.text((w // 2, 408), data["tagline"], fill=(225, 235, 250), font=font_meta, anchor="mm")

    # Đường phân cách ánh sáng
    draw.line([(50, 436), (w - 50, 436)], fill=(255, 255, 255, 80), width=1)

    # 10. Đánh giá sao & Thông số kỹ thuật rạp
    draw.text((w // 2, 464), data["stars"], fill=(255, 215, 0), font=font_stars, anchor="mm")
    draw.text((w // 2, 498), data["tech_spec"], fill=(185, 200, 220), font=font_meta, anchor="mm")
    draw.text((w // 2, 524), "DOLBY ATMOS 7.1 • LASER PROJECTION • D-BOX 4D", fill=accent, font=font_footer, anchor="mm")

    # 11. Footer CINEVERSE Branding
    draw.rounded_rectangle([(w // 2 - 140, 552), (w // 2 + 140, 584)], radius=8, fill=(12, 18, 32), outline=(72, 202, 228), width=1)
    draw.text((w // 2, 568), "CINEVERSE EXCLUSIVE THEATRICAL RELEASE", fill=(240, 248, 255), font=font_footer, anchor="mm")

    out_path = os.path.join(POSTER_DIR, data["filename"])
    img.save(out_path, "PNG", quality=95)
    print(f"[POSTER] Đã tạo thành công poster Ultra-HD: {out_path} (440x620)")

def generate_all():
    print("[POSTER] Bắt đầu khởi tạo bộ poster sắc nét Ultra-HD cho CINEVERSE...")
    for d in POSTER_DATA:
        render_ultra_hd_poster(d)
    print("[POSTER] Hoàn tất 100% việc tạo toàn bộ poster Ultra-HD sắc nét!")

if __name__ == "__main__":
    generate_all()
