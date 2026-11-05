# Laporan Bug

Bagian **Akar masalah** wajib ditulis dengan kata-kata sendiri dan memakai konsep dari
*Crafting Interpreters* (sebutkan bab). Bagian ini diuji lisan.

> Catatan penyusun: teks "Akar masalah" di bawah masih DRAFT. Baca, pahami, lalu tulis ulang
> dengan kalimat sendiri sebelum dikumpulkan.

---

## Bug 1: Keyword huruf kecil terbaca sebagai IDENT

**Ditemukan oleh:** Fathimah · **Diperbaiki oleh:** Fathimah

**Gejala.** `tokenize("select id from t")` menghasilkan token pertama `IDENT 'select'`, padahal
SPESIFIKASI.md bagian 2.2 menyatakan keyword tidak peka huruf besar/kecil dan nilainya
dinormalisasi ke huruf besar. Test terlihat `test_keyword_huruf_kecil` gagal.

**Reproduksi minimal.**

```sql
select id from t
```

**Akar masalah.** (DRAFT) Lexer membaca satu kata utuh, lalu memutuskan jenisnya dengan mencari
kata itu di tabel `KEYWORDS`. Tabel hanya berisi huruf besar, sedangkan pencarian memakai teks
mentah, sehingga `"select" in KEYWORDS` bernilai False dan kata jatuh ke cabang IDENT. Ini
berkaitan dengan *reserved words* pada scanner (Bab 4): identifier dipindai dulu, lalu dicek
terhadap tabel kata cadangan. Kesalahan ini menjalar ke parser karena parser mengharapkan
token KEYWORD.

**Perbaikan.** `crud/lexer.py`, fungsi `_word`: pencarian memakai `text.upper()`, token
keyword menyimpan nilai huruf besar, token IDENT tetap menyimpan teks asli (normalisasi huruf
kecil adalah tugas parser). Alternatif yang ditolak: mengubah `KEYWORDS` menjadi huruf kecil
(melanggar aturan nilai token keyword selalu huruf besar) dan memakai `startswith` (membuat
`selection` salah terbaca sebagai keyword).

**Test regresi.** `test_regresi_keyword_tidak_peka_huruf` dan
`test_regresi_ident_berawalan_keyword_tetap_ident` di `tests/test_tambahan.py`.

**Peran AI.** AI menunjukkan lokasi masalah dan memberi kode perbaikan. Diverifikasi dengan
menulis test yang gagal sebelum perbaikan dan lulus sesudahnya, serta menjalankan seluruh test.

---

## Bug 2: Operator `<>` terpecah menjadi dua token

**Ditemukan oleh:** Fathimah · **Diperbaiki oleh:** Fathimah

**Gejala.** `a <> b` menghasilkan token `<` dan `>`, padahal SPESIFIKASI.md bagian 2.5
mewajibkan `<>` satu token (maximal munch). Akibatnya `laporan_penjualan.sql` baris 6 gagal
di parser dengan `Baris 6, kolom 41: diharapkan ekspresi, ditemukan '>'`. Gejala muncul di
parser, tetapi akarnya di lexer, dan test terlihat tidak menangkapnya secara langsung.

**Reproduksi minimal.**

```sql
SELECT 1 FROM t WHERE a <> 'x'
```

**Akar masalah.** (DRAFT) Setelah membaca `<`, kode hanya melihat satu karakter berikutnya
untuk `=`. Lexeme terpanjang yang cocok adalah `<>`, tetapi kode tidak mencobanya. Ini
melanggar prinsip *maximal munch* dan penggunaan *lookahead* satu karakter pada scanner
(Bab 4). Parser kemudian menerima `>` di posisi operand.

**Perbaikan.** `crud/lexer.py`, blok `if ch == "<"`: tambahkan cabang `elif self._match(">")`
yang menghasilkan `<>`. Alternatif yang ditolak: menggabungkan `<` dan `>` di parser
(mencampur tanggung jawab lexer dan parser).

**Test regresi.** `test_regresi_operator_tidak_sama_satu_token`.

**Peran AI.** AI membantu menghubungkan kegagalan `test_matrix_laporan_penjualan` ke baris 6
data uji dan memberi kode perbaikan. Diverifikasi lewat test baru dan seluruh test.

---

## Bug 3: `''` di dalam string tidak dibaca sebagai satu kutip

**Ditemukan oleh:** Fathimah · **Diperbaiki oleh:** Fathimah

**Gejala.** `'O''Brien'` menjadi dua token STRING (`'O'` dan `'Brien'`), padahal
SPESIFIKASI.md bagian 2.4 menyatakan satu token STRING bernilai `O'Brien`.

**Reproduksi minimal.**

```sql
SELECT 1 FROM t WHERE nama = 'O''Brien'
```

**Akar masalah.** (DRAFT) Fungsi `_string` menganggap kutip tunggal pertama sebagai penutup
string. Scanner perlu lookahead satu karakter setelah kutip untuk membedakan penutup dari kutip
yang ditulis dua kali (Bab 4, bagian string literal). Akibatnya satu nilai terpecah menjadi
dua token berurutan.

**Perbaikan.** `crud/lexer.py`, fungsi `_string`: jika setelah `'` masih ada `'`, konsumsi
keduanya dan tambahkan satu `'` ke isi string, lalu lanjut. String tidak tertutup tetap
`LexError`.

**Test regresi.** `test_regresi_kutip_ganda_dalam_string`.

**Peran AI.** AI membantu menyusun test dan kode perbaikan. Diverifikasi dengan test yang gagal dulu
(`2 == 1` token) lalu lulus, serta percobaan `''`, `''''`, `'it''s'`, dan `'abc` (LexError).

---

## Fitur dilengkapi (bukan bug): TODO(T3) komentar blok

**Gejala.** Setiap `/*` langsung `LexError: komentar blok belum didukung`
(`test_komentar_blok` gagal). SPESIFIKASI.md bagian 2.3 mewajibkan komentar blok, boleh lintas
baris, boleh berisi `*`, tidak bersarang, dan `LexError` bila tidak ditutup.

**Akar masalah.** (DRAFT) Fitur belum diimplementasi. Pada scanner (Bab 4), komentar adalah
lexeme yang dikonsumsi lalu dibuang tanpa menghasilkan token, dengan lookahead dua karakter
untuk mengenali penutup `*/` dan error untuk lexeme yang tidak ditutup.

**Perbaikan.** `crud/lexer.py`, `_scan_token`: setelah `/*`, majukan sampai `*/`; bila teks
habis, `LexError` di posisi awal komentar. Semua karakter dibaca lewat `_advance()` sehingga
nomor baris dan kolom tetap benar.

**Test.** `test_komentar_blok_lintas_baris_dan_nomor_baris`,
`test_komentar_blok_boleh_berisi_bintang`, `test_komentar_blok_tidak_ditutup_adalah_lexerror`.

---