import Foundation
import UIKit
import WidgetKit

@MainActor
final class NoteStore: ObservableObject {
    @Published private(set) var notes: [TodoNote] = []

    private let imageCache = NSCache<NSString, UIImage>()

    init() {
        try? FileManager.default.createDirectory(at: NotesRepository.imagesDirectory, withIntermediateDirectories: true)
        notes = NotesRepository.load()

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
                TodoItem(text: "植物に水やり", isDone: true)
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
            try? FileManager.default.removeItem(at: NotesRepository.imagesDirectory.appendingPathComponent(fileName))
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
        let resized = image.resizedIfNeeded(maxDimension: 1600)
        guard let data = resized.jpegData(compressionQuality: 0.8) else { return nil }
        let fileName = "\(UUID().uuidString).jpg"
        let url = NotesRepository.imagesDirectory.appendingPathComponent(fileName)
        do {
            try data.write(to: url, options: .atomic)
            imageCache.setObject(resized, forKey: fileName as NSString)
            return fileName
        } catch {
            return nil
        }
    }

    func loadImage(fileName: String) -> UIImage? {
        if let cached = imageCache.object(forKey: fileName as NSString) {
            return cached
        }
        let url = NotesRepository.imagesDirectory.appendingPathComponent(fileName)
        guard let data = try? Data(contentsOf: url), let image = UIImage(data: data) else { return nil }
        imageCache.setObject(image, forKey: fileName as NSString)
        return image
    }

    func deleteImage(fileName: String) {
        try? FileManager.default.removeItem(at: NotesRepository.imagesDirectory.appendingPathComponent(fileName))
        imageCache.removeObject(forKey: fileName as NSString)
    }

    // MARK: - Persistence

    /// Re-reads from disk. The widget extension (and its
    /// `ToggleTodoItemIntent`) runs in a separate process, so when it
    /// changes a note while this app isn't running, our in-memory `notes`
    /// goes stale until we reload — call this when the app returns to
    /// the foreground.
    func reload() {
        notes = NotesRepository.load()
    }

    private func save() {
        NotesRepository.save(notes)
        WidgetCenter.shared.reloadTimelines(ofKind: WidgetKind.todoNotes)
    }
}

private extension UIImage {
    /// Downscales images from the photo library (often 4000px+) before we
    /// persist them, so a single attached photo doesn't cost several MB.
    func resizedIfNeeded(maxDimension: CGFloat) -> UIImage {
        let largestSide = max(size.width, size.height)
        guard largestSide > maxDimension else { return self }
        let scale = maxDimension / largestSide
        let newSize = CGSize(width: size.width * scale, height: size.height * scale)
        let renderer = UIGraphicsImageRenderer(size: newSize)
        return renderer.image { _ in
            draw(in: CGRect(origin: .zero, size: newSize))
        }
    }
}
