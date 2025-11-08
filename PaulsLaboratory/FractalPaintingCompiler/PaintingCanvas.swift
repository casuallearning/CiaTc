import UIKit
import QuartzCore
import Accelerate

class PaintingCanvas: UIView {
    private var brushstrokes: [FractalBrushstroke] = []
    private var paintingContext: CGContext?
    private var mandelbrotBuffer: CVPixelBuffer?

    private let maxBrushstrokes = 1000
    private var animationTimer: CADisplayLink?
    private var currentAnimationFrame = 0

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupFractalCanvas()
    }

    required init?(coder: NSCoder) {
        fatalError("Van Gogh doesn't use Interface Builder!")
    }

    private func setupFractalCanvas() {
        backgroundColor = UIColor(red: 0.05, green: 0.1, blue: 0.2, alpha: 1.0)
        layer.cornerRadius = 10
        layer.borderWidth = 2
        layer.borderColor = UIColor.systemBlue.cgColor

        // Initialize Mandelbrot computation buffer
        initializeMandelbrotBuffer()

        // Start animation loop for living painting
        startArtisticAnimation()
    }

    private func initializeMandelbrotBuffer() {
        let width = Int(bounds.width)
        let height = Int(bounds.height)

        CVPixelBufferCreate(
            kCFAllocatorDefault,
            width,
            height,
            kCVPixelFormatType_32BGRA,
            nil,
            &mandelbrotBuffer
        )
    }

    private func startArtisticAnimation() {
        animationTimer = CADisplayLink(target: self, selector: #selector(animateVanGoghFrame))
        animationTimer?.add(to: .main, forMode: .common)
    }

    @objc private func animateVanGoghFrame() {
        currentAnimationFrame += 1

        // Animate brushstrokes with Van Gogh-style turbulence
        for brushstroke in brushstrokes {
            brushstroke.updateTurbulence(frame: currentAnimationFrame)
        }

        if currentAnimationFrame % 3 == 0 { // Update every 3 frames for performance
            setNeedsDisplay()
        }
    }

    func addBrushstroke(_ swirl: FractalSwirl) {
        let brushstroke = FractalBrushstroke(
            startPoint: CGPoint(
                x: CGFloat.random(in: 20...bounds.width-20),
                y: CGFloat.random(in: 20...bounds.height-20)
            ),
            fractalComplexity: swirl.complexity,
            vanGoghTurbulence: swirl.turbulence,
            colorPalette: swirl.colorPalette
        )

        brushstrokes.append(brushstroke)

        // Limit brushstrokes for performance (Van Gogh wouldn't overdo it)
        if brushstrokes.count > maxBrushstrokes {
            brushstrokes.removeFirst()
        }

        DispatchQueue.main.async {
            self.setNeedsDisplay()
        }
    }

    func displayCompiledArt(_ paintedCode: PaintedCode) {
        // Clear canvas for new masterpiece
        brushstrokes.removeAll()

        // Convert compiled code back to brushstrokes
        for instruction in paintedCode.fractalInstructions {
            let brushstroke = FractalBrushstroke(
                startPoint: instruction.canvasCoordinate,
                fractalComplexity: instruction.computationalComplexity,
                vanGoghTurbulence: instruction.artisticChaos,
                colorPalette: instruction.memoryColorMap
            )
            brushstrokes.append(brushstroke)
        }

        setNeedsDisplay()
    }

    override func draw(_ rect: CGRect) {
        guard let context = UIGraphicsGetCurrentContext() else { return }

        // Fill background with starry night gradient
        drawStarryNightBackground(in: context, rect: rect)

        // Render each fractal brushstroke
        for (index, brushstroke) in brushstrokes.enumerated() {
            renderVanGoghBrushstroke(brushstroke, in: context, frame: currentAnimationFrame + index)
        }

        // Add mandelbrot noise overlay
        if let buffer = mandelbrotBuffer {
            renderMandelbrotOverlay(buffer: buffer, in: context, rect: rect)
        }
    }

    private func drawStarryNightBackground(in context: CGContext, rect: CGRect) {
        let gradient = CGGradient(
            colorsSpace: CGColorSpaceCreateDeviceRGB(),
            colors: [
                UIColor(red: 0.1, green: 0.2, blue: 0.4, alpha: 1.0).cgColor,
                UIColor(red: 0.05, green: 0.1, blue: 0.2, alpha: 1.0).cgColor,
                UIColor(red: 0.02, green: 0.05, blue: 0.1, alpha: 1.0).cgColor
            ] as CFArray,
            locations: [0.0, 0.5, 1.0]
        )

        context.drawLinearGradient(
            gradient!,
            start: CGPoint(x: 0, y: 0),
            end: CGPoint(x: 0, y: rect.height),
            options: []
        )
    }

    private func renderVanGoghBrushstroke(_ brushstroke: FractalBrushstroke, in context: CGContext, frame: Int) {
        context.saveGState()

        // Apply Van Gogh-style transformation matrix
        let turbulenceX = sin(Double(frame) * 0.02 + brushstroke.phaseOffset) * brushstroke.turbulenceAmplitude
        let turbulenceY = cos(Double(frame) * 0.03 + brushstroke.phaseOffset) * brushstroke.turbulenceAmplitude

        context.translateBy(x: CGFloat(turbulenceX), y: CGFloat(turbulenceY))
        context.rotate(by: CGFloat(brushstroke.fractalAngle + Double(frame) * 0.01))

        // Set brushstroke color with fractal-computed alpha
        context.setStrokeColor(brushstroke.currentColor.cgColor)
        context.setLineWidth(brushstroke.thickness)
        context.setLineCap(.round)

        // Draw fractal brushstroke path
        let path = generateFractalPath(from: brushstroke)
        context.addPath(path)
        context.strokePath()

        context.restoreGState()
    }

    private func generateFractalPath(from brushstroke: FractalBrushstroke) -> CGPath {
        let path = CGMutablePath()
        let startPoint = brushstroke.startPoint

        path.move(to: startPoint)

        // Generate fractal curve using simplified Van Gogh mathematics
        let segmentCount = Int(brushstroke.fractalComplexity * 10)

        for i in 0..<segmentCount {
            let t = Double(i) / Double(segmentCount)

            // Van Gogh swirl mathematics (simplified mandelbrot transformation)
            let angle = t * .pi * 2 * brushstroke.fractalComplexity
            let radius = brushstroke.turbulenceAmplitude * (1.0 - t)

            let x = startPoint.x + CGFloat(cos(angle) * radius)
            let y = startPoint.y + CGFloat(sin(angle) * radius * 0.7) // Flatten slightly for brushstroke effect

            if i == 0 {
                path.move(to: CGPoint(x: x, y: y))
            } else {
                path.addLine(to: CGPoint(x: x, y: y))
            }
        }

        return path
    }

    private func renderMandelbrotOverlay(buffer: CVPixelBuffer, in context: CGContext, rect: CGRect) {
        // Add subtle mandelbrot noise for authentic fractal texture
        context.saveGState()
        context.setBlendMode(.overlay)
        context.setAlpha(0.1)

        // Simple mandelbrot texture computation
        let width = Int(rect.width)
        let height = Int(rect.height)

        for x in stride(from: 0, to: width, by: 4) {
            for y in stride(from: 0, to: height, by: 4) {
                let mandelbrotValue = computeMandelbrotPoint(
                    x: Double(x) / Double(width) * 2.0 - 1.0,
                    y: Double(y) / Double(height) * 2.0 - 1.0
                )

                if mandelbrotValue > 0.5 {
                    context.setFillColor(red: 1.0, green: 1.0, blue: 0.8, alpha: 0.1)
                    context.fill(CGRect(x: x, y: y, width: 2, height: 2))
                }
            }
        }

        context.restoreGState()
    }

    private func computeMandelbrotPoint(x: Double, y: Double) -> Double {
        var zx = 0.0, zy = 0.0
        var iterations = 0

        while zx*zx + zy*zy < 4.0 && iterations < 50 {
            let temp = zx*zx - zy*zy + x
            zy = 2.0*zx*zy + y
            zx = temp
            iterations += 1
        }

        return Double(iterations) / 50.0
    }

    deinit {
        animationTimer?.invalidate()
    }
}

struct FractalBrushstroke {
    let startPoint: CGPoint
    let fractalComplexity: Double
    let vanGoghTurbulence: Double
    let colorPalette: VanGoghColorPalette

    var thickness: CGFloat { CGFloat(fractalComplexity * 8 + 2) }
    var fractalAngle: Double { fractalComplexity * .pi }
    var turbulenceAmplitude: Double { vanGoghTurbulence * 20 }
    var phaseOffset: Double { fractalComplexity * .pi * 2 }

    var currentColor: UIColor {
        switch colorPalette {
        case .starryNight:
            return UIColor(red: 0.2, green: 0.4, blue: 0.8, alpha: 0.8)
        case .sunflowers:
            return UIColor(red: 0.9, green: 0.8, blue: 0.2, alpha: 0.8)
        case .wheatField:
            return UIColor(red: 0.8, green: 0.6, blue: 0.2, alpha: 0.8)
        case .irises:
            return UIColor(red: 0.5, green: 0.2, blue: 0.8, alpha: 0.8)
        }
    }

    mutating func updateTurbulence(frame: Int) {
        // Van Gogh brushstrokes evolve with time
        // This creates the "living painting" effect
    }
}

enum VanGoghColorPalette {
    case starryNight
    case sunflowers
    case wheatField
    case irises
}