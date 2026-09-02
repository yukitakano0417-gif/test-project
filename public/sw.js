// 買い物メモ アプリ用の簡易サービスワーカー
// ホーム画面追加（PWAインストール）を可能にするための最小構成
const CACHE_NAME = 'shopping-memo-cache-v1'

// インストール時に即座に有効化する
self.addEventListener('install', (event) => {
  self.skipWaiting()
})

// 有効化時に古いキャッシュを削除する
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))),
    ),
  )
  self.clients.claim()
})

// ネットワーク優先、失敗時はキャッシュから返す（オフライン起動対応）
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const clone = response.clone()
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone))
        return response
      })
      .catch(() => caches.match(event.request)),
  )
})
