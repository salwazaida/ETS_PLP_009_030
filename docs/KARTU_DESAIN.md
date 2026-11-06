# Kartu Desain

Lima keputusan desain penting beserta alternatif yang ditolak dan alasannya.
Keputusan 1 dan 2 oleh Fathimah (lexer dan parser). Keputusan 3 sampai 5 oleh Salwa (resolver dan analyzer).

## Keputusan 1 (Fathimah): presedensi AND/OR dinyatakan sebagai dua fungsi bertingkat

- **Keputusan.** `_logical` hanya menangani `OR` dan memanggil `_and` untuk operandnya. `_and` menangani `AND` dan memanggil `_not`. Presedensi tercermin dari urutan pemanggilan fungsi, sama seperti grammar `or_expr`, `and_expr`, `not_expr`.
- **Alternatif yang ditolak.** Satu fungsi dengan tabel presedensi (precedence climbing), dan satu loop yang menerima `AND` dan `OR` sekaligus (kode awal, yang salah).
- **Alasan.** Struktur fungsi sama persis dengan grammar di SPESIFIKASI.md sehingga mudah diperiksa baris demi baris; satu loop untuk dua operator membuat keduanya berpresedensi sama.
Kelemahan: setiap tingkat presedensi baru menambah fungsi.

## Keputusan 2 (Fathimah): komentar dibuang di lexer, tanpa token

- **Keputusan.** Komentar `--` dan `/* ... */` dikonsumsi oleh lexer dan tidak menghasilkan token. Komentar blok yang tidak ditutup adalah `LexError` di posisi awal komentar.
- **Alternatif yang ditolak.** Menghasilkan token `COMMENT` lalu menyaringnya di parser.
- **Alasan.** Spesifikasi 2.3 menyatakan komentar tidak menghasilkan token, dan parser tidak perlu tahu komentar. Membuang di lexer membuat parser lebih sederhana dan posisi baris/kolom tetap benar karena semua karakter dibaca lewat `_advance()`. 
Kelemahan: tool tidak bisa menampilkan komentar (misalnya untuk dokumentasi).

## Keputusan 3 (Salwa): resolver sebagai pass terpisah setelah parser

- **Keputusan.** Resolusi nama (menghubungkan setiap `ColumnRef` ke tabelnya) dikerjakan oleh `Resolver`, satu penelusuran AST tersendiri setelah parsing selesai dan sebelum analyzer. Parser hanya membangun pohon, dan field `ColumnRef.resolved` diisi belakangan oleh resolver.
- **Alternatif yang ditolak.** Menyelesaikan nama sambil parsing, yaitu parser langsung mengisi tabel kolom saat membaca kolom itu.
- **Alasan.** Dalam grammar SQL, daftar kolom ditulis sebelum `FROM`, sehingga saat parser membaca `p.id` ia belum melihat `FROM pelanggan p` dan belum tahu `p` itu apa. Resolusi satu lintasan tidak mungkin tanpa menambal ulang belakangan. Setelah pohon utuh, resolver bisa melihat seluruh scope sekaligus. Spesifikasi bagian 7 juga mewajibkan urutan lexer, parser, resolver, analyzer, dengan resolver sebagai pass terpisah dan parser tanpa resolusi. Ini sejalan dengan Bab 11 yang menaruh resolusi variabel di pass sendiri antara parser dan interpreter.
- **Kelemahan.** Ada satu penelusuran pohon tambahan, dan AST dimutasi setelah dibangun (`resolved` awalnya `None`). Analyzer harus dijalankan setelah resolver, kalau tidak `column_usage` kosong.

## Keputusan 4 (Salwa): scope sebagai tumpukan scope bersarang

- **Keputusan.** Setiap `SELECT` (termasuk subquery), `UPDATE`, dan `DELETE` membuka scope baru lewat `_push`, dan menutupnya lewat `_pop` di akhir. Tiap scope menyimpan peta alias ke tabel dan menunjuk scope sebelumnya sebagai induk. Alias ber-qualifier dicari dari scope terdalam naik ke luar dan berhenti di yang pertama ketemu. Kolom tanpa qualifier hanya dilihat di scope terdalam.
- **Alternatif yang ditolak.** (a) Satu kamus alias datar untuk seluruh statement tanpa scope bersarang. (b) Mencari alias dari scope terluar (perilaku kode awal). (c) Mencari kolom tanpa qualifier juga ke scope luar bila tidak ketemu.
- **Alasan.** (a) Tidak bisa menyatakan dua alias bernama sama di tingkat berbeda, misalnya alias `x` di luar dan di subquery pada `audit.sql` baris 12, dan tidak bisa menyatakan correlated subquery yang boleh mengacu alias luar (spesifikasi 4.3). (b) Alias luar mengalahkan alias dalam, melanggar shadowing, dan itulah Bug 1. (c) Tanpa skema database, menebak kolom milik tabel luar bisa menautkan ke tabel yang salah, jadi aturan spesifikasi memilih tidak menelusur dan cukup memberi warning. Pasangan `_push` dan `_pop` yang selalu seimbang menjaga aturan 4.5: setiap statement berdiri sendiri.
- **Kelemahan.** Satu `_pop` yang hilang membuat scope bocor ke statement berikutnya (terbukti pada `_delete`, Bug 8). Kolom tanpa qualifier yang sebenarnya milik tabel luar di correlated subquery tidak ter-resolve, dan kolom tanpa qualifier pada scope berisi lebih dari satu tabel selalu ambigu karena tidak ada skema untuk membedakannya.

## Keputusan 5 (Salwa): analyzer bekerja di atas AST, tanpa regex

- **Keputusan.** `analyze_statement` menentukan operasi CRUD per tabel dengan menelusuri AST yang sudah diparse dan di-resolve. Analyzer tidak membaca teks SQL mentah dan tidak memakai regex. Peran tabel (target atau sumber baca) ditentukan dari posisi node di pohon.
- **Alternatif yang ditolak.** Mengekstrak tabel dengan regex langsung dari teks SQL, seperti `baseline/regex_extractor.py`.
- **Alasan.** Spesifikasi bagian 7 melarangnya. Hasil evaluasi menunjukkan perbedaannya: parser 1.00 pada seluruh triple berlabel, sedangkan regex 0.54 precision dan 0.76 recall (tiga file berlabel). Regex salah karena tidak mengenal komentar dan string yang berisi kata kunci, menghitung `DELETE FROM x` juga sebagai `FROM`, dan tetap menghitung statement yang rusak. Aturan CRUD butuh membedakan tabel target dari tabel yang hanya dibaca lewat subquery, dan itu hanya jelas dari struktur pohon.
- **Kelemahan.** Analyzer sepenuhnya bergantung pada grammar parser: konstruk di luar lingkup (CTE, UNION, DDL) gagal diparse sehingga tabelnya tidak dihitung sama sekali, sedangkan regex setidaknya menangkap sebagian. Selain itu analyzer salah kalau aturan peran dicampur, seperti pada saat subquery di UPDATE ditandai `U`.