# Poranek Zuzi 🐶

Ośmiobitowa gra 2D dla dzieci. Zuzia wstaje, ogarnia cały poranek w domu
i zdąża do szkoły — a wszystko trzeba zrobić **cichutko**, bo tata śpi po
wczorajszej imprezie w Teatrze Leśnym. **Sterowanie: same strzałki.**

▶ **Zagraj: https://qunabu.github.io/gra-zuzia/**

Zuzia dostaje wszystko **przeczytane na głos** — narrator po polsku zapowiada
każdy poziom i każde zadanie, więc do grania nie trzeba umieć czytać.

## Sterowanie

| Klawisz | Co robi |
|---|---|
| ◀ ▶ | chodzenie (w minigrach: kręcenie, mop, skradanie) |
| ▲ | skok, a także „zacznij / dalej” |
| **P** / **O** | **DEBUG**: następny / poprzedni etap (do podglądania planszy) |

Na telefonie i tablecie pojawiają się przyciski dotykowe. W etapach, w których
naciska się ◀ i ▶ na zmianę (wstawanie, kredki, podłoga), **◀ ląduje przy lewej
krawędzi, a ▶ przy prawej** — telefon trzyma się wtedy jak pada i gra się
**dwoma kciukami**. ▲ siedzi na środku pod spodem. W platformówce jest po
staremu: chodzenie pod lewym kciukiem, skok pod prawym. Telefon trzymany
pionowo prosi o obrócenie na poziomo.

Przedmioty zbiera się samym dotknięciem. Świecąca rzecz ze strzałką to ta,
po którą trzeba iść teraz. **Nie da się przegrać** — po spadnięciu Zuzia
wraca w bezpieczne miejsce, a nawet obudzenie taty kończy się tylko cofnięciem
o kawałek.

## Poziomy (8)

1. **Wstawaj, Zuziu!** — wstać wcale nie jest łatwo. Naprzemienne ◀ ▶ podnoszą
   pasek „wstawanie”, a sen ciągnie z powrotem; co chwilę przychodzi **atak snu**
   (ekran ciemnieje, lecą Z-tki) i pasek spada szybciej. Zamiast wołania z drzwi
   dzwoni budzik na szafce — cicho, bo tata śpi. Po 20 sekundach sen odpuszcza,
   więc nawet powolne stukanie w końcu wystarczy
2. **Nakarm Jogiego** — schody na dół, potem miska → karma → **Jogi**. Pies
   wyjada całą miskę i dziękuje ogonkiem
3. **Kredki do temperowania** — pięć kredek stoi w kubku „DO ZROBIENIA”.
   Naprzemienne ◀ ▶ kręcą kredką w temperówce, z wylotu lecą wiórki, a czubek
   robi się coraz dłuższy i ostrzejszy. Gotowa kredka wskakuje do kubka „GOTOWE”
4. **Umyj podłogę** — mop jeździ za ◀ ▶, a dziewięć plam schodzi **od ruchu**:
   samo stanie nad plamą nic nie daje, trzeba szorować tam i z powrotem.
   Pasek u góry pokazuje czystość
5. **Wyrzuć śmieci** — worek → skórka od banana → zgnieciony papier → butelka,
   a na końcu wielki kosz z uchyloną klapą
6. **Podlej kwiatki** — konewka i trzy spragnione kwiatki na półkach.
   Przy ostatnim leci ekran „PODLANE!” z kroplami wody
7. **Nie obudź taty!** — tata śpi na kanapie po wczorajszej imprezie
   w **Teatrze Leśnym** (na ścianie wisi plakat, na podłodze zgubiony bilet,
   a wokół balony, kubki i konfetti). Kiedy **chrapie** (zielony dymek „CHRRR… IDŹ!”) można iść.
   Kiedy przestaje i się wierci (czerwone „CICHO! STÓJ!”) trzeba stanąć jak
   myszka, bo rośnie **hałas**. Przy pełnym hałasie tata tylko mruczy, a Zuzia
   cofa się kawałek — obudzić go się nie da
8. **Do szkoły!** — bluza → spodnie → buty → plecak i biegiem do drzwi

Zuzia **ubiera się na oczach gracza** — każda zebrana rzecz pojawia się na
postaci, razem z plecakiem na plecach.

## Jak to zrobione

- Wszystko renderowane na kanwie **480×270 px**, skalowanej bez wygładzania —
  stąd wygląd 8-bitowy. Własna czcionka bitmapowa 5×7 z polskimi znakami.
- Twarz Zuzi i taty to **prawdziwe zdjęcia przerobione na piksele**
  (macOS Vision wycina sylwetkę, potem redukcja do 24×24 i 40×40 pikseli).
- Postać ma 4-klatkowy cykl chodu i osobną klatkę skoku.
- **Narrator i efekty wygenerowane przez ElevenLabs** (`audio/*.mp3`).
  Gdyby plików zabrakło, gra sama piszczy przez WebAudio.

Gra wyrosła z [gra-franek](https://github.com/qunabu/franek-poranek) — silnik,
czcionka i platformówka są stamtąd, poziomy i trzy minigry (kredki, podłoga,
skradanie) są nowe.

## Instalacja na pulpicie (PWA)

Gra jest aplikacją PWA, więc da się ją **zainstalować jak zwykły program**
i uruchamiać na pełnym ekranie, bez paska adresu.

Najprościej: na ekranie tytułowym (a na telefonie trzymanym pionowo — pod
prośbą o obrót) jest przycisk **📲 ZAINSTALUJ GRĘ**. Na Androidzie i na
komputerze otwiera prawdziwe okienko instalacji, a na iPhonie tłumaczy krok po
kroku, gdzie kliknąć. Przycisk chowa się na czas gry, żeby nie zasłaniał planszy.

Ręcznie, gdyby ktoś wolał:

- **Komputer (Chrome / Edge):** ikona instalacji po prawej w pasku adresu
  (albo menu ⋮ → *Zainstaluj*).
- **Android (Chrome):** menu ⋮ → *Zainstaluj aplikację* / *Dodaj do ekranu głównego*.
- **iPhone / iPad (Safari):** przycisk *Udostępnij* → *Do ekranu początkowego*.
  Safari **nigdy** nie proponuje instalacji sam — na iPhonie zawsze robi się to ręcznie.

Po instalacji gra:

- startuje **na pełnym ekranie i w poziomie** (`display: fullscreen`,
  `orientation: landscape`),
- **zawsze pokazuje najnowszą wersję** — `sw.js` bierze `index.html` najpierw
  z sieci, a gdy w tle pojawi się nowa wersja, okno samo się przeładowuje,
- **działa bez internetu** — ikony, twarze i strona są zapisane od razu,
  a dźwięki dogrywają się do zapasu przy pierwszym graniu.

Ikony na pulpit robi `tools/gen_ikony.py` z pikselowego portretu Zuzi
(czysty Python, bez bibliotek).

## Uruchomienie lokalnie

Otwórz `index.html` w przeglądarce (dwuklik). Wymaga tylko plików z tego repo.
Service worker działa jednak dopiero po `http://`, więc żeby sprawdzić PWA,
odpal `python3 -m http.server` w katalogu gry.

## Skrypty pomocnicze

```bash
# twarz Zuzi ze zdjęcia: wycięcie tła (Vision) + pikselizacja
swiftc -O tools/cutout.swift   -o /tmp/cutout
swiftc -O tools/pixelize.swift -o /tmp/pixelize
/tmp/cutout   zdjecia/zuzia.jpeg zdjecia/zuzia_wyciete.png 55 150 920 960
/tmp/pixelize zdjecia/zuzia_wyciete.png glowa_zuzia.png   30 100 860 850 24 24 surowe 1.05 1.2 0 kontur
/tmp/pixelize zdjecia/zuzia_wyciete.png portret_zuzia.png 10  25 900 920 40 40 surowe 1.02 1.2 0 kontur

# tak samo tata
/tmp/cutout   zdjecia/tata.jpeg zdjecia/tata_wyciete.png 130 20 540 700
/tmp/pixelize zdjecia/tata_wyciete.png glowa_tata.png   20 10 500 640 20 24 surowe 1.02 1.2 0 kontur
/tmp/pixelize zdjecia/tata_wyciete.png portret_tata.png 10  5 520 660 34 41 surowe 1.0  1.2 0 kontur

python3 tools/gen_ikony.py     # ikony PWA z portret_zuzia.png
python3 tools/gen_audio.py     # narrator i efekty (potrzebny klucz ElevenLabs w .env)
```

`tools/gen_audio.py` pomija pliki, które już są, więc można go odpalać
wielokrotnie — dolatuje tylko to, czego brakuje. Klucz trzyma się w `.env`
(`ELEVEN_LABS_API_KEY=...`), którego **nie ma w repozytorium**.

## Podglądanie etapów (debug)

Żeby nie przechodzić całej gry za każdą zmianą, wystarczy nacisnąć **P** —
gra przeskakuje do następnego etapu, a **O** wraca do poprzedniego (na końcu
zawija się na początek). Na ekranie tytułowym **P** od razu zaczyna grę.
W prawym dolnym narożniku na chwilę pokazuje się `DEBUG ETAP 3/8`.
