/* 收藏檔案 Service Worker — 離線可用 */
var CACHE = "momo-coll-v4";
var SHELL = [
  "./",
  "index.html",
  "admin.html",
  "manifest.webmanifest",
  "manifest-admin.webmanifest",
  "data/public.json",
  "data/schema.json",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/apple-touch-icon.png"
];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(CACHE).then(function (c) {
      return Promise.all(
        SHELL.map(function (u) {
          return c.add(u).catch(function () { /* 單一檔案失敗唔好拖死成個 install */ });
        })
      );
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (ks) {
      return Promise.all(ks.map(function (k) {
        if (k !== CACHE) return caches.delete(k);
      }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  if (url.origin !== location.origin) return;

  /* 資料檔：先網絡，失敗才用 cache（確保見到最新） */
  if (url.pathname.indexOf("/data/") >= 0) {
    e.respondWith(
      fetch(req).then(function (r) {
        var cp = r.clone();
        caches.open(CACHE).then(function (c) { c.put(req, cp); });
        return r;
      }).catch(function () {
        return caches.match(req).then(function (m) {
          return m || new Response('{"meta":{},"items":[]}',
            { headers: { "Content-Type": "application/json" } });
        });
      })
    );
    return;
  }

  /* HTML：先網絡（確保更新即刻見到），失敗才用 cache */
  if (url.pathname.endsWith(".html") || url.pathname.endsWith("/")) {
    e.respondWith(
      fetch(req).then(function (r) {
        var cp = r.clone();
        caches.open(CACHE).then(function (c) { c.put(req, cp); });
        return r;
      }).catch(function () {
        return caches.match(req).then(function (m) {
          return m || caches.match("index.html");
        });
      })
    );
    return;
  }

  /* 其他：先 cache，後網絡（相片／icon） */
  e.respondWith(
    caches.match(req).then(function (m) {
      if (m) return m;
      return fetch(req).then(function (r) {
        if (r && r.status === 200 && r.type === "basic") {
          var cp = r.clone();
          caches.open(CACHE).then(function (c) { c.put(req, cp); });
        }
        return r;
      });
    }).catch(function () {
      return caches.match("index.html");
    })
  );
});
