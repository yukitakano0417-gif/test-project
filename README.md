# Todoメモ (TodoNotes)

App Store配信を想定した、付箋（Lock Screen Notes系アプリ）スタイルのTodoリストアプリです。
SwiftUI（iOS 16+）で実装しています。

## できること

- カラフルな付箋カード形式でTodoリストを管理（10色から選択）
- 各カードはチェックリスト形式。カードをタップせずにそのままチェックのオン/オフが可能
- 写真をメモに添付
- メモの検索
- ローカル保存のみ（サーバー通信なし、外部トラッキングなし）
- ハプティクス・アニメーションなどの細かい使い心地の作り込み
- VoiceOver対応（各Todo項目・ボタンにアクセシビリティラベルを付与）

## プロジェクト構成

```
TodoNotes.xcodeproj/         Xcodeプロジェクト
TodoNotes/
  TodoNotesApp.swift         Appのエントリーポイント
  Models/                    TodoNote, TodoItem, NoteColor
  Store/                     NoteStore（永続化）, Haptics
  Views/                     ContentView, NoteCardView, NoteEditorView, ColorPickerRow
  Assets.xcassets/           AppIcon, AccentColor
  PrivacyInfo.xcprivacy      プライバシーマニフェスト
  Preview Content/           SwiftUI Previews用アセット
scripts/
  generate_app_icon.py       AppIcon.png(1024x1024)を生成するスクリプト
  generate_pbxproj.py        project.pbxprojを生成するスクリプト（下記「重要な注意」を参照）
```

## 開くには（Xcodeが必要）

このプロジェクトはmacOS + Xcodeでの作業を前提としています（本セッションはLinux環境のため、実機ビルド・シミュレータ実行・Xcode上での検証は行えていません）。

1. `TodoNotes.xcodeproj` をXcodeで開く
2. 「Signing & Capabilities」であなたのApple Developerチームを選択（`PRODUCT_BUNDLE_IDENTIFIER` も必要に応じて自分のもの、例: `com.yourname.todonotes` に変更）
3. シミュレータまたは実機でRunして動作確認
4. 問題なければ Product > Archive でApp Store Connectに配信

### 重要な注意（正直に）

`project.pbxproj` は、このセッションにmacOS/Xcodeがないため、`scripts/generate_pbxproj.py` で手動生成しました。構造的な検証（ID参照の整合性、括弧の対応など）は行っていますが、**実際にXcodeで開いて問題なくビルドできることまでは確認できていません。** Xcodeで開いて警告が出た場合は、まず「Update to recommended settings」を試すか、問題があれば教えてください。

もしXcodeで開けない・様子がおかしい場合は、Xcodeで新規iOSアプリ（SwiftUI）プロジェクトを作り直し、`TodoNotes/` 配下のSwiftファイル・Assets・PrivacyInfo.xcprivacyだけをドラッグ＆ドロップで追加するのが一番確実です。

## App Store提出チェックリスト

- [ ] Apple Developer Program登録（$99/年）
- [ ] App Store Connectで新規Appを作成し、Bundle IDを一致させる
- [ ] アプリアイコンの確認（`TodoNotes/Assets.xcassets/AppIcon.appiconset/AppIcon.png`、必要なら差し替え）
- [ ] スクリーンショット撮影（6.7インチ / 6.5インチ等、必須サイズはApp Store Connectの指示に従う）
- [ ] プライバシーポリシーURL（データを一切収集しないアプリですが、URLの提出自体は必須。GitHub Pagesや簡易LPで用意する）
- [ ] App Store Connectの「App Privacy」質問票で「データ収集なし」を選択（本アプリは通信を行わないため該当）
- [ ] 年齢制限・カテゴリ設定（カテゴリ: 仕事効率化 / Productivity を想定し `LSApplicationCategoryType` を設定済み）
- [ ] TestFlightで動作確認してから提出

### ストア掲載文（たたき台）

**アプリ名**: Todoメモ

**サブタイトル**: 付箋みたいにサクサク書けるTodoリスト

**説明文（日本語）**:
```
付箋を貼るような感覚で、やることをサクッと書き留められるTodoリストアプリです。

・カラフルな付箋でリストを色分け
・チェックボックス付きでそのままタスク管理
・写真を貼り付けてメモをもっとわかりやすく
・検索ですぐに目的のメモを見つけられる
・データは端末内に保存、外部送信なし
```

**Description (English)**:
```
A sticky-note style to-do list app. Jot things down fast, check them off,
and keep every list color-coded and easy to scan.

- Colorful sticky notes for each list
- Built-in checkboxes for quick task tracking
- Attach a photo to any note
- Search to find a note instantly
- All data stays on your device — nothing is sent anywhere
```

**キーワード例**: todo,タスク,付箋,メモ,チェックリスト,checklist,task,sticky note

## 今後の拡張候補

- ロックスクリーン／ホーム画面ウィジェット（WidgetKit + App Intentsでインタラクティブなチェック操作）
- iCloud同期（CloudKit）
- 手書き文字風フォントやドローイング機能
