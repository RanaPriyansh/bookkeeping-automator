import SwiftUI
import RevenueCat

class StoreManager: ObservableObject {
    @Published var isSubscribed = false
    @Published var customerInfo: CustomerInfo?
    
    init() {
        setupListener()
        checkStatus()
    }
    
    private func setupListener() {
        Purchases.shared.delegate = self
    }
    
    private func checkStatus() {
        Task {
            do {
                let info = try await Purchases.shared.customerInfo()
                await MainActor.run {
                    self.customerInfo = info
                    self.isSubscribed = info.entitlements["premium"]?.isActive == true
                }
            } catch {
                print("Error checking status: \(error)")
            }
        }
    }
    
    @MainActor
    func purchase() async {
        do {
            let offerings = try await Purchases.shared.offerings()
            if let package = offerings?.current?.availablePackages.first {
                _ = try await Purchases.shared.purchase(package: package)
                checkStatus()
            }
        } catch {
            print("Purchase error: \(error)")
        }
    }
    
    func restorePurchases() {
        Task {
            do {
                _ = try await Purchases.shared.restorePurchases()
                checkStatus()
            } catch {
                print("Restore error: \(error)")
            }
        }
    }
}

extension StoreManager: PurchasesDelegate {
    func purchases(_ purchases: Purchases, receivedUpdated customerInfo: CustomerInfo) {
        self.customerInfo = customerInfo
        self.isSubscribed = customerInfo.entitlements["premium"]?.isActive == true
    }
}
