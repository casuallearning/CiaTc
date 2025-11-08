import Foundation
import simd
import Accelerate

// MARK: - Waggle Dance Computer Vision Analysis
struct WaggleMovementPattern {
    let angle: Double          // Dance angle in radians
    let duration: TimeInterval // Duration of waggle run
    let frequency: Double      // Wing beat frequency (Hz)
    let amplitude: Double      // Movement amplitude
    let timestamp: Date        // When pattern was observed

    var distance: Double {
        // Convert duration to distance using von Frisch's formula
        return max(0, (duration - 0.1) * 1000) // meters
    }

    var direction: Double {
        // Angle relative to sun position (0 = straight up)
        return angle
    }
}

struct BeeMovementVector {
    let x: Double
    let y: Double
    let velocity: Double
    let acceleration: Double
    let timestamp: TimeInterval
}

// MARK: - Computer Vision Processing
class WaggleDanceVisionProcessor {
    private var movementBuffer: [BeeMovementVector] = []
    private let bufferSize = 1000

    func processFrameData(_ frame: [Double]) -> [WaggleMovementPattern] {
        // Simulate computer vision processing of bee movements
        let movements = extractMovementVectors(from: frame)
        movementBuffer.append(contentsOf: movements)

        if movementBuffer.count > bufferSize {
            movementBuffer.removeFirst(movementBuffer.count - bufferSize)
        }

        return detectWagglePatterns()
    }

    private func extractMovementVectors(from frame: [Double]) -> [BeeMovementVector] {
        var vectors: [BeeMovementVector] = []

        // Simulate optical flow analysis
        for i in stride(from: 0, to: frame.count - 3, by: 4) {
            let x = frame[i]
            let y = frame[i + 1]
            let prevX = frame.count > i + 2 ? frame[i + 2] : x
            let prevY = frame.count > i + 3 ? frame[i + 3] : y

            let velocity = sqrt(pow(x - prevX, 2) + pow(y - prevY, 2))
            let acceleration = velocity * 0.1 // Simplified

            vectors.append(BeeMovementVector(
                x: x, y: y,
                velocity: velocity,
                acceleration: acceleration,
                timestamp: Date().timeIntervalSince1970
            ))
        }

        return vectors
    }

    private func detectWagglePatterns() -> [WaggleMovementPattern] {
        guard movementBuffer.count >= 10 else { return [] }

        var patterns: [WaggleMovementPattern] = []

        // Analyze movement buffer for waggle dance characteristics
        let windowSize = 20
        for i in 0..<(movementBuffer.count - windowSize) {
            let window = Array(movementBuffer[i..<(i + windowSize)])

            if isWagglePattern(window) {
                let pattern = extractPattern(from: window)
                patterns.append(pattern)
            }
        }

        return patterns
    }

    private func isWagglePattern(_ vectors: [BeeMovementVector]) -> Bool {
        // Check for characteristic figure-8 pattern
        let velocities = vectors.map { $0.velocity }
        let avgVelocity = velocities.reduce(0, +) / Double(velocities.count)

        // Look for oscillating movement with high frequency components
        let highFreqCount = velocities.filter { $0 > avgVelocity * 1.5 }.count
        return Double(highFreqCount) / Double(velocities.count) > 0.3
    }

    private func extractPattern(from vectors: [BeeMovementVector]) -> WaggleMovementPattern {
        let startTime = vectors.first?.timestamp ?? 0
        let endTime = vectors.last?.timestamp ?? 0
        let duration = endTime - startTime

        // Calculate dominant angle using FFT-like analysis
        let angles = vectors.map { atan2($0.y, $0.x) }
        let dominantAngle = angles.reduce(0, +) / Double(angles.count)

        // Estimate wing beat frequency from velocity oscillations
        let velocities = vectors.map { $0.velocity }
        let frequency = estimateFrequency(from: velocities)

        // Calculate movement amplitude
        let positions = vectors.map { simd_double2($0.x, $0.y) }
        let amplitude = calculateAmplitude(positions)

        return WaggleMovementPattern(
            angle: dominantAngle,
            duration: duration,
            frequency: frequency,
            amplitude: amplitude,
            timestamp: Date()
        )
    }

    private func estimateFrequency(from signal: [Double]) -> Double {
        // Simplified frequency estimation using zero crossings
        var crossings = 0
        let mean = signal.reduce(0, +) / Double(signal.count)

        for i in 1..<signal.count {
            if (signal[i - 1] - mean) * (signal[i] - mean) < 0 {
                crossings += 1
            }
        }

        return Double(crossings) / 2.0 // Convert zero crossings to frequency estimate
    }

    private func calculateAmplitude(_ positions: [simd_double2]) -> Double {
        guard !positions.isEmpty else { return 0 }

        let center = positions.reduce(simd_double2(0, 0)) { $0 + $1 } / Double(positions.count)
        let distances = positions.map { simd_length($0 - center) }
        return distances.max() ?? 0
    }
}

// MARK: - Waggle Dance Compiler
class WaggleDanceCompiler {
    private let visionProcessor = WaggleDanceVisionProcessor()
    private var patternHistory: [WaggleMovementPattern] = []

    // Compilation state
    private var instructionPointer: Int = 0
    private var compilationStack: [Any] = []

    func compileFromWaggleDance(_ videoFrames: [[Double]]) -> CompiledBioCode {
        var allPatterns: [WaggleMovementPattern] = []

        // Process all video frames
        for frame in videoFrames {
            let patterns = visionProcessor.processFrameData(frame)
            allPatterns.append(contentsOf: patterns)
        }

        patternHistory.append(contentsOf: allPatterns)

        // Convert waggle patterns to computational instructions
        return translatePatternsToCode(allPatterns)
    }

    private func translatePatternsToCode(_ patterns: [WaggleMovementPattern]) -> CompiledBioCode {
        var instructions: [BioInstruction] = []

        for pattern in patterns {
            let instruction = waggleToInstruction(pattern)
            instructions.append(instruction)
        }

        return CompiledBioCode(
            instructions: instructions,
            sourcePatterns: patterns,
            compilationTimestamp: Date(),
            energyLevel: calculateEnergyLevel(patterns)
        )
    }

    private func waggleToInstruction(_ pattern: WaggleMovementPattern) -> BioInstruction {
        // Map waggle dance parameters to computational operations
        let operation: BioOperation

        switch pattern.frequency {
        case 0..<50:
            operation = .load(value: pattern.amplitude)
        case 50..<100:
            operation = .store(address: Int(pattern.angle * 100))
        case 100..<200:
            operation = .compute(function: .add, operands: [pattern.distance, pattern.amplitude])
        case 200..<300:
            operation = .branch(condition: pattern.amplitude > 10.0, target: Int(pattern.direction))
        default:
            operation = .transform(matrix: createTransformMatrix(from: pattern))
        }

        return BioInstruction(
            operation: operation,
            energy: pattern.duration * pattern.frequency,
            timestamp: pattern.timestamp,
            sourcePattern: pattern
        )
    }

    private func createTransformMatrix(from pattern: WaggleMovementPattern) -> simd_double3x3 {
        let angle = pattern.angle
        let scale = pattern.amplitude / 100.0

        return simd_double3x3(
            simd_double3(cos(angle) * scale, -sin(angle) * scale, 0),
            simd_double3(sin(angle) * scale, cos(angle) * scale, 0),
            simd_double3(0, 0, 1)
        )
    }

    private func calculateEnergyLevel(_ patterns: [WaggleMovementPattern]) -> Double {
        return patterns.reduce(0) { total, pattern in
            total + (pattern.frequency * pattern.duration * pattern.amplitude)
        }
    }
}

// MARK: - Bio Instruction Set
enum BioOperation {
    case load(value: Double)
    case store(address: Int)
    case compute(function: ComputeFunction, operands: [Double])
    case branch(condition: Bool, target: Int)
    case transform(matrix: simd_double3x3)
    case ferment(substrate: String, time: TimeInterval)
    case quantumEntangle(qubits: [Int])
}

enum ComputeFunction {
    case add, multiply, fibonacci, factorial, prime
}

struct BioInstruction {
    let operation: BioOperation
    let energy: Double
    let timestamp: Date
    let sourcePattern: WaggleMovementPattern
}

struct CompiledBioCode {
    let instructions: [BioInstruction]
    let sourcePatterns: [WaggleMovementPattern]
    let compilationTimestamp: Date
    let energyLevel: Double

    func execute() -> BioExecutionResult {
        var result = BioExecutionResult()

        for instruction in instructions {
            switch instruction.operation {
            case .load(let value):
                result.accumulator = value
            case .store(let address):
                result.memory[address] = result.accumulator
            case .compute(let function, let operands):
                result.accumulator = performComputation(function, operands)
            case .branch(let condition, let target):
                if condition {
                    result.programCounter = target
                }
            case .transform(let matrix):
                result.transformationMatrix = matrix
            case .ferment(let substrate, let time):
                result.fermentationProducts.append((substrate, time))
            case .quantumEntangle(let qubits):
                result.entangledQubits.append(contentsOf: qubits)
            }
        }

        return result
    }

    private func performComputation(_ function: ComputeFunction, _ operands: [Double]) -> Double {
        switch function {
        case .add:
            return operands.reduce(0, +)
        case .multiply:
            return operands.reduce(1, *)
        case .fibonacci:
            let n = Int(operands.first ?? 0)
            return Double(fibonacci(n))
        case .factorial:
            let n = Int(operands.first ?? 0)
            return Double(factorial(n))
        case .prime:
            let n = Int(operands.first ?? 0)
            return isPrime(n) ? 1.0 : 0.0
        }
    }

    private func fibonacci(_ n: Int) -> Int {
        guard n > 1 else { return n }
        var a = 0, b = 1
        for _ in 2...n {
            let temp = a + b
            a = b
            b = temp
        }
        return b
    }

    private func factorial(_ n: Int) -> Int {
        guard n > 0 else { return 1 }
        return n * factorial(n - 1)
    }

    private func isPrime(_ n: Int) -> Bool {
        guard n > 1 else { return false }
        guard n > 3 else { return true }
        guard n % 2 != 0 && n % 3 != 0 else { return false }

        var i = 5
        while i * i <= n {
            if n % i == 0 || n % (i + 2) == 0 {
                return false
            }
            i += 6
        }
        return true
    }
}

struct BioExecutionResult {
    var accumulator: Double = 0
    var memory: [Int: Double] = [:]
    var programCounter: Int = 0
    var transformationMatrix: simd_double3x3 = matrix_identity_double3x3
    var fermentationProducts: [(String, TimeInterval)] = []
    var entangledQubits: [Int] = []
}