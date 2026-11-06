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

**Peran AI.** AI menunjukkan lokasi masalah dan membantu menyusun kode perbaikan. Diverifikasi dengan
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

**Peran AI.** AI membantu memverifikasi kegagalan `test_matrix_laporan_penjualan` ke baris 6
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

## Fitur dilengkapi (bukan bug): TODO(T1) INSERT ... SELECT

**Gejala.** `INSERT INTO arsip (id) SELECT id FROM pesanan` ditolak dengan
`INSERT ... SELECT belum didukung`. SPESIFIKASI.md bagian 3 dan 5 mewajibkan bentuk ini; tabel
target `C`, tabel sumber `R`. `test_insert_select` gagal, dan `laporan_penjualan.sql` baris 10
gagal di-parse.

**Akar masalah.** (DRAFT) Cabang `SELECT` di `_insert` sengaja dibiarkan melempar error.
Grammar `insert_stmt` punya dua alternatif setelah daftar kolom: `VALUES ...` atau `select_stmt`.
Karena `select_stmt` sudah punya fungsi sendiri, cukup dipanggil dari `_insert` (rekursi
antar aturan, Bab 6).

**Perbaikan.** `crud/parser.py`, `_insert`: panggil `self._select()` dan kembalikan
`ast.Insert(table, columns, [], query)`.

**Test regresi.** `test_regresi_insert_select_menghasilkan_query`.

---

## Bug 4: AND dan OR memiliki presedensi yang sama

**Ditemukan oleh:** Fathimah · **Diperbaiki oleh:** Fathimah

**Gejala.** `a = 1 OR b = 2 AND c = 3` terbaca `(a = 1 OR b = 2) AND c = 3`; akar pohon AST
adalah `AND`. SPESIFIKASI.md 3.1 menyatakan `OR` presedensi terendah dan `AND` lebih tinggi,
sehingga seharusnya `a = 1 OR (b = 2 AND c = 3)`. Statement pertama `audit.sql` menguji ini.

**Reproduksi minimal.**

```sql
SELECT a FROM t WHERE a = 1 OR b = 2 AND c = 3
```

**Akar masalah.** (DRAFT) Grammar memisahkan `or_expr` dan `and_expr` menjadi dua tingkat,
tetapi `_logical` menggabungkannya dalam satu loop `while ... in ("AND", "OR")`. Pada recursive
descent (Bab 6), presedensi dibentuk oleh jumlah fungsi bertingkat: operator yang lebih
rendah dipanggil lebih dulu dan memanggil operator yang lebih tinggi untuk operandnya. Satu
fungsi untuk dua operator membuat keduanya berasosiasi kiri pada tingkat yang sama.

**Perbaikan.** `crud/parser.py`: `_logical` hanya menangani `OR` dan memanggil fungsi baru
`_and` untuk operandnya; `_and` menangani `AND` dan memanggil `_not`. Alternatif yang ditolak:
precedence climbing dengan tabel presedensi, karena mengubah gaya parser dan tidak sesuai
struktur grammar.

**Test regresi.** `test_regresi_presedensi_or_lebih_rendah_dari_and`.

**Peran AI.** AI membantu menelusuri bahwa `_logical` menggabungkan dua tingkat.
Diverifikasi dengan test yang gagal dulu (`'AND' == 'OR'`) lalu lulus.

---

## Bug 5: Error recovery membuang seluruh sisa file

**Ditemukan oleh:** Fathimah · **Diperbaiki oleh:** Fathimah

**Gejala.** Setelah satu statement rusak, semua statement valid sesudahnya tidak diproses.
SPESIFIKASI.md bagian 6: buang token sampai dan termasuk `;` berikutnya, lalu lanjutkan.

**Reproduksi minimal.**

```sql
SELECT FROM x; SELECT a FROM t;
```

**Akar masalah.** (DRAFT) `_synchronize` mengulang `_advance()` sampai akhir input, bukan
berhenti di titik aman. Pada *panic mode* (Bab 6), parser membuang token sampai batas
statement lalu melanjutkan agar error berikutnya tetap terlaporkan. Di SQL, batas itu adalah `;`.

**Perbaikan.** `crud/parser.py`, `_synchronize`: berhenti setelah mengonsumsi token
`SEMICOLON`.

**Test regresi.** `test_regresi_error_recovery_sampai_titik_koma`,
`test_tepi_satu_error_per_statement_rusak`.

**Peran AI.** AI membantu menelusuri bagian fungsi yang membuang semua token.
Diverifikasi dengan test (`1 == 2` sebelum perbaikan).

---

## Bug 6: LEFT OUTER JOIN tidak diterima

**Ditemukan oleh:** Fathimah · **Diperbaiki oleh:** Fathimah

**Gejala.** `LEFT OUTER JOIN` menghasilkan `diharapkan JOIN, ditemukan 'OUTER'`. Grammar
bagian 3: `join = [ "INNER" | "LEFT" [ "OUTER" ] ] "JOIN" ...`.

**Reproduksi minimal.**

```sql
SELECT a FROM t LEFT OUTER JOIN u ON t.id = u.id
```

**Akar masalah.** (DRAFT) `_join` tidak mengimplementasikan bagian opsional `[ "OUTER" ]`.
Pada parser recursive descent (Bab 6), setiap bagian opsional di grammar harus punya
pemeriksaan `match` sendiri; fungsi yang menerima lebih sedikit dari grammar menolak input yang
sah.

**Perbaikan.** `crud/parser.py`, `_join`: setelah `LEFT`, panggil `self._match_kw("OUTER")`.

**Test regresi.** `test_regresi_left_outer_join`.

**Peran AI.** AI membandingkan `_join` dengan grammar.

---

## Bug 7: pencarian alias dimulai dari scope terluar (shadowing salah)

**Ditemukan oleh:** Salwa · **Diperbaiki oleh:** Salwa

**Gejala.** Pada `data/sample/audit.sql` baris 12, `python -m crud.cli data\sample\audit.sql --ast` menampilkan `x.pelanggan_id -> pelanggan` dan `x.total -> pelanggan`. Padahal alias `x` di dalam subquery milik `pesanan`, sehingga seharusnya `-> pesanan` (SPESIFIKASI.md 4.3: alias di subquery menutupi alias yang sama di luar).


**Reproduksi minimal.**

```sql
SELECT x.id FROM pelanggan x
WHERE x.id IN (SELECT x.pelanggan_id FROM pesanan x WHERE x.total > 5);
```

**Akar masalah.** Resolver menyimpan scope sebagai rantai: setiap scope punya induk. Kode lama membangun daftar scope dari yang terdalam ke terluar, lalu membaliknya (`reversed`), sehingga yang diperiksa pertama adalah scope terluar. Jika alias yang sama ada di dalam dan di luar, yang ditemukan adalah yang luar. Itu melanggar lexical scope, yaitu deklarasi terdalam harus menutupi (*shadow*) deklarasi di luarnya. Konsep: environment berantai dan shadowing (bab 8), dan `resolveLocal` yang menelusuri dari scope terdalam ke luar lalu berhenti di yang pertama ketemu (bab 11).

**Perbaikan.** `crud/resolver.py`, fungsi `_lookup`: mulai dari `self.scope`, periksa, lalu naik ke `parent` sampai ketemu atau habis. Alternatif yang dipertimbangkan: tetap membangun daftar lalu mengiterasinya tanpa `reversed`. Hasilnya sama, tetapi lebih panjang dan tidak perlu.

**Test regresi.** `test_regresi_shadowing_alias_subquery_menutupi_alias_luar` di `tests/test_tambahan.py`. Lulus setelah perbaikan (terlihat `1 passed`).

**Peran AI.** AI memberi usulan perbaikan serta test.

---

## Bug 8: Scope DELETE tidak ditutup, sehingga bocor ke statement berikutnya

**Ditemukan oleh:** Salwa · **Diperbaiki oleh:** Salwa

**Gejala.** Di `audit.sql`, statement baris 16 adalah `DELETE ... sesi s`. Pada statement baris 18, `--ast` menampilkan `s.id -> sesi` dan tidak ada diagnostik error. Seharusnya alias `s` tidak terdefinisi di statement itu (SPESIFIKASI.md 4.5: setiap statement berdiri sendiri, tidak ada scope tersisa). Setelah perbaikan, `python -m crud.cli data\sample\audit.sql` menampilkan `audit.sql: baris 18: error: alias 's' tidak terdefinisi`.

**Reproduksi minimal.**

```sql
DELETE FROM sesi s WHERE s.id = 1;
SELECT s.id FROM pengguna u;
```

**Akar masalah.** Resolver memakai tumpukan scope. Setiap konstruk yang membuka scope harus menutupnya lagi. `_delete` membuka scope untuk alias tabel target tetapi tidak pernah menutupnya, sehingga scope itu tertinggal dan menjadi induk bagi statement berikutnya. Alias `s` milik DELETE jadi tetap terlihat. Konsep: `beginScope` dan `endScope` harus berpasangan (bab 11), sama seperti `executeBlock` yang memulihkan environment lama di blok `finally`.

**Perbaikan.** `crud/resolver.py`, fungsi `_delete`: tambahkan `self._pop()` di akhir. Alternatif yang dipertimbangkan: mengosongkan `self.scope` di awal tiap statement dalam `resolve_script`. Tidak memilih itu karena itu menyembunyikan kebocoran, bukan malah memperbaikinya; pasangan push dan pop yang benar menjaga invarian di tempat kerusakannya terjadi.

**Test regresi.** `test_regresi_scope_delete_tidak_bocor_ke_statement_berikutnya` di `tests/test_tambahan.py`. Lulus setelah perbaikan.

**Peran AI.** AI memverifikasi bug yang ditemukan.

---

## Bug 9: Tabel di subquery UPDATE ditandai U, seharusnya R

**Ditemukan oleh:** Salwa · **Diperbaiki oleh:** Salwa

**Gejala.** `pytest` menampilkan `test_matrix_laporan_penjualan` gagal: `pesanan` bernilai `RUD`, seharusnya `RD`. `evaluate.py` melaporkan parser salah: FP `('laporan_penjualan.sql', 12, 'pesanan', 'U')` dan FN `('laporan_penjualan.sql', 12, 'pesanan', 'R')`, parser 0.90. Spek bagian 5: tabel yang dibaca lewat subquery selalu `R`. Setelah perbaikan, parser 1.00.

**Reproduksi minimal.**

```sql
UPDATE a SET x = (SELECT MAX(y) FROM b) WHERE id IN (SELECT id FROM c);
```

**Akar masalah.** Operasi pada sebuah tabel ditentukan oleh perannya di statement: target (U) atau sumber baca (R). Di cabang UPDATE, kode lama meneruskan operasi `"U"` ke fungsi penelusur ekspresi, sehingga semua tabel di subquery ikut ditandai U, padahal subquery hanya membaca. Konsep: penelusuran pohon sintaks dengan visitor, tempat setiap node dikunjungi dengan konteks yang benar.

**Perbaikan.** `crud/analyzer.py`, fungsi `analyze_statement`, cabang `ast.Update`: dua pemanggilan `_collect(..., "U")` (untuk nilai `SET` dan `WHERE`) diubah menjadi `"R"`. Tabel target tetap `U`. Alternatifnya dengan menambah parameter peran per jenis statement. Tidak dipilih karena `op` sudah ada dan perubahan minimal cukup.

**Test regresi.** `test_regresi_subquery_di_update_adalah_read`. `test_matrix_laporan_penjualan` juga passed.

**Peran AI.** AI memverifikasi bug yang ditemukan.

---

## Fitur dilengkapi (bukan bug): TODO(T2) kolom tanpa qualifier di resolver

**Gejala.** `test_kolom_tanpa_qualifier_satu_tabel` gagal dengan
`AssertionError: assert {None} == {'pelanggan'}`: pada `SELECT nama FROM pelanggan WHERE aktif = 1`,
kolom `nama` dan `aktif` tidak pernah ter-resolve (`resolved` tetap `None`). SPESIFIKASI.md bagian
4.3 mewajibkan kolom tanpa qualifier hanya dicari di scope terdalam: bila ada tepat satu tabel,
kolom di-resolve ke tabel itu; bila lebih dari satu tabel, keluar warning
`kolom 'nama' ambigu tanpa skema` dan `resolved` tetap `None`; bila tidak ada tabel, keluar warning.

**Akar masalah.** ada Fitur belum diimplementasi: cabang kolom tanpa qualifier di `_column`
hanya berisi `pass`. Pada resolver (Bab 11), setiap penggunaan nama harus dihubungkan ke
deklarasinya secara statis, sebelum program dijalankan. Bedanya dengan kolom ber-qualifier,
kolom tanpa qualifier tidak menyebut tabel mana yang dimaksud, sedangkan proyek ini tidak punya
skema database (SPESIFIKASI.md bagian 7). Satu-satunya dasar keputusan adalah isi scope terdalam:
satu tabel berarti tidak ada keraguan, lebih dari satu berarti tidak bisa ditentukan sehingga
cukup diberi warning (analog bab 11.3.3: nama yang tidak bisa di-resolve tidak dipaksakan).

**Perbaikan.** `crud/resolver.py`, `_column`: ambil tabel-tabel di scope terdalam saja (tidak
naik ke scope luar). Satu tabel: isi `col.resolved` dengan tabel itu (untuk subquery di FROM:
`<subquery alias>`). Lebih dari satu: warning ambigu. Tidak ada tabel: warning. Ada pengecekan
`self.scope is not None` karena `INSERT` tidak membuat scope (SPESIFIKASI.md 4.1), sehingga
`INSERT ... VALUES (b)` tidak crash.

**Test.** `test_kolom_tanpa_qualifier_satu_tabel` (passed),
`test_regresi_kolom_tanpa_qualifier_dua_tabel_ambigu` dan
`test_tepi_insert_values_dengan_kolom_tanpa_scope_tidak_crash` (passed).

**Peran AI.** memverifikasi
lewat pytest `--ast` (kolom tanpa qualifier ter-resolve).

---