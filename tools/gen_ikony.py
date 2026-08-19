#!/usr/bin/env python3
"""Robi ikony PWA z pikselowego portretu Zuzi – bez żadnych bibliotek.

Powiększanie jest „schodkowe" (nearest neighbour), żeby ikona na pulpicie
wyglądała tak samo ośmiobitowo jak gra.
"""
import struct, zlib, os

KAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

def wczytaj_png(sciezka):
    d = open(sciezka, 'rb').read()
    assert d[:8] == b'\x89PNG\r\n\x1a\n', 'to nie PNG'
    i, dane, ihdr = 8, b'', None
    while i < len(d):
        dl = struct.unpack('>I', d[i:i+4])[0]
        typ = d[i+4:i+8]
        if typ == b'IHDR': ihdr = struct.unpack('>IIBBBBB', d[i+8:i+21])
        elif typ == b'IDAT': dane += d[i+8:i+8+dl]
        i += 12 + dl
    w, h, bd, ct, _, _, il = ihdr
    assert bd == 8 and il == 0 and ct in (2, 6), 'obsługuję tylko 8-bit RGB/RGBA bez przeplotu'
    kan = 4 if ct == 6 else 3
    sur = zlib.decompress(dane)
    piks, poprz, poz = [], bytearray(w*kan), 0
    for _ in range(h):
        filtr = sur[poz]; poz += 1
        wiersz = bytearray(sur[poz:poz+w*kan]); poz += w*kan
        for x in range(w*kan):
            a = wiersz[x-kan] if x >= kan else 0
            b = poprz[x]
            c = poprz[x-kan] if x >= kan else 0
            if   filtr == 1: wiersz[x] = (wiersz[x] + a) & 255
            elif filtr == 2: wiersz[x] = (wiersz[x] + b) & 255
            elif filtr == 3: wiersz[x] = (wiersz[x] + (a+b)//2) & 255
            elif filtr == 4:
                p = a + b - c
                pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                wiersz[x] = (wiersz[x] + pred) & 255
        poprz = wiersz
        piks.append([tuple(wiersz[x*kan:x*kan+kan]) + ((255,) if kan == 3 else ())
                     for x in range(w)])
    return w, h, piks

def zapisz_png(sciezka, w, h, piks):
    sur = b''.join(b'\x00' + bytes(v for p in wiersz for v in p[:3]) for wiersz in piks)
    def chunk(typ, dane):
        return struct.pack('>I', len(dane)) + typ + dane + \
               struct.pack('>I', zlib.crc32(typ + dane) & 0xffffffff)
    d = b'\x89PNG\r\n\x1a\n'
    d += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    d += chunk(b'IDAT', zlib.compress(sur, 9))
    d += chunk(b'IEND', b'')
    open(sciezka, 'wb').write(d)

def kolor(hx):
    return (int(hx[1:3],16), int(hx[3:5],16), int(hx[5:7],16))

NIEBO, ZIEMIA, TRAWA, GWIAZDA = kolor('#0000bc'), kolor('#007800'), kolor('#58d854'), kolor('#fffeff')

def ikona(rozmiar, plik, skala_tresci=1.0):
    pw, ph, pp = wczytaj_png(os.path.join(KAT, 'portret_zuzia.png'))
    ziemia = int(rozmiar * 0.80)
    plotno = [[NIEBO if y < ziemia else ZIEMIA for _ in range(rozmiar)] for y in range(rozmiar)]
    for x in range(rozmiar):                       # pas jasnej trawy
        for y in range(ziemia, min(ziemia + max(2, rozmiar//64), rozmiar)):
            plotno[y][x] = TRAWA
    for i in range(26):                            # gwiazdki na niebie
        x, y = (i*97) % rozmiar, (i*53) % (ziemia - rozmiar//6)
        for dx in range(max(1, rozmiar//110)):
            for dy in range(max(1, rozmiar//110)):
                plotno[y+dy][x+dx] = GWIAZDA

    s = max(1, int(rozmiar * 0.92 * skala_tresci / ph))       # całkowite powiększenie
    ox = (rozmiar - pw*s) // 2
    oy = ziemia + max(2, rozmiar//64) - ph*s                  # portret stoi na ziemi
    for y in range(ph):
        for x in range(pw):
            r, g, b, a = pp[y][x]
            if a < 128: continue
            for dy in range(s):
                for dx in range(s):
                    px, py = ox + x*s + dx, oy + y*s + dy
                    if 0 <= px < rozmiar and 0 <= py < rozmiar:
                        plotno[py][px] = (r, g, b)
    zapisz_png(os.path.join(KAT, plik), rozmiar, rozmiar, plotno)
    print('%-26s %dx%d (powiększenie x%d)' % (plik, rozmiar, rozmiar, s))

ikona(512, 'ikona-512.png')
ikona(192, 'ikona-192.png')
ikona(180, 'apple-touch-icon.png')
ikona(512, 'ikona-maskowalna-512.png', 0.72)      # zapas na obcinanie rogów
