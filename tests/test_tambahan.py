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