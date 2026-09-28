# MÔN AN TOÀN VÀ BẢO MẬT THÔNG TIN

## 1. Thuật toán mã hóa đối xứng DES và AES

### Thuật toán DES (Data Encryption Standard)
- **Mô tả:** Là thuật toán mã hóa đối xứng mã khối (block cipher), kích thước khối 64-bit, sử dụng khóa độ dài 56-bit. Dựa trên cấu trúc Feistel gồm 16 vòng lặp.
- **Quy trình mã hóa/giải mã:**
  1. Plaintext 64-bit đi qua Hoán vị ban đầu (IP).
  2. Chia làm 2 nửa L (Left) và R (Right) 32-bit.
  3. Trải qua 16 vòng biến đổi Feistel kết hợp với 16 khóa con (Subkeys).
  4. Ghép 2 nửa L, R và đi qua Hoán vị nghịch đảo (IP^-1) tạo ra Ciphertext.
  5. Giải mã thực hiện quy trình tương tự nhưng dùng các khóa con theo thứ tự ngược lại.

### Thuật toán AES (Advanced Encryption Standard)
- **Mô tả:** Thuật toán mã hóa đối xứng thay thế DES. Mã hóa khối 128-bit với các kích thước khóa 128, 192, hoặc 256-bit. Sử dụng mạng thay thế - hoán vị (Substitution-Permutation Network).
- **Quy trình mã hóa/giải mã (dùng AES-128 - 10 vòng):**
  1. **AddRoundKey:** Cộng trạng thái ban đầu với khóa lặp đầu tiên.
  2. **Các vòng lặp (Rounds 1 đến 9):**
     - *SubBytes:* Thay thế các byte phi tuyến bằng bảng S-Box.
     - *ShiftRows:* Dịch chuyển các hàng của ma trận trạng thái.
     - *MixColumns:* Trộn các cột để tăng độ khuếch tán.
     - *AddRoundKey:* Cộng khóa lặp tương ứng.
  3. **Vòng cuối (Round 10):** Thực hiện SubBytes, ShiftRows, AddRoundKey (không có MixColumns).
  4. Giải mã dùng các phép biến đổi ngược tương ứng: InvSubBytes, InvShiftRows, InvMixColumns, AddRoundKey.

---

## 2. Thuật toán mã hóa bất đối xứng RSA

### Nguyên lý sinh cặp khóa (Public Key & Private Key)
1. Chọn 2 số nguyên tố lớn ngẫu nhiên `p` và `q`.
2. Tính tích `n = p * q` (n là mô-đun cho cả khóa công khai và bí mật).
3. Tính hàm Euler: `phi(n) = (p - 1) * (q - 1)`.
4. Chọn số nguyên `e` sao cho `1 < e < phi(n)` và `gcd(e, phi(n)) = 1` (thường chọn `e = 65537`).
5. Tính `d` sao cho `(d * e) mod phi(n) = 1` (`d` là nghịch đảo nhân modular của `e`).
6. **Khóa công khai (Public Key):** cặp `(e, n)`.
7. **Khóa bí mật (Private Key):** cặp `d` (hoặc `(d, n)`).

---

## 3. Các mô hình áp dụng RSA và kết hợp RSA + AES

### Các mô hình áp dụng RSA
1. **Xác thực người nhận (Bảo mật thông tin):**
   - Người gửi dùng **Public Key của người nhận** để mã hóa.
   - Chỉ người nhận có **Private Key tương ứng** mới giải mã được.
2. **Xác thực người gửi (Chữ ký số - Digital Signature):**
   - Người gửi dùng **Private Key của mình** để mã hóa (ký số).
   - Người nhận dùng **Public Key của người gửi** để giải mã và kiểm tra nguồn gốc.
3. **Kết hợp cả hai (Vừa bảo mật vừa xác thực):**
   - Người gửi ký thông điệp bằng **Private Key của mình**, sau đó mã hóa toàn bộ bằng **Public Key của người nhận**.

### So sánh thời gian mã hóa/giải mã RSA và AES
- **AES:** Tốc độ mã hóa/giải mã rất nhanh, chi phí tính toán thấp, thích hợp truyền tải lượng dữ liệu lớn.
- **RSA:** Tốc độ mã hóa/giải mã rất chậm (chậm hơn AES hàng nghìn lần) do phải tính toán số mũ với số nguyên rất lớn.

### Mô hình kết hợp sức mạnh RSA và AES (Hybrid Encryption)
- **Ý tưởng:** Dùng AES để mã hóa dữ liệu thực tế (nhanh) và dùng RSA để trao đổi khóa AES (an toàn).
- **Quy trình:**
  1. Người gửi tạo một khóa đối xứng AES ngẫu nhiên (Session Key).
  2. Dùng khóa AES này để mã hóa toàn bộ dữ liệu dung lượng lớn.
  3. Dùng **Public Key RSA của người nhận** để mã hóa khóa AES đó.
  4. Gửi cả dữ liệu đã mã hóa (bằng AES) và khóa AES đã mã hóa (bằng RSA) cho người nhận.
  5. Người nhận dùng **Private Key RSA** để giải mã lấy khóa AES, sau đó dùng khóa AES giải mã lấy dữ liệu ban đầu.
