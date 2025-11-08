# Dependencies - Van Gogh Fractal Painting AI Compiler

## Core Dependencies

### iOS Framework Dependencies
- **UIKit**: Base iOS application framework
- **CoreGraphics**: Real-time painting canvas and layer management
- **Metal**: GPU-accelerated fractal computations and memory management
- **MetalPerformanceShaders**: Optimized Mandelbrot set calculations
- **Vision**: High-level computer vision for brushstroke analysis
- **WebKit**: WebGL fragment shader execution via WKWebView

### Third-Party Libraries
- **OpenCV for iOS**: Computer vision library for detailed brushstroke vectorization
  - Version: 4.x recommended
  - Integration: Swift bridging headers
  - Performance Risk: Large binary size, memory usage

### Custom LLVM Integration
- **LLVM C++ Libraries**: Custom compilation backend
  - Components: Core, CodeGen, ExecutionEngine
  - Integration Challenge: Swift-C++ interoperability
  - Memory Management: Manual memory handling required

### WebGL Shader Dependencies
- **WebGL 2.0**: Fragment shader execution environment
- **GLSL ES 3.0**: Shader language for fractal computations
- **Canvas API**: Integration with iOS WebKit view

## Technical Debt Considerations
- **OpenCV Size**: Large framework increases app bundle size significantly
- **LLVM Complexity**: C++ integration requires careful memory management
- **GPU Memory**: Metal shaders need efficient texture memory handling
- **Real-time Performance**: Computer vision analysis must maintain 60fps for live painting

## Performance Considerations
- **Memory Usage**: Fractal calculations generate large texture data
- **CPU/GPU Balance**: Offload computations to Metal shaders where possible
- **I/O Bottlenecks**: High-resolution Van Gogh painting analysis may require streaming
- **Battery Impact**: Intensive GPU usage needs power optimization