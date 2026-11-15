import CoreLocation

struct LocationFix: Equatable {
    let latitude: Double
    let longitude: Double
    let accuracy: Double
}

/// Position ponctuelle, prise au moment du scan ou de la photo.
final class LocationService: NSObject, CLLocationManagerDelegate {
    static let shared = LocationService()

    private let manager = CLLocationManager()
    private var waiting: [CheckedContinuation<LocationFix?, Never>] = []

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
    }

    /// Renvoie la position actuelle, ou nil si elle est refusée ou trop lente (10 s).
    @MainActor
    func current() async -> LocationFix? {
        switch manager.authorizationStatus {
        case .denied, .restricted: return nil
        default: break
        }
        return await withCheckedContinuation { cont in
            waiting.append(cont)
            if manager.authorizationStatus == .notDetermined {
                manager.requestWhenInUseAuthorization()
            } else {
                manager.requestLocation()
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 10) { self.deliver(nil) }
        }
    }

    private func deliver(_ fix: LocationFix?) {
        let list = waiting
        waiting.removeAll()
        list.forEach { $0.resume(returning: fix) }
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        guard !waiting.isEmpty else { return }
        switch manager.authorizationStatus {
        case .authorizedWhenInUse, .authorizedAlways: manager.requestLocation()
        case .denied, .restricted: deliver(nil)
        default: break
        }
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let l = locations.last else { return }
        deliver(LocationFix(latitude: l.coordinate.latitude, longitude: l.coordinate.longitude, accuracy: l.horizontalAccuracy))
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        deliver(nil)
    }
}
