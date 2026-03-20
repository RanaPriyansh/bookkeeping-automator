import SwiftUI

struct OnboardingView: View {
    @EnvironmentObject var storeManager: StoreManager
    
    var body: some View {
        VStack(spacing: 50) {
            Spacer()
            
            Image(systemName: "sparkles")
                .font(.system(size: 80))
                .foregroundColor(.blue)
            
            VStack(spacing: 10) {
                Text("Welcome to AI Resume Builder")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .multilineTextAlignment(.center)
                
                Text("Create a job-winning resume in 30 seconds using AI")
                    .font(.title3)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
            }
            .padding()
            
            Spacer()
            
            VStack(spacing: 15) {
                Button(action: {
                    UserDefaults.standard.set(true, forKey: "hasShownOnboarding")
                }) {
                    Text("Get Started")
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                }
                
                Button("Try Free Version") {
                    UserDefaults.standard.set(true, forKey: "hasShownOnboarding")
                }
                .font(.subheadline)
                .foregroundColor(.blue)
            }
            .padding()
        }
        .padding()
    }
}
