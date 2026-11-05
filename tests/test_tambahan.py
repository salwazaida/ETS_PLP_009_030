"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""
import pytest

from crud.lexer import LexError, TokenType as T, tokenize


def test_regresi_keyword_tidak_peka_huruf():
    # Bug 1: keyword huruf kecil/campuran terbaca IDENT (SPESIFIKASI 2.2)
    for sumber in ["select", "Select", "SELECT"]:
        tok = tokenize(sumber)[0]
        assert tok.type == T.KEYWORD
        assert tok.value == "SELECT"      # nilai keyword selalu huruf besar


def test_regresi_ident_berawalan_keyword_tetap_ident():
    # Kata yang hanya DIAWALI keyword bukan keyword (SPESIFIKASI 2.2)
    toks = tokenize("selection fromage")
    assert toks[0].type == T.IDENT
    assert toks[1].type == T.IDENT

def test_regresi_operator_tidak_sama_satu_token():
    # Bug 2: '<>' terpecah menjadi '<' dan '>' (SPESIFIKASI 2.5, maximal munch)
    toks = [t for t in tokenize("a <> b") if t.type != T.EOF]
    assert [t.value for t in toks] == ["a", "<>", "b"]
    assert toks[1].type == T.OP    

def values(src):
    return [t.value for t in tokenize(src) if t.type != T.EOF]

def test_komentar_blok_lintas_baris_dan_nomor_baris():
    # Komentar lintas baris tidak menghasilkan token, dan baris/kolom sesudahnya benar
    toks = tokenize("/* a\n b */ SELECT")
    assert [t.type for t in toks] == [T.KEYWORD, T.EOF]
    assert (toks[0].line, toks[0].col) == (2, 7)


def test_komentar_blok_boleh_berisi_bintang():
    # '*' di dalam komentar tidak boleh menutup komentar sebelum '*/'
    assert values("/* a * b ** c */ x") == ["x"]


def test_komentar_blok_tidak_ditutup_adalah_lexerror():
    # Komentar yang tidak ditutup harus LexError (SPESIFIKASI 2.3)
    with pytest.raises(LexError):
        tokenize("SELECT /* tidak ditutup")    

def test_regresi_kutip_ganda_dalam_string():
    # Bug 3: '' di dalam string harus jadi satu karakter kutip (SPESIFIKASI 2.4)
    toks = [t for t in tokenize("'O''Brien'") if t.type != T.EOF]
    assert len(toks) == 1
    assert toks[0].type == T.STRING
    assert toks[0].value == "O'Brien"        