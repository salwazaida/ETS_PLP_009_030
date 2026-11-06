"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""
import pytest

from crud.lexer import LexError, TokenType as T, tokenize
from crud.parser import parse_sql
from crud import ast_nodes as ast
from crud.analyzer import analyze_statement
from crud.resolver import Resolver


def resolve(sql):
    script = parse_sql(sql)
    assert script.errors == [], script.errors
    resolver = Resolver()
    return script, resolver.resolve_script(script), resolver


def kolom(node):
    return [n for n in ast.iter_nodes(node) if isinstance(n, ast.ColumnRef)]


def test_regresi_kolom_tanpa_qualifier_dua_tabel_ambigu():
    script, diags, _ = resolve("SELECT id FROM a, b")
    assert kolom(script)[0].resolved is None
    assert [d.level for d in diags] == ["warning"] and "ambigu" in diags[0].message

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

def test_regresi_insert_select_menghasilkan_query():
    # T1: INSERT ... SELECT harus di-parse dan menyimpan SELECT-nya (SPESIFIKASI 3 dan 5)
    s = parse_sql("INSERT INTO arsip (id) SELECT id FROM pesanan").statements[0]
    assert s.query is not None and s.values == []


def test_regresi_presedensi_or_lebih_rendah_dari_and():
    # Bug 4: a = 1 OR (b = 2 AND c = 3), bukan (a = 1 OR b = 2) AND c = 3 (SPESIFIKASI 3.1)
    s = parse_sql("SELECT a FROM t WHERE a = 1 OR b = 2 AND c = 3").statements[0]
    assert s.where.op == "OR" and s.where.right.op == "AND"


def test_regresi_error_recovery_sampai_titik_koma():
    # Bug 5: statement valid sesudah error tetap diproses (SPESIFIKASI 6)
    sc = parse_sql("SELECT FROM x; SELECT a FROM t; UPDATE FROM; DELETE FROM u")
    assert len(sc.errors) == 2 and len(sc.statements) == 2


def test_regresi_left_outer_join():
    # Bug 6: LEFT OUTER JOIN harus diterima (SPESIFIKASI 3, aturan join)
    sc = parse_sql("SELECT a FROM t LEFT OUTER JOIN u ON t.id = u.id")
    assert sc.errors == []    


def test_tepi_string_kosong_dan_hanya_kutip():
    # '' adalah string kosong, '''' adalah satu karakter kutip: pembeda penutup vs kutip ganda
    assert values("''") == [""]
    assert values("''''") == ["'"]


def test_tepi_pembagian_bukan_komentar():
    # '/' tunggal harus tetap operator, bukan awal komentar blok
    assert values("a / b") == ["a", "/", "b"]


def test_tepi_between_and_milik_between():
    # AND pertama milik BETWEEN, AND kedua operator logika (SPESIFIKASI 3.2)
    s = parse_sql("SELECT a FROM t WHERE x BETWEEN 1 AND 2 AND y = 3").statements[0]
    assert s.where.op == "AND"
    assert type(s.where.left).__name__ == "Between"


def test_tepi_perbandingan_tidak_berantai():
    # a = b = c bukan ekspresi sah (SPESIFIKASI 3.1, tingkat 4 tidak berantai)
    sc = parse_sql("SELECT a FROM t WHERE a = b = c")
    assert len(sc.errors) == 1 and sc.statements == []


def test_tepi_satu_error_per_statement_rusak():
    # statement rusak menghasilkan tepat satu error, statement valid sesudahnya tetap diproses
    sc = parse_sql("SELECT a b c FROM t; SELECT 1 FROM x")
    assert len(sc.errors) == 1 and len(sc.statements) == 1   

def test_regresi_shadowing_alias_subquery_menutupi_alias_luar():
    script, diags, _ = resolve(
        "SELECT x.id FROM pelanggan x "
        "WHERE x.id IN (SELECT x.pelanggan_id FROM pesanan x WHERE x.total > 5)")
    dalam = [c for c in kolom(script) if c.name in ("pelanggan_id", "total")]
    assert {c.resolved for c in dalam} == {"pesanan"}
    assert {c.resolved for c in kolom(script) if c.name == "id"} == {"pelanggan"}
    assert diags == []

def test_regresi_scope_delete_tidak_bocor_ke_statement_berikutnya():
    script, diags, resolver = resolve(
        "DELETE FROM sesi s WHERE s.id = 1; SELECT s.id FROM pengguna u")
    assert resolver.scope is None
    assert [d.level for d in diags] == ["error"] and "'s'" in diags[0].message

def test_regresi_subquery_di_update_adalah_read():
    script = parse_sql("UPDATE a SET x = (SELECT MAX(y) FROM b) "
                       "WHERE id IN (SELECT id FROM c)")
    assert analyze_statement(script.statements[0]) == {"a": {"U"}, "b": {"R"}, "c": {"R"}}

def test_tepi_insert_values_dengan_kolom_tanpa_scope_tidak_crash():
    # INSERT tidak membuat scope, jadi self.scope == None. T2 yang langsung
    # memakai self.scope.entries akan melempar AttributeError.
    script, diags, _ = resolve("INSERT INTO t (a) VALUES (b)")
    assert kolom(script)[0].resolved is None
    assert [d.level for d in diags] == ["warning"]


def test_tepi_subquery_di_from_tidak_melihat_tabel_saudara():
    _, diags, _ = resolve("SELECT p.id FROM pelanggan p, (SELECT p.id FROM pesanan o) d")
    assert [d.level for d in diags] == ["error"] and "'p'" in diags[0].message


def test_tepi_update_membaca_tabel_yang_sama_gabungan_ru():
    script = parse_sql("UPDATE a SET x = 1 WHERE id IN (SELECT id FROM a)")
    assert analyze_statement(script.statements[0]) == {"a": {"U", "R"}}