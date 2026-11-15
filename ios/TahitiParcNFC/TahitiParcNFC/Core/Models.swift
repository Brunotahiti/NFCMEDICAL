import Foundation

struct MeResponse: Decodable { let me: Me }

struct Me: Decodable, Hashable {
    let id: Int
    let login: String
    let name: String
    let role: String
    let pharmacy: PharmacyRef?
    let mustChange: Bool
}

struct PharmacyRef: Decodable, Hashable {
    let id: Int
    let name: String
    let commune: String
}

struct Pharmacy: Decodable, Identifiable, Hashable {
    let id: Int
    let name: String
    let commune: String
    let email: String?
}

struct Patient: Decodable, Identifiable, Hashable {
    let id: Int
    let name: String
    let address: String?
    let commune: String?
    let phone: String?
    let lat: Double?
    let lon: Double?
    let anonymized: Bool?
}

struct Prescription: Decodable, Hashable {
    let date: String
    let valid: String?
    let ref: String
    let at: String
    let by: String
}

struct PhotoInfo: Decodable, Identifiable, Hashable {
    let id: Int
    let at: String
    let by: String
    let kind: String
    let lat: Double?
    let lon: Double?
}

struct EventInfo: Decodable, Identifiable, Hashable {
    let id: Int
    let at: String
    let text: String
    let by: String
    let photo: Int?
}

struct ScanInfo: Decodable, Hashable {
    let at: String
    let by: String
    let lat: Double?
    let lon: Double?
    let accuracy: Double?
    let source: String
}

struct Equipment: Decodable, Identifiable, Hashable {
    let id: Int
    let ref: String
    let name: String
    let brand: String
    let kind: String
    let photo: String?
    let catalog: String?
    let weekPrice: Int
    let status: String
    let since: String?
    let nextCheck: String?
    let patientId: Int?
    let pharmacyId: Int?
    let plannedEnd: String?
    let rentalId: Int?
    let prescription: Prescription?
    let photos: [PhotoInfo]?
    let events: [EventInfo]
    let lastScan: ScanInfo?
    let buyPrice: Int?
    let buyEstimated: Bool?
    let rentedDays: Int?
    let link: String?

    var state: EquipmentState { EquipmentState(rawValue: status) ?? .dispo }
}

struct ClosedEquipment: Decodable, Hashable {
    let id: Int
    let ref: String
    let name: String
    let photo: String?
    let kind: String
    let weekPrice: Int
}

struct ClosedRental: Decodable, Identifiable, Hashable {
    let id: Int
    let equipment: ClosedEquipment
    let patientId: Int
    let pharmacyId: Int
    let start: String
    let end: String
    let amount: Int
}

struct AppState: Decodable {
    let me: Me
    let today: String
    let linkBase: String
    let communes: [String]
    let pharmacies: [Pharmacy]
    let patients: [Patient]
    let equipment: [Equipment]
    let closed: [ClosedRental]
    let requests: [RequestItem]?
    let catalog: [CatalogItem]?
    let reasons: [String: String]?
}

/// Demande d'une pharmacie : location, reprise, prolongation ou problème.
struct RequestItem: Decodable, Identifiable, Hashable {
    let id: Int
    let kind: String
    let pharmacyId: Int
    let patientId: Int?
    let patient: String
    let equipmentId: Int?
    let product: String
    let days: Int?
    let wanted: String?
    let reason: String
    let note: String
    let status: String
    let planned: String?
    let answer: String
    let rentalId: Int?
    let createdAt: String
    let createdBy: String
    let updatedAt: String?
    let updatedBy: String

    var type: RequestKind { RequestKind(rawValue: kind) ?? .location }
    var state: RequestStatus { RequestStatus(rawValue: status) ?? .nouvelle }
    var isOpen: Bool { state == .nouvelle || state == .planifiee }
}

struct CatalogItem: Decodable, Identifiable, Hashable {
    let name: String
    let kind: String
    let photo: String?
    let brand: String?
    let weekPrice: Int
    let total: Int
    let dispo: Int
    var id: String { name }
}

enum RequestKind: String, CaseIterable, Identifiable {
    case location, reprise, prolongation, probleme
    var id: String { rawValue }
    var label: String {
        switch self {
        case .location: return "Location"
        case .reprise: return "Reprise"
        case .prolongation: return "Prolongation"
        case .probleme: return "Problème"
        }
    }
    var subtitle: String {
        switch self {
        case .location: return "Demander du matériel"
        case .reprise: return "Faire reprendre un équipement"
        case .prolongation: return "Prolonger une location"
        case .probleme: return "Signaler un souci sur un matériel"
        }
    }
    var symbol: String {
        switch self {
        case .location: return "calendar.badge.plus"
        case .reprise: return "arrow.uturn.backward"
        case .prolongation: return "clock.arrow.circlepath"
        case .probleme: return "exclamationmark.triangle"
        }
    }
}

enum RequestStatus: String {
    case nouvelle, planifiee, faite, refusee, annulee
    var label: String {
        switch self {
        case .nouvelle: return "Nouvelle"
        case .planifiee: return "Planifiée"
        case .faite: return "Effectuée"
        case .refusee: return "Refusée"
        case .annulee: return "Annulée"
        }
    }
}

struct DetailScan: Decodable, Hashable {
    let at: String
    let userName: String?
    let lat: Double?
    let lon: Double?
    let accuracy: Double?
    let source: String
}

struct EquipmentDetail: Decodable {
    let events: [EventInfo]
    let scans: [DetailScan]
    let photos: [PhotoInfo]
}

struct BillingLine: Decodable, Identifiable, Hashable {
    let rentalId: Int
    let pharmacyId: Int
    let pharmacy: String
    let patient: String
    let ref: String
    let equipment: String
    let from: String
    let to: String
    let days: Int
    let weekPrice: Int
    let amount: Int
    let open: Bool
    let prescDate: String?
    let prescRef: String?
    var id: Int { rentalId }
}

struct Billing: Decodable {
    let month: String
    let provisional: Bool
    let total: Int
    let lines: [BillingLine]
}

struct CreatedID: Decodable { let id: Int }

enum EquipmentState: String, CaseIterable, Identifiable {
    case loc, dispo, desinf, maint
    var id: String { rawValue }
    var label: String {
        switch self {
        case .loc: return "En location"
        case .dispo: return "Disponible"
        case .desinf: return "Désinfection"
        case .maint: return "Maintenance"
        }
    }
    var symbol: String {
        switch self {
        case .loc: return "calendar"
        case .dispo: return "checkmark.circle"
        case .desinf: return "drop"
        case .maint: return "wrench.and.screwdriver"
        }
    }
}

enum AlertLevel { case crit, warn, info }

struct AlertItem: Identifiable {
    let id = UUID()
    let equipmentId: Int?
    let title: String
    let detail: String
    let tag: String
    let level: AlertLevel
}
