import MapKit
import SwiftUI

struct EquipmentDetailView: View {
    @Environment(AppModel.self) private var model
    let id: Int
    init(id: Int) { self.id = id }
    @State private var detail: EquipmentDetail?
    @State private var sheet: DetailSheet?
    @State private var confirm: ConfirmAction?
    @State private var viewedPhoto: PhotoInfo?

    enum DetailSheet: String, Identifiable {
        case rent, prescription, photo, prescriptionFile
        var id: String { rawValue }
    }

    struct ConfirmAction: Identifiable {
        let id = UUID()
        let title: String
        let message: String
        let action: String
        let toast: String
        var destructive = false
    }

    var body: some View {
        Group {
            if let e = model.equipment(id: id) {
                content(e)
            } else {
                ContentUnavailableView("Équipement introuvable", systemImage: "questionmark.square.dashed",
                                       description: Text("Il n'est plus rattaché à votre compte."))
            }
        }
        .background(Color.tpBackground)
        .navigationBarTitleDisplayMode(.inline)
    }

    @ViewBuilder
    private func content(_ e: Equipment) -> some View {
        ScrollView {
            VStack(spacing: 14) {
                header(e)
                if e.state == .loc {
                    rentalCard(e)
                    PrescriptionCard(e: e, onVerify: { sheet = .prescription }, onFile: { sheet = .prescriptionFile })
                }
                if model.isStaff { actionsCard(e) }
                scanCard(e)
                photosCard(e)
                if model.isStaff {
                    profitCard(e)
                    nfcCard(e)
                }
                historyCard(e)
            }
            .padding(16)
        }
        .navigationTitle(e.ref)
        .task(id: e.events.first?.id) { detail = await model.detail(e) }
        .refreshable { await model.refresh(); detail = await model.detail(e) }
        .sheet(item: $sheet) { s in
            switch s {
            case .rent: NewRentalView(equipment: e)
            case .prescription: PrescriptionSheet(e: e)
            case .photo: PhotoCaptureView(e: e)
            case .prescriptionFile: PrescriptionFileView(e: e)
            }
        }
        .sheet(item: $viewedPhoto) { p in PhotoViewer(photo: p, canDelete: model.isStaff) }
        .confirmationDialog(confirm?.title ?? "", isPresented: Binding(get: { confirm != nil }, set: { if !$0 { confirm = nil } }), titleVisibility: .visible, presenting: confirm) { c in
            Button(c.title, role: c.destructive ? .destructive : nil) { Task { await model.action(e, c.action, message: c.toast) } }
            Button("Annuler", role: .cancel) {}
        } message: { c in Text(c.message) }
    }

    // MARK: En-tête

    private func header(_ e: Equipment) -> some View {
        Card {
            HStack(spacing: 14) {
                EquipmentThumb(photo: e.photo, size: 84)
                VStack(alignment: .leading, spacing: 5) {
                    Text(e.name).font(.title3.bold()).foregroundStyle(Color.tpInk)
                    Text(e.brand + " · " + e.kind).font(.subheadline).foregroundStyle(Color.tpMuted)
                    Text(e.ref).font(.system(.caption, design: .monospaced).weight(.semibold)).foregroundStyle(Color.tpAccent)
                    StatusBadge(state: e.state)
                }
            }
            Divider()
            row("Tarif", Fmt.xpf(e.weekPrice) + " / semaine")
            if e.state != .loc { row("Depuis le", Fmt.date(e.since)) }
            if let c = model.daysToCheck(e) {
                row("Prochain contrôle", Fmt.date(e.nextCheck), color: c < 0 ? Color.tpCrit : c <= 30 ? Color.tpWarn : nil)
            }
        }
    }

    // MARK: Location

    private func rentalCard(_ e: Equipment) -> some View {
        Card {
            Label("Location en cours", systemImage: "calendar").font(.headline)
            if let p = model.patient(e.patientId) {
                HStack(spacing: 12) {
                    Text(Fmt.initials(p.name))
                        .font(.subheadline.bold()).foregroundStyle(.white)
                        .frame(width: 42, height: 42).background(Color.tpInfo, in: Circle())
                    VStack(alignment: .leading, spacing: 2) {
                        Text(p.name).font(.subheadline.weight(.semibold))
                        Text([p.address, p.commune].compactMap { $0 }.filter { !$0.isEmpty }.joined(separator: ", "))
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    Spacer()
                    if let phone = p.phone, !phone.isEmpty, let url = URL(string: "tel:" + phone.filter { $0.isNumber || $0 == "+" }) {
                        Link(destination: url) { Image(systemName: "phone.fill").padding(10).background(Color.tpOK.opacity(0.15), in: Circle()) }
                            .foregroundStyle(Color.tpOK)
                    }
                }
            }
            if let ph = model.pharmacy(e.pharmacyId) { row("Pharmacie", ph.name + " (" + ph.commune + ")") }
            row("Début", Fmt.date(e.since) + (model.daysRented(e).map { " · depuis \(Fmt.duration($0))" } ?? ""))
            if let left = model.daysLeft(e) {
                row("Fin prévue", Fmt.date(e.plannedEnd) + " · " + (left < 0 ? "retard de \(Fmt.duration(-left))" : left == 0 ? "aujourd'hui" : "reste \(Fmt.duration(left))"),
                    color: left < 0 ? Color.tpCrit : left <= 3 ? Color.tpWarn : nil)
                let elapsed = Double(max(model.daysRented(e) ?? 0, 0)), total = elapsed + Double(max(left, 0))
                ProgressView(value: min(elapsed, max(total, 1)), total: max(total, 1)).tint(left < 0 ? Color.tpCrit : Color.tpAccent)
            }
        }
    }

    // MARK: Actions

    private func actionsCard(_ e: Equipment) -> some View {
        Card {
            Label("Actions", systemImage: "bolt").font(.headline)
            switch e.state {
            case .loc:
                Menu {
                    ForEach([7, 14, 28, 90], id: \.self) { d in
                        Button(d == 90 ? "3 mois" : Fmt.duration(d)) { Task { await model.extend(e, days: d) } }
                    }
                } label: { actionLabel("Prolonger la location", "calendar.badge.plus", .tpAccent) }
                actionButton("Retour du matériel", "arrow.uturn.backward", .tpInfo) {
                    confirm = ConfirmAction(title: "Enregistrer le retour", message: "La location se termine aujourd'hui et l'équipement passe en désinfection.", action: "return", toast: "Retour enregistré")
                }
            case .dispo:
                actionButton("Mettre en location", "plus.circle.fill", .tpAccent) { sheet = .rent }
            case .desinf:
                actionButton("Désinfection validée", "checkmark.seal", .tpOK) {
                    confirm = ConfirmAction(title: "Désinfection validée", message: "L'équipement est remis en stock, disponible à la location.", action: "clean", toast: "Remis en stock")
                }
            case .maint:
                actionButton("Maintenance clôturée", "wrench.and.screwdriver", .tpOK) {
                    confirm = ConfirmAction(title: "Clôturer la maintenance", message: "L'équipement est contrôlé conforme et redevient disponible.", action: "repair", toast: "Maintenance clôturée")
                }
            }
            if e.state != .maint, let c = model.daysToCheck(e), c <= 30 {
                actionButton("Contrôle effectué", "checkmark.shield", .tpOK) {
                    confirm = ConfirmAction(title: "Contrôle effectué", message: "Le contrôle de sécurité est conforme : prochain contrôle dans un an.", action: "check", toast: "Contrôle enregistré")
                }
            }
            if e.state != .maint {
                actionButton("Signaler une panne", "exclamationmark.triangle", .tpCrit) {
                    confirm = ConfirmAction(title: "Signaler une panne", message: e.state == .loc ? "La location en cours sera close et l'équipement envoyé à l'atelier." : "L'équipement part à l'atelier.", action: "fault", toast: "Panne signalée", destructive: true)
                }
            }
        }
    }

    private func actionButton(_ title: String, _ icon: String, _ color: Color, _ action: @escaping () -> Void) -> some View {
        Button(action: action) { actionLabel(title, icon, color) }.buttonStyle(.plain).disabled(model.busy)
    }

    private func actionLabel(_ title: String, _ icon: String, _ color: Color) -> some View {
        HStack {
            Image(systemName: icon).frame(width: 24)
            Text(title).fontWeight(.semibold)
            Spacer()
            Image(systemName: "chevron.right").font(.caption).foregroundStyle(.tertiary)
        }
        .foregroundStyle(color)
        .padding(12)
        .background(color.opacity(0.1), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }

    // MARK: Passages et position

    private func scanCard(_ e: Equipment) -> some View {
        Card {
            Label("Position", systemImage: "mappin.and.ellipse").font(.headline)
            if let s = e.lastScan, let lat = s.lat, let lon = s.lon {
                let coord = CLLocationCoordinate2D(latitude: lat, longitude: lon)
                Map(initialPosition: .region(MKCoordinateRegion(center: coord, latitudinalMeters: 600, longitudinalMeters: 600))) {
                    Marker(e.ref, systemImage: "wave.3.right", coordinate: coord).tint(Color.tpAccent)
                }
                .frame(height: 180)
                .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                Text("Dernier scan le \(Fmt.dateTime(s.at)) par \(s.by)" + (s.accuracy.map { String(format: " (±%.0f m)", $0) } ?? ""))
                    .font(.caption).foregroundStyle(.secondary)
                Button {
                    let item = MKMapItem(placemark: MKPlacemark(coordinate: coord))
                    item.name = e.name + " · " + e.ref
                    item.openInMaps()
                } label: { Label("Itinéraire dans Plans", systemImage: "arrow.triangle.turn.up.right.diamond") }
                    .font(.subheadline)
            } else if let s = e.lastScan {
                Text("Dernier scan le \(Fmt.dateTime(s.at)) par \(s.by), sans position.").font(.caption).foregroundStyle(.secondary)
            } else {
                Text("Aucun scan enregistré.").font(.subheadline).foregroundStyle(.secondary)
            }
            Button {
                Task {
                    let fix = await LocationService.shared.current()
                    await model.recordScan(e, source: "saisie", location: fix)
                }
            } label: { actionLabel("Enregistrer ma position ici", "location.fill", .tpAccent) }
                .buttonStyle(.plain)
                .disabled(model.busy)
        }
    }

    // MARK: Photos

    private func photosCard(_ e: Equipment) -> some View {
        Card {
            HStack {
                Label("Photos horodatées", systemImage: "camera").font(.headline)
                Spacer()
                Button { sheet = .photo } label: { Label("Prendre", systemImage: "camera.fill").font(.subheadline.weight(.semibold)) }
            }
            let photos = detail?.photos ?? e.photos ?? []
            if photos.isEmpty {
                Text("Aucune photo. Photographiez le matériel à la livraison, au retour ou en cas de panne.").font(.caption).foregroundStyle(.secondary)
            } else {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 10) {
                        ForEach(photos) { p in
                            Button { viewedPhoto = p } label: {
                                VStack(alignment: .leading, spacing: 4) {
                                    AuthImage(url: Server.userPhoto(p.id))
                                        .frame(width: 120, height: 90)
                                        .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                                    Text(PhotoKind(rawValue: p.kind)?.label ?? p.kind).font(.caption2.weight(.semibold))
                                    Text(Fmt.dateTime(p.at)).font(.caption2).foregroundStyle(.secondary)
                                }
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
            }
        }
    }

    // MARK: Rentabilité

    private func profitCard(_ e: Equipment) -> some View {
        Card {
            Label("Rentabilité", systemImage: "chart.line.uptrend.xyaxis").font(.headline)
            let days = (e.rentedDays ?? 0) + (e.state == .loc ? max(model.daysRented(e) ?? 0, 0) : 0)
            let revenue = Int((Double(e.weekPrice) * Double(days) / 7).rounded())
            let buy = e.buyPrice ?? 0
            row("Prix d'achat", buy > 0 ? Fmt.xpf(buy) + (e.buyEstimated == true ? " (estimé)" : "") : "—")
            row("Jours loués", "\(days)")
            row("Chiffre d'affaires", Fmt.xpf(revenue))
            if buy > 0 {
                let ratio = Double(revenue) / Double(buy)
                ProgressView(value: min(ratio, 1)).tint(ratio >= 1 ? Color.tpOK : Color.tpAccent)
                Text(ratio >= 1 ? "Amorti : \(Int(ratio * 100)) % du prix d'achat" : "Amorti à \(Int(ratio * 100)) %")
                    .font(.caption.weight(.semibold)).foregroundStyle(ratio >= 1 ? Color.tpOK : Color.tpMuted)
            }
        }
    }

    // MARK: Puce NFC

    private func nfcCard(_ e: Equipment) -> some View {
        Card {
            Label("Puce NFC", systemImage: "wave.3.right").font(.headline)
            let link = (e.link ?? "").isEmpty ? nil : e.link
            row("Lien", link ?? "Aucune puce associée")
            Button {
                Task {
                    let target = link ?? ((model.state?.linkBase ?? Server.site) + e.ref)
                    guard let url = URL(string: target) else { return }
                    do {
                        try await NFCService.shared.write(url)
                        if link == nil { _ = await model.setLink(e, link: target) } else { model.show("Puce programmée") }
                    } catch is CancellationError {} catch { model.errorMessage = error.localizedDescription }
                }
            } label: { actionLabel("Programmer une puce vierge", "square.and.pencil", .tpAccent) }
                .buttonStyle(.plain)
            Button {
                Task {
                    do {
                        let text = try await NFCService.shared.read()
                        _ = await model.setLink(e, link: text)
                    } catch is CancellationError {} catch { model.errorMessage = error.localizedDescription }
                }
            } label: { actionLabel("Associer une puce déjà programmée", "link", .tpInfo) }
                .buttonStyle(.plain)
            if link != nil {
                Button(role: .destructive) { Task { _ = await model.setLink(e, link: "") } } label: {
                    actionLabel("Retirer la puce", "xmark.circle", .tpCrit)
                }.buttonStyle(.plain)
            }
        }
    }

    // MARK: Historique

    private func historyCard(_ e: Equipment) -> some View {
        Card {
            Label("Historique", systemImage: "clock.arrow.circlepath").font(.headline)
            let events = detail?.events ?? e.events
            if events.isEmpty { Text("Aucun événement.").font(.subheadline).foregroundStyle(.secondary) }
            ForEach(events) { ev in
                HStack(alignment: .top, spacing: 10) {
                    Image(systemName: ev.photo != nil ? "camera.fill" : "circle.fill")
                        .font(.system(size: ev.photo != nil ? 12 : 7))
                        .foregroundStyle(Color.tpAccent)
                        .frame(width: 16, height: 18)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(ev.text).font(.subheadline)
                        Text(Fmt.dateTime(ev.at) + (ev.by.isEmpty ? "" : " · " + ev.by)).font(.caption).foregroundStyle(.secondary)
                    }
                    Spacer(minLength: 0)
                    if let pid = ev.photo {
                        Button { viewedPhoto = (detail?.photos ?? e.photos ?? []).first { $0.id == pid } } label: {
                            AuthImage(url: Server.userPhoto(pid)).frame(width: 44, height: 44).clipShape(RoundedRectangle(cornerRadius: 8))
                        }.buttonStyle(.plain)
                    }
                }
            }
            if let scans = detail?.scans, !scans.isEmpty {
                Divider()
                Text("Derniers scans").font(.subheadline.weight(.semibold))
                ForEach(Array(scans.prefix(10).enumerated()), id: \.offset) { _, s in
                    Text("\(Fmt.dateTime(s.at)) · \(s.userName ?? "") · \(s.source == "nfc" ? "puce NFC" : s.source)" + (s.lat != nil ? " · position" : ""))
                        .font(.caption).foregroundStyle(.secondary)
                }
            }
        }
    }

    private func row(_ label: String, _ value: String, color: Color? = nil) -> some View {
        HStack(alignment: .firstTextBaseline) {
            Text(label).font(.subheadline).foregroundStyle(Color.tpMuted)
            Spacer(minLength: 12)
            Text(value).font(.subheadline.weight(.medium)).foregroundStyle(color ?? Color.tpInk).multilineTextAlignment(.trailing)
        }
    }
}

/// Image protégée : chargée avec le cookie de session.
struct AuthImage: View {
    let url: URL?
    @State private var image: UIImage?

    var body: some View {
        ZStack {
            Color.tpBackground
            if let image { Image(uiImage: image).resizable().scaledToFill() } else { ProgressView() }
        }
        .clipped()
        .task(id: url) {
            guard let url else { return }
            if let result = try? await APIClient.shared.session.data(from: url), let img = UIImage(data: result.0) { image = img }
        }
    }
}

struct PhotoViewer: View {
    @Environment(AppModel.self) private var model
    @Environment(\.dismiss) private var dismiss
    let photo: PhotoInfo
    let canDelete: Bool

    var body: some View {
        NavigationStack {
            VStack(spacing: 12) {
                AuthImage(url: Server.userPhoto(photo.id))
                    .aspectRatio(4 / 3, contentMode: .fit)
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                Text((PhotoKind(rawValue: photo.kind)?.label ?? photo.kind) + " · " + Fmt.dateTime(photo.at) + " · " + photo.by)
                    .font(.subheadline)
                if let lat = photo.lat, let lon = photo.lon {
                    Text(String(format: "Position : %.5f, %.5f", lat, lon)).font(.caption).foregroundStyle(.secondary)
                }
                Spacer()
            }
            .padding()
            .navigationTitle("Photo")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) { Button("Fermer") { dismiss() } }
                if canDelete {
                    ToolbarItem(placement: .destructiveAction) {
                        Button(role: .destructive) { Task { await model.deletePhoto(photo.id); dismiss() } } label: { Image(systemName: "trash") }
                    }
                }
            }
        }
    }
}
