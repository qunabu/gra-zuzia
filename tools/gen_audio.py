#!/usr/bin/env python3
"""Generuje narratora i efekty „Poranka Zuzi" przez ElevenLabs do katalogu audio/.

Pliki, które już są i mają sensowny rozmiar, są pomijane – więc skrypt można
odpalać wielokrotnie, a doleci tylko to, czego brakuje.
Klucz API bierze z .env obok tego repo (ELEVEN_LABS_API_KEY=...).
"""
import json, os, subprocess, sys, time

KAT_GRY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KLUCZ = None
for sciezka in (os.path.join(KAT_GRY, '.env'),
                os.path.expanduser('~/Desktop/localhost/gra-franek/.env')):
    if not os.path.exists(sciezka):
        continue
    for linia in open(sciezka):
        if linia.startswith('ELEVEN_LABS_API_KEY='):
            KLUCZ = linia.split('=', 1)[1].strip()
    if KLUCZ:
        break
assert KLUCZ, 'brak klucza ELEVEN_LABS_API_KEY w .env'

KAT = os.path.join(KAT_GRY, 'audio')
os.makedirs(KAT, exist_ok=True)

GLOS = os.environ.get('GLOS', 'FGY2WhTYpPnrIDTdsKH5')   # Laura
MODEL = 'eleven_multilingual_v2'

def poslij(url, dane, plik, proby=3):
    """Wysyła przez curl – Pythonowy urllib nie ma tu certyfikatów SSL."""
    sciezka = os.path.join(KAT, plik)
    if os.path.exists(sciezka) and os.path.getsize(sciezka) > 2000:
        return 'pominięto (jest)'
    for p in range(proby):
        wynik = subprocess.run(
            ['curl', '-s', '-o', sciezka, '-w', '%{http_code}', '--max-time', '300',
             '-X', 'POST', url,
             '-H', 'xi-api-key: ' + KLUCZ,
             '-H', 'Content-Type: application/json',
             '-d', json.dumps(dane)],
            capture_output=True, text=True)
        kod = wynik.stdout.strip()
        rozmiar = os.path.getsize(sciezka) if os.path.exists(sciezka) else 0
        if kod == '200' and rozmiar > 1000:
            return 'OK %.0f KB' % (rozmiar / 1024)
        tresc = ''
        if os.path.exists(sciezka):
            tresc = open(sciezka, 'rb').read()[:200].decode('utf-8', 'replace')
            os.remove(sciezka)
        if p == proby - 1:
            return 'BLAD HTTP %s %s' % (kod, tresc)
        time.sleep(3 * (p + 1))

def mowa(plik, tekst):
    return poslij('https://api.elevenlabs.io/v1/text-to-speech/' + GLOS,
                  {'text': tekst, 'model_id': MODEL,
                   'voice_settings': {'stability': 0.45, 'similarity_boost': 0.75,
                                      'style': 0.35, 'use_speaker_boost': True}},
                  plik)

def efekt(plik, opis, sek):
    return poslij('https://api.elevenlabs.io/v1/sound-generation',
                  {'text': opis, 'duration_seconds': sek, 'prompt_influence': 0.75}, plik)

NARRACJA = {
    'z_start':   'Poranek Zuzi! Naciśnij strzałkę w górę, żeby zacząć.',
    'z_koniec':  'Brawo Zuziu! Wszystko zrobione i zdążyłaś do szkoły!',

    'z_poziom1': 'Poziom pierwszy. Wstawaj Zuziu! Wygrzeb się z łóżka, tylko cichutko.',
    'z_poziom2': 'Poziom drugi. Nakarm Jogiego! Piesek czeka na śniadanie.',
    'z_poziom3': 'Poziom trzeci. Natemperuj wszystkie kredki!',
    'z_poziom4': 'Poziom czwarty. Umyj podłogę mopem!',
    'z_poziom5': 'Poziom piąty. Pozbieraj śmieci i wyrzuć je do kosza!',
    'z_poziom6': 'Poziom szósty. Podlej kwiatki, bo są bardzo spragnione!',
    'z_poziom7': 'Poziom siódmy. Ciiii! Tata śpi, bo wczoraj był na imprezie '
                 'w Teatrze Leśnym. Nie obudź go!',
    'z_poziom8': 'Ostatni poziom! Ubierz się, weź plecak i leć do szkoły!',

    'z_wstawanie_jak': 'Naciskaj w lewo i w prawo na zmianę, żeby wstać z łóżka. '
                       'Tylko cichutko, bo tata jeszcze śpi!',
    'z_wstawanie_ok':  'Wstałaś! Brawo Zuziu! Jogi już czeka na śniadanie.',

    'zad_karma_pies': 'Znajdź karmę dla Jogiego!',
    'zad_jogi':       'Nakarm Jogiego!',
    'jogi_je':        'Mniam mniam! Jogi zjadł całą miskę i macha ogonem. Dziękuje ci!',

    'kredki_jak':    'Kręć kredką w lewo i w prawo, żeby ją zatemperować!',
    'kredka_gotowa': 'Ostra jak igiełka! Bierzemy następną kredkę.',
    'kredki_ok':     'Wszystkie kredki zatemperowane! Brawo Zuziu!',

    'podloga_jak':   'Jeźdź mopem w lewo i w prawo, żeby zmyć wszystkie plamy z podłogi!',
    'podloga_ok':    'Podłoga aż lśni! Brawo Zuziu!',

    'zad_worek':   'Weź worek na śmieci!',
    'zad_smieci':  'Podnieś śmieć i wrzuć go do worka!',
    'zad_kosz':    'Wyrzuć śmieci do kosza!',

    'zad_konewka': 'Znajdź konewkę z wodą!',
    'zad_kwiatek': 'Podlej kwiatka!',
    'kwiatki_ok':  'Wszystkie kwiatki napite i szczęśliwe! Brawo!',

    'cicho_jak':  'Tata śpi na kanapie po wczorajszej imprezie w Teatrze Leśnym. '
                  'Idź do przodu tylko wtedy, kiedy chrapie. Gdy przestanie, '
                  'stój cichutko jak myszka!',
    'cicho_stop': 'Stój! Tata się rusza!',
    'cicho_ups':  'Ups! Prawie się obudził. Cofnij się i spróbuj jeszcze raz.',
    'cicho_ok':   'Udało się! Tata śpi dalej. Lecimy do szkoły!',

    'zad_plecak': 'Weź plecak!',
    'zad_szkola': 'Leć do szkoły!',
}

EFEKTY = {
    'sfx_hau': ('8-bit chiptune dog bark sound effect, retro NES video game, '
                'two short square wave barks, playful', 0.8),
}

def main():
    wynik = {}
    print('=== NARRATOR (glos %s) ===' % GLOS, flush=True)
    for k, t in NARRACJA.items():
        wynik[k] = mowa(k + '.mp3', t)
        print('%-18s %s' % (k, wynik[k]), flush=True)
    print('=== EFEKTY ===', flush=True)
    for k, (opis, sek) in EFEKTY.items():
        wynik[k] = efekt(k + '.mp3', opis, sek)
        print('%-18s %s' % (k, wynik[k]), flush=True)

    bledy = {k: v for k, v in wynik.items() if v and v.startswith('BLAD')}
    json.dump({'narracja': NARRACJA, 'wynik': wynik},
              open(os.path.join(KAT, 'manifest.json'), 'w'), ensure_ascii=False, indent=1)
    print('\nGOTOWE. plikow: %d, bledow: %d' % (len(wynik), len(bledy)), flush=True)
    if bledy:
        print('BLEDY:', json.dumps(bledy, ensure_ascii=False, indent=1), flush=True)

main()
