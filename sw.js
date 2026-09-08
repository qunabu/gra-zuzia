/* Service worker gry „Poranek Zuzi".

   Zasada: gra ma zawsze chodzić z najnowszej wersji, ale też działać bez
   internetu.

   • index.html, manifest i sam sw.js  -> NAJPIERW SIEĆ (cache to tylko zapas
     na offline), więc po wejściu zawsze widać świeżą wersję gry;
   • obrazki (png)                    -> NAJPIERW CACHE, a w tle po cichu
     pobiera się nowsza wersja pliku, żeby start był natychmiastowy;
   • dźwięki (mp3)                    -> TYLKO CACHE (patrz komentarz przy
     funkcji `dzwiek` – Safari i odświeżanie w tle zacinały grę);
   • nowy worker nie czeka w kolejce (skipWaiting + clients.claim), a strona
     sama się przeładuje, kiedy przejmie ją nowa wersja.                     */

const WERSJA = '2026-09-08-iOS-plynnosc';
const CACHE  = 'zuzia-' + WERSJA;

/* to, co musi być dostępne offline od pierwszego uruchomienia */
const SZKIELET = [
  './',
  './index.html',
  './manifest.webmanifest',
  './ikona-192.png',
  './ikona-512.png',
  './ikona-maskowalna-512.png',
  './apple-touch-icon.png',
  './glowa_zuzia.png', './portret_zuzia.png',
  './glowa_tata.png', './portret_tata.png'
];

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    // pojedynczy brakujący plik nie może wywrócić instalacji
    await Promise.all(SZKIELET.map(u => c.add(new Request(u, {cache:'reload'})).catch(()=>{})));
    self.skipWaiting();
  })());
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const nazwy = await caches.keys();
    await Promise.all(nazwy.filter(n => n !== CACHE).map(n => caches.delete(n)));
    if(self.registration.navigationPreload) await self.registration.navigationPreload.enable();
    await self.clients.claim();
  })());
});

// ręczne „sprawdź aktualizacje" ze strony
self.addEventListener('message', e => { if(e.data === 'sprawdz-wersje') self.skipWaiting(); });

/* do cache trafiają tylko pełne odpowiedzi 200 – kawałki plików (206, tak
   przeglądarka pobiera mp3) w Cache API nie wolno zapisywać */
function schowaj(c, zad, odp){
  if(odp && odp.status === 200 && odp.type !== 'opaque') c.put(zad, odp.clone()).catch(()=>{});
}
function najpierwSiec(zad, wstepne){
  return (async () => {
    const c = await caches.open(CACHE);
    try{
      const odp = await (wstepne || fetch(zad, {cache:'no-store'}));
      schowaj(c, zad, odp);
      return odp;
    }catch(err){
      const zapas = await c.match(zad) || await c.match('./index.html');
      if(zapas) return zapas;
      throw err;
    }
  })();
}

function najpierwCache(zad){
  return (async () => {
    const c = await caches.open(CACHE);
    const z = await c.match(zad);
    const swiezy = fetch(zad).then(odp => {
      schowaj(c, zad, odp);                            // po cichu odświeża zapas
      return odp;
    }).catch(() => null);
    return z || (await swiezy) || Response.error();
  })();
}

/* Dźwięki (mp3) mają własną ścieżkę i to z dwóch powodów:

   1. Safari pobiera media kawałkami (nagłówek Range), więc dostawaliśmy 206,
      a 206 do Cache API wrzucić nie wolno – w efekcie na iPhonie mp3 NIGDY nie
      trafiały do cache i każde odtworzenie szło do sieci. Dlatego przy chybieniu
      pobieramy plik osobnym, pełnym żądaniem (bez Range) i to jego zapisujemy.
   2. Nie ma tu odświeżania w tle: przy stukaniu ◀ ▶ gra prosiła o ten sam
      dźwięk kilka razy na sekundę, a każde żądanie ciągnęło za sobą strzał do
      sieci i zapis na dysk. O świeżość plików dba WERSJA cache'u – przy
      aktywacji nowego workera stary cache i tak leci do kosza. */
function dzwiek(zad){
  return (async () => {
    const c = await caches.open(CACHE);
    const z = await c.match(zad, {ignoreVary:true});
    if(z) return z;
    // pełne żądanie: bez Range, więc odpowiedź ma 200 i wolno ją schować
    const pelne = new Request(zad.url, {cache:'no-store'});
    try{
      const odp = await fetch(pelne);
      if(odp && odp.status === 200 && odp.type !== 'opaque')
        c.put(pelne, odp.clone()).catch(()=>{});
      return odp;                    // <audio> radzi sobie z 200 zamiast 206
    }catch(err){
      return Response.error();
    }
  })();
}

self.addEventListener('fetch', e => {
  const zad = e.request;
  if(zad.method !== 'GET') return;
  const url = new URL(zad.url);
  if(url.origin !== location.origin) return;

  if(zad.mode === 'navigate'){
    e.respondWith(najpierwSiec(zad, e.preloadResponse ? e.preloadResponse.then(r => r || fetch(zad, {cache:'no-store'})) : null));
    return;
  }
  if(/\.(html|webmanifest|json)$/.test(url.pathname)){
    e.respondWith(najpierwSiec(zad));
    return;
  }
  if(/\.mp3$/.test(url.pathname)){
    e.respondWith(dzwiek(zad));
    return;
  }
  e.respondWith(najpierwCache(zad));
});
