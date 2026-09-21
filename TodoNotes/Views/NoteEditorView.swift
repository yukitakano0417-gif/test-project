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
    @State private var reminderTarget: ReminderTarget?
    @FocusState private var focusedItemID: UUID?

    private struct ReminderTarget: Identifiable {
        let id: UUID
    }

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
            .sheet(item: $reminderTarget) { target in
                if let index = draft.items.firstIndex(where: { $0.id == target.id }) {
                    ReminderSheet(dueDate: $draft.items[index].dueDate)
                }
            }
        }
    }

    private func itemRow(item: Binding<TodoItem>) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(spacing: 10) {
                Button {
                    Haptics.tap()
                    item.wrappedValue.isDone.toggle()
                } label: {
                    Image(systemName: item.wrappedValue.isDone ? "checkmark.square.fill" : "square")
                        .font(.system(.title3))
                }
                .buttonStyle(.plain)

                TextField("やることを入力", text: item.text)
                    .font(.system(.body, design: .rounded))
                    .foregroundStyle(item.wrappedValue.isDone ? draft.color.foreground.opacity(0.5) : draft.color.foreground)
                    .focused($focusedItemID, equals: item.wrappedValue.id)
                    .submitLabel(.next)
                    .onSubmit {
                        addItem()
                    }

                Button {
                    reminderTarget = ReminderTarget(id: item.wrappedValue.id)
                } label: {
                    Image(systemName: item.wrappedValue.dueDate != nil ? "bell.fill" : "bell")
                        .font(.system(.body))
                        .opacity(item.wrappedValue.dueDate != nil ? 1 : 0.4)
                }
                .buttonStyle(.plain)
                .accessibilityLabel(Text(item.wrappedValue.dueDate != nil ? "リマインダーを編集" : "リマインダーを設定"))

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

            if let dueDate = item.wrappedValue.dueDate {
                let isOverdue = dueDate < Date() && !item.wrappedValue.isDone
                Label(dueDate.formatted(date: .abbreviated, time: .shortened), systemImage: "clock")
                    .font(.system(.caption2, design: .rounded))
                    .foregroundStyle(isOverdue ? Color.red : draft.color.foreground.opacity(0.7))
                    .padding(.leading, 32)
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

private struct ReminderSheet: View {
    @Binding var dueDate: Date?
    @Environment(\.dismiss) private var dismiss
    @State private var selection: Date

    init(dueDate: Binding<Date?>) {
        self._dueDate = dueDate
        self._selection = State(initialValue: dueDate.wrappedValue ?? Date().addingTimeInterval(3600))
    }

    var body: some View {
        NavigationStack {
            DatePicker(
                "日時",
                selection: $selection,
                in: Date()...,
                displayedComponents: [.date, .hourAndMinute]
            )
            .datePickerStyle(.graphical)
            .padding()
            .navigationTitle("リマインダー")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("キャンセル") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("設定") {
                        dueDate = selection
                        dismiss()
                    }
                    .fontWeight(.semibold)
                }
                if dueDate != nil {
                    ToolbarItem(placement: .bottomBar) {
                        Button("リマインダーを削除", role: .destructive) {
                            dueDate = nil
                            dismiss()
                        }
                    }
                }
            }
            .onAppear {
                NotificationManager.requestAuthorizationIfNeeded()
            }
        }
    }
}
