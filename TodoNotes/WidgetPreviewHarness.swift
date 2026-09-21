#if DEBUG
import SwiftUI
import WidgetKit

/// Renders the exact same `TodoNotesWidgetView` the widget extension uses,
/// at each supported family's real point size, so we can screenshot what
/// the Lock Screen / Home Screen widget looks like without needing to
/// drive the system's actual widget gallery (which isn't scriptable via
/// `simctl`). Only reachable in Debug builds with WIDGET_PREVIEW=1 set
/// (see .github/workflows/ios-build.yml) — never compiled into Release.
struct WidgetPreviewHarness: View {
    @EnvironmentObject private var store: NoteStore

    var body: some View {
        let entry = NoteEntry(date: Date(), note: store.notes.first)

        ScrollView {
            VStack(spacing: 28) {
                Text("ウィジェットプレビュー")
                    .font(.system(.title2, design: .rounded, weight: .bold))

                labeled("ロック画面 · rectangular") {
                    TodoNotesWidgetView(entry: entry)
                        .environment(\.widgetFamily, .accessoryRectangular)
                        .frame(width: 160, height: 56)
                        .foregroundStyle(.white)
                        .padding(8)
                        .background(Color.black)
                        .clipShape(RoundedRectangle(cornerRadius: 16))
                }

                labeled("ロック画面 · circular") {
                    TodoNotesWidgetView(entry: entry)
                        .environment(\.widgetFamily, .accessoryCircular)
                        .frame(width: 56, height: 56)
                        .foregroundStyle(.white)
                        .background(Color.black)
                        .clipShape(Circle())
                }

                labeled("ロック画面 · inline") {
                    TodoNotesWidgetView(entry: entry)
                        .environment(\.widgetFamily, .accessoryInline)
                        .foregroundStyle(.white)
                        .padding(8)
                        .background(Color.black)
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                }

                labeled("ホーム画面 · small") {
                    TodoNotesWidgetView(entry: entry)
                        .environment(\.widgetFamily, .systemSmall)
                        .frame(width: 155, height: 155)
                        .clipShape(RoundedRectangle(cornerRadius: 24))
                }

                labeled("ホーム画面 · medium") {
                    TodoNotesWidgetView(entry: entry)
                        .environment(\.widgetFamily, .systemMedium)
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
