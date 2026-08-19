/* Service worker gry „Poranek Zuzi".

   Zasada: gra ma zawsze chodzić z najnowszej wersji, ale też działać bez
   internetu.

   • index.html, manifest i sam sw.js  -> NAJPIERW SIEĆ (cache to tylko zapas
     na offline), więc po wejściu zawsze widać świeżą wersję gry;
   • dźwięki i obrazki (mp3, png)      -> NAJPIERW CACHE, a w tle po cichu
     pobiera się nowsza wersja pliku, żeby start był natychmiastowy;
   • nowy worker nie czeka w kolejce (skipWaiting + clients.claim), a strona
     sama się przeładuje, kiedy przejmie ją nowa wersja.                     */

const WERSJA = '2026-08-19-zuzia-1';
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
  e.respondWith(najpierwCache(zad));
});
