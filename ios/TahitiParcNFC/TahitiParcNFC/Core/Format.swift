import Foundation

/// Mise en forme : francs pacifiques, dates et durées en français.
enum Fmt {
    static let posix: Locale = Locale(identifier: "en_US_POSIX")
    static let fr: Locale = Locale(identifier: "fr_FR")
    static let tahiti = TimeZone(identifier: "Pacific/Tahiti")!

    static var calendar: Calendar {
        var c = Calendar(identifier: .gregorian)
        c.timeZone = tahiti
        c.locale = fr
        return c
    }

    private static let dayParser: DateFormatter = {
        let f = DateFormatter(); f.locale = posix; f.timeZone = tahiti; f.dateFormat = "yyyy-MM-dd"; return f
    }()
    private static let stampParser: DateFormatter = {
        let f = DateFormatter(); f.locale = posix; f.timeZone = tahiti; f.dateFormat = "yyyy-MM-dd HH:mm:ss"; return f
    }()
    private static let shortDay: DateFormatter = {
        let f = DateFormatter(); f.locale = fr; f.timeZone = tahiti; f.dateFormat = "dd/MM/yyyy"; return f
    }()
    private static let longDay: DateFormatter = {
        let f = DateFormatter(); f.locale = fr; f.timeZone = tahiti; f.dateFormat = "d MMMM yyyy"; return f
    }()
    private static let monthTitle: DateFormatter = {
        let f = DateFormatter(); f.locale = fr; f.timeZone = tahiti; f.dateFormat = "LLLL yyyy"; return f
    }()

    static func day(_ s: String?) -> Date? {
        guard let s else { return nil }
        return dayParser.date(from: String(s.prefix(10)))
    }
    static func stamp(_ s: String) -> Date? { stampParser.date(from: s) ?? day(s) }
    static func iso(_ d: Date) -> String { dayParser.string(from: d) }
    static func month(_ d: Date) -> String { String(iso(d).prefix(7)) }

    static func date(_ s: String?) -> String {
        guard let d = day(s) else { return "—" }
        return shortDay.string(from: d)
    }
    static func longDate(_ s: String?) -> String {
        guard let d = day(s) else { return "—" }
        return longDay.string(from: d)
    }
    static func dateTime(_ s: String) -> String {
        guard let d = stamp(s) else { return s }
        return shortDay.string(from: d) + " à " + d.formatted(.dateTime.hour().minute().locale(fr))
    }
    static func monthName(_ ym: String) -> String {
        guard let d = day(ym + "-01") else { return ym }
        return monthTitle.string(from: d).capitalized(with: fr)
    }

    /// Nombre de jours entre deux dates « aaaa-mm-jj » (b − a).
    static func days(from a: String?, to b: String?) -> Int? {
        guard let x = day(a), let y = day(b) else { return nil }
        return calendar.dateComponents([.day], from: x, to: y).day
    }

    static func addDays(_ s: String, _ n: Int) -> String {
        guard let d = day(s), let r = calendar.date(byAdding: .day, value: n, to: d) else { return s }
        return iso(r)
    }

    static func xpf(_ n: Int) -> String {
        n.formatted(.number.grouping(.automatic).locale(fr)) + " F"
    }

    static func duration(_ days: Int) -> String {
        let n = abs(days)
        if n >= 60 { return "\(Int((Double(n) / 30.4).rounded())) mois" }
        if n >= 14, n % 7 == 0 { return "\(n / 7) semaines" }
        return n <= 1 ? "\(n) jour" : "\(n) jours"
    }

    static func initials(_ name: String) -> String {
        name.split(separator: " ").compactMap { $0.first.map(String.init) }.prefix(2).joined().uppercased()
    }
}
