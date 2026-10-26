# 🔐 Bài 1 — Mã hoá AES-256 (đối xứng) bằng C# / .NET 8

> Môn: An toàn & Bảo mật thông tin  
> Ứng dụng desktop (WinForms) + bản console, mã hoá **văn bản** và **file dung lượng lớn (hàng GB)** bằng AES-256.

<img width="983" height="715" alt="image" src="https://github.com/user-attachments/assets/bb2ea782-ff9e-4a5c-bc8a-a717bf107543" />

<!-- Chụp màn hình tab "Bài 1 — AES" rồi đặt vào docs/images/aes-tab.png -->

---

## 📋 Mục lục
1. [Đề bài](#-đề-bài)
2. [Tính năng](#-tính-năng)
3. [Công nghệ & cấu trúc project](#-công-nghệ--cấu-trúc-project)
4. [Thiết kế](#-thiết-kế)
5. [Cài đặt & chạy](#-cài-đặt--chạy)
6. [Hướng dẫn sử dụng](#-hướng-dẫn-sử-dụng)
7. [Đoạn code chính](#-đoạn-code-chính)
8. [Thử nghiệm file hàng GB](#-thử-nghiệm-file-hàng-gb)
9. [Bảng số liệu & kết luận](#-bảng-số-liệu--kết-luận)
10. [Lỗi thường gặp](#-lỗi-thường-gặp)
11. [Hạn chế & hướng mở rộng](#-hạn-chế--hướng-mở-rộng)

---

## 📝 Đề bài

**AES** là mã hoá đối xứng: mã hoá và giải mã dùng **cùng 1 khoá**.

Tạo ứng dụng (không phải web — console hoặc form) với 5 chức năng:

1. Sinh khoá AES
2. Lưu khoá ra file
3. Import khoá từ file
4. Mã hoá 1 đoạn văn bản → kết quả mã hoá hiện ra màn hình
5. Mã hoá 1 file → lưu vào 1 file

**Yêu cầu thêm:** thử nghiệm với file kích thước lớn (hàng GB), tính **thời gian mã hoá**, **thời gian giải mã**, **so sánh theo byte** giữa file nguồn và file giải mã, rồi **kết luận dựa trên số liệu thu được**.

---

## ✨ Tính năng

| # | Chức năng | Cách làm |
|---|-----------|----------|
| 1 | Sinh khoá | Khoá **256 bit = 32 byte** từ bộ sinh số ngẫu nhiên an toàn (`RandomNumberGenerator`) |
| 2 | Lưu khoá | Ghi file `.key` dạng **base64** |
| 3 | Import khoá | Đọc base64, kiểm tra đúng 32 byte |
| 4 | Mã hoá văn bản | Kết quả base64 hiện trên màn hình, giải mã ngược lại được |
| 5 | Mã hoá / giải mã file | Xử lý theo **stream 1 MB**, có thanh tiến trình |
| + | Đo thời gian | `Stopwatch`, hiển thị giây và MB/s |
| + | So sánh file | So từng byte, báo vị trí byte khác đầu tiên (nếu có) |

---

## 🧱 Công nghệ & cấu trúc project

- C# / **.NET 8**, WinForms (giao diện) + Console (menu)
- Thư viện mật mã có sẵn: `System.Security.Cryptography` (không cần cài thêm gói)

```
CryptoLab/
├── CryptoLab.Core/            # Logic mật mã (không phụ thuộc giao diện)
│   └── AesService.cs          # ← toàn bộ Bài 1 nằm ở đây
├── CryptoLab.WinForms/        # Giao diện, tab "Bài 1 — AES"
│   └── MainForm.cs
└── CryptoLab.Console/         # Bản menu console
    └── Program.cs
```

Tách `Core` khỏi giao diện để cùng một logic dùng được cho cả form lẫn console, và dễ kiểm thử.

---

## 🧠 Thiết kế

### Thuật toán
- **AES-256, chế độ CBC, padding PKCS7**.
- **IV** (16 byte) sinh **ngẫu nhiên mỗi lần mã hoá**. IV không cần giữ bí mật nên được ghi ngay đầu dữ liệu → cùng một bản rõ, mã hoá 2 lần sẽ ra 2 bản mã khác nhau.

### Định dạng dữ liệu mã hoá

```
File mã hoá :  [ IV (16 byte) ][ ciphertext ... ]
Văn bản     :  base64( IV (16 byte) + ciphertext )
Khoá        :  base64( 32 byte )
```

### Vì sao chạy được file hàng GB
Không đọc cả file vào RAM. Chương trình đọc **từng khối 1 MB** → qua `CryptoStream` → ghi ra file đích. Bộ nhớ dùng gần như cố định (vài MB) dù file 100 MB hay 10 GB.

```
File nguồn ──(đọc 1 MB)──► CryptoStream (AES) ──(ghi 1 MB)──► File đích
```

### So sánh file theo byte
Đọc song song 2 file theo từng khối 1 MB, dừng ngay ở byte khác đầu tiên. Trả về `-1` nếu hai file giống hệt.

---

## ⚙️ Cài đặt & chạy

**Yêu cầu:** Windows, [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)

```bash
# Kiểm tra SDK (phải thấy số bắt đầu bằng 8.)
dotnet --version

# Chạy giao diện
cd CryptoLab.WinForms
dotnet run

# Hoặc chạy bản console
cd CryptoLab.Console
dotnet run
```

---

## 🖱️ Hướng dẫn sử dụng

Mở tab **Bài 1 — AES**.

### 1) Quản lý khoá
1. Bấm **1. Sinh khoá** → chuỗi base64 hiện ở ô "Khoá AES-256".
2. Bấm **2. Lưu khoá ra file** → chọn nơi lưu (ví dụ `aes.key`).
3. Lần sau bấm **3. Import khoá từ file** để nạp lại khoá cũ.

> ⚠️ Mất khoá = mất dữ liệu. Phải dùng **đúng khoá** đã mã hoá thì mới giải mã được.

### 2) Mã hoá văn bản
1. Nhập chữ vào ô **Văn bản gốc**.
2. Bấm **Mã hoá ↓** → kết quả base64 hiện ở ô "Kết quả mã hoá".
3. Bấm **Giải mã ↑** → văn bản gốc quay lại.

### 3) Mã hoá / giải mã file
1. **Chọn file nguồn…** và **Chọn file đích…**
2. Bấm **Mã hoá file** → thanh tiến trình chạy, nhật ký ghi thời gian + MB/s.
3. Đổi vai trò: nguồn = file đã mã hoá, đích = file mới → bấm **Giải mã file**.
4. Bấm **So sánh 2 file theo byte…** → chọn file gốc và file vừa giải mã.  
   Kết quả: `GIỐNG HỆT` hoặc `KHÁC tại byte #...`.

### Bản console (tuỳ chọn)
Chạy `dotnet run` ở `CryptoLab.Console`, chọn các mục `1` → `5`, `5b` trong menu.

---

## 💻 Đoạn code chính

**Sinh / lưu / nạp khoá**
```csharp
public static byte[] GenerateKey() => RandomNumberGenerator.GetBytes(32); // 256 bit

public static void SaveKey(byte[] key, string path) =>
    File.WriteAllText(path, Convert.ToBase64String(key));

public static byte[] LoadKey(string path)
{
    var key = Convert.FromBase64String(File.ReadAllText(path).Trim());
    if (key.Length != 32) throw new InvalidDataException("Khoá AES phải 32 byte (256 bit).");
    return key;
}
```

**Mã hoá file theo stream**
```csharp
using var aes = Aes.Create();
aes.Key = key; aes.GenerateIV();

using var fin  = new FileStream(inPath,  FileMode.Open,   FileAccess.Read,  FileShare.Read, 1 << 20, FileOptions.SequentialScan);
using var fout = new FileStream(outPath, FileMode.Create, FileAccess.Write, FileShare.None, 1 << 20, FileOptions.SequentialScan);

fout.Write(aes.IV, 0, 16);                                   // ghi IV ở đầu file
using var cs = new CryptoStream(fout, aes.CreateEncryptor(), CryptoStreamMode.Write);
// đọc từng khối 1 MB từ fin, ghi vào cs
cs.FlushFinalBlock();
```

**Giải mã**: đọc 16 byte đầu làm IV, phần còn lại qua `aes.CreateDecryptor()`.

---
## 🧪 Thử nghiệm file hàng MB

<img width="983" height="715" alt="image" src="https://github.com/user-attachments/assets/50897e24-2f1a-43b3-b3cd-632ea2e3b13d" />


## 🧪 Thử nghiệm file hàng GB

### Tạo file thử (PowerShell)
```powershell
# File 2 GB 
fsutil file createnew D:\test\big_2GB.bin 2147483648

# File 5 GB
fsutil file createnew D:\test\big_5GB.bin 5368709120
```
Hoặc dùng một file thật (video, file ISO, file nén...) từ vài GB trở lên.
VD file 2GB 
<img width="986" height="715" alt="image" src="https://github.com/user-attachments/assets/63dbee01-10a8-4d97-900e-e8e8e3b6641a" />

### Quy trình đo (làm cho mỗi file)
1. Import khoá → **Mã hoá file** → ghi thời gian vào bảng.
2. **Giải mã file** ra file mới → ghi thời gian.
3. **So sánh 2 file theo byte** (gốc ↔ giải mã) → ghi kết quả.
4. (Kiểm chứng thêm bằng công cụ ngoài)
   ```powershell
   certutil -hashfile D:\test\big_2GB.bin SHA256
   certutil -hashfile D:\test\big_2GB.dec SHA256
   ```
   Hai chuỗi băm phải trùng nhau.

### Lưu ý để số liệu đáng tin
- Đóng bớt chương trình nặng; chạy **mỗi mức dung lượng ít nhất 3 lần** rồi lấy trung bình.
- Dùng cùng một ổ đĩa cho mọi lần đo. Lần chạy đầu và các lần sau có thể chênh nhau vì **bộ nhớ đệm của hệ điều hành**.
- Cần ổ đĩa còn trống ≥ (dung lượng file × 2), vì có file mã hoá và file giải mã.

---

## 📊 Bảng số liệu & kết luận

> Điền số liệu **đo thật trên máy của bạn**. Công thức: `MB/s = dung lượng (MB) / thời gian (giây)`.

**Cấu hình máy:** CPU: `...` · RAM: `...` · Ổ đĩa (SSD/HDD): `...` · .NET 8

| Dung lượng | Thời gian mã hoá (s) | Thời gian giải mã (s) | MB/s mã hoá | MB/s giải mã | So sánh byte |
|-----------:|---------------------:|----------------------:|------------:|-------------:|:------------:|
| 100 MB     |                      |                       |             |              |              |
| 1 GB       |                      |                       |             |              |              |
| 2 GB       |                      |                       |             |              |              |
| 5 GB       |                      |                       |             |              |              |

### Kết luận (viết lại theo số liệu của bạn)

Gợi ý khung kết luận — thay `...` bằng số thật:

1. **Tính đúng đắn:** với mọi file thử, so sánh theo byte cho kết quả *giống hệt* → mã hoá rồi giải mã khôi phục chính xác dữ liệu gốc.
2. **Tốc độ:** AES-256 đạt khoảng `...` MB/s khi mã hoá và `...` MB/s khi giải mã.
3. **Tuyến tính:** thời gian tăng gần **tỉ lệ thuận** với dung lượng (gấp đôi dung lượng ≈ gấp đôi thời gian), nên tốc độ MB/s gần như không đổi.
4. **Điểm nghẽn:** nếu tốc độ gần với tốc độ đọc/ghi của ổ đĩa thì **ổ đĩa là điểm nghẽn**, không phải thuật toán (CPU hiện đại có tập lệnh AES-NI nên mã hoá rất nhanh).
5. **Bộ nhớ:** nhờ xử lý theo stream 1 MB, RAM sử dụng gần như không đổi dù file lên tới hàng GB (có thể mở Task Manager để chứng minh).

---

## 🛠️ Lỗi thường gặp

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| `Chưa có khoá AES` | Chưa sinh hoặc import khoá | Bấm Sinh khoá hoặc Import khoá |
| `Padding is invalid and cannot be removed` khi giải mã | Sai khoá, hoặc file không phải file do app mã hoá | Dùng đúng file `.key` đã mã hoá |
| `Khoá AES phải 32 byte` | File khoá bị sửa / sai định dạng | Sinh khoá mới hoặc dùng lại file `.key` gốc |
| Lỗi truy cập file | File nguồn và đích trùng nhau, hoặc file đang mở ở app khác | Chọn file đích khác, đóng app đang dùng file |
| Hết dung lượng ổ đĩa | File lớn cần chỗ cho cả bản mã hoá và giải mã | Dọn ổ đĩa hoặc dùng ổ khác |

---

## 🚧 Hạn chế & hướng mở rộng

- **CBC không có xác thực toàn vẹn:** nếu file mã hoá bị sửa, chương trình không phát hiện được (có thể ra rác hoặc báo lỗi padding). Hướng cải tiến: dùng **AES-GCM** hoặc thêm **HMAC-SHA256**.
- Khoá lưu trong file base64 **không được bảo vệ**; thực tế nên bọc khoá bằng mật khẩu (PBKDF2/Argon2) hoặc bằng RSA (liên quan Bài 2).
- Chưa hỗ trợ huỷ tác vụ giữa chừng trên giao diện (code lõi đã có `CancellationToken`).

---

## 📄 Giấy phép
Dùng cho mục đích học tập.
