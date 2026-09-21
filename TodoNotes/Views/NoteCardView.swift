import SwiftUI
import UIKit

struct NoteCardView: View {
    @EnvironmentObject private var store: NoteStore
    let note: TodoNote
    var onOpen: () -> Void

    private let maxPreviewItems = 6

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Spacer()
                Button(action: onOpen) {
                    Image(systemName: "pencil.circle.fill")
                        .font(.system(.subheadline))
                        .opacity(0.55)
                }
                .buttonStyle(.plain)
                .accessibilityLabel(Text("メモを編集"))
            }
            .padding(.bottom, -4)

            if let fileName = note.imageFileName, let image = store.loadImage(fileName: fileName) {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFill()
                    .frame(height: 90)
                    .frame(maxWidth: .infinity)
                    .clipped()
                    .clipShape(RoundedRectangle(cornerRadius: 10))
            }

            ForEach(previewItems) { item in
                Button {
                    Haptics.tap()
                    withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                        store.toggleItem(noteID: note.id, itemID: item.id)
                    }
                } label: {
                    HStack(alignment: .firstTextBaseline, spacing: 6) {
                        Image(systemName: item.isDone ? "checkmark.square.fill" : "square")
                            .font(.system(.subheadline))
                        Text(item.text)
                            .font(.system(.subheadline, design: .rounded, weight: .medium))
                            .strikethrough(item.isDone)
                            .lineLimit(1)
                            .multilineTextAlignment(.leading)
                    }
                }
                .buttonStyle(.plain)
                .opacity(item.isDone ? 0.6 : 1)
                .accessibilityLabel(item.text)
                .accessibilityAddTraits(item.isDone ? [.isSelected] : [])
                .accessibilityHint(Text("タップで完了を切り替え"))
            }

            if note.items.count > maxPreviewItems {
                Text("他 \(note.items.count - maxPreviewItems) 件")
                    .font(.system(.caption2, design: .rounded))
                    .opacity(0.7)
            }

            Spacer(minLength: 0)

            HStack(spacing: 4) {
                Spacer()
                if hasContent && note.remainingCount == 0 {
                    Image(systemName: "checkmark.seal.fill")
                        .font(.system(.caption2))
                    Text("すべて完了")
                        .font(.system(.caption2, design: .rounded, weight: .semibold))
                } else {
                    Text("\(note.remainingCount) 件残り")
                        .font(.system(.caption2, design: .rounded))
                }
            }
            .opacity(0.75)
        }
        .foregroundStyle(note.color.foreground)
        .padding(14)
        .frame(minHeight: 140, alignment: .topLeading)
        .frame(maxWidth: .infinity, alignment: .topLeading)
        .background(note.color.background)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .black.opacity(0.15), radius: 4, x: 0, y: 2)
        .rotationEffect(.degrees(tiltAngle))
        .contentShape(Rectangle())
        .onTapGesture(perform: onOpen)
    }

    private var previewItems: [TodoItem] {
        Array(note.items.filter { !$0.text.trimmingCharacters(in: .whitespaces).isEmpty }.prefix(maxPreviewItems))
    }

    private var hasContent: Bool {
        note.items.contains { !$0.text.trimmingCharacters(in: .whitespaces).isEmpty }
    }

    /// A small, stable tilt derived from the note's identity so the board reads
    /// like a scattered pile of sticky notes rather than a rigid grid.
    private var tiltAngle: Double {
        let hash = note.id.uuidString.hashValue
        let normalized = Double(hash % 200) / 100.0 // -2.0...2.0
        return normalized
    }
}
