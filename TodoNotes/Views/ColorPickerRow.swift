import SwiftUI

struct ColorPickerRow: View {
    @Binding var selection: NoteColor

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(NoteColor.allCases) { color in
                    Circle()
                        .fill(color.background)
                        .frame(width: 32, height: 32)
                        .overlay(
                            Image(systemName: "checkmark")
                                .font(.system(size: 13, weight: .bold))
                                .foregroundStyle(color.foreground)
                                .opacity(selection == color ? 1 : 0)
                        )
                        .overlay(
                            Circle()
                                .stroke(Color.primary, lineWidth: selection == color ? 2 : 0)
                                .padding(-3)
                        )
                        .onTapGesture {
                            Haptics.tap()
                            selection = color
                        }
                        .accessibilityLabel(Text(color.displayName))
                        .accessibilityAddTraits(selection == color ? [.isSelected] : [])
                }
            }
            .padding(.vertical, 4)
        }
    }
}
