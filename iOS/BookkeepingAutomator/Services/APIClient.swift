import Foundation

class APIClient: ObservableObject {
    @Published var canGenerateFree = true
    @Published var generationsUsed = 0
    @Published var maxFreeGenerations = 1
    
    private let baseURL = "https://your-backend-api.com"
    
    func generateResume(input: String) async throws -> String {
        // Check free limit
        if !canGenerateFree {
            throw NSError(domain: "APIClient", code: 403, userInfo: [NSLocalizedDescriptionKey: "Free limit reached. Please upgrade."])
        }
        
        guard let url = URL(string: "\(baseURL)/api/v1/generate") else {
            throw NSError(domain: "APIClient", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"])
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "email": "user@example.com", // Replace with user's email
            "app_type": "resume_builder",
            "input": input
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw NSError(domain: "APIClient", code: -2, userInfo: [NSLocalizedDescriptionKey: "Server error"])
        }
        
        let result = try JSONDecoder().decode(GenerateResponse.self, from: data)
        return result.output
    }
}

struct GenerateResponse: Codable {
    let success: Bool
    let output: String
}
