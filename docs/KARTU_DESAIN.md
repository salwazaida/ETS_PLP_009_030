# Kartu Desain

Tuliskan lima keputusan desain penting dalam pekerjaan kalian. Untuk tiap keputusan, sebutkan
alternatif yang ditolak dan alasannya. Contoh topik (boleh memilih yang lain):

- bagaimana parser membedakan `*` sebagai "semua kolom" dan sebagai perkalian;
- di mana dan bagaimana presedensi `AND`/`OR` dinyatakan;
- mengapa error recovery berhenti di `;`, bukan di keyword `SELECT` berikutnya;
- urutan pencarian scope dan akibatnya pada shadowing serta correlated subquery;
- mengapa kolom tanpa qualifier hanya dilihat di scope terdalam, dan apa kelemahannya;
- bagaimana implementasi `INSERT ... SELECT` atau komentar blok kalian.

| No | Keputusan | Alternatif yang ditolak | Alasan |
| --- | --- | --- | --- |

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

## Keputusan 3 (Salwa): isi di sini

| Keputusan | Alternatif yang ditolak | Alasan |
| --- | --- | --- |
| | | |

## Keputusan 4 (Salwa): isi di sini

## Keputusan 5 (Salwa): isi di sini
