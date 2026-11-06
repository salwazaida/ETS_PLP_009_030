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

**Refleksi.** AI membantu menunjukkan lokasi bug dan menghubungkan satu gejala di parser ke penyebabnya di lexer (`<>`). 
AI sempat keliru menyebut `test_tambahan.py` sudah punya fungsi helper, padahal tidak, dan kami mengetahuinya karena test gagal lalu kami memeriksa isi file.
Semua hasil bantuan AI kami verifikasi dengan test dan tidak dipakai tanpa dijalankan.