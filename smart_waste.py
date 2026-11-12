"""Smart Waste - sistem pakar pemilahan sampah rumah tangga (Forward Chaining).

Program membaca aturan IF-THEN dari kb_sampah.json, menanyakan fakta ke
pengguna, lalu menyimpulkan dengan forward chaining beserta alasannya.
"""
import json
import os
import sys

BERKAS_KB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kb_sampah.json")


def muat_kb(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def syarat_terpenuhi(aturan, memori):
    """mode 'dan': semua syarat ada di memori; mode 'atau': salah satu cukup."""
    ada = [p for p in aturan["jika"] if p in memori]
    if aturan["mode"] == "dan":
        return len(ada) == len(aturan["jika"])
    return len(ada) > 0


def tanya(nomor, fakta):
    while True:
        jawab = input(f"{nomor}. Apakah {fakta}? (y/t) > ").strip().lower()
        if jawab in ("y", "ya"):
            return True
        if jawab in ("t", "tidak"):
            return False
        print("   Jawab y atau t.")


def fakta_yang_ditanyakan(kb):
    """Fakta yang tidak pernah menjadi hasil aturan lain ditanyakan ke pengguna."""
    hasil_aturan = {r["maka"] for r in kb["aturan"]}
    daftar = []
    for r in kb["aturan"]:
        for p in r["jika"]:
            if p not in hasil_aturan and p not in daftar:
                daftar.append(p)
    return daftar


def forward_chaining(kb, memori):
    """Jalankan aturan sampai tidak ada yang baru.
    Kembalikan dict: kesimpulan -> aturan yang menghasilkannya."""
    asal = {}
    siklus = 0
    while True:
        siklus += 1
        cocok = [r for r in kb["aturan"]
                 if r["maka"] not in memori and syarat_terpenuhi(r, memori)]
        if not cocok:
            print(f"Siklus {siklus}: tidak ada aturan baru, berhenti")
            return asal
        r = cocok[0]                      # ambil aturan pertama
        memori.add(r["maka"])             # tambahkan hasil ke memori
        asal[r["maka"]] = r               # catat asalnya (bahan alasan)
        print(f"Siklus {siklus}: {r['id']} -> {r['maka']}")


def cetak_alasan(kesimpulan, asal, memori, tingkat=0):
    r = asal[kesimpulan]
    ada = [p for p in r["jika"] if p in memori]
    print("  " * (tingkat + 1) + f"{kesimpulan}  <- {r['id']} ({', '.join(ada)}) [{r['sumber']}]")
    for p in ada:
        if p in asal:
            cetak_alasan(p, asal, memori, tingkat + 1)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else BERKAS_KB
    kb = muat_kb(path)

    print(kb["judul"])
    print("Jawab y/t.")
    memori = set()
    fakta_ya = []
    for i, fakta in enumerate(fakta_yang_ditanyakan(kb), 1):
        if tanya(i, fakta):
            memori.add(fakta)
            fakta_ya.append(fakta)

    print()
    print("Fakta awal:", ", ".join(fakta_ya) if fakta_ya else "(tidak ada)")
    print()
    asal = forward_chaining(kb, memori)

    # kesimpulan akhir = hasil aturan yang tidak dipakai sebagai syarat aturan lain
    semua_syarat = {p for r in kb["aturan"] for p in r["jika"]}
    akhir = [k for k in asal if k not in semua_syarat]

    print()
    if akhir:
        print("Kesimpulan:", "; ".join(akhir))
        print("Alasan:")
        for k in akhir:
            cetak_alasan(k, asal, memori)
    else:
        print("Kesimpulan: belum ada kesimpulan akhir dari fakta yang diberikan.")
        if asal:
            print("Fakta turunan yang diperoleh:", ", ".join(asal))

    print()
    print("Catatan:", kb["batas"])


if __name__ == "__main__":
    main()