/// The widget `kind` identifier, shared so the app (which calls
/// `WidgetCenter.shared.reloadTimelines(ofKind:)` after every save) and
/// the widget extension (which declares its `StaticConfiguration` with
/// this same kind) can never drift apart.
enum WidgetKind {
    static let todoNotes = "TodoNotesWidget"
}
