import MapKit
import SwiftUI

struct MapPin: Identifiable {
    let id: String
    let title: String
    let subtitle: String
    let coordinate: CLLocationCoordinate2D
}

/// Carte Apple Plans des lieux où se trouve le matériel, zoomable jusqu'à l'adresse.
struct MapScreen: View {
    let pins: [MapPin]
    let focus: String?

    @Environment(\.dismiss) private var dismiss
    @State private var position: MapCameraPosition = .automatic
    @State private var selected: String?

    var body: some View {
        NavigationStack {
            Map(position: $position, selection: $selected) {
                ForEach(pins) { pin in
                    Marker(pin.title,
                           systemImage: pin.id == "depot" ? "shippingbox.fill" : "cross.case.fill",
                           coordinate: pin.coordinate)
                        .tint(.teal)
                        .tag(pin.id)
                }
            }
            .mapControls {
                MapCompass()
                MapScaleView()
            }
            .safeAreaInset(edge: .bottom) {
                if let pin = pins.first(where: { $0.id == selected }) {
                    placeCard(pin)
                }
            }
            .navigationTitle("Plan du matériel")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Fermer") { dismiss() }
                }
                ToolbarItem(placement: .primaryAction) {
                    Button("Tout voir") {
                        selected = nil
                        withAnimation { position = .automatic }
                    }
                }
            }
            .onAppear {
                if let pin = pins.first(where: { $0.id == focus }) {
                    selected = pin.id
                    zoom(to: pin)
                }
            }
            .onChange(of: selected) { _, newValue in
                if let pin = pins.first(where: { $0.id == newValue }) {
                    withAnimation { zoom(to: pin) }
                }
            }
        }
    }

    private func zoom(to pin: MapPin) {
        position = .region(MKCoordinateRegion(center: pin.coordinate,
                                              latitudinalMeters: 500,
                                              longitudinalMeters: 500))
    }

    private func placeCard(_ pin: MapPin) -> some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 2) {
                Text(pin.title).font(.headline)
                Text(pin.subtitle).font(.subheadline).foregroundStyle(.secondary)
            }
            Spacer()
            Button("Itinéraire") {
                let item = MKMapItem(placemark: MKPlacemark(coordinate: pin.coordinate))
                item.name = pin.title
                item.openInMaps(launchOptions: [
                    MKLaunchOptionsDirectionsModeKey: MKLaunchOptionsDirectionsModeDriving
                ])
            }
            .buttonStyle(.borderedProminent)
            .tint(.teal)
        }
        .padding()
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 20))
        .padding()
    }
}
