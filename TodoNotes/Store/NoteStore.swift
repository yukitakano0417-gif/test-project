import Foundation
import UIKit

@MainActor
final class NoteStore: ObservableObject {
    @Published private(set) var notes: [TodoNote] = []

    private let fileURL: URL
    private let imagesDirectory: URL
    private let imageCache = NSCache<NSString, UIImage>()

    init() {
        let documents = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        fileURL = documents.appendingPathComponent("notes.json")
        imagesDirectory = documents.appendingPathComponent("NoteImages", isDirectory: true)
        try? FileManager.default.createDirectory(at: imagesDirectory, withIntermediateDirectories: true)
        load()

        #if DEBUG
        if ProcessInfo.processInfo.environment["SEED_SAMPLE_DATA"] == "1" {
            notes = Self.sampleNotes
        }
        #endif
    }

    #if DEBUG
    /// Demo content used only for screenshot generation (see .github/workflows/ios-build.yml).
    /// Compiled out of Release builds, so this never ships to the App Store.
    private static let sampleNotes: [TodoNote] = [
        TodoNote(
            color: .yellow,
            items: [
                TodoItem(text: "食材を買う"),
                TodoItem(text: "クリーニング回収", isDone: true),
                TodoItem(text: "犬の散歩")
            ]
        ),
        TodoNote(
            color: .teal,
            items: [
                TodoItem(text: "資料を作成する"),
                TodoItem(text: "10:00 ミーティング"),
                TodoItem(text: "メールを返信", isDone: true)
            ]
        ),
        TodoNote(
            color: .pink,
            items: [
                TodoItem(text: "本を読む"),
                TodoItem(text: "ヨガ", isDone: true)
            ]
        ),
        TodoNote(
            color: .charcoal,
            items: [
                TodoItem(text: "家賃を払う"),
                TodoItem(text: "電気代を払う")
            ]
        ),
        TodoNote(
            color: .green,
            items: [
                TodoItem(text: "植物に水やり")
            ]
        ),
        TodoNote(
            color: .purple,
            items: [
                TodoItem(text: "誕生日プレゼントを探す"),
                TodoItem(text: "カードを書く", isDone: true)
            ]
        )
    ]
    #endif

    func addNote(_ note: TodoNote) {
        notes.insert(note, at: 0)
        save()
    }

    func updateNote(_ note: TodoNote) {
        guard let index = notes.firstIndex(where: { $0.id == note.id }) else { return }
        var updated = note
        updated.updatedAt = Date()
        notes.remove(at: index)
        notes.insert(updated, at: 0)
        save()
    }

    func deleteNote(_ note: TodoNote) {
        if let fileName = note.imageFileName {
            try? FileManager.default.removeItem(at: imagesDirectory.appendingPathComponent(fileName))
            imageCache.removeObject(forKey: fileName as NSString)
        }
        notes.removeAll { $0.id == note.id }
        save()
    }

    func delete(at offsets: IndexSet) {
        for index in offsets {
            deleteNote(notes[index])
        }
    }

    func toggleItem(noteID: UUID, itemID: UUID) {
        guard let noteIndex = notes.firstIndex(where: { $0.id == noteID }),
              let itemIndex = notes[noteIndex].items.firstIndex(where: { $0.id == itemID }) else { return }
        notes[noteIndex].items[itemIndex].isDone.toggle()
        notes[noteIndex].updatedAt = Date()
        save()
    }

    // MARK: - Images

    func saveImage(_ image: UIImage) -> String? {
        guard let data = image.jpegData(compressionQuality: 0.85) else { return nil }
        let fileName = "\(UUID().uuidString).jpg"
        let url = imagesDirectory.appendingPathComponent(fileName)
        do {
            try data.write(to: url, options: .atomic)
            imageCache.setObject(image, forKey: fileName as NSString)
            return fileName
        } catch {
            return nil
        }
    }

    func loadImage(fileName: String) -> UIImage? {
        if let cached = imageCache.object(forKey: fileName as NSString) {
            return cached
        }
        let url = imagesDirectory.appendingPathComponent(fileName)
        guard let data = try? Data(contentsOf: url), let image = UIImage(data: data) else { return nil }
        imageCache.setObject(image, forKey: fileName as NSString)
        return image
    }

    func deleteImage(fileName: String) {
        try? FileManager.default.removeItem(at: imagesDirectory.appendingPathComponent(fileName))
        imageCache.removeObject(forKey: fileName as NSString)
    }

    // MARK: - Persistence

    private func load() {
        guard let data = try? Data(contentsOf: fileURL) else {
            notes = []
            return
        }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        notes = (try? decoder.decode([TodoNote].self, from: data)) ?? []
    }

    private func save() {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        guard let data = try? encoder.encode(notes) else { return }
        try? data.write(to: fileURL, options: .atomic)
    }
}
