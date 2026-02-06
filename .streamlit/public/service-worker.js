self.addEventListener("install", event => {
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  clients.claim();
});

// Non intercetta le richieste Streamlit → nessun blocco WebSocket
self.addEventListener("fetch", event => {});
