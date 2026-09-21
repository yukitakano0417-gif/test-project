import SwiftUI
import PhotosUI
import UIKit

struct NoteEditorView: View {
    @EnvironmentObject private var store: NoteStore
    @Environment(\.dismiss) private var dismiss

    @State private var draft: TodoNote
    @State private var selectedPhoto: PhotosPickerItem?
    @State private var previewImage: UIImage?
    @State private var isShowingDeleteConfirmation = false
    @FocusState private var focusedItemID: UUID?

    private let isNew: Bool

    init(note: TodoNote? = nil) {
        _draft = State(initialValue: note ?? TodoNote())
        isNew = note == nil
    }

    private var canSave: Bool {
        draft.imageFileName != nil ||
            draft.items.contains { !$0.text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    ColorPickerRow(selection: $draft.color)
                        .padding(.horizontal)

                    photoSection

                    VStack(spacing: 0) {
                        ForEach($draft.items) { $item in
                            itemRow(item: $item)
                        }

                        Button {
                            addItem()
                        } label: {
                            Label("項目を追加", systemImage: "plus.circle.fill")
                                .font(.system(.body, design: .rounded))
                        }
                        .padding(.top, 8)
                    }
                    .padding()
                    .background(draft.color.background)
                    .foregroundStyle(draft.color.foreground)
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                    .padding(.horizontal)
                }
                .padding(.vertical)
            }
            .background(Color(uiColor: .systemGroupedBackground))
            .navigationTitle(isNew ? "新規メモ" : "メモを編集")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("キャンセル") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("保存") { save() }
                        .fontWeight(.semibold)
                        .disabled(!canSave)
                }
                if !isNew {
                    ToolbarItem(placement: .bottomBar) {
                        Button(role: .destructive) {
                            isShowingDeleteConfirmation = true
                        } label: {
                            Label("メモを削除", systemImage: "trash")
                        }
                    }
                }
            }
            .onAppear {
                if let fileName = draft.imageFileName {
                    previewImage = store.loadImage(fileName: fileName)
                }
                if draft.items.isEmpty {
                    draft.items = [TodoItem()]
                }
                if isNew {
                    focusedItemID = draft.items.first?.id
                }
            }
            .onChange(of: selectedPhoto) { newValue in
                Task { await loadPhoto(newValue) }
            }
            .confirmationDialog(
                "このメモを削除しますか?",
                isPresented: $isShowingDeleteConfirmation,
                titleVisibility: .visible
            ) {
                Button("削除", role: .destructive) {
                    Haptics.success()
                    store.deleteNote(draft)
                    dismiss()
                }
                Button("キャンセル", role: .cancel) {}
            }
        }
    }

    private func itemRow(item: Binding<TodoItem>) -> some View {
        HStack(spacing: 10) {
            Button {
                Haptics.tap()
                item.wrappedValue.isDone.toggle()
            } label: {
                Image(systemName: item.wrappedValue.isDone ? "checkmark.square.fill" : "square")
                    .font(.system(.title3))
            }
            .buttonStyle(.plain)

            TextField("やることを入力", text: item.text, axis: .vertical)
                .font(.system(.body, design: .rounded))
                .foregroundStyle(item.wrappedValue.isDone ? draft.color.foreground.opacity(0.5) : draft.color.foreground)
                .focused($focusedItemID, equals: item.wrappedValue.id)
                .submitLabel(.next)
                .onSubmit {
                    addItem()
                }

            if draft.items.count > 1 {
                Button {
                    draft.items.removeAll { $0.id == item.wrappedValue.id }
                } label: {
                    Image(systemName: "minus.circle.fill")
                        .font(.system(.body))
                        .opacity(0.6)
                }
                .buttonStyle(.plain)
                .accessibilityLabel(Text("この項目を削除"))
            }
        }
        .padding(.vertical, 6)
    }

    private var photoSection: some View {
        HStack {
            if let previewImage {
                Image(uiImage: previewImage)
                    .resizable()
                    .scaledToFill()
                    .frame(height: 120)
                    .frame(maxWidth: .infinity)
                    .clipped()
                    .clipShape(RoundedRectangle(cornerRadius: 14))
                    .overlay(alignment: .topTrailing) {
                        Button {
                            removePhoto()
                        } label: {
                            Image(systemName: "xmark.circle.fill")
                                .font(.system(.title2))
                                .foregroundStyle(.white, .black.opacity(0.6))
                        }
                        .padding(6)
                        .accessibilityLabel(Text("写真を削除"))
                    }
            } else {
                PhotosPicker(selection: $selectedPhoto, matching: .images) {
                    Label("写真を追加", systemImage: "photo.badge.plus")
                        .font(.system(.body, design: .rounded))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                }
                .buttonStyle(.bordered)
            }
        }
        .padding(.horizontal)
    }

    private func addItem() {
        let newItem = TodoItem()
        draft.items.append(newItem)
        focusedItemID = newItem.id
    }

    private func removePhoto() {
        if let fileName = draft.imageFileName {
            store.deleteImage(fileName: fileName)
        }
        draft.imageFileName = nil
        previewImage = nil
        selectedPhoto = nil
    }

    private func loadPhoto(_ item: PhotosPickerItem?) async {
        guard let item, let data = try? await item.loadTransferable(type: Data.self),
              let image = UIImage(data: data) else { return }
        if let oldFileName = draft.imageFileName {
            store.deleteImage(fileName: oldFileName)
        }
        if let fileName = store.saveImage(image) {
            draft.imageFileName = fileName
            previewImage = image
        }
    }

    private func save() {
        draft.items.removeAll { $0.text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
        if draft.items.isEmpty {
            draft.items = [TodoItem()]
        }
        if isNew {
            store.addNote(draft)
        } else {
            store.updateNote(draft)
        }
        dismiss()
    }
}
