import SwiftUI
import RevenueCat

struct PaywallView: View {
    @EnvironmentObject var storeManager: StoreManager
    @State private var isLoading = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                Image(systemName: "crown.fill")
                    .font(.system(size: 60))
                    .foregroundColor(.yellow)
                
                Text("Unlock Unlimited AI Generations")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .multilineTextAlignment(.center)
                
                VStack(alignment: .leading, spacing: 15) {
                    FeatureRow(icon: "infinity", title: "Unlimited generations", detail: "Create as many resumes as you need")
                    FeatureRow(icon: "bolt.fill", title: "Priority processing", detail: "Faster AI responses")
                    FeatureRow(icon: "square.and.arrow.down", title: "PDF export", detail: "Download professional PDFs")
                    FeatureRow(icon: "star.fill", title: "Premium templates", detail: "Access exclusive designs")
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(15)
                
                VStack(spacing: 10) {
                    Text("$9.99/month")
                        .font(.title)
                        .fontWeight(.bold)
                    
                    Text("Billed monthly. Cancel anytime.")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                
                Button(action: subscribe) {
                    HStack {
                        if isLoading {
                            ProgressView()
                                .tint(.white)
                        }
                        Text("Subscribe Now")
                            .font(.headline)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(12)
                }
                .disabled(isLoading)
                
                Button("Restore Purchases") {
                    storeManager.restorePurchases()
                }
                .font(.caption)
                .foregroundColor(.blue)
                
                Spacer()
            }
            .padding()
            .navigationTitle("Upgrade")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Close") {
                        // Dismiss
                    }
                }
            }
        }
    }
    
    private func subscribe() {
        isLoading = true
        Task {
            await storeManager.purchase()
            isLoading = false
        }
    }
}

struct FeatureRow: View {
    let icon: String
    let title: String
    let detail: String
    
    var body: some View {
        HStack(spacing: 15) {
            Image(systemName: icon)
                .foregroundColor(.blue)
                .frame(width: 24)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                Text(detail)
                    .font(.caption)
                    .foregroundColor(.gray)
            }
        }
    }
}
