import SwiftUI
import RevenueCat

@main
struct AIApp: App {
    @StateObject private var storeManager = StoreManager()
    @StateObject private var apiClient = APIClient()
    @State private var showingOnboarding = false
    
    init() {
        // Initialize RevenueCat
        Purchases.configure(
            with: .init(apiKey: "REVENUECAT_API_KEY")
        )
        
        // Check onboarding
        let hasShownOnboarding = UserDefaults.standard.bool(forKey: "hasShownOnboarding")
        showingOnboarding = !hasShownOnboarding
    }
    
    var body: some Scene {
        WindowGroup {
            if showingOnboarding {
                OnboardingView()
                    .environmentObject(storeManager)
                    .environmentObject(apiClient)
            } else {
                ContentView()
                    .environmentObject(storeManager)
                    .environmentObject(apiClient)
            }
        }
    }
}
