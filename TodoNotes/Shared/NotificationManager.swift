import Foundation
import UserNotifications

/// Schedules the local notifications that give this app a Trigger beyond
/// "the user happens to glance at the widget." Lives in Shared/ because
/// NotesRepository.save(_:) calls resync(with:) after every write — from
/// either the app or the widget's ToggleTodoItemIntent — so a reminder
/// set in the app and one completed from the widget both stay correct
/// without either target having to remember to call this separately.
enum NotificationManager {
    static func requestAuthorizationIfNeeded() {
        UNUserNotificationCenter.current().getNotificationSettings { settings in
            guard settings.authorizationStatus == .notDetermined else { return }
            UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { _, _ in }
        }
    }

    /// Full resync rather than incremental diffing: at this app's scale
    /// (a personal todo list, not thousands of items) removing and
    /// re-adding every pending reminder on each save is simple, cheap,
    /// and can't drift out of sync with what's actually in `notes`.
    static func resync(with notes: [TodoNote]) {
        let center = UNUserNotificationCenter.current()
        center.removeAllPendingNotificationRequests()
        for note in notes {
            for item in note.items where !item.isDone {
                guard let dueDate = item.dueDate, dueDate > Date() else { continue }
                schedule(itemID: item.id, text: item.text, dueDate: dueDate)
            }
        }
    }

    private static func schedule(itemID: UUID, text: String, dueDate: Date) {
        let content = UNMutableNotificationContent()
        content.title = "Todoメモ"
        content.body = text
        content.sound = .default

        let components = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute], from: dueDate)
        let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: false)
        let request = UNNotificationRequest(identifier: itemID.uuidString, content: content, trigger: trigger)
        UNUserNotificationCenter.current().add(request)
    }
}
