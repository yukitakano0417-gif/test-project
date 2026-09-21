import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var store: NoteStore
    @State private var editingNote: TodoNote?
    @State private var isCreatingNote = false
    @State private var searchText = ""

    private let columns = [
        GridItem(.adaptive(minimum: 150, maximum: 220), spacing: 14)
    ]

    private var filteredNotes: [TodoNote] {
        guard !searchText.trimmingCharacters(in: .whitespaces).isEmpty else { return store.notes }
        return store.notes.filter { note in
            note.items.contains { $0.text.localizedCaseInsensitiveContains(searchText) }
        }
    }

    var body: some View {
        NavigationStack {
            Group {
                if store.notes.isEmpty {
                    emptyState
                } else if filteredNotes.isEmpty {
                    noResultsState
                } else {
                    ScrollView {
                        LazyVGrid(columns: columns, spacing: 14) {
                            ForEach(filteredNotes) { note in
                                NoteCardView(note: note) {
                                    editingNote = note
                                }
                                .contextMenu {
                                    Button(role: .destructive) {
                                        withAnimation {
                                            store.deleteNote(note)
                                        }
                                    } label: {
                                        Label("削除", systemImage: "trash")
                                    }
                                }
                                .transition(.scale.combined(with: .opacity))
                            }
                        }
                        .padding(16)
                        .animation(.spring(response: 0.35, dampingFraction: 0.8), value: filteredNotes)
                    }
                }
            }
            .background(Color(uiColor: .systemGroupedBackground))
            .navigationTitle("Todoメモ")
            .searchable(text: $searchText, prompt: Text("メモを検索"))
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        Haptics.tap()
                        isCreatingNote = true
                    } label: {
                        Image(systemName: "plus.circle.fill")
                            .font(.system(.title2))
                    }
                    .accessibilityLabel(Text("新規メモを作成"))
                }
            }
            .sheet(isPresented: $isCreatingNote) {
                NoteEditorView()
            }
            .sheet(item: $editingNote) { note in
                NoteEditorView(note: note)
            }
        }
    }

    private var emptyState: some View {
        VStack(spacing: 12) {
            Image(systemName: "note.text.badge.plus")
                .font(.system(size: 44))
                .foregroundStyle(.secondary)
            Text("まだメモがありません")
                .font(.system(.headline, design: .rounded))
            Text("右上の + をタップして最初のTodoメモを作成しましょう")
                .font(.system(.subheadline, design: .rounded))
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private var noResultsState: some View {
        VStack(spacing: 12) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 36))
                .foregroundStyle(.secondary)
            Text("見つかりませんでした")
                .font(.system(.headline, design: .rounded))
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

#Preview {
    ContentView()
        .environmentObject(NoteStore())
}
