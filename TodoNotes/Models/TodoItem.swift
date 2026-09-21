import Foundation

struct TodoItem: Identifiable, Codable, Equatable {
    let id: UUID
    var text: String
    var isDone: Bool
    /// Optional reminder time. Missing in older saved data decodes to nil
    /// automatically (Codable's synthesized decoder treats an absent key
    /// for an Optional property as nil), so this needed no migration.
    var dueDate: Date?

    init(id: UUID = UUID(), text: String = "", isDone: Bool = false, dueDate: Date? = nil) {
        self.id = id
        self.text = text
        self.isDone = isDone
        self.dueDate = dueDate
    }
}
