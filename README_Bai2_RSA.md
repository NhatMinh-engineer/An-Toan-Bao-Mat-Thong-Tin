# 🔐 Bài 2 — Mã hoá RSA (bất đối xứng) bằng C# / .NET 8

> Môn: An toàn & Bảo mật thông tin  
> Ứng dụng desktop (WinForms) + bản console: sinh cặp khoá, xuất/xem/nhập **PEM**, mã hoá/giải mã, đo tốc độ, băm **SHA-256**, và **chữ ký số**.

<img width="980" height="703" alt="image" src="https://github.com/user-attachments/assets/0eea04bd-3b7b-4569-a799-1080a70eac45" />

<!-- Chụp màn hình tab "Bài 2 — RSA" rồi đặt vào docs/images/rsa-tab.png -->

---

## 📋 Mục lục
1. [Đề bài](#-đề-bài)
2. [Tính năng](#-tính-năng)
3. [Công nghệ & cấu trúc project](#-công-nghệ--cấu-trúc-project)
4. [Thiết kế](#-thiết-kế)
5. [Cài đặt & chạy](#-cài-đặt--chạy)
6. [Hướng dẫn sử dụng](#-hướng-dẫn-sử-dụng)
7. [Đoạn code chính](#-đoạn-code-chính)
8. [Thử nghiệm & số liệu tốc độ](#-thử-nghiệm--số-liệu-tốc-độ)
9. [Câu hỏi 9 — chữ ký số khác nhau mỗi lần ký](#-câu-hỏi-9--chữ-ký-số-khác-nhau-mỗi-lần-ký)
10. [Lỗi thường gặp](#-lỗi-thường-gặp)
11. [Hạn chế & hướng mở rộng](#-hạn-chế--hướng-mở-rộng)

---

## 📝 Đề bài

**RSA** là mã hoá bất đối xứng: mã hoá bằng 1 chìa (khoá), giải mã bằng chìa còn lại.

Tạo ứng dụng **.NET** với các chức năng:

1. Sinh cặp khoá
2. Xuất cặp khoá ra file (**PEM**)
3. View PEM: cùng ý nghĩa các byte trong format PEM
4. Nhập 1 file PEM public → lấy được **n, e**; nhập 1 file PEM private → lấy được **n, e, d, p, q...**
5. Mã hoá dữ liệu (mảng byte ≤ 190 byte, ví dụ khoá AES-256 = 32 byte) bằng key vừa import → kết quả base64 → lưu file
6. Giải mã (đầu vào: PEM + file chứa data đã mã hoá base64) → so sánh với bản gốc
7. Đánh giá tốc độ mã hoá/giải mã: dùng public key (n, e bé) hay private key (n, d to) thì nhanh/chậm ra sao?
8. Giao diện sinh chuỗi băm **SHA-256**: thay đổi đầu vào (rất ít) → đánh giá sự thay đổi của kết quả băm
9. **Chữ ký số** = mã hoá bằng RSA với khoá bí mật trên kết quả băm của dữ liệu. Yêu cầu: **cùng dữ liệu, cùng private key** nhưng **mỗi lần ký ra chữ ký khác nhau** → đề xuất phương pháp.

---

## ✨ Tính năng

| # | Chức năng | Cách làm |
|---|-----------|----------|
| 1 | Sinh cặp khoá | **RSA-2048 bit** (`RSA.Create(2048)`) |
| 2 | Xuất PEM | public → `SubjectPublicKeyInfo` (`BEGIN PUBLIC KEY`), private → `PKCS#8` (`BEGIN PRIVATE KEY`) |
| 3 | View PEM | tự viết parser **DER/ASN.1 (TLV)**: in offset, tag, length, giá trị + nhãn n, e, d, p, q, dP, dQ, qInv |
| 4 | Import PEM | đọc lại public/private, tách đúng n, e (và d, p, q... nếu là private) |
| 5 | Mã hoá dữ liệu ≤ 190 byte | **OAEP-SHA256**, kết quả base64, lưu ra file |
| 6 | Giải mã | đọc PEM private + file base64 → so sánh với bản gốc |
| 7 | Đo tốc độ | `Stopwatch`, lặp 200 lần, so public vs private |
| 8 | SHA-256 realtime | băm lại mỗi khi gõ, so bit khác với lần băm trước + test lật 1 bit × 200 lần |
| 9 | Chữ ký số ngẫu nhiên | **RSASSA-PSS** (xem mục 9 bên dưới) |

---

## 🧱 Công nghệ & cấu trúc project

- C# / **.NET 8**, WinForms (giao diện) + Console (menu)
- Thư viện mật mã có sẵn: `System.Security.Cryptography` (không cần cài thêm gói)

```
CryptoLab/
├── CryptoLab.Core/
│   ├── RsaService.cs         # ← Bài 2, mục 1,2,4,5,6,7
│   ├── PemInspector.cs       # ← Bài 2, mục 3 (giải DER/ASN.1)
│   ├── HashService.cs        # ← Bài 2, mục 8 (SHA-256 + avalanche)
│   └── SignatureService.cs   # ← Bài 2, mục 9 (chữ ký số PSS / PKCS#1)
├── CryptoLab.WinForms/        # Giao diện, tab "Bài 2 — RSA" + "Bài 8 — SHA-256" + "Bài 9 — Chữ ký số"
│   └── MainForm.cs
└── CryptoLab.Console/         # Bản menu console
    └── Program.cs
```

Tách `Core` khỏi giao diện để cùng một logic dùng được cho cả form lẫn console, và dễ kiểm thử.

---

## 🧠 Thiết kế

### Vì sao giới hạn 190 byte?

RSA-2048 với đệm **OAEP-SHA256** chỉ mã hoá tối đa:

```
256 byte (= 2048 bit)  −  2 × 32 byte (2 lần hash SHA-256 trong OAEP)  −  2 byte  =  190 byte
```

Đây chính là lý do con số 190 trong đề — vừa đủ để "bọc" 1 khoá AES-256 (32 byte, hoặc ~44 ký tự base64).

### Định dạng PEM

```
public.pem   :  -----BEGIN PUBLIC KEY-----   (SubjectPublicKeyInfo, chứa OID rsaEncryption + n, e)
private.pem  :  -----BEGIN PRIVATE KEY-----  (PKCS#8, chứa version + n, e, d, p, q, dP, dQ, qInv)
```

`PemInspector` tự giải khối DER bên trong (không dùng thư viện ngoài): mỗi phần tử ASN.1 gồm **Tag (1 byte) + Length (1-n byte) + Value**, in ra theo cây lồng nhau kèm chú thích byte nào là n, e, d, p, q...

### Vì sao public key mã hoá nhanh, private key giải mã chậm

- Public exponent `e` mặc định = **65537** (chỉ ~17 bit, nhị phân chỉ có 2 bit 1) → phép luỹ thừa mod `cipher = m^e mod n` chỉ cần ~17 phép bình phương/nhân.
- Private exponent `d` dài **~2048 bit** → `plain = c^d mod n` cần hàng nghìn phép nhân lớn, chậm hơn nhiều.
- .NET dùng **CRT** (Chinese Remainder Theorem, nhờ có sẵn p, q, dP, dQ, qInv trong khoá riêng) để tăng tốc giải mã, nếu không có CRT còn chậm hơn nữa.

### Chữ ký số

`chữ ký = RSA_encrypt(SHA256(dữ liệu), private_key)` — ký bằng khoá bí mật, verify bằng khoá công khai. Dùng **RSASSA-PSS** thay vì PKCS#1 v1.5 để mỗi lần ký ra kết quả khác nhau (xem mục 9).

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

# Chạy bộ test tự động (roundtrip 190B, PEM, benchmark, PSS, avalanche)
cd CryptoLab.Console
dotnet run -- selftest
```

---

## 🖱️ Hướng dẫn sử dụng

### Tab "Bài 2 — RSA"

1. **1+2. Sinh cặp khoá 2048 & xuất PEM** → chọn nơi lưu `public.pem` và `private.pem`.
2. **3. View PEM…** → chọn 1 file PEM bất kỳ → ô "Giải mã cấu trúc PEM/DER" hiện cây TLV kèm chú thích.
3. **4a. Import public.pem** / **4b. Import private.pem** → ô "Thành phần khoá vừa import" hiện n, e (và d, p, q... nếu import private).
<img width="977" height="895" alt="image" src="https://github.com/user-attachments/assets/fcee1b71-e733-431e-ba44-d88f6ce7f52d" />

4. Gõ dữ liệu vào ô **"5. Dữ liệu (≤ 190 byte, UTF-8)"** → bấm **Mã hoá (public) → lưu file base64**. Ô "Ciphertext (base64)" hiện kết quả, đồng thời lưu ra file.
5. Bấm **6. Giải mã (private) ← file base64** → chọn lại file vừa lưu → ô "Kết quả" hiện văn bản giải mã + xác nhận **khớp dữ liệu gốc: CÓ/KHÔNG**.
6. Bấm **7. Đánh giá tốc độ** (cần đã import private key) → hiện số ms/lần của mã hoá (public) và giải mã (private), cùng tỉ lệ chậm hơn bao nhiêu lần.
<img width="976" height="982" alt="image" src="https://github.com/user-attachments/assets/3562959b-4423-479b-9409-73689ec0d751" />

> ⚠️ Dữ liệu ở bước 5 phải ≤ 190 byte (UTF-8) — nếu dài hơn ứng dụng sẽ báo lỗi, đúng giới hạn OAEP-SHA256 của RSA-2048.

### Tab "Bài 8 — SHA-256"

- Gõ chuỗi vào ô nhập → kết quả SHA-256 (hex) tự cập nhật theo từng ký tự, kèm **số bit khác so với lần băm trước**.
- Bấm **"Thống kê: lật 1 bit ngẫu nhiên × 200 lần"** → hiện trung bình/min/max số bit đầu ra thay đổi khi chỉ lật **1 bit** đầu vào (hiệu ứng avalanche).
<img width="978" height="513" alt="image" src="https://github.com/user-attachments/assets/c50a6f85-8ea1-4ba4-9b58-73e09e54ba35" />

### Tab "Bài 9 — Chữ ký số"

- Nhập dữ liệu cần ký → bấm **"Ký 3 lần: PSS vs PKCS#1 v1.5"** → hiện 3 chữ ký PKCS#1 (giống hệt nhau) rồi 3 chữ ký PSS (khác nhau mỗi lần, verify đều đúng), và kết quả verify khi sửa 1 ký tự dữ liệu (phải ra `False`).
<img width="975" height="665" alt="image" src="https://github.com/user-attachments/assets/fcf0e3d6-d28c-4760-8f03-ebeef053bac9" />

### Bản console (tuỳ chọn)

Chạy `dotnet run` ở `CryptoLab.Console`, chọn các mục **6 → 14** trong menu (sinh khoá/PEM, view PEM, import, mã hoá, giải mã, benchmark, avalanche, chữ ký số).

---

## 💻 Đoạn code chính

**Sinh khoá & xuất PEM**
```csharp
public static RSA GenerateKeyPair(int bits = 2048) => RSA.Create(bits);

public static void ExportPem(RSA rsa, string publicPath, string privatePath)
{
    File.WriteAllText(publicPath, rsa.ExportSubjectPublicKeyInfoPem());
    File.WriteAllText(privatePath, rsa.ExportPkcs8PrivateKeyPem());
}
```

**Mã hoá / giải mã (≤ 190 byte, OAEP-SHA256)**
```csharp
public static readonly RSAEncryptionPadding Padding = RSAEncryptionPadding.OaepSHA256;
public static int MaxPlainBytes(int keyBits) => keyBits / 8 - 2 * 32 - 2;   // = 190 với 2048 bit

public static string Encrypt(RSA rsa, byte[] data)
{
    int max = MaxPlainBytes(rsa.KeySize);
    if (data.Length > max) throw new ArgumentException($"Dữ liệu tối đa {max} byte, hiện có {data.Length}.");
    return Convert.ToBase64String(rsa.Encrypt(data, Padding));
}

public static byte[] Decrypt(RSA rsa, string base64) =>
    rsa.Decrypt(Convert.FromBase64String(base64.Trim()), Padding);
```

**Đo tốc độ (public vs private)**
```csharp
public static (double encMsPerOp, double decMsPerOp) Benchmark(RSA rsa, int iterations = 200)
{
    var data = RandomNumberGenerator.GetBytes(32);
    var cipher = rsa.Encrypt(data, Padding);
    var sw = Stopwatch.StartNew();
    for (int i = 0; i < iterations; i++) rsa.Encrypt(data, Padding);
    double enc = sw.Elapsed.TotalMilliseconds / iterations;
    sw.Restart();
    for (int i = 0; i < iterations; i++) rsa.Decrypt(cipher, Padding);
    double dec = sw.Elapsed.TotalMilliseconds / iterations;
    return (enc, dec);
}
```

**Chữ ký số — PSS (ngẫu nhiên) vs PKCS#1 v1.5 (tất định)**
```csharp
public static byte[] SignPss(RSA privateKey, byte[] data) =>
    privateKey.SignData(data, HashAlgorithmName.SHA256, RSASignaturePadding.Pss);

public static bool VerifyPss(RSA publicKey, byte[] data, byte[] sig) =>
    publicKey.VerifyData(data, sig, HashAlgorithmName.SHA256, RSASignaturePadding.Pss);
```

---

## 🧪 Thử nghiệm & số liệu tốc độ

### Quy trình đo
1. Sinh khoá 2048 bit, xuất PEM, import lại public + private.
2. Chạy **"7. Đánh giá tốc độ"** (hoặc menu console mục 12) với 200 lần lặp, có warm-up để giảm nhiễu do JIT.
3. Ghi lại ms/lần mã hoá (public) và ms/lần giải mã (private).

### Bảng số liệu

> Điền số liệu **đo thật trên máy của bạn**.

| Thao tác | Khoá dùng | Độ lớn số mũ | Thời gian / lần (ms) |
|---|---|---|---:|
| Mã hoá   | public (n, e)  | e = 65537 (~17 bit) | 0,034 ms/lần  |
| Giải mã  | private (n, d) | d ~2048 bit          | 0,411 ms/lần |
=> Giải mã chậm hơn ≈ 12 lần
→ e nhỏ (65537, ~17 bit) nên luỹ thừa mod nhanh; d ~2048 bit nên chậm.


### Kết luận 

1. **Public key luôn nhanh hơn private key** khi dùng để mã hoá/giải mã, vì số mũ `e` rất nhỏ còn `d` có kích thước bằng cả khoá (2048 bit).
2. Chênh lệch tốc độ không đổi nhiều theo dữ liệu (dữ liệu ≤ 190 byte, chi phí chủ yếu nằm ở phép luỹ thừa mod, không phụ thuộc độ dài dữ liệu).
3. Vì lý do này, trong thực tế RSA **không dùng để mã hoá trực tiếp dữ liệu lớn** mà chỉ dùng để mã hoá (bọc) một khoá đối xứng (AES) ngắn — đúng như gợi ý "khoá AES 256 bit (32 byte)" trong đề.
4. **Tính đúng đắn:** mọi lần mã hoá rồi giải mã (≤ 190 byte) đều khôi phục chính xác dữ liệu gốc (roundtrip = đúng); nếu đưa 191 byte trở lên, chương trình từ chối ngay với thông báo lỗi.

---

## 🖊️ Câu hỏi 9 — Chữ ký số khác nhau mỗi lần ký

**Yêu cầu đề:** cùng 1 dữ liệu, cùng 1 private key → mỗi lần ký cho ra **chữ ký khác nhau**.

**Vấn đề:** RSA ký kiểu **PKCS#1 v1.5** là *tất định* (deterministic): cùng data + cùng khoá luôn cho đúng 1 kết quả, không bao giờ đổi — vì phần đệm (padding) trước khi luỹ thừa với `d` là cố định.

**Giải pháp đề xuất — RSASSA-PSS (`RSASignaturePadding.Pss`):**

1. Băm dữ liệu: `H = SHA256(data)`.
2. Sinh một **salt ngẫu nhiên** (ở đây 32 byte) **mới cho mỗi lần ký**.
3. Trộn `H` và `salt` qua hàm `MGF1` để tạo chuỗi đã đệm (padded message).
4. Ký bằng phép luỹ thừa mod với khoá bí mật `d` như bình thường.

→ Vì salt ngẫu nhiên khác nhau mỗi lần, **chữ ký ra khác nhau ở mỗi lần ký**, dù data và private key giữ nguyên. Khi **verify**, bên nhận chỉ cần public key — không cần biết salt — vì salt đã nằm sẵn trong chữ ký và thuật toán verify tự tách ra để kiểm tra lại.

Project cài cả 2 kiểu để so sánh trực quan: `SignatureService.SignPss()/VerifyPss()` (đúng yêu cầu đề — ngẫu nhiên) và `SignatureService.SignPkcs1()/VerifyPkcs1()` (tất định — minh hoạ vấn đề cần giải quyết).

*Phương án khác (không chọn):* ghép thêm nonce/timestamp vào `data` trước khi ký — nhưng khi đó "dữ liệu" đem ký đã khác với dữ liệu gốc, và bên verify phải biết trước nonce/timestamp đó mới verify được, rườm rà hơn PSS (PSS không đổi gì ở data, chỉ ngẫu nhiên hoá bước đệm).

### Kết quả mẫu (selftest)
```
PSS: 2 lần ký giống nhau? False | verify1=True verify2=True
PSS sai dữ liệu verify?           False
```
→ Hai chữ ký PSS khác nhau nhưng cả hai đều verify đúng; sửa dữ liệu thì verify sai như mong đợi.

---

## 🛠️ Lỗi thường gặp

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| `Dữ liệu tối đa 190 byte, hiện có ...` | Nhập dữ liệu dài hơn giới hạn OAEP-SHA256 của RSA-2048 | Rút ngắn dữ liệu, hoặc chỉ dùng RSA để mã hoá 1 khoá AES ngắn |
| `File này không phải public key.` / `...private key.` | Import nhầm loại PEM (bấm nút 4a nhưng chọn file private, hoặc ngược lại) | Chọn đúng file `public.pem` / `private.pem` |
| Lỗi khi giải mã (`Bad Data` / exception từ `rsa.Decrypt`) | Dùng sai private key (không khớp với public key đã mã hoá), hoặc file base64 bị sửa | Dùng đúng cặp khoá đã sinh ra cùng nhau |
| `Chưa import public key.` / `Chưa import private key.` | Bấm Mã hoá/Giải mã/Đánh giá tốc độ trước khi import khoá tương ứng | Import đúng PEM (4a trước khi mã hoá, 4b trước khi giải mã/đo tốc độ) |
| `FormatException` khi đọc file PEM | File không đúng định dạng PEM (thiếu `-----BEGIN...-----`) | Dùng đúng file do chương trình xuất ra (nút 1+2), không sửa tay nội dung |

---

## 🚧 Hạn chế & hướng mở rộng

- **Không dùng để mã hoá dữ liệu lớn:** RSA chỉ mã hoá được tối đa 190 byte/lần (RSA-2048 + OAEP-SHA256); muốn mã hoá file lớn phải kết hợp **RSA + AES** (RSA mã hoá khoá AES, AES mã hoá dữ liệu — mô hình hybrid encryption, liên quan trực tiếp Bài 1).
- **PemInspector** hiện chỉ hỗ trợ đọc đúng cấu trúc RSA (SPKI/PKCS#8 chuẩn do chính chương trình xuất ra); PEM từ nguồn khác có thể có cấu trúc OID/đệm khác nên hiển thị không chính xác.
- Khoá private PEM xuất ra **không được mã hoá bằng mật khẩu**; thực tế nên dùng PKCS#8 có mật khẩu (`ExportEncryptedPkcs8PrivateKeyPem`) để bảo vệ file khi lưu trữ.
- Chưa benchmark với các độ dài khoá khác (1024, 3072, 4096 bit) để so sánh tốc độ/độ an toàn.

---

## 📄 Giấy phép
Dùng cho mục đích học tập.
