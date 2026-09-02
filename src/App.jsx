import { useEffect, useRef, useState } from 'react'

// localStorage に保存するときのキー
const STORAGE_KEY = 'shopping-memo-items'
// 長押しと判定するまでの時間(ミリ秒)
const LONG_PRESS_MS = 600

// 今日の日付を YYYY-MM-DD 形式で取得する（input[type=date] の value 用）
function todayStr() {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

// YYYY-MM-DD を YYYY/MM/DD 表示に変換する
function formatDateSlash(dateStr) {
  if (!dateStr) return ''
  return dateStr.replaceAll('-', '/')
}

// 金額を「¥1,234」のようなカンマ区切りの円表示に変換する
function formatYen(amount) {
  return `¥${amount.toLocaleString('ja-JP')}`
}

// 金額入力文字列から数字だけを取り出して数値化する（未入力は0扱い）
function parsePrice(value) {
  const digits = value.replace(/[^0-9]/g, '')
  return digits === '' ? 0 : parseInt(digits, 10)
}

// localStorage から初期データを読み込む
function loadItems() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

export default function App() {
  const [items, setItems] = useState(loadItems)

  // 追加フォームの入力state
  const [nameInput, setNameInput] = useState('')
  const [priceInput, setPriceInput] = useState('')
  const [dateInput, setDateInput] = useState(todayStr())

  // どの項目のどのフィールドを編集中かを管理する
  const [editing, setEditing] = useState(null) // { id, field } | null
  const [draft, setDraft] = useState('')

  // 長押し判定用のタイマーとフラグ
  const longPressTimer = useRef(null)
  const longPressFired = useRef(false)

  // items が変わるたびに localStorage へ保存する
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
  }, [items])

  // 品名・金額・日付を入力してメモを追加する
  const handleAdd = (e) => {
    e.preventDefault()
    const trimmedName = nameInput.trim()
    if (!trimmedName) return

    const newItem = {
      id: Date.now().toString(),
      name: trimmedName,
      price: parsePrice(priceInput),
      date: dateInput || todayStr(),
      bought: false,
    }
    setItems((prev) => [...prev, newItem])

    // フォームをリセット（日付は今日のまま維持）
    setNameInput('')
    setPriceInput('')
    setDateInput(todayStr())
  }

  // 購入済みフラグを切り替える
  const toggleBought = (id) => {
    setItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, bought: !item.bought } : item)),
    )
  }

  // 項目を削除する
  const deleteItem = (id) => {
    setItems((prev) => prev.filter((item) => item.id !== id))
  }

  // 全項目を削除する（確認ダイアログあり）
  const handleClearAll = () => {
    if (items.length === 0) return
    if (window.confirm('すべてのメモを削除します。よろしいですか？')) {
      setItems([])
    }
  }

  // 項目の指定フィールドの編集を開始する
  const startEdit = (item, field) => {
    setEditing({ id: item.id, field })
    setDraft(field === 'price' ? String(item.price) : item[field])
  }

  // 編集内容を確定してitemsに反映する
  const commitEdit = () => {
    if (!editing) return
    const { id, field } = editing

    setItems((prev) =>
      prev.map((item) => {
        if (item.id !== id) return item
        if (field === 'name') {
          const trimmed = draft.trim()
          return trimmed ? { ...item, name: trimmed } : item
        }
        if (field === 'price') {
          return { ...item, price: parsePrice(draft) }
        }
        if (field === 'date') {
          return draft ? { ...item, date: draft } : item
        }
        return item
      }),
    )
    setEditing(null)
    setDraft('')
  }

  // 長押し開始：一定時間後に削除を実行する
  const handlePressStart = (id) => {
    longPressFired.current = false
    longPressTimer.current = setTimeout(() => {
      longPressFired.current = true
      deleteItem(id)
    }, LONG_PRESS_MS)
  }

  // 長押しタイマーの解除
  const clearPressTimer = () => {
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current)
      longPressTimer.current = null
    }
  }

  // タップ終了：長押しが発火していなければ購入済みフラグを切り替える
  const handlePressEnd = (id) => {
    clearPressTimer()
    if (!longPressFired.current) {
      toggleBought(id)
    }
    longPressFired.current = false
  }

  // 日付が新しい順（降順）に並べ替える
  const sortedItems = [...items].sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0))

  // 未購入合計・購入済み合計を計算する
  const unboughtTotal = items.filter((i) => !i.bought).reduce((sum, i) => sum + i.price, 0)
  const boughtTotal = items.filter((i) => i.bought).reduce((sum, i) => sum + i.price, 0)

  return (
    <div className="min-h-screen bg-gray-100 pb-24">
      <div className="mx-auto max-w-sm px-4 pt-6">
        <h1 className="mb-4 text-center text-xl font-bold text-gray-800">買い物メモ</h1>

        {/* 合計金額表示エリア */}
        <div className="mb-4 grid grid-cols-2 gap-3">
          <div className="rounded-xl bg-white p-3 text-center shadow">
            <p className="text-xs text-gray-500">未購入の合計</p>
            <p className="text-lg font-bold text-blue-600">{formatYen(unboughtTotal)}</p>
          </div>
          <div className="rounded-xl bg-white p-3 text-center shadow">
            <p className="text-xs text-gray-500">購入済みの合計</p>
            <p className="text-lg font-bold text-gray-400">{formatYen(boughtTotal)}</p>
          </div>
        </div>

        {/* 追加フォーム */}
        <form onSubmit={handleAdd} className="mb-5 space-y-2 rounded-xl bg-white p-3 shadow">
          <input
            type="text"
            value={nameInput}
            onChange={(e) => setNameInput(e.target.value)}
            placeholder="品名（必須）"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          />
          <div className="flex gap-2">
            {/* inputMode="numeric" によりスマホで数字キーパッドを表示する */}
            <input
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              value={priceInput}
              onChange={(e) => setPriceInput(e.target.value.replace(/[^0-9]/g, ''))}
              placeholder="金額（円・任意）"
              className="w-1/2 rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
            <input
              type="date"
              value={dateInput}
              onChange={(e) => setDateInput(e.target.value)}
              className="w-1/2 rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
          </div>
          <button
            type="submit"
            className="w-full rounded-lg bg-blue-600 py-2 text-sm font-bold text-white active:bg-blue-700"
          >
            追加
          </button>
        </form>

        {/* メモ一覧 */}
        <ul className="space-y-2">
          {sortedItems.map((item) => (
            <li
              key={item.id}
              onPointerDown={() => handlePressStart(item.id)}
              onPointerUp={() => handlePressEnd(item.id)}
              onPointerLeave={clearPressTimer}
              onPointerCancel={clearPressTimer}
              onContextMenu={(e) => e.preventDefault()}
              className={`select-none rounded-xl bg-white p-3 shadow ${
                item.bought ? 'opacity-50' : ''
              }`}
            >
              <div className="flex items-center gap-3">
                {/* 購入済みチェック表示 */}
                <div
                  className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 ${
                    item.bought ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-300'
                  }`}
                >
                  {item.bought ? '✓' : ''}
                </div>

                <div className="min-w-0 flex-1">
                  {/* 品名（タップで編集） */}
                  {editing?.id === item.id && editing.field === 'name' ? (
                    <input
                      autoFocus
                      type="text"
                      value={draft}
                      onChange={(e) => setDraft(e.target.value)}
                      onBlur={commitEdit}
                      onKeyDown={(e) => e.key === 'Enter' && commitEdit()}
                      onPointerDown={(e) => e.stopPropagation()}
                      onPointerUp={(e) => e.stopPropagation()}
                      className="w-full rounded border border-blue-400 px-1 text-sm"
                    />
                  ) : (
                    <p
                      onPointerDown={(e) => e.stopPropagation()}
                      onPointerUp={(e) => e.stopPropagation()}
                      onClick={() => startEdit(item, 'name')}
                      className={`truncate text-sm font-medium text-gray-800 ${
                        item.bought ? 'line-through' : ''
                      }`}
                    >
                      {item.name}
                    </p>
                  )}

                  <div className="mt-1 flex gap-3 text-xs text-gray-500">
                    {/* 金額（タップで編集） */}
                    {editing?.id === item.id && editing.field === 'price' ? (
                      <input
                        autoFocus
                        type="text"
                        inputMode="numeric"
                        pattern="[0-9]*"
                        value={draft}
                        onChange={(e) => setDraft(e.target.value.replace(/[^0-9]/g, ''))}
                        onBlur={commitEdit}
                        onKeyDown={(e) => e.key === 'Enter' && commitEdit()}
                        onPointerDown={(e) => e.stopPropagation()}
                        onPointerUp={(e) => e.stopPropagation()}
                        className="w-20 rounded border border-blue-400 px-1"
                      />
                    ) : (
                      <span
                        onPointerDown={(e) => e.stopPropagation()}
                        onPointerUp={(e) => e.stopPropagation()}
                        onClick={() => startEdit(item, 'price')}
                      >
                        {formatYen(item.price)}
                      </span>
                    )}

                    {/* 日付（タップで編集） */}
                    {editing?.id === item.id && editing.field === 'date' ? (
                      <input
                        autoFocus
                        type="date"
                        value={draft}
                        onChange={(e) => setDraft(e.target.value)}
                        onBlur={commitEdit}
                        onKeyDown={(e) => e.key === 'Enter' && commitEdit()}
                        onPointerDown={(e) => e.stopPropagation()}
                        onPointerUp={(e) => e.stopPropagation()}
                        className="rounded border border-blue-400 px-1"
                      />
                    ) : (
                      <span
                        onPointerDown={(e) => e.stopPropagation()}
                        onPointerUp={(e) => e.stopPropagation()}
                        onClick={() => startEdit(item, 'date')}
                      >
                        {formatDateSlash(item.date)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </li>
          ))}

          {sortedItems.length === 0 && (
            <p className="pt-8 text-center text-sm text-gray-400">メモがありません</p>
          )}
        </ul>

        {/* 全消しボタン */}
        <button
          type="button"
          onClick={handleClearAll}
          className="mt-6 w-full rounded-lg border border-red-300 py-2 text-sm font-bold text-red-500 active:bg-red-50"
        >
          全消し
        </button>

        <p className="mt-3 text-center text-xs text-gray-400">
          タップでチェック / 長押しで削除 / 各項目タップで編集
        </p>
      </div>
    </div>
  )
}
