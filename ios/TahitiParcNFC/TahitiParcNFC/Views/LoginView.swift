import SwiftUI

struct LoginView: View {
    @Environment(AppModel.self) private var model
    @State private var login = ""
    @State private var password = ""
    @FocusState private var field: Int?

    var body: some View {
        ZStack {
            LinearGradient.tpHero.ignoresSafeArea()
            ScrollView {
                VStack(spacing: 28) {
                    BrandMark(size: 60).padding(.top, 60)
                    Text("Gestion du parc de matériel médical en location")
                        .font(.subheadline)
                        .foregroundStyle(.white.opacity(0.8))
                        .multilineTextAlignment(.center)

                    VStack(spacing: 12) {
                        TextField("Identifiant", text: $login)
                            .textContentType(.username)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()
                            .submitLabel(.next)
                            .focused($field, equals: 0)
                            .onSubmit { field = 1 }
                        SecureField("Mot de passe", text: $password)
                            .textContentType(.password)
                            .submitLabel(.go)
                            .focused($field, equals: 1)
                            .onSubmit(submit)
                    }
                    .textFieldStyle(LoginFieldStyle())

                    Button(action: submit) {
                        HStack {
                            if model.busy { ProgressView().tint(.tpHero) }
                            Text("Se connecter").fontWeight(.semibold)
                        }
                        .frame(maxWidth: .infinity, minHeight: 50)
                    }
                    .background(Color.tpBrand, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
                    .foregroundStyle(Color.tpHero)
                    .disabled(login.isEmpty || password.isEmpty || model.busy)

                    VStack(spacing: 6) {
                        Label("Aucune ordonnance n'est stockée en ligne.", systemImage: "lock.shield")
                        Text("Les comptes sont créés par l'administrateur du parc.")
                    }
                    .font(.footnote)
                    .foregroundStyle(.white.opacity(0.75))
                    .multilineTextAlignment(.center)
                }
                .padding(.horizontal, 24)
                .frame(maxWidth: 460)
                .frame(maxWidth: .infinity)
            }
            .scrollDismissesKeyboard(.interactively)
        }
    }

    private func submit() {
        guard !login.isEmpty, !password.isEmpty else { return }
        field = nil
        Task { await model.login(login, password) }
    }
}

struct LoginFieldStyle: TextFieldStyle {
    func _body(configuration: TextField<Self._Label>) -> some View {
        configuration
            .padding(.horizontal, 16)
            .frame(minHeight: 50)
            .background(.white, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
            .foregroundStyle(Color(hex: 0x0D2730))
    }
}

struct PasswordView: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let forced: Bool
    init(forced: Bool) { self.forced = forced }
    @State private var current = ""
    @State private var next = ""
    @State private var confirm = ""

    private var problem: String? {
        if next.isEmpty { return nil }
        if next.count < 10 { return "Au moins 10 caractères." }
        if next.rangeOfCharacter(from: .letters) == nil || next.rangeOfCharacter(from: .decimalDigits) == nil { return "Des lettres et des chiffres." }
        if !confirm.isEmpty && confirm != next { return "Les deux saisies ne correspondent pas." }
        return nil
    }

    var body: some View {
        NavigationStack {
            Form {
                if forced {
                    Section {
                        Text("Bienvenue \(model.me?.name ?? "") ! Choisissez votre mot de passe personnel pour remplacer le mot de passe provisoire.")
                    }
                }
                Section("Mot de passe actuel") {
                    SecureField(forced ? "Mot de passe provisoire" : "Mot de passe actuel", text: $current).textContentType(.password)
                }
                Section {
                    SecureField("Nouveau mot de passe", text: $next).textContentType(.newPassword)
                    SecureField("Confirmer", text: $confirm).textContentType(.newPassword)
                } header: {
                    Text("Nouveau mot de passe")
                } footer: {
                    Text(problem ?? "10 caractères minimum, avec des lettres et des chiffres.")
                        .foregroundStyle(problem == nil ? Color.secondary : Color.tpCrit)
                }
                Section {
                    Button {
                        Task { if await model.changePassword(current: current, next: next), !forced { dismiss() } }
                    } label: {
                        HStack { Spacer(); if model.busy { ProgressView() } else { Text("Enregistrer").bold() }; Spacer() }
                    }
                    .disabled(current.isEmpty || next.isEmpty || confirm != next || problem != nil || model.busy)
                }
                if forced {
                    Section { Button("Se déconnecter", role: .destructive) { Task { await model.logout() } } }
                }
            }
            .navigationTitle("Mot de passe")
            .toolbar { if !forced { ToolbarItem(placement: .cancellationAction) { Button("Annuler") { dismiss() } } } }
        }
    }
}
