# Todoメモ (TodoNotes)

App Store配信を想定した、付箋（Lock Screen Notes系アプリ）スタイルのTodoリストアプリです。
SwiftUI（iOS 17+）で実装しています。

## できること

- カラフルな付箋カード形式でTodoリストを管理（10色から選択）
- 各カードはチェックリスト形式。カードをタップせずにそのままチェックのオン/オフが可能
- **ロック画面・ホーム画面ウィジェット**（WidgetKit）: 直近のメモをロック画面（rectangular / circular / inline）やホーム画面（small / medium）に置いて、アプリを開かずにチェックできる
- 写真をメモに添付
- メモの検索
- ローカル保存のみ（サーバー通信なし、外部トラッキングなし）
- ハプティクス・アニメーションなどの細かい使い心地の作り込み
- VoiceOver対応（各Todo項目・ボタンにアクセシビリティラベルを付与）
- WCAG AA相当のコントラスト比を確保した配色
- Dynamic Type対応（文字サイズ設定に追従）

## プロジェクト構成

```
TodoNotes.xcodeproj/         Xcodeプロジェクト（TodoNotes / TodoNotesWidgetExtension の2ターゲット）
TodoNotes/
  TodoNotesApp.swift         Appのエントリーポイント
  WidgetPreviewHarness.swift ウィジェットの見た目をアプリ内で確認するためのデバッグ専用画面
  Models/                    TodoNote, TodoItem, NoteColor（アプリ・ウィジェット両方にコンパイル）
  Shared/                    AppGroup, NotesRepository, WidgetKind（アプリ・ウィジェット共有のデータ層）
  Store/                     NoteStore（永続化のラッパー）, Haptics
  Views/                     ContentView, NoteCardView, NoteEditorView, ColorPickerRow
  Assets.xcassets/           AppIcon, AccentColor
  PrivacyInfo.xcprivacy      プライバシーマニフェスト
  TodoNotes.entitlements     App Groups設定
  Preview Content/           SwiftUI Previews用アセット
TodoNotesWidget/              ウィジェット拡張ターゲット
  TodoNotesWidget.swift      Widget / WidgetBundle定義
  Provider.swift             TimelineProvider（直近のメモを1件表示）
  TodoNotesWidgetView.swift  ロック画面・ホーム画面それぞれの見た目
  ToggleTodoItemIntent.swift アプリを開かずにチェックを切り替えるAppIntent
  Info.plist, *.entitlements, PrivacyInfo.xcprivacy
scripts/
  generate_app_icon.py       AppIcon.png(1024x1024)を生成するスクリプト
  generate_pbxproj.py        project.pbxprojを生成するスクリプト（下記「重要な注意」を参照）
.github/workflows/
  ios-build.yml              macOSランナーでビルド・ウィジェット組み込み確認・シミュレータのスクリーンショットを撮ってdocs/screenshots/にコミットするCI
```

## 開くには（Xcodeが必要）

このプロジェクトはmacOS + Xcodeでの作業を前提としています（本セッションはLinux環境のため、実機ビルド・シミュレータ実行・Xcode上での検証は行えていません。代わりにGitHub Actions（macOSランナー）でビルド・スクリーンショット撮影を自動化しています）。

1. `TodoNotes.xcodeproj` をXcodeで開く
2. **両方のターゲット**（TodoNotes / TodoNotesWidgetExtension）で「Signing & Capabilities」からあなたのApple Developerチームを選択
3. **App Groups**: 両ターゲットに `group.com.yukitakano.todonotes` というApp Groupが設定済みです。あなたのApple Developerアカウントでこの識別子（またはあなた自身の命名）を作成し、`TodoNotes/Shared/AppGroup.swift` の `identifier` と両方の `.entitlements` ファイルを合わせて書き換えてください
4. `PRODUCT_BUNDLE_IDENTIFIER` も必要に応じて自分のもの（例: `com.yourname.todonotes` とその子である `com.yourname.todonotes.TodoNotesWidget`）に変更
5. シミュレータまたは実機でRunして動作確認。ウィジェットはロック画面を編集 → 「Todoメモ」を追加、またはホーム画面をロングタップ→ウィジェットを追加、で確認できます
6. 問題なければ Product > Archive でApp Store Connectに配信

### なぜiOS 17以上なのか

ロック画面・ホーム画面ウィジェットからアプリを開かずにチェックを切り替える「インタラクティブウィジェット」はiOS 17で追加されたAPI（App Intents + WidgetKitのButton）が必要です。この機能が今回のアプリの核なので、最低対応OSをiOS 16→17に引き上げています。

### 重要な注意（正直に）

`project.pbxproj` は、このセッションにmacOS/Xcodeがないため、`scripts/generate_pbxproj.py` で手動生成しました（2ターゲット構成・App Group・Widget Extensionの組み込みまで含む、かなり複雑な構成です）。ID参照の整合性・括弧の対応・重複がないことは検証済みで、GitHub ActionsのmacOSランナー上で実際に `xcodebuild` を実行してビルド成功とウィジェットの組み込み（`.appex`がアプリバンドルの`PlugIns/`に入っていること）まで確認しています。ただし、実機やXcode上での対話的な動作確認（実際にロック画面に追加してタップする、など）はできていません。

ロック画面ウィジェットの実際の見た目は、システムのウィジェットギャラリーをCIから自動操作する方法がないため、`WidgetPreviewHarness`（デバッグ専用画面）でウィジェットと全く同じView（`TodoNotesWidgetView`）を実寸大でレンダリングしてスクリーンショットしています。見た目はほぼ実物と同じはずですが、システム標準のロック画面の縁取りやvibrancy（半透明の質感）表現までは再現できていません。

もしXcodeで開けない・様子がおかしい場合は、Xcodeで新規iOSアプリ（SwiftUI）＋Widget Extensionプロジェクトを作り直し、各ファイルをドラッグ＆ドロップで追加するのが一番確実です。

## App Store提出チェックリスト

- [ ] Apple Developer Program登録（$99/年）
- [ ] App Store Connectで新規Appを作成し、Bundle IDを一致させる
- [ ] App Groupを自分のアカウントで作成し、`AppGroup.swift`と両方の`.entitlements`を更新
- [ ] アプリアイコンの確認（`TodoNotes/Assets.xcassets/AppIcon.appiconset/AppIcon.png`、必要なら差し替え）
- [ ] スクリーンショット撮影（6.7インチ / 6.5インチ等、必須サイズはApp Store Connectの指示に従う。ウィジェットも紹介するとダウンロード率が上がりやすい）
- [ ] プライバシーポリシーURL（データを一切収集しないアプリですが、URLの提出自体は必須。GitHub Pagesや簡易LPで用意する）
- [ ] App Store Connectの「App Privacy」質問票で「データ収集なし」を選択（本アプリは通信を行わないため該当）
- [ ] 年齢制限・カテゴリ設定（カテゴリ: 仕事効率化 / Productivity を想定し `LSApplicationCategoryType` を設定済み）
- [ ] TestFlightで動作確認してから提出（特にウィジェットの動作は実機/TestFlightでの確認を強く推奨）

### ストア掲載文（たたき台）

**アプリ名**: Todoメモ

**サブタイトル**: 付箋みたいにサクサク書けるTodoリスト

**説明文（日本語）**:
```
付箋を貼るような感覚で、やることをサクッと書き留められるTodoリストアプリです。

・カラフルな付箋でリストを色分け
・チェックボックス付きでそのままタスク管理
・ロック画面・ホーム画面のウィジェットからアプリを開かずにチェック
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
- Lock Screen and Home Screen widgets you can check off without opening the app
- Attach a photo to any note
- Search to find a note instantly
- All data stays on your device — nothing is sent anywhere
```

**キーワード例**: todo,タスク,付箋,メモ,チェックリスト,ウィジェット,checklist,task,sticky note,widget

## 今後の拡張候補

- iCloud同期（CloudKit）— 複数端末間でメモを同期
- ウィジェットの設定機能（表示するメモを選べるように、`AppIntentConfiguration`化）
- 手書き文字風フォントやドローイング機能
- StandBy表示への最適化
