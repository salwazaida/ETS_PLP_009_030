# Log Penggunaan AI

Catat setiap penggunaan AI atau coding agent yang memengaruhi kode atau laporan.

- Siapa: Fathimah. Tugas: menceritakan kebutuhan kami pada AI dan membagi pekerjaan untuk fathimah dan salwa. 
  Hasil: diterima, pembagian disesuaikan per bagian dari modul. 
  Alasan: pembagian disesuaikan dengan ukuran modul. 
  Verifikasi: dicek terhadap ukuran file `crud/*.py`.

- Siapa: Fathimah. Tugas: setup repo dan menjalankan pytest. 
  Hasil: diterima. 
  Alasan: AI membantu mendiagnosis dari output terminal. 
  Verifikasi: `dir` memperlihatkan file 0 byte, lalu pytest menunjukkan 5 failed 25 passed sesuai tugas.

- Siapa: Fathimah. Tugas: bug 1 keyword huruf kecil. 
  Hasil: membantu penyusunan kode, indentasi saat menempel diperbaiki sendiri. 
  Alasan: sesuai SPESIFIKASI 2.2.
  Verifikasi: test gagal dulu, lulus sesudahnya, seluruh test dijalankan.

- Siapa: Fathimah. Tugas: bug 2 `<>`. 
  Hasil:  membantu penyusunan kode, kode diperbaiki sendiri. 
  Alasan: sesuai SPESIFIKASI 2.5. 
  Verifikasi: test baru dan penelusuran `laporan_penjualan.sql` baris 6.

- Siapa: Fathimah. Tugas: T3 komentar blok. 
  Hasil: membantu penyusunan kode, kode diperbaiki sendiri. 
  Alasan: sesuai SPESIFIKASI 2.3. 
  Verifikasi: tiga test baru (lintas baris dan nomor baris, berisi `*`, tidak ditutup).

- Siapa: Fathimah. Tugas: bug 3 `''` di string. 
  Hasil: membantu penyusunan kode, kode diperbaiki sendiri. 
  Alasan: sesuai SPESIFIKASI 2.4. 
  Verifikasi: test gagal `2 == 1`, lalu lulus, dan kasus `''`, `''''`, `'abc`.

- Siapa: Fathimah. Tugas: T1 INSERT SELECT dan audit `parser.py` terhadap grammar. 
  Hasil: membantu penyusunan kode, kode diperbaiki sendiri untuk T1, presedensi AND/OR, `_synchronize`, dan `LEFT OUTER`. 
  Alasan: sesuai SPESIFIKASI 3, 3.1, dan 6. 
  Verifikasi: empat test regresi gagal dulu lalu lulus.

- Siapa: Fathimah. Tugas: lima test kasus tepi. 
  Hasil: diterima. 
  Alasan: melindungi perilaku berisiko (kutip ganda, pembagian vs komentar, BETWEEN AND, perbandingan tak berantai, satu error per statement). 
  Verifikasi: semua lulus saat dijalankan.

- Siapa: Fathimah. Tugas: label `ground_truth.csv` untuk `audit.sql`. 
  Hasil: menurunkan label dengan membaca SPESIFIKASI bagian 5 dan 8 (tidak menjalankan tool), diterima setelah dicek ulang sendiri statement demi statement. 
  Verifikasi:

- Siapa: Fathimah. Tugas: draf laporan bug, kartu desain 1-2, dan batas pendekatan. 
  Hasil:  
  Verifikasi: 

- Siapa: Salwa. Tugas: memahami panduan unutk mengerjakan.
  Hasil: diterima sebagai panduan.
  Alasan: butuh peta tugas agar tidak melenceng kemana-mana.

- Siapa: Salwa. Tugas: memverifikasi bug di resolver, analyzer, pipeline, dan cli dengan membandingkan kode dengan SPESIFIKASI.md.
  Hasil: diterima. AI berhsil memverifikasi bug yan ditemukan.
  Alasan: membandingkan kode dengan spek baris demi baris, dan test terlihat hanya menangkap sebagian masalah.
  Verifikasi: gejalanya dikonfirmasi sendiri lewat `--ast` baris 12 dan 18 pada `audit.sql`, FP/FN pada `evaluate.py`, nilai `RUD` (seharusnya `RD`) pada pytest.

- Siapa: Salwa. Tugas: membantu menyelesaikan kolom tanpa qualifier di `resolver.py`.
  Hasil: diterima.
  Alasan: aturannya jelas di spek 4.3 dan kolom ini perlu di-resolve ke tabel.
  Verifikasi: `test_kolom_tanpa_qualifier_satu_tabel` lulus dan seluruh `test_resolver.py` hijau.

- Siapa: Salwa. Tugas: verifikasi penambahan `self._pop()` di akhir `_delete` pada `resolver.py`.
  Hasil: diterima.
  Alasan: sesuai SPESIFIKASI.md 4.5 (scope tidak boleh bocor antar statement).
  Verifikasi: `python -m crud.cli data\sample\audit.sql` sekarang menampilkan `audit.sql: baris 18: error: alias 's' tidak terdefinisi` (sebelumnya tidak ada error). serta sebelumnya test gagal tanpa `_pop`.

- Siapa: Salwa. Tugas: apakah 2 pemanggilan `_collect` di cabang `Update` pada `analyzer.py` diubah dari `"U"` menjadi `"R"`.
  Hasil: diterima.
  Alasan: sesuai SPESIFIKASI.md bagian 5 (tabel yang dibaca lewat subquery selalu `R`).
  Verifikasi: `test_matrix_laporan_penjualan` lulus, `evaluate.py` menunjukkan parser 1.00 (sebelumnya 0.90 dengan FP/FN di baris 12).

- Siapa: Salwa. Tugas: `tests/test_tambahan.py`.
  Hasil: diterima.
  Alasan: syarat tugas, test regresi untuk setiap bug.
  Verifikasi: ketiganya lulus setelah perbaikan. 

- Siapa: Salwa. Tugas: memberi komentar di `tests/test_tambahan.py` (INSERT dengan kolom tanpa scope, subquery di FROM tidak melihat tabel saudara, UPDATE yang membaca tabel yang sama jadi `RU`).
  Hasil: diubah.
  Alasan: mencari kasus berisiko di luar bug yang sudah ditemukan.
  Verifikasi: hasil `python -m pytest -k tepi -v` (semua passed).

- Siapa: Salwa. Tugas: label manual `pemeliharaan.sql` untuk `data/ground_truth.csv`.
  Hasil: diterima.
  Alasan: belum paham cara menentukan peran tabel (target atau sumber baca) pada INSERT...SELECT dan subquery.
  Verifikasi: dibaca terhadap spek bagian 5, `evaluate.py` menunjukkan parser 1.00.

- Siapa: Salwa. Tugas: menganalisis daftar FP/FN regex pada `evaluate.py`.
  Hasil: diterima.
  Alasan: butuh bantuan menghubungkan setiap FP/FN dengan kode `regex_extractor.py`.
  Verifikasi: potongan SQL di laporan sudah disalin.

- Siapa: Salwa. Tugas: memeriksa apakah semua saran AI melanggar SPESIFIKASI.md atau aturan yang ada.
  Hasil: diterima.
  Alasan: ingin memastikan tidak ada pelanggaran sebelum mengumpulkan.
  Verifikasi: dibandingkan dengan aturan di deskripsi tugas dan menindaklanjuti dengan mencatat label di log ini.

- Siapa: Salwa. Tugas: menyelesaikan masalah lingkungan (konflik `git pull` karena file `.pyc`, `IndentationError` di `test_tambahan.py`).
  Hasil: diterima. 
  Alasan: sempat gagal/error.
  Verifikasi: perintah berhasil dan keluaran terminal sesuai harapan.

**Refleksi.** AI membantu membandingkan kode dengan SPESIFIKASI.md secara sistematis, memverifikasi lokasi bug, dan menghubungkan satu gejala di parser ke penyebabnya di lexer (`<>`). AI juga keliru di beberapa hal, misalnya sempat menyebut `test_tambahan.py` sudah punya fungsi helper padahal tidak. Kami mengetahuinya dengan menjalankan test, membaca pesan error di terminal, dan mencocokkan dengan spesifikasi tugas.