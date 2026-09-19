# Web Đọc Truyện & Cào Tự Động: Xà Tiên: Khai Cục Thôn Phệ Tiên Đế

Hệ thống hoàn chỉnh gồm: thu thập dữ liệu chương phân mảnh (trang 1/2 và 2/2) từ `novel543.com`, đa tầng dịch thuật sang tiếng Việt mượt mà tự nhiên, lưu trữ CSDL SQLite (`novel.db`), và website đọc truyện giao diện hiện đại.

---

## 1. Cài đặt môi trường (Nếu chạy lần đầu trên máy mới)

Mở PowerShell tại thư mục dự án và cài các thư viện cần thiết:
```powershell
pip install -r requirements.txt
```

---

## 2. Cách Khởi Động Website Đọc Truyện

Chạy lệnh:
```powershell
python app.py
```
- Web server sẽ chạy tại cổng **8088** (tránh xung đột với cổng 8000).
- 👉 Mở trình duyệt và truy cập: **[http://localhost:8088](http://localhost:8088)**
- Để dừng web server: Nhấn tổ hợp phím **`Ctrl + C`** tại cửa sổ Terminal đang chạy.

---

## 3. Cách Dịch Thuật Các Chương Chưa Dịch (Chạy Ngầm từ CSDL)

Dữ liệu tiếng Trung gốc của tất cả các chương từ 2000 đến 2223 đã nằm sẵn trong file CSDL `novel.db`. Để dịch hoặc dịch lại sang tiếng Việt chuẩn mà không cần mở trình duyệt:

```powershell
python retranslate.py 2000
```
- Công cụ sẽ tự động quét các chương còn thiếu tiếng Việt và dịch đa luồng (3 workers song song).
- Có thể vừa mở web đọc truyện vừa chạy lệnh dịch này song song.

---

## 4. Cách Cào Thêm Chương Mới (Khi Tác Giả Xuất Bản Chương Mới)

Để cào các chương tiếp theo (ví dụ từ chương 2224 trở đi):

```powershell
python crawler.py 2224
```
- Trình duyệt Chrome sẽ tự động khởi động.
- Nếu gặp màn hình xác thực Cloudflare (Turnstile), bạn chỉ cần tích xác thực bằng tay 1 lần trên cửa sổ đó.
- Công cụ sẽ tự nhận diện, tự gộp các trang phân mảnh `(1/2)` và `(2/2)`, tự dịch tiếng Việt và lưu thẳng vào CSDL.

---

## 5. Các Tính Năng & Phím Tắt Trên Web

- **Đổi giao diện**: Hỗ trợ 3 màu nền: 🌙 **Tối (Dark)**, 📜 **Giấy cũ (Sepia)**, ☀️ **Sáng (Light)**.
- **Tùy chỉnh cỡ chữ**: Nút **A-** / **A+** hoặc lưu cấu hình tự động.
- **Chế độ hiển thị**:
  - *Tiếng Việt*: Bản dịch thuật đã tối ưu hoá cấu trúc đoạn.
  - *Song ngữ*: Đọc song song đoạn văn tiếng Việt và đối chiếu bản gốc tiếng Trung.
  - *Bản gốc*: Hiển thị nguyên bản tiếng Trung.
- **Điều hướng nhanh bằng bàn phím**:
  - Phím mũi tên sang trái **`←`**: Về chương trước.
  - Phím mũi tên sang phải **`→`**: Sang chương kế tiếp.
