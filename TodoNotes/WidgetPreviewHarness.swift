#if DEBUG
import SwiftUI
import WidgetKit

/// Renders `TodoNotesWidgetContent` — the exact same view code the widget
/// extension uses — at each supported family's real point size, so we can
/// screenshot what the Lock Screen / Home Screen widget looks like without
/// needing to drive the system's actual widget gallery (which isn't
/// scriptable via `simctl`). We use `TodoNotesWidgetContent` directly
/// rather than `TodoNotesWidgetView` because `widgetFamily` is a read-only
/// environment key outside a real widget host — there's no way to override
/// it with `.environment(\.widgetFamily, ...)`. Only reachable in Debug
/// builds with WIDGET_PREVIEW=1 set (see .github/workflows/ios-build.yml)
/// — never compiled into Release.
struct WidgetPreviewHarness: View {
    @EnvironmentObject private var store: NoteStore

    var body: some View {
        let note = store.notes.first

        ScrollView {
            VStack(spacing: 28) {
                Text("ウィジェットプレビュー")
                    .font(.system(.title2, design: .rounded, weight: .bold))

                labeled("ロック画面 · rectangular") {
                    TodoNotesWidgetContent(family: .accessoryRectangular, note: note)
                        .frame(width: 160, height: 56)
                        .foregroundStyle(.white)
                        .padding(8)
                        .background(Color.black)
                        .clipShape(RoundedRectangle(cornerRadius: 16))
                }

                labeled("ロック画面 · circular") {
                    TodoNotesWidgetContent(family: .accessoryCircular, note: note)
                        .frame(width: 56, height: 56)
                        .foregroundStyle(.white)
                        .background(Color.black)
                        .clipShape(Circle())
                }

                labeled("ロック画面 · inline") {
                    TodoNotesWidgetContent(family: .accessoryInline, note: note)
                        .foregroundStyle(.white)
                        .padding(8)
                        .background(Color.black)
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                }

                labeled("ホーム画面 · small") {
                    TodoNotesWidgetContent(family: .systemSmall, note: note)
                        .frame(width: 155, height: 155)
                        .clipShape(RoundedRectangle(cornerRadius: 24))
                }

                labeled("ホーム画面 · medium") {
                    TodoNotesWidgetContent(family: .systemMedium, note: note)
                        .frame(width: 329, height: 155)
                        .clipShape(RoundedRectangle(cornerRadius: 24))
                }
            }
            .padding(24)
            .frame(maxWidth: .infinity)
        }
        .background(Color(uiColor: .systemGroupedBackground))
    }

    @ViewBuilder
    private func labeled(_ title: String, @ViewBuilder content: () -> some View) -> some View {
        VStack(spacing: 10) {
            Text(title)
                .font(.system(.caption, design: .rounded))
                .foregroundStyle(.secondary)
            content()
        }
    }
}
#endif
