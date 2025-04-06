# RepoStructureVisualizer

RepoStructureVisualizer is a tool to analyze the structure of a directory and generate a Markdown file with the folder tree and file contents. Ideal for documenting projects on GitHub or getting a quick overview of a repository.

## Features
- Generate a directory tree in Markdown format.
- Automatically ignore irrelevant folders (e.g. `.git`, `node_modules`, `venv`).
- Includes the contents of text files in the report.
- Compatible with projects in many programming language.


## Output Example:
------------

## Directory Tree

```
.
├── activity/
│   ├── FermataDetailView.swift
│   ├── FermateListView.swift
│   ├── HeaderView.swift
│   ├── LinesActivityAroundMe.swift
│   ├── MainActivity.swift
│   ├── NewsActivity.swift
│   ├── StopActivity.swift
│   ├── StopAdapter.swift
│   ├── StopInfoView.swift
│   └── TransportTabBarView.swift
├── api/
│   ├── ApiFermata.swift
│   ├── ApiListaMezzi.swift
│   └── ApiMezzo.swift
├── controller/
│   ├── FindAroundMeHelper.swift
│   ├── RicercaAroundMe.swift
│   ├── RicercaInfoFermata.swift
│   ├── RicercaInfoMezzo.swift
│   ├── RicercaMezzi.swift
│   └── RicercaNews.swift
├── model/
│   ├── Category.swift
│   ├── CodableValue.swift
│   ├── Fermata.swift
│   ├── JourneyPatterns.swift
│   ├── Line.swift
│   ├── LineInfo.swift
│   ├── Link.swift
│   ├── ListaMezzi.swift
│   ├── Location.swift
│   ├── Mezzo.swift
│   ├── News.swift
│   ├── Stop.swift
│   └── TrafficBulletin.swift
├── service/
│   └── CallAtm.swift
├── .gitignore
└── icon.png
```

## File Details

## Root
- `.gitignore`

```text
*.iml
.gradle
/local.properties
/.idea/caches
/.idea/libraries
/.idea/modules.xml
/.idea/workspace.xml
/.idea/navEditor.xml
/.idea/assetWizardSettings.xml
.DS_Store
/build
/captures
.externalNativeBuild
.cxx
local.properties
```

- `FermataDetailView.swift`

```text
import SwiftUI
import MapKit

struct FermataDetailView: View {
    var fermata: Stop
    @State private var detailFermata: ApiFermata?
    @State private var errorMessage: String?
    @State private var region: MKCoordinateRegion
    @State private var timer: Timer?

    private let ricercaFermata = RicercaInfoFermata()

    init(fermata: Stop) {
        self.fermata = fermata
        _region = State(initialValue: MKCoordinateRegion(
            center: CLLocationCoordinate2D(latitude: 0.0, longitude: 0.0),
            span: MKCoordinateSpan(latitudeDelta: 0.002, longitudeDelta: 0.002)
        ))
    }

    var body: some View {
        VStack {
            if let error = errorMessage {
                Text("Error: \(error)")
                    .foregroundColor(.red)
                    .padding()
            } else if let detail = detailFermata {
                VStack {
                    Text(detail.description)
                        .font(.title)
                        .padding()

                    Text("Waiting Message: \(detail.waitingMessage)")
                        .padding()

                    Map(coordinateRegion: $region, showsUserLocation: false, annotationItems: [detail]) { fermataDetail in
                        MapPin(coordinate: CLLocationCoordinate2D(latitude: fermataDetail.y, longitude: fermataDetail.x), tint: .blue)
                    }
                    .frame(height: 300)
                    .padding()
                }
            } else {
                ProgressView("Loading...")
                    .padding()
            }
        }
        .onAppear {
            fetchFermataDetails()
            startTimer()
        }
        .onDisappear {
            timer?.invalidate()
        }
        .navigationTitle(fermata.description)
        .padding()
    }

    func fetchFermataDetails() {
        ricercaFermata.infoFermata(input: fermata.code) { details in
            DispatchQueue.main.async {
                if let firstDetail = details.first {
                    let bookInfo = firstDetail.bookInfo.isEmpty ? "N/A" : firstDetail.bookInfo
                    detailFermata = ApiFermata(
                        description: firstDetail.description,
                        bookInfo: bookInfo,
                        waitingMessage: firstDetail.waitingMessage,
                        y: firstDetail.y,
                        x: firstDetail.x,
                        code: firstDetail.code
                    )
                    region.center = CLLocationCoordinate2D(latitude: firstDetail.y, longitude: firstDetail.x)
                } else {
                    errorMessage = "No details found for stop \(fermata.code)"
                }
            }
        }
    }

    func startTimer() {
        timer = Timer.scheduledTimer(withTimeInterval: 10, repeats: true) { _ in
            fetchFermataDetails()
        }
    }
}
```
- `FermateListView.swift`

```text
import SwiftUI

struct FermateListView: View {
    var mezzo: ApiListaMezzi
    @State private var fermateList: [Stop] = []
    @State private var direzioneSelezionata: Int = 0
    @State private var searchText = ""

    private let ricercaFermate = RicercaInfoMezzo()

    var body: some View {
        VStack {
            Text("Fermate per Mezzo \(mezzo.code)")
                .font(.title)
                .padding()

            Picker("Direzione", selection: $direzioneSelezionata) {
                Text("Andata").tag(0)
                Text("Ritorno").tag(1)
            }
            .pickerStyle(SegmentedPickerStyle())
            .padding()

            TextField("Cerca fermata...", text: $searchText)
                .padding()
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .onChange(of: searchText) { _ in
                    filterFermateList()
                }

            if !fermateList.isEmpty {
                List(fermateList, id: \.code) { fermata in
                    NavigationLink(destination: FermataDetailView(fermata: fermata)) {
                        Text(fermata.description)
                    }
                }
            } else {
                Text("Nessuna fermata trovata").padding()
            }
        }
        .onAppear {
            fetchFermateForMezzo()
        }
        .onChange(of: direzioneSelezionata) { _ in
            fetchFermateForMezzo()
        }
        .navigationTitle(mezzo.lineDescription)
    }

    func fetchFermateForMezzo() {
        ricercaFermate.infoMezzo(input: mezzo.code, direzione: direzioneSelezionata) { fermate in
            DispatchQueue.main.async {
                fermateList = fermate
                filterFermateList()
            }
        }
    }

    func filterFermateList() {
        if searchText.isEmpty {
            fetchFermateForMezzo()
        } else {
            fermateList = fermateList.filter { fermata in
                fermata.description.lowercased().contains(searchText.lowercased()) ||
                fermata.code.lowercased().contains(searchText.lowercased())
            }
        }
    }
}
```
- `HeaderView.swift`

```text
import Foundation
import SwiftUI

struct HeaderView: View {
    @State private var newsTitle: String = "Caricamento notizie..."
    @State private var offsetX: CGFloat = UIScreen.main.bounds.width

    var body: some View {
        VStack {
            Text(newsTitle)
                .offset(x: offsetX)
                .onAppear {
                    withAnimation(Animation.linear(duration: 8).repeatForever(autoreverses: false)) {
                        offsetX = -UIScreen.main.bounds.width
                    }
                    fetchNews()
                }
                .padding()
        }
        .contentShape(Rectangle())
        .onTapGesture {
            print("Vai alla HomeView")
        }
    }

    func fetchNews() {
        DispatchQueue.global(qos: .background).async {
            let fetchedTitle = "⚡ Ultime notizie ATM disponibili ora!"
            DispatchQueue.main.async {
                newsTitle = fetchedTitle
            }
        }
    }
}
```
- `LinesActivityAroundMe.swift`

```text
import SwiftUI
import CoreLocation

class LocationManagerWrapper: NSObject, ObservableObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    @Published var lastLocation: CLLocation?
    
    override init() {
        super.init()
        manager.delegate = self
    }
    
    func start() {
        manager.requestWhenInUseAuthorization()
        manager.startUpdatingLocation()
    }
    
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        lastLocation = locations.last
    }
}

struct LinesActivityAroundMe: View {
    @StateObject private var locationWrapper = LocationManagerWrapper()
    @State private var mezziArrayNomi = [String]()
    @State private var searchText = ""
    
    var body: some View {
        VStack {
            List(mezziArrayNomi.filter {
                searchText.isEmpty ? true : $0.contains(searchText)
            }, id: \.self) { mezzo in
                Text(mezzo)
            }
            
            TextField("Search", text: $searchText)
                .padding()
        }
        .onAppear {
            locationWrapper.start()
        }
    }
}
```
- `MainActivity.swift`

```text
import SwiftUI

struct MainActivity: View {
    @State private var selectedTransport = -1
    @State private var mezziList: [ApiListaMezzi] = []
    @State private var originalMezziList: [ApiListaMezzi] = []
    @State private var searchText = ""
    private let ricercaMezzi = RicercaMezzi()
    private let ricercaAroundMe = RicercaAroundMe()

    var body: some View {
        NavigationStack {
            VStack {
                Text("Selected Transport: \(selectedTransport == -1 ? "None" : "\(selectedTransport)")")
                    .padding()

                TransportTabBarView { transportIndex in
                    selectedTransport = transportIndex
                    handleTransportSelection(transportIndex)
                }

                if selectedTransport != -1 {
                    TextField("Cerca mezzo...", text: $searchText)
                        .padding()
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .onChange(of: searchText) { newValue in
                            filterMezziList()
                        }
                }

                if !mezziList.isEmpty {
                    List(mezziList, id: \.code) { mezzo in
                        NavigationLink(destination: FermateListView(mezzo: mezzo)) {
                            if selectedTransport == 3 {
                                Text("Bus \(mezzo.code)")
                            } else if selectedTransport == 2 {
                                Text("Treno \(mezzo.code)")
                            } else if selectedTransport == 1 {
                                Text("Tram \(mezzo.code)")
                            } else {
                                Text("Mezzo \(mezzo.code)")
                            }
                        }
                    }
                } else {
                    Text("Nessun mezzo trovato").padding()
                }
            }
            .navigationTitle("Transport Selector")
        }
    }

    func handleTransportSelection(_ transportIndex: Int) {
        if transportIndex == 4 {
            ricercaAroundMe.listaMezziAroundMe(y: 45.0, x: 9.0) { mezzi in
                DispatchQueue.main.async {
                    let uniqueMezzi = removeDuplicateMezzi(mezzi)
                    mezziList = uniqueMezzi
                    originalMezziList = uniqueMezzi
                    filterMezziList()
                }
            }
        } else {
            ricercaMezzi.listaMezzi(input: transportIndex) { mezzi in
                DispatchQueue.main.async {
                    let uniqueMezzi = removeDuplicateMezzi(mezzi)
                    mezziList = uniqueMezzi
                    originalMezziList = uniqueMezzi
                    filterMezziList()
                }
            }
        }
    }

    func removeDuplicateMezzi(_ mezzi: [ApiListaMezzi]) -> [ApiListaMezzi] {
        var seenCodes = Set<String>()
        return mezzi.filter { mezzo in
            if seenCodes.contains(mezzo.code) {
                return false
            } else {
                seenCodes.insert(mezzo.code)
                return true
            }
        }
    }

    func filterMezziList() {
        if searchText.isEmpty {
            mezziList = originalMezziList
        } else {
            mezziList = originalMezziList.filter { mezzo in
                mezzo.lineDescription.lowercased().contains(searchText.lowercased()) ||
                mezzo.code.lowercased().contains(searchText.lowercased())
            }
        }
    }
}
```
- `NewsActivity.swift`

```text
import Foundation
import SwiftUI

struct NewsActivity: View {
    @State private var newsTitles = [String]()

    var body: some View {
        List(newsTitles, id: \.self) { title in
            Text(title)
        }
        .onAppear {
            fetchNews()
        }
    }
    
    func fetchNews() {
    }
}
```
- `StopActivity.swift`

```text
import Foundation
import SwiftUI
import MapKit

struct StopActivity: View {
    @State private var region = MKCoordinateRegion(
        center: CLLocationCoordinate2D(latitude: 43.0, longitude: 12.0),
        span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
    )

    var body: some View {
        VStack {
            Map(coordinateRegion: $region, interactionModes: .all, showsUserLocation: true)
                .edgesIgnoringSafeArea(.all)
            
            Text("Stop Description")
            Text("Book Info")
            Text("Waiting Message")
        }
        .onAppear {
            updateStopInfo()
        }
    }

    func updateStopInfo() {
    }
}
```
- `StopAdapter.swift`

```text
import Foundation
import SwiftUI

struct StopAdapter: View {
    var stops: [String]
    
    var body: some View {
        List(stops, id: \.self) { stop in
            Text(stop)
        }
    }
}
```
- `StopInfoView.swift`

```text
import Foundation
import SwiftUI

struct StopInfoView: View {
    var descriptionText: String
    var bookInfoText: String
    var waitingMessageText: String

    var body: some View {
        VStack(spacing: 16) {
            Text(descriptionText)
                .font(.title2)
            Text(bookInfoText)
                .font(.body)
            Text(waitingMessageText)
                .font(.footnote)
                .foregroundColor(.gray)
        }
        .padding()
    }
}
```
- `TransportTabBarView.swift`

```text
import Foundation
import SwiftUI

struct TransportTabBarView: View {
    var onSelectTransport: (Int) -> Void

    var body: some View {
        HStack(spacing: 16) {
            Button("🚋 Tram") {
                onSelectTransport(1)
            }
            Button("🚌 Bus") {
                onSelectTransport(3)
            }
            Button("🚆 Treno") {
                onSelectTransport(2)
            }
        }
        .padding()
        .buttonStyle(.borderedProminent)
    }
}
```
### api
- `ApiFermata.swift`

```text
import Foundation

struct ApiFermata: Codable, Identifiable {
    var id: String { code }
    var description: String
    var bookInfo: String
    var waitingMessage: String
    var y: Double
    var x: Double
    var address: String?
    var municipality: String?
    var code: String 

    var debugDescription: String {
        return """
        ApiFermata:
        - Description: \(description)
        - BookInfo: \(bookInfo)
        - WaitingMessage: \(waitingMessage)
        - Location: (\(y), \(x))
        """
    }
}
```
- `ApiListaMezzi.swift`

```text
import Foundation
import Foundation

struct ApiListaMezzi: Codable, CustomStringConvertible {
    var code: String
    var direction: String
    var lineDescription: String
    var tipologia: Int

    var description: String {
        return "ApiListaMezzi(code: \(code), direction: \(direction), lineDescription: \(lineDescription), tipologia: \(tipologia))"
    }
}
```
- `ApiMezzo.swift`

```text
import Foundation
import Foundation

struct ApiMezzo: Codable {
    var code: String
    var lineDescription: String
    var direction: Int
    var stops: [Stop]
}
```
### controller
- `FindAroundMeHelper.swift`

```text
import Foundation
import CoreLocation
class FindAroundMeHelper: NSObject, CLLocationManagerDelegate {
    private let locationManager = CLLocationManager()
    var callback: ((Double, Double) -> Void)?
    var errorCallback: ((String) -> Void)?

    override init() {
        super.init()
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
    }

    func startLocationUpdates(callback: @escaping (Double, Double) -> Void, onError: @escaping (String) -> Void) {
        self.callback = callback
        self.errorCallback = onError

        let status = locationManager.authorizationStatus
        if status == .denied || status == .restricted {
            onError("Location permission not granted")
            return
        }

        locationManager.requestWhenInUseAuthorization()
        locationManager.startUpdatingLocation()
    }

    func stopLocationUpdates() {
        locationManager.stopUpdatingLocation()
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.first else { return }
        callback?(location.coordinate.latitude, location.coordinate.longitude)
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        errorCallback?("Location error: \(error.localizedDescription)")
    }
}
```
- `RicercaAroundMe.swift`

```text
import Foundation
import CoreLocation

class RicercaAroundMe {
    func listaMezziAroundMe(y: Double, x: Double, completion: @escaping ([ApiListaMezzi]) -> Void) {
        Task {
            do {
                let response = try await CallAtm.infoAroundMe(y: y, x: x)
                
                let listaMezzi = response.journeyPatterns
                
                let result = listaMezzi.map {
                    ApiListaMezzi(
                        code: $0.code,
                        direction: $0.direction,
                        lineDescription: $0.line.lineDescription,
                        tipologia: $0.line.transportMode ?? 0
                    )
                }
                completion(result)
            } catch {
                completion([])
            }
        }
    }
}
```
- `RicercaInfoFermata.swift`

```text
class RicercaInfoFermata {
    func infoFermata(input: String, completion: @escaping ([ApiFermata]) -> Void) {
        Task {
            do {
                let fermata = try await CallAtm.infoFermata(numero: input)
                let firstLine = fermata.lines?.first
                let waitingMessage = firstLine?.waitMessage ?? "Nessun messaggio disponibile"
                
                let detailsDescription: String
                if let details = fermata.details as? String, !details.isEmpty {
                    detailsDescription = details
                } else {
                    detailsDescription = "Dettagli non disponibili"
                }
                
                let siteUrl = fermata.siteUrl ?? "N/A"
                
                let result = [ApiFermata(
                    description: fermata.description ?? "Descrizione non disponibile",
                    bookInfo: siteUrl,
                    waitingMessage: waitingMessage,
                    y: fermata.location?.y ?? 0.0,
                    x: fermata.location?.x ?? 0.0,
                    code: fermata.code ?? "N/A"
                )]
                
                completion(result)
            } catch {
                completion([])
            }
        }
    }
}
```
- `RicercaInfoMezzo.swift`

```text
import Foundation

class RicercaInfoMezzo {
    func infoMezzo(input: String, direzione: Int, completion: @escaping ([Stop]) -> Void) {
        Task {
            do {
                let mezzo: Mezzo = try await CallAtm.infoMezzo(input: input, direzione: direzione)
                completion(mezzo.stops ?? [])
            } catch {
                completion([])
            }
        }
    }
}
```
- `RicercaMezzi.swift`

```text
import Foundation

class RicercaMezzi {
    func listaMezzi(input: Int, completion: @escaping ([ApiListaMezzi]) -> Void) {
        Task {
            do {
                let response = try await CallAtm.listaMezzi()
                
                let result: [ApiListaMezzi] = response.journeyPatterns.compactMap { mezzo in
                    guard mezzo.line.transportMode == input else {
                        return nil
                    }
                    return ApiListaMezzi(
                        code: mezzo.code,
                        direction: mezzo.direction,
                        lineDescription: mezzo.line.lineDescription,
                        tipologia: mezzo.line.transportMode
                    )
                }
                
                completion(result)
            } catch {
                completion([])
            }
        }
    }
}
```
- `RicercaNews.swift`

```text
import Foundation

class RicercaNews {
    func listaNews(completion: @escaping ([News]) -> Void) {
        Task {
            do {
                let newsList: [News] = try await CallAtm.news()
                completion(newsList)
            } catch {
                completion([])
            }
        }
    }
}
```
### model
- `Category.swift`

```text
import Foundation

struct Category: Codable {
    var categoryId: String?
    var categoryName: String?
    var hasTimeTables: Bool?
    var icons: [String]?

    enum CodingKeys: String, CodingKey {
        case categoryId = "CategoryId"
        case categoryName = "CategoryName"
        case hasTimeTables = "HasTimeTables"
        case icons = "Icons"
    }
}
```
- `CodableValue.swift`

```text
import Foundation

struct CodableValue: Codable {
    let value: Any?

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()

        if let int = try? container.decode(Int.self) {
            value = int
        } else if let double = try? container.decode(Double.self) {
            value = double
        } else if let bool = try? container.decode(Bool.self) {
            value = bool
        } else if let string = try? container.decode(String.self) {
            value = string
        } else if let dict = try? container.decode([String: CodableValue].self) {
            value = dict
        } else if let array = try? container.decode([CodableValue].self) {
            value = array
        } else {
            value = nil
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()

        switch value {
        case let int as Int:
            try container.encode(int)
        case let double as Double:
            try container.encode(double)
        case let bool as Bool:
            try container.encode(bool)
        case let string as String:
            try container.encode(string)
        case let dict as [String: CodableValue]:
            try container.encode(dict)
        case let array as [CodableValue]:
            try container.encode(array)
        default:
            try container.encodeNil()
        }
    }
}
```
- `Fermata.swift`

```text
struct Fermata: Codable {
    var code: String?
    var description: String?
    var location: Location?
    var customerCode: String?
    var municipality: String?
    var address: String?
    var telephone: String?
    var fax: String?
    var siteUrl: String?
    var email: String?
    var category: Category?
    var details: CodableValue? // Optional
    var dynamicFirstLevel: CodableValue? // Optional
    var lines: [LineInfo]? // Optional
    var pointAccessible: Bool?
    var pointStopPath: CodableValue?
    var pointStopStatus: CodableValue?
    var pointStopInfo: CodableValue?
    var links: [Link]?

    enum CodingKeys: String, CodingKey {
        case code = "Code"
        case description = "Description"
        case location = "Location"
        case customerCode = "CustomerCode"
        case municipality = "Municipality"
        case address = "Address"
        case telephone = "Telephone"
        case fax = "Fax"
        case siteUrl = "SiteUrl"
        case email = "Email"
        case category = "Category"
        case details = "Details" // Optional
        case dynamicFirstLevel = "Dynamic_First_Level" // Optional
        case lines = "Lines" // Optional
        case pointAccessible
        case pointStopPath
        case pointStopStatus
        case pointStopInfo
        case links
    }
}
```
- `JourneyPatterns.swift`

```text
import Foundation
struct JourneyPatterns: Codable {
    var journeyPatterns: [ListaMezzi]

    enum CodingKeys: String, CodingKey {
        case journeyPatterns = "JourneyPatterns"
    }
}
```
- `Line.swift`

```text
import Foundation

struct Line: Codable {
    let operatorCode: String
    let lineCode: String
    let lineDescription: String
    let suburban: Bool
    let transportMode: Int
    let otherRoutesAvailable: Bool
    let links: [Link]?

    enum CodingKeys: String, CodingKey {
        case operatorCode = "OperatorCode"
        case lineCode = "LineCode"
        case lineDescription = "LineDescription"
        case suburban = "Suburban"
        case transportMode = "TransportMode"
        case otherRoutesAvailable = "OtherRoutesAvailable"
        case links = "Links"
    }
}
```
- `LineInfo.swift`

```text
import Foundation

struct LineInfo: Codable {
    var line: Line
    var direction: String?
    var bookletUrl: String?
    var bookletUrl2: String?
    var waitMessage: String?
    var journeyPatternId: String
    var trafficBulletins: [TrafficBulletin]?
    var links: [Link]?

    enum CodingKeys: String, CodingKey {
        case line = "Line"
        case direction = "Direction"
        case bookletUrl = "BookletUrl"
        case bookletUrl2 = "BookletUrl2"
        case waitMessage = "WaitMessage"
        case journeyPatternId = "JourneyPatternId"
        case trafficBulletins = "TrafficBulletins"
        case links = "Links"
    }
}
```
- `Link.swift`

```text
import Foundation

struct Link: Codable {
    let rel: String?
    let href: String
    let title: String?

    enum CodingKeys: String, CodingKey {
        case rel = "Rel"
        case href = "Href"
        case title = "Title"
    }
}
```
- `ListaMezzi.swift`

```text
import Foundation

struct ListaMezzi: Codable {
    let id: String
    let code: String
    let direction: String
    let line: Line
    let stops: [Stop]?
    let geometry: CodableValue?
    let links: [Link]?

    enum CodingKeys: String, CodingKey {
        case id = "Id"
        case code = "Code"
        case direction = "Direction"
        case line = "Line"
        case stops = "Stops"
        case geometry = "Geometry"
        case links = "Links"
    }
}
```
- `Location.swift`

```text
import Foundation

struct Location: Codable {
    var x: Double
    var y: Double

    enum CodingKeys: String, CodingKey {
        case x = "X"
        case y = "Y"
    }
}
```
- `Mezzo.swift`

```text
import Foundation

struct Mezzo: Codable {
    var id: String
    var code: String
    var direction: String
    var line: Line
    var stops: [Stop]

    enum CodingKeys: String, CodingKey {
        case id = "Id"
        case code = "Code"
        case direction = "Direction"
        case line = "Line"
        case stops = "Stops"
    }
}
```
- `News.swift`

```text
import Foundation

struct News: Codable {
    var publication: String
    var expiration: String
    var title: String
    var body: String
    var lines: [String]
    var guid: String

    enum CodingKeys: String, CodingKey {
        case publication = "Publication"
        case expiration = "Expiration"
        case title = "Title"
        case body = "Body"
        case lines = "Lines"
        case guid = "Guid"
    }
}
```
- `Stop.swift`

```text
import Foundation

struct Stop: Codable {
    var operatorCode: String
    var code: String
    var description: String
    var location: Location
    var pointType: Int
    var stopType: String

    enum CodingKeys: String, CodingKey {
        case operatorCode = "OperatorCode"
        case code = "Code"
        case description = "Description"
        case location = "Location"
        case pointType = "PointType"
        case stopType = "StopType"
    }
}
```
- `TrafficBulletin.swift`

```text
import Foundation

struct TrafficBulletin: Codable {
    var title: String?
    var body: String?
    var publicationDate: String?
    var expirationDate: String? 

    enum CodingKeys: String, CodingKey {
        case title = "Title"
        case body = "Body"
        case publicationDate = "PublicationDate"
        case expirationDate = "ExpirationDate"
    }
}
```
### service
- `CallAtm.swift`

```text
import Foundation

struct CallAtm {
    private static let baseUrl = "https://giromilano.atm.it/proxy.tpportal/api/tpportal"

    private static func fetch<T: Decodable>(from urlString: String, as type: T.Type) async throws -> T {
        guard let url = URL(string: urlString) else {
            throw URLError(.badURL)
        }

        var request = URLRequest(url: url)
        request.setValue("gzip", forHTTPHeaderField: "Accept-Encoding")
        request.setValue("Mozilla/5.0", forHTTPHeaderField: "User-Agent")

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }

        guard 200..<300 ~= httpResponse.statusCode else {
            throw URLError(.badServerResponse)
        }

        return try JSONDecoder().decode(T.self, from: data)
    }

    static func infoMezzo(input: String, direzione: Int) async throws -> Mezzo {
        let url = "\(baseUrl)/tpl/journeyPatterns/\(input)%7C\(direzione)/?alternativeRoutesMode=false"
        return try await fetch(from: url, as: Mezzo.self)
    }

    static func infoFermata(numero: String) async throws -> Fermata {
        let url = "\(baseUrl)/geodata/pois/stops/\(numero)"
        return try await fetch(from: url, as: Fermata.self)
    }

    static func listaMezzi() async throws -> JourneyPatterns {
        let url = "\(baseUrl)/tpl/journeyPatterns"
        return try await fetch(from: url, as: JourneyPatterns.self)
    }

    static func news() async throws -> [News] {
        let url = "\(baseUrl)/tpl/atm/it"
        return try await fetch(from: url, as: [News].self)
    }

    static func infoAroundMe(y: Double, x: Double) async throws -> JourneyPatterns {
        let url = "\(baseUrl)/tpl/journeyPatterns/nearest?radius=200&Point.Y=\(y)&Point.X=\(x)"
        return try await fetch(from: url, as: JourneyPatterns.self)
    }
}
```
