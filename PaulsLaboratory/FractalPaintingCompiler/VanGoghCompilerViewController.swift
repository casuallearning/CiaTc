import UIKit
import Metal
import MetalKit

class VanGoghCompilerViewController: UIViewController {
    private var paintingCanvas: PaintingCanvas!
    private var vanGoghCompiler: VanGoghCompiler!
    private var fractalMemoryManager: FractalMemoryManager!

    private var compileButton: UIButton!
    private var codeTextView: UITextView!
    private var statusLabel: UILabel!

    override func viewDidLoad() {
        super.viewDidLoad()

        setupArtisticInterface()
        initializeFractalSystems()
        startVanGoghCompilation()
    }

    private func setupArtisticInterface() {
        view.backgroundColor = .black

        paintingCanvas = PaintingCanvas(frame: CGRect(x: 0, y: 100, width: view.bounds.width, height: 400))
        view.addSubview(paintingCanvas)

        codeTextView = UITextView(frame: CGRect(x: 20, y: 520, width: view.bounds.width - 40, height: 150))
        codeTextView.backgroundColor = UIColor(red: 0.1, green: 0.1, blue: 0.2, alpha: 1.0)
        codeTextView.textColor = .yellow
        codeTextView.font = UIFont(name: "Courier", size: 12)
        codeTextView.text = """
        // Van Gogh Code Being Painted...
        func starryNightAlgorithm() {
            let swirls = generateFractalSwirls()
            paintBrushstrokes(swirls)
        }
        """
        view.addSubview(codeTextView)

        compileButton = UIButton(frame: CGRect(x: 50, y: 690, width: view.bounds.width - 100, height: 50))
        compileButton.setTitle("🎨 COMPILE WITH BRUSHSTROKES", for: .normal)
        compileButton.backgroundColor = UIColor(red: 0.2, green: 0.4, blue: 0.8, alpha: 1.0)
        compileButton.layer.cornerRadius = 25
        compileButton.addTarget(self, action: #selector(startArtisticCompilation), for: .touchUpInside)
        view.addSubview(compileButton)

        statusLabel = UILabel(frame: CGRect(x: 20, y: 750, width: view.bounds.width - 40, height: 60))
        statusLabel.textColor = .white
        statusLabel.numberOfLines = 3
        statusLabel.textAlignment = .center
        statusLabel.font = UIFont.systemFont(ofSize: 14)
        statusLabel.text = "Van Gogh Fractal Compiler Ready\n🌀 Mandelbrot Memory Initialized\n✨ Artistic Optimization Engine Loaded"
        view.addSubview(statusLabel)
    }

    private func initializeFractalSystems() {
        fractalMemoryManager = FractalMemoryManager()
        vanGoghCompiler = VanGoghCompiler(memoryManager: fractalMemoryManager)

        print("🎨 Fractal systems initialized with Van Gogh patterns")
    }

    private func startVanGoghCompilation() {
        DispatchQueue.global(qos: .userInteractive).async { [weak self] in
            self?.simulateBrushstrokeCompilation()
        }
    }

    @objc private func startArtisticCompilation() {
        statusLabel.text = "🎨 Analyzing brushstrokes...\n🌀 Converting swirls to bytecode...\n⚡ Executing fractal instructions..."

        let code = codeTextView.text ?? ""
        vanGoghCompiler.compilePaintingToCode(sourceCode: code) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let paintedCode):
                    self?.statusLabel.text = "✅ Artistic compilation complete!\n🎨 \(paintedCode.brushstrokeCount) brushstrokes converted\n🌟 Fractal execution successful"
                    self?.paintingCanvas.displayCompiledArt(paintedCode)
                case .failure(let error):
                    self?.statusLabel.text = "❌ Artistic compilation failed!\n🎨 \(error.localizedDescription)\n🔧 Adjusting Van Gogh parameters..."
                }
            }
        }
    }

    private func simulateBrushstrokeCompilation() {
        var brushstrokeCount = 0

        while brushstrokeCount < 100 {
            let swirl = vanGoghCompiler.generateFractalSwirl()

            DispatchQueue.main.async { [weak self] in
                self?.paintingCanvas.addBrushstroke(swirl)
            }

            Thread.sleep(forTimeInterval: 0.1)
            brushstrokeCount += 1
        }
    }
}