# DWSERVICE AGENT - LỊCH SỬ SỬA LỖI & QUY TẮC KỸ THUẬT (DEV NOTES)

Tài liệu này lưu lại nguyên nhân gốc rễ (Root Cause) của các lỗi nghiêm trọng đã xảy ra trong dự án để **tuyệt đối không lặp lại** trong các lần chỉnh sửa tiếp theo.

---

## 1. Lỗi đệ quy vô tận khi chạy ngầm bằng `pythonw.exe` (RecursionError)
* **Triệu chứng**: Chạy bằng `python agent.py` (có console) thì kết nối web thành công bình thường. Nhưng khi chạy ngầm bằng `pythonw.exe` (`start_agent_background.bat` hoặc `start_agent.bat`), tiến trình vừa bật lên được vài giây thì tự chết hoặc treo cứng, trên web DWService luôn ở trạng thái **UNAVAILABLE**.
* **Nguyên nhân gốc rễ**:
  * Khi chạy qua `python.exe`, `sys.stdout` và `sys.stderr` là đối tượng stream thật trỏ tới cửa sổ console.
  * Khi chạy qua `pythonw.exe` (chế độ không có cửa sổ của Windows), `sys.stdout` và `sys.stderr` không có stream hợp lệ.
  * Trong `core/utils.py`, class `Logger` khởi tạo `hdlr = logging.StreamHandler(sys.stdout)`. Khi `sys.stdout` là None/invalid, Python mặc định trỏ về `sys.stderr`.
  * Sau đó ở dòng tiếp theo, `sys.stderr` bị gán đè bằng `LoggerStdRedirect(self._logger, logging.ERROR)`.
  * Kết quả: Mỗi khi có log phát sinh, `StreamHandler` ghi vào `sys.stderr` -> gọi `LoggerStdRedirect.write()` -> gọi `logger.log()` -> lại kích hoạt `StreamHandler` -> **tạo vòng lặp đệ quy vô tận (`RecursionError: maximum recursion depth exceeded`)**.
* **Cách khắc phục triệt để**:
  1. Trong `LoggerStdRedirect`: Bổ sung cờ chặn lồng nhau `self._in_write` để ngăn mọi khả năng đệ quy.
  2. Trong `Logger.__init__`: Nếu chạy ngầm (không có console thật `sys.__stdout__`), tự động ghi log vào file `dwagent.log` xoay vòng thay vì dùng `StreamHandler`.

---

## 2. Lỗi nạp DLL âm thanh `__gxx_personality_sj0` (ABI Exception Incompatibility)
* **Triệu chứng**: Khi Agent kết nối hoặc khi người dùng truy cập web DWService mở màn hình/âm thanh, Windows hiện hộp thoại:
  `The procedure entry point __gxx_personality_sj0 could not be located in the dynamic link library ... librtaudio.dll`
* **Nguyên nhân gốc rễ**:
  * File `librtaudio.dll` cũ đi kèm repo được build bằng MinGW với mô hình ngoại lệ **SJLJ (Setjmp/Longjmp)**, yêu cầu symbol `__gxx_personality_sj0` từ `libstdc++-6.dll`.
  * Bộ MinGW cài đặt trên máy người dùng (WinLibs POSIX UCRT) là bản **SEH (Structured Exception Handling)** hiện đại, chỉ cung cấp `__gxx_personality_seh0`.
* **Cách khắc phục triệt để**:
  1. Tải source code chính thức `RtAudio 5.1.0` và build lại `librtaudio.dll` bằng chính trình biên dịch C++ SEH của hệ thống với cờ `-static-libgcc -static-libstdc++`.
  2. Recompile `dwagsoundcapture.dll` liên kết vào `librtaudio.dll` mới.
  3. Xóa bỏ file `libgcc_s_sjlj-1.dll` khỏi `make/native/` để tránh Windows loader nạp nhầm bản cũ.

---

## 3. Lỗi xung đột tài khoản `Error initializing agent: Already online`
* **Triệu chứng**: Sau khi tắt agent và bật lại quá nhanh, hoặc nhấp đúp chạy nhiều lần cùng lúc, agent không thể kết nối tới server DWService.
* **Nguyên nhân gốc rễ**:
  * Server DWService giữ kết nối TCP cũ trong khoảng 15 - 45 giây trước khi xác nhận ngắt kết nối hoàn toàn.
  * Nếu một tiến trình Agent mới kết nối với cùng một mã Agent Key trong khi tiến trình cũ chưa được dọn sạch, server trả về lỗi `#ALREADY_ONLINE` và từ chối kết nối mới.
* **Cách khắc phục triệt để**:
  * Trong `start_agent.bat`, luôn kiểm tra xem có tiến trình `agent.py` nào đang chạy hay không trước khi khởi chạy tiến trình mới.
  * Trong `stop_agent.bat`, dùng PowerShell CIM để quét và dừng sạch mọi tiến trình `python.exe` / `pythonw.exe` đang chạy `agent.py`.

---

## 4. Chuẩn hóa bộ file điều khiển
* `start_agent.bat`: Chạy ngầm an toàn bằng `pythonw.exe agent.py -filelog`. Tự động chống trùng lặp tiến trình. Cho phép xem log bằng tham số `--debug`.
* `stop_agent.bat`: Dừng sạch mọi tiến trình ngầm, không lỗi redirection.
* `Run_Agent_Hidden.lnk`: Shortcut Windows chuẩn, trỏ vào `start_agent.bat`.
