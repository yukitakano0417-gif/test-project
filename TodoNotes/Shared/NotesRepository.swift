import Foundation

/// Shared read/write access to the notes file, used by both the app
/// (via `NoteStore`) and the widget extension (via its timeline provider
/// and `ToggleTodoItemIntent`). Keeping this in one place means the two
/// targets can never drift into incompatible file formats.
enum NotesRepository {
    /// Bump this and add a migration branch in `decodeNotes(from:)` if
    /// `TodoNote`'s shape ever changes in a way older saved data can't decode.
    static let currentSchemaVersion = 1

    struct PersistedNotes: Codable {
        var version: Int
        var notes: [TodoNote]
    }

    /// The App Group container when the entitlement is set up correctly,
    /// falling back to the app's own sandbox so the app still works
    /// standalone (e.g. before the widget target's entitlements are wired
    /// up in a fresh checkout).
    static var containerURL: URL {
        FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: AppGroup.identifier)
            ?? FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }

    static var notesFileURL: URL { containerURL.appendingPathComponent("notes.json") }
    static var backupFileURL: URL { containerURL.appendingPathComponent("notes.backup.json") }
    static var imagesDirectory: URL { containerURL.appendingPathComponent("NoteImages", isDirectory: true) }

    // MARK: - Load/save
    //
    // Never let a read failure silently wipe the user's notes. A future
    // schema change, a partially-written file, or disk corruption should
    // fall back to the last-known-good backup rather than resetting to [].

    static func load() -> [TodoNote] {
        if let notes = decodeNotes(from: notesFileURL) {
            return notes
        }
        if let notes = decodeNotes(from: backupFileURL) {
            save(notes) // restore the primary file from the backup we just recovered
            return notes
        }
        return []
    }

    static func save(_ notes: [TodoNote]) {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        let payload = PersistedNotes(version: currentSchemaVersion, notes: notes)
        guard let data = try? encoder.encode(payload) else { return }
        try? FileManager.default.createDirectory(at: containerURL, withIntermediateDirectories: true)
        // Keep one prior generation on disk before overwriting, so a bad
        // write or a future decode failure has something to recover from.
        if FileManager.default.fileExists(atPath: notesFileURL.path) {
            try? FileManager.default.removeItem(at: backupFileURL)
            try? FileManager.default.copyItem(at: notesFileURL, to: backupFileURL)
        }
        try? data.write(to: notesFileURL, options: .atomic)
        NotificationManager.resync(with: notes)
    }

    private static func decodeNotes(from url: URL) -> [TodoNote]? {
        guard let data = try? Data(contentsOf: url) else { return nil }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        if let wrapped = try? decoder.decode(PersistedNotes.self, from: data) {
            return wrapped.notes
        }
        // Falls back to the pre-versioning format (a bare [TodoNote] array)
        // so upgrading to the versioned format never loses existing data.
        return try? decoder.decode([TodoNote].self, from: data)
    }
}
