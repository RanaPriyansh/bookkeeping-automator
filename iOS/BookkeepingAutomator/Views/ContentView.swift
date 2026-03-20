import SwiftUI
import UniformTypeIdentifiers

struct ContentView: View {
    @EnvironmentObject var storeManager: StoreManager
    @EnvironmentObject var apiClient: APIClient
    @State private var inputText = ""
    @State private var outputText = ""
    @State private var isLoading = false
    @State private var showingPaywall = false
    @State private var errorMessage: String?
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Input section
                VStack(alignment: .leading, spacing: 8) {
                    Text("Enter your information")
                        .font(.headline)
                    
                    TextEditor(text: $inputText)
                        .frame(minHeight: 150)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(10)
                    
                    Button(action: generate) {
                        HStack {
                            if isLoading {
                                ProgressView()
                                    .tint(.white)
                            }
                            Text(isLoading ? "Generating..." : "Generate")
                                .fontWeight(.semibold)
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(isLoading ? Color.gray : Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                    }
                    .disabled(isLoading || inputText.isEmpty)
                }
                .padding()
                
                // Output section
                if !outputText.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Result")
                                .font(.headline)
                            Spacer()
                            Button("Copy") {
                                UIPasteboard.general.string = outputText
                            }
                        }
                        
                        Text(outputText)
                            .font(.system(.body, design: .monospaced))
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding()
                            .background(Color(.systemGray6))
                            .cornerRadius(10)
                    }
                    .padding()
                }
                
                Spacer()
                
                // Subscription status
                HStack {
                    if storeManager.isSubscribed {
                        Label("Pro", systemImage: "crown.fill")
                            .foregroundColor(.yellow)
                    } else {
                        Button("Upgrade to Pro") {
                            showingPaywall = true
                        }
                        .font(.subheadline)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(20)
                    }
                }
                .padding()
            }
            .navigationTitle("AI Bookkeeping Automator")
            .sheet(isPresented: $showingPaywall) {
                PaywallView()
            }
            .alert("Error", isPresented: .constant(errorMessage != nil)) {
                Button("OK", role: .cancel) { errorMessage = nil }
            } message: {
                Text(errorMessage ?? "")
            }
        }
    }
    
    private func generate() {
        // Check subscription for freemium limit
        if !storeManager.isSubscribed && !apiClient.canGenerateFree {
            showingPaywall = true
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                let result = try await apiClient.generateResume(input: inputText)
                outputText = result
                isLoading = false
            } catch {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }
}
