import SwiftUI

enum NoteColor: String, Codable, CaseIterable, Identifiable, Equatable {
    case yellow, red, orange, pink, purple, blue, teal, green, cream, charcoal

    var id: String { rawValue }

    var background: Color {
        switch self {
        case .yellow: return Color(red: 0.98, green: 0.82, blue: 0.22)
        // Darkened from the original (0.85, 0.29, 0.24) so white text clears
        // the WCAG AA 4.5:1 contrast threshold (was ~4.2:1).
        case .red: return Color(red: 0.80, green: 0.24, blue: 0.20)
        case .orange: return Color(red: 0.93, green: 0.55, blue: 0.20)
        case .pink: return Color(red: 0.95, green: 0.55, blue: 0.62)
        case .purple: return Color(red: 0.47, green: 0.38, blue: 0.78)
        // Darkened from the original (0.28, 0.45, 0.82) for a safer contrast
        // margin with white text (was ~4.5:1, right at the threshold).
        case .blue: return Color(red: 0.22, green: 0.40, blue: 0.75)
        case .teal: return Color(red: 0.22, green: 0.58, blue: 0.55)
        case .green: return Color(red: 0.18, green: 0.35, blue: 0.24)
        case .cream: return Color(red: 0.94, green: 0.89, blue: 0.78)
        case .charcoal: return Color(red: 0.16, green: 0.16, blue: 0.17)
        }
    }

    var foreground: Color {
        switch self {
        // Pastel/mid-tone backgrounds where white text fails WCAG AA
        // (pink was ~2.3:1, teal was ~3.6:1) — dark text reads correctly instead.
        case .cream, .yellow, .orange, .pink, .teal:
            return Color.black.opacity(0.85)
        default:
            return Color.white
        }
    }

    var displayName: String {
        switch self {
        case .yellow: return "イエロー"
        case .red: return "レッド"
        case .orange: return "オレンジ"
        case .pink: return "ピンク"
        case .purple: return "パープル"
        case .blue: return "ブルー"
        case .teal: return "ティール"
        case .green: return "グリーン"
        case .cream: return "クリーム"
        case .charcoal: return "チャコール"
        }
    }
}
