import SwiftUI
import WidgetKit

struct TodoNotesWidget: Widget {
    let kind: String = WidgetKind.todoNotes

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: Provider()) { entry in
            TodoNotesWidgetView(entry: entry)
        }
        .configurationDisplayName("Todoメモ")
        .description("直近のメモをロック画面やホーム画面からチェックできます。")
        .supportedFamilies([
            .accessoryRectangular,
            .accessoryCircular,
            .accessoryInline,
            .systemSmall,
            .systemMedium
        ])
    }
}

@main
struct TodoNotesWidgetBundle: WidgetBundle {
    var body: some Widget {
        TodoNotesWidget()
    }
}
