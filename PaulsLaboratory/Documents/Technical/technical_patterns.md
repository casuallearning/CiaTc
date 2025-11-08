# Technical Patterns - Van Gogh Fractal Painting AI Compiler

## Core Architecture Patterns

### 1. Artistic-Computational Fusion Pattern
- **VanGoghCompiler class**: Transforms CV-analyzed brushstrokes into executable LLVM IR
- **FractalMemoryManager**: Uses Mandelbrot set calculations for memory address allocation
- **BrushstrokeOpcode enum**: Maps painting techniques to computational primitives

### 2. Computer Vision Pipeline Pattern
- **OpenCV + MediaPipe integration**: Vectorizes high-resolution Van Gogh paintings
- **CVPixelBuffer processing**: Real-time brushstroke analysis and vectorization
- **Edge detection algorithms**: Extract directional vectors from artistic patterns

### 3. GPU-Accelerated Execution Pattern
- **WebGL fragment shaders**: Execute fractal computations based on painting samples
- **Metal Performance Shaders**: Mandelbrot-guided garbage collection
- **Core Graphics CALayer subclasses**: Live painting visualization during code execution

### 4. LLVM Custom Backend Pattern
- **Brushstroke Assembly Language (BSAL)**: Domain-specific language for artistic compilation
- **ArtisticLLVMBackend**: Converts painting techniques to optimized machine code
- **Fractal instruction mapping**: Swirls→loops, colors→types, pressure→computational weight

## Implementation Technologies
- **Swift + Swift Macros**: Core language with gesture-to-function expansion
- **OpenCV 4.x**: Computer vision for brushstroke analysis
- **LLVM 15+**: Custom compilation backend
- **WebGL 2.0**: GPU-accelerated fractal computation
- **Metal Performance Shaders**: iOS-optimized GPU operations
- **Core Graphics**: Real-time painting interface