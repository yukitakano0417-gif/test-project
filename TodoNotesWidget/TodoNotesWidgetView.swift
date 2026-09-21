import SwiftUI
import WidgetKit

struct TodoNotesWidgetView: View {
    @Environment(\.widgetFamily) private var family
    let entry: NoteEntry

    var body: some View {
        if let note = entry.note {
            content(for: note)
        } else {
            emptyState
        }
    }

    @ViewBuilder
    private func content(for note: TodoNote) -> some View {
        switch family {
        case .accessoryRectangular:
            rectangularBody(note)
                .containerBackground(.clear, for: .widget)
        case .accessoryCircular:
            circularBody(note)
                .containerBackground(.clear, for: .widget)
        case .accessoryInline:
            inlineBody(note)
                .containerBackground(.clear, for: .widget)
        default:
            homeScreenBody(note)
                .containerBackground(note.color.background, for: .widget)
        }
    }

    private var emptyState: some View {
        Group {
            switch family {
            case .accessoryCircular:
                Image(systemName: "checklist")
            case .accessoryInline:
                Text("メモがありません")
            default:
                Text("Todoメモを開いて\n最初のメモを作りましょう")
                    .font(.system(.caption, design: .rounded))
                    .multilineTextAlignment(.leading)
            }
        }
        .containerBackground(.clear, for: .widget)
    }

    // MARK: - Lock Screen

    private func rectangularBody(_ note: TodoNote) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            ForEach(previewItems(of: note, limit: 3)) { item in
                toggleRow(note: note, item: item)
            }
        }
        .font(.system(.caption2, design: .rounded))
    }

    private func circularBody(_ note: TodoNote) -> some View {
        let remaining = note.remainingCount
        return VStack(spacing: 1) {
            Image(systemName: "checklist")
                .font(.system(.caption))
            Text("\(remaining)")
                .font(.system(.headline, design: .rounded))
        }
    }

    private func inlineBody(_ note: TodoNote) -> some View {
        let firstOpenItem = note.items.first {
            !$0.isDone && !$0.text.trimmingCharacters(in: .whitespaces).isEmpty
        }
        return Label(firstOpenItem?.text ?? "すべて完了", systemImage: "checklist")
    }

    // MARK: - Home Screen

    private func homeScreenBody(_ note: TodoNote) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Todoメモ")
                .font(.system(.caption2, design: .rounded, weight: .semibold))
                .opacity(0.7)
            ForEach(previewItems(of: note, limit: family == .systemMedium ? 5 : 3)) { item in
                toggleRow(note: note, item: item)
            }
        }
        .foregroundStyle(note.color.foreground)
        .padding(12)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
    }

    // MARK: - Shared

    private func toggleRow(note: TodoNote, item: TodoItem) -> some View {
        Button(intent: ToggleTodoItemIntent(noteID: note.id.uuidString, itemID: item.id.uuidString)) {
            HStack(alignment: .firstTextBaseline, spacing: 4) {
                Image(systemName: item.isDone ? "checkmark.square.fill" : "square")
                Text(item.text)
                    .strikethrough(item.isDone)
                    .lineLimit(1)
            }
        }
        .buttonStyle(.plain)
        .opacity(item.isDone ? 0.6 : 1)
    }

    private func previewItems(of note: TodoNote, limit: Int) -> [TodoItem] {
        Array(note.items.filter { !$0.text.trimmingCharacters(in: .whitespaces).isEmpty }.prefix(limit))
    }
}
