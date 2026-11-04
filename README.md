# Ekstraktor CRUD Matrix

Tugas ETS mata kuliah **Programming Language Pragmatics**.

Tool ini membaca file SQL dan menghasilkan **CRUD matrix**: tabel mana yang dibuat (**C**), dibaca (**R**), diubah (**U**), dan dihapus (**D**) oleh setiap file. Hasil per file adalah gabungan seluruh statement di dalamnya. Tool juga melaporkan error sintaks dan diagnostik resolusi (alias tidak terdefinisi, kolom ambigu, dan sebagainya).

## Anggota Kelompok

- **Fathimah Az-Zahra Suriawinata** (251524009): lexer dan parser
- **Salwa Zaida Nasrullah** (251524030): resolver, analyzer, dan evaluasi

Pengerjaan dilakukan dengan pair programming, bergantian driver dan navigator, sehingga kedua anggota memahami seluruh kode. Pembagian di atas hanya menunjukkan siapa yang memimpin tiap bagian.

## Latar Belakang

Codebase awal sengaja dibuat belum lengkap dan mengandung beberapa bug. Pipeline-nya mengikuti buku *Crafting Interpreters*:

- **Lexer** (`crud/lexer.py`): Bab 4 (Scanning)
- **Grammar dan AST** (`crud/ast_nodes.py`): Bab 5 (Representing Code)
- **Parser recursive descent** (`crud/parser.py`): Bab 6 (Parsing Expressions)
- **Resolver scope dan alias** (`crud/resolver.py`): Bab 11 (Resolving and Binding)
- **Analyzer aturan CRUD** (`crud/analyzer.py`): tidak ada rujukan bab

Urutan pipeline tetap: **lexer → parser → resolver → analyzer**. Resolver adalah pass terpisah setelah parsing, dan analyzer bekerja di atas AST tanpa membaca teks SQL mentah.

## Yang Dikerjakan

1. **Melengkapi tiga bagian yang belum selesai**
   - `TODO(T1)`: `INSERT ... SELECT` di parser.
   - `TODO(T2)`: resolusi kolom tanpa qualifier di resolver.
   - `TODO(T3)`: komentar blok `/* ... */` di lexer.
2. **Menemukan dan memperbaiki bug.** Acuan kebenaran adalah `SPESIFIKASI.md`. Bila kode, komentar, dan spesifikasi berbeda, spesifikasi yang dianggap benar.
3. **Membuktikan perbaikan dengan test regresi** di `tests/test_tambahan.py`, ditambah lima test kasus tepi.
4. **Menjelaskan akar masalah** setiap bug memakai konsep dari buku (maximal munch, lookahead, presedensi, recursive descent, scope chain, dan seterusnya).
5. **Melabeli `data/ground_truth.csv`** untuk `audit.sql` dan `pemeliharaan.sql` secara manual berdasarkan spesifikasi, bukan dengan menyalin output tool.
6. **Mengevaluasi parser terhadap baseline regex** (precision dan recall) serta menganalisis kesalahan regex dan batas pendekatan.

## Struktur Repositori

- `SPESIFIKASI.md`: acuan kebenaran, berisi aturan lexer, grammar, resolver, dan CRUD
- `crud/`: kode utama (lexer, AST, parser, resolver, analyzer, pipeline, CLI)
- `baseline/regex_extractor.py`: pembanding berbasis regex (sengaja naif, tidak diubah)
- `evaluate.py`: perhitungan precision dan recall parser vs regex
- `data/sample/*.sql`: data uji
- `data/ground_truth.csv`: label benar untuk evaluasi
- `tests/`: test bawaan (tidak diubah) dan `test_tambahan.py` (test kami)
- `docs/`: dokumen deliverable

## Dokumen

- [`docs/LAPORAN_BUG.md`](docs/LAPORAN_BUG.md): satu entri per bug, lengkap dengan akar masalah.
- [`docs/KARTU_DESAIN.md`](docs/KARTU_DESAIN.md): lima keputusan desain beserta alternatif yang ditolak.
- [`docs/LAPORAN_AKHIR.md`](docs/LAPORAN_AKHIR.md): hasil evaluasi, analisis kesalahan regex, dan batas pendekatan.
- [`docs/LOG_AI.md`](docs/LOG_AI.md): log penggunaan AI.

## Batasan

Sesuai `SPESIFIKASI.md` bagian 9, hal berikut berada di luar lingkup: CTE (`WITH`), `UNION`, `MERGE`, DDL, quoted identifier, `t.*`, window function, alias kolom di `ORDER BY`, komentar bersarang, stored procedure, trigger, dan view. Tool juga tidak memakai skema database; semua keputusan diambil dari teks query.

## Atribusi

Struktur lexer, AST, parser, dan resolver diadaptasi dari konsep dan kode dalam *Crafting Interpreters* oleh Robert Nystrom (https://craftinginterpreters.com). Penggunaan AI dalam pengerjaan dicatat di `docs/LOG_AI.md`.
