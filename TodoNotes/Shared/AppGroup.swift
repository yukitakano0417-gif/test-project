import Foundation

/// The App Group shared between TodoNotes and TodoNotesWidget so both
/// targets read/write the same notes file. Must match the identifier
/// registered in both targets' entitlements files and in your Apple
/// Developer account when you set up your own Team/Bundle ID.
enum AppGroup {
    static let identifier = "group.com.yukitakano.todonotes"
}
