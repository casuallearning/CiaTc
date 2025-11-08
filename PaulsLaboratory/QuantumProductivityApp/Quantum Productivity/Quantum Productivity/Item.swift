//
//  Item.swift
//  Quantum Productivity
//
//  Created by Phil Hudson on 9/26/25.
//

import Foundation
import SwiftData
import CoreLocation

@Model
final class QuantumTask {
    var timestamp: Date
    var title: String
    var quantumState: QuantumState
    var circadianPhase: CircadianPhase
    var energyLevel: Double
    var mycorrhizalConnections: [String]
    var waggleDanceIntensity: Double
    var jungianArchetype: JungianArchetype
    var origamiFoldLevel: Int
    var fugueVoicePosition: Int
    var chaosCoefficient: Double
    var fermentationStage: FermentationStage

    init(title: String, timestamp: Date = Date()) {
        self.timestamp = timestamp
        self.title = title
        self.quantumState = .superposition
        self.circadianPhase = CircadianAnalyzer.currentPhase()
        self.energyLevel = Double.random(in: 0.1...1.0)
        self.mycorrhizalConnections = []
        self.waggleDanceIntensity = 0.5
        self.jungianArchetype = .shadow
        self.origamiFoldLevel = 1
        self.fugueVoicePosition = 1
        self.chaosCoefficient = Double.random(in: 0.0...1.0)
        self.fermentationStage = .preparation
    }
}

enum QuantumState: String, CaseIterable, Codable {
    case superposition = "⚛️ Superposition"
    case entangled = "🔗 Entangled"
    case collapsed = "💥 Collapsed"
    case tunneling = "🌀 Tunneling"
}

enum CircadianPhase: String, CaseIterable, Codable {
    case dawn = "🌅 Dawn Burst"
    case morning = "☀️ Solar Peak"
    case midday = "🔥 Chromodynamic High"
    case afternoon = "🌤️ Golden Resonance"
    case evening = "🌆 Twilight Decay"
    case night = "🌙 Quantum Rest"
}

enum JungianArchetype: String, CaseIterable, Codable {
    case shadow = "🌑 Shadow Work"
    case anima = "🌸 Anima Flow"
    case animus = "⚔️ Animus Drive"
    case self = "🌟 Self Integration"
    case persona = "🎭 Persona Task"
}

enum FermentationStage: String, CaseIterable, Codable {
    case preparation = "🧪 Preparation"
    case fermentation = "🫧 Active Fermentation"
    case maturation = "🍯 Maturation"
    case completion = "✨ Essence Complete"
}

class CircadianAnalyzer {
    static func currentPhase() -> CircadianPhase {
        let hour = Calendar.current.component(.hour, from: Date())
        switch hour {
        case 5...7: return .dawn
        case 8...11: return .morning
        case 12...14: return .midday
        case 15...17: return .afternoon
        case 18...20: return .evening
        default: return .night
        }
    }

    static func quantumChromoColor(for phase: CircadianPhase) -> (red: Double, green: Double, blue: Double, alpha: Double) {
        switch phase {
        case .dawn: return (1.0, 0.7, 0.3, 0.8)
        case .morning: return (1.0, 1.0, 0.0, 0.9)
        case .midday: return (1.0, 0.3, 0.0, 1.0)
        case .afternoon: return (1.0, 0.8, 0.0, 0.85)
        case .evening: return (0.6, 0.2, 0.8, 0.7)
        case .night: return (0.1, 0.1, 0.3, 0.6)
        }
    }
}
