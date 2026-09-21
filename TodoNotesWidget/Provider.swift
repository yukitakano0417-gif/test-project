import WidgetKit

struct NoteEntry: TimelineEntry {
    let date: Date
    let note: TodoNote?
}

/// Shows the most recently touched note (index 0 — both `addNote` and
/// `updateNote` in `NoteStore` keep the freshest note at the front).
/// The timeline never auto-refreshes on a schedule (`.never`); instead
/// the app and `ToggleTodoItemIntent` both call
/// `WidgetCenter.shared.reloadTimelines` right after they change data,
/// which keeps the widget in sync without unnecessary background work.
struct Provider: TimelineProvider {
    func placeholder(in context: Context) -> NoteEntry {
        NoteEntry(
            date: Date(),
            note: TodoNote(color: .yellow, items: [TodoItem(text: "食材を買う"), TodoItem(text: "犬の散歩")])
        )
    }

    func getSnapshot(in context: Context, completion: @escaping (NoteEntry) -> Void) {
        completion(NoteEntry(date: Date(), note: NotesRepository.load().first))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<NoteEntry>) -> Void) {
        let entry = NoteEntry(date: Date(), note: NotesRepository.load().first)
        completion(Timeline(entries: [entry], policy: .never))
    }
}
