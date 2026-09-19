import Foundation

struct TodoNote: Identifiable, Codable, Equatable {
    let id: UUID
    var color: NoteColor
    var items: [TodoItem]
    var imageFileName: String?
    var createdAt: Date
    var updatedAt: Date

    init(
        id: UUID = UUID(),
        color: NoteColor = .yellow,
        items: [TodoItem] = [TodoItem()],
        imageFileName: String? = nil,
        createdAt: Date = Date(),
        updatedAt: Date = Date()
    ) {
        self.id = id
        self.color = color
        self.items = items
        self.imageFileName = imageFileName
        self.createdAt = createdAt
        self.updatedAt = updatedAt
    }

    var isEmpty: Bool {
        items.allSatisfy { $0.text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
    }

    var remainingCount: Int {
        items.filter { !$0.isDone && !$0.text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }.count
    }
}
