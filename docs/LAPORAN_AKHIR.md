# Laporan Akhir

## 1. Hasil evaluasi

Keluaran `python evaluate.py` setelah `data/ground_truth.csv` dilengkapi untuk keempat file:

```text

Dievaluasi: audit.sql, campuran_error.sql, laporan_penjualan.sql, pemeliharaan.sql (27 triple)

Metode   Precision  Recall     F1
parser        1.00    1.00   1.00
regex         0.65    0.81   0.72

[regex]
  salah ditemukan (FP): ('audit.sql', 16, 'sesi', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 4, 'pesanan', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 8, 'keranjang', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'D')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pesanan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'rahasia', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 15, 'pesanan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.alamat', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.pelanggan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'pelanggan_lama', 'U')
  salah ditemukan (FP): ('pemeliharaan.sql', 15, 'crm.alamat', 'R')
  terlewat (FN):       ('audit.sql', 2, 'pesanan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pelanggan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pesanan', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.alamat', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.pelanggan', 'R')
```

Parser mencapai precision dan recall 1.00 pada 27 triple berlabel, sedangkan regex hanya 0.65 dan 0.81. Kesalahan regex dijelaskan di bagian 2.

## 2. Tiga kasus dimana regex salah

Untuk tiap kasus: SQL-nya, kesalahan regex, dan mengapa parser benar (kaitkan dengan konsep
lexing, parsing, atau resolusi).

1. **Kasus 1: komentar dan string yang berisi kata kunci (lexing).**

```sql
-- Laporan penjualan bulanan
-- DELETE FROM pelanggan   (baris ini komentar, bukan perintah)
SELECT p.nama, SUM(o.total) AS omzet
FROM pelanggan p
JOIN pesanan o ON o.pelanggan_id = p.id
WHERE o.status = 'LUNAS' AND o.catatan <> 'FROM rahasia'
GROUP BY p.nama;
```

(`laporan_penjualan.sql` baris 1-7.) Regex memotong teks per `;`, lalu memakai kata `SELECT|INSERT|UPDATE|DELETE` pertama di potongan itu, termasuk yang ada di komentar. Statement dianggap mulai di baris 2 (bukan 3). Semua pola dijalankan juga pada isi komentar dan string, sehingga muncul `pelanggan D` dan `rahasia R` palsu, dan label yang benar di baris 3 menjadi FN. Hal yang sama terjadi pada komentar blok `pemeliharaan.sql` baris 1-2 (`UPDATE pelanggan_lama`). Parser benar karena lexer membuang komentar dan membaca isi string sebagai satu token `STRING`, jadi kata kunci di dalamnya tidak pernah sampai ke parser (bab 4).

2. **Kasus 2: `DELETE FROM x` ikut terbaca sebagai `FROM` biasa (parsing).**

```sql
DELETE FROM pesanan WHERE tanggal < :batas;
```

(`laporan_penjualan.sql` baris 15; kasus serupa di `campuran_error.sql` baris 8 dan `pemeliharaan.sql` baris 15.) Regex punya pola `FROM nama` (R) dan `DELETE FROM nama` (D), dan keduanya cocok pada kalimat yang sama, sehingga tabel yang seharusnya hanya `D` mendapat `R` palsu. Parser benar karena grammar `delete_stmt` menempatkan `FROM` sebagai bagian dari DELETE, bukan sebagai `table_ref` SELECT. Peran sebuah kata ditentukan oleh posisinya dalam grammar (bab 6).

3. **Kasus 3: statement yang gagal diparse tetap dihitung (error recovery).**

```sql
SELECT id nama, FROM pesanan;
```

(`campuran_error.sql` baris 4.) Regex melaporkan `pesanan R` untuk statement yang rusak. Spek bagian 5 menyatakan statement yang gagal diparse tidak dihitung. Parser melaporkan `Baris 4, kolom 17: diharapkan ekspresi, ditemukan 'FROM'`, membuang token sampai `;` (panic mode, spek bagian 6), lalu melanjutkan ke statement baris 6 dan 8 yang valid (bab 6).

## 3. Batas pendekatan kami

Minimal tiga hal yang **tidak bisa** ditangani dengan benar oleh tool ini meskipun semua bug
sudah diperbaiki. Untuk tiap batas: contoh SQL atau situasinya, akibatnya pada CRUD matrix,
dan informasi apa yang dibutuhkan untuk mengatasinya.

1. **Kolom tanpa qualifier saat ada lebih dari satu tabel.** `SELECT id FROM pelanggan p JOIN pesanan o ON o.pelanggan_id = p.id`. Resolver hanya memberi warning ambigu dan `resolved` tetap `None`, sehingga atribusi kolom itu hilang dari laporan `--kolom` (matrix tingkat tabel tetap benar). Dibutuhkan skema database (daftar kolom per tabel).
2. **Konstruk di luar lingkup (SPESIFIKASI.md bagian 9)**, misalnya CTE: `WITH baru AS (SELECT * FROM pesanan) SELECT * FROM baru`. Parser tidak mengenal `WITH`, statement dilaporkan sebagai error sintaks lalu tidak dihitung, sehingga `pesanan R` hilang dari matrix. Dibutuhkan dukungan grammar `WITH` dan resolusi nama CTE.
3. **Tabel yang tidak tampak sebagai teks SQL statis.** SQL yang dirakit di kode aplikasi (`"SELECT * FROM " + nama`), view, trigger, dan stored procedure. Tabel dasar di balik view tidak muncul di matrix. Dibutuhkan definisi view dan katalog database, atau analisis kode aplikasi.

## 4. Pembagian kerja

Siapa mengerjakan apa, dan bagaimana kalian memastikan keduanya memahami seluruh kode.

- **Salwa:** resolver (menyelesaikan TODO(T2), memperbaiki Bug 7 dan Bug 8), analyzer (Bug 9), memeriksa `pipeline.py` dan `cli.py` terhadap format bagian 8 (tidak ada bug), label `pemeliharaan.sql`, menjalankan `evaluate.py`, test regresi dan kasus tepi sisi B.
- **Fathimah:** lexer (keyword huruf kecil, `<>`, `''` di string, komentar blok), parser (INSERT ... SELECT, presedensi AND/OR, error recovery, `LEFT OUTER JOIN`), label `audit.sql`, test regresi dan lima kasus tepi, serta README dan riwayat commit.
- **Memastikan keduanya paham seluruh kode:** saling menjelaskan lexer, parser, resolver, dan analyzer secara lisan, serta menjalankan test bersama.