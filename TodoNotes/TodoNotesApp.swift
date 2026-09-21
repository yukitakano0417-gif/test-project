import SwiftUI

@main
struct TodoNotesApp: App {
    @StateObject private var store = NoteStore()
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            #if DEBUG
            if ProcessInfo.processInfo.environment["WIDGET_PREVIEW"] == "1" {
                WidgetPreviewHarness()
                    .environmentObject(store)
            } else {
                ContentView()
                    .environmentObject(store)
            }
            #else
            ContentView()
                .environmentObject(store)
            #endif
        }
        .onChange(of: scenePhase) { newPhase in
            // The widget extension can change notes while this app isn't
            // running; resync our in-memory copy whenever we come back.
            if newPhase == .active {
                store.reload()
            }
        }
    }
}
