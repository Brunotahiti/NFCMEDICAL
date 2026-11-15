import SwiftUI

@main
struct TahitiParcNFCApp: App {
    @State private var model = AppModel()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(model)
                .tint(.tpAccent)
        }
    }
}

/// Aiguillage : connexion, changement de mot de passe, puis application.
struct RootView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        Group {
            switch model.phase {
            case .loading:
                SplashView()
            case .login:
                LoginView()
            case .changePassword(let forced):
                PasswordView(forced: forced)
            case .ready:
                MainTabs()
            }
        }
        .task { await model.start() }
        .overlay(alignment: .top) { ToastView(text: model.toast) }
        .alert("Une erreur est survenue", isPresented: Binding(get: { model.errorMessage != nil }, set: { if !$0 { model.errorMessage = nil } })) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(model.errorMessage ?? "")
        }
    }
}

struct SplashView: View {
    var body: some View {
        ZStack {
            LinearGradient.tpHero.ignoresSafeArea()
            VStack(spacing: 16) {
                BrandMark(size: 72)
                ProgressView().tint(.white)
            }
        }
    }
}

struct MainTabs: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        TabView {
            DashboardView()
                .tabItem { Label("Accueil", systemImage: "house") }
            if model.isStaff {
                ParcView()
                    .tabItem { Label("Parc", systemImage: "square.grid.2x2") }
            } else {
                LocationsView()
                    .tabItem { Label("Locations", systemImage: "calendar") }
            }
            ScanView()
                .tabItem { Label("Scanner", systemImage: "wave.3.right") }
            if model.isStaff {
                LocationsView()
                    .tabItem { Label("Locations", systemImage: "calendar") }
            } else {
                BillingView()
                    .tabItem { Label("Facturation", systemImage: "doc.text") }
            }
            MoreView()
                .tabItem { Label("Plus", systemImage: "ellipsis.circle") }
        }
    }
}
