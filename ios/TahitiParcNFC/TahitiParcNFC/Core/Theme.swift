import SwiftUI

extension Color {
    init(hex: UInt32) {
        self.init(.sRGB, red: Double((hex >> 16) & 0xFF) / 255, green: Double((hex >> 8) & 0xFF) / 255, blue: Double(hex & 0xFF) / 255)
    }
    /// Couleur qui s'adapte au mode clair ou sombre.
    init(light: UInt32, dark: UInt32) {
        self.init(UIColor { $0.userInterfaceStyle == .dark ? UIColor(Color(hex: dark)) : UIColor(Color(hex: light)) })
    }

    static let tpAccent = Color(light: 0x0A7C88, dark: 0x5FC9D2)
    static let tpBrand = Color(hex: 0x62CFC4)
    static let tpHero = Color(hex: 0x0B5361)
    static let tpHero2 = Color(hex: 0x0E8F93)
    static let tpInk = Color(light: 0x0D2730, dark: 0xE6F1F3)
    static let tpMuted = Color(light: 0x5B7078, dark: 0x9DB3BA)
    static let tpBackground = Color(light: 0xEDF6F8, dark: 0x061A20)
    static let tpSurface = Color(light: 0xFFFFFF, dark: 0x0F2A32)
    static let tpOK = Color(light: 0x1A7F54, dark: 0x5FD6A0)
    static let tpWarn = Color(light: 0xA65F00, dark: 0xF5BE6B)
    static let tpCrit = Color(light: 0xB8352B, dark: 0xFF9288)
    static let tpInfo = Color(light: 0x3154C4, dark: 0x7FA0FF)
}

extension LinearGradient {
    static let tpHero = LinearGradient(colors: [.tpHero, .tpHero2], startPoint: .topLeading, endPoint: .bottomTrailing)
}

extension EquipmentState {
    var color: Color {
        switch self {
        case .loc: return .tpInfo
        case .dispo: return .tpOK
        case .desinf: return .tpWarn
        case .maint: return .tpCrit
        }
    }
}

extension AlertLevel {
    var color: Color {
        switch self {
        case .crit: return .tpCrit
        case .warn: return .tpWarn
        case .info: return .tpInfo
        }
    }
}

/// Logo : « Tahiti Parc » sur fond dégradé, avec l'onde NFC.
struct BrandMark: View {
    var size: CGFloat = 56
    var body: some View {
        VStack(spacing: size * 0.18) {
            ZStack {
                RoundedRectangle(cornerRadius: size * 0.28, style: .continuous)
                    .fill(Color.white.opacity(0.14))
                    .frame(width: size * 1.3, height: size * 1.3)
                Image(systemName: "wave.3.right")
                    .font(.system(size: size * 0.6, weight: .semibold))
                    .foregroundStyle(Color.tpBrand)
            }
            HStack(spacing: 0) {
                Text("Tahiti ").foregroundStyle(Color.tpBrand)
                Text("Parc NFC").foregroundStyle(.white)
            }
            .font(.system(size: size * 0.42, weight: .bold, design: .rounded))
        }
    }
}

struct Card<Content: View>: View {
    @ViewBuilder var content: Content
    var body: some View {
        VStack(alignment: .leading, spacing: 10) { content }
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.tpSurface, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
            .shadow(color: .black.opacity(0.06), radius: 12, y: 4)
    }
}

struct StatusBadge: View {
    let state: EquipmentState
    var body: some View {
        Label(state.label, systemImage: state.symbol)
            .font(.caption.weight(.semibold))
            .padding(.horizontal, 8).padding(.vertical, 4)
            .foregroundStyle(state.color)
            .background(state.color.opacity(0.14), in: Capsule())
    }
}

struct Tag: View {
    let text: String
    let color: Color
    var body: some View {
        Text(text)
            .font(.caption2.weight(.bold))
            .padding(.horizontal, 7).padding(.vertical, 3)
            .foregroundStyle(color)
            .background(color.opacity(0.14), in: Capsule())
    }
}

/// Photo du catalogue (servie par le site).
struct EquipmentThumb: View {
    let photo: String?
    var size: CGFloat = 56
    var body: some View {
        AsyncImage(url: photo.flatMap(Server.photo)) { image in
            image.resizable().scaledToFill()
        } placeholder: {
            Image(systemName: "bed.double").foregroundStyle(Color.tpMuted)
        }
        .frame(width: size, height: size)
        .background(Color.tpBackground)
        .clipShape(RoundedRectangle(cornerRadius: size * 0.22, style: .continuous))
    }
}

struct ToastView: View {
    let text: String?
    var body: some View {
        if let text {
            Text(text)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.white)
                .padding(.horizontal, 16).padding(.vertical, 10)
                .background(Color.tpHero, in: Capsule())
                .shadow(radius: 8)
                .padding(.top, 8)
                .transition(.move(edge: .top).combined(with: .opacity))
        }
    }
}
