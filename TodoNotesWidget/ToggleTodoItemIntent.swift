import AppIntents
import WidgetKit

/// Lets a Lock Screen / Home Screen widget check an item off without
/// opening the app. IDs are passed as strings since `AppIntent`
/// parameters need simple, `Codable`-friendly types.
struct ToggleTodoItemIntent: AppIntent {
    static var title: LocalizedStringResource = "チェックを切り替え"
    static var openAppWhenRun: Bool = false

    @Parameter(title: "Note ID")
    var noteID: String

    @Parameter(title: "Item ID")
    var itemID: String

    init() {
        noteID = ""
        itemID = ""
    }

    init(noteID: String, itemID: String) {
        self.noteID = noteID
        self.itemID = itemID
    }

    func perform() async throws -> some IntentResult {
        var notes = NotesRepository.load()
        if let noteIndex = notes.firstIndex(where: { $0.id.uuidString == noteID }),
           let itemIndex = notes[noteIndex].items.firstIndex(where: { $0.id.uuidString == itemID }) {
            notes[noteIndex].items[itemIndex].isDone.toggle()
            notes[noteIndex].updatedAt = Date()
            NotesRepository.save(notes)
        }
        WidgetCenter.shared.reloadTimelines(ofKind: WidgetKind.todoNotes)
        return .result()
    }
}
