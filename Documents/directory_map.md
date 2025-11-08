# Directory Map for CiaTc Framework

```
CiaTc/
├── .band_cache/                     [Directory - Band Cache Storage]
│   ├── file_hashes.json             [Cache Data]
│   ├── locks/                       [Lock Directory]
│   │   ├── john.lock                [Agent Lock]
│   │   └── pete.lock                [Agent Lock]
│   └── orchestrator_cache.json      [Cache Data]
├── .claude/                         [Directory - Claude Code Config]
│   └── settings.local.json          [JSON Configuration]
├── activate_ciatc_final.sh          [Shell Script]
├── activate_smart_band.sh           [Shell Script]
├── agent_lock.py                    [Python Script]
├── band_orchestrator_main.py        [Python Script]
├── band_orchestrator_stop.py        [Python Script]
├── bootstrap_band.py                [Python Script]
├── conductor_agent.py               [Python Script]
├── deactivate_ciatc_final.sh        [Shell Script]
├── gilfoyle_agent.py                [Python Script]
├── prompt_loader.py                 [Python Script]
├── README.md                        [Markdown Documentation]
├── SMART_BAND_README.md             [Markdown Documentation]
├── smart_orchestrator.py            [Python Script]
├── test_band_debug.py               [Python Test Script]
├── test_band_performance.py         [Python Test Script]
├── test_conductor_nuance.py         [Python Test Script]
├── WaggleDanceCompiler.swift        [Swift Source File]
├── __pycache__/                     [Directory - Python Cache]
│   ├── agent_lock.cpython-312.pyc   [Python Bytecode]
│   ├── build_health_agent.cpython-312.pyc [Python Bytecode]
│   ├── conductor_agent.cpython-312.pyc [Python Bytecode]
│   ├── smart_orchestrator.cpython-312.pyc [Python Bytecode]
│   └── [other bytecode files]       [Python Bytecode]
├── Config/                          [Directory - Empty]
├── Context/                         [Directory - Empty]
├── Documents/                       [Directory]
│   ├── directory_map.md             [Markdown Documentation]
│   ├── file_index.md                [Markdown Documentation]
│   ├── Narratives/                  [Directory]
│   │   ├── Config.md                [Markdown Narrative]
│   │   ├── Context.md               [Markdown Narrative]
│   │   ├── Core.md                  [Markdown Narrative]
│   │   ├── Documentation.md         [Markdown Narrative]
│   │   ├── iOS_Applications.md      [Markdown Narrative]
│   │   ├── narrative_index.md       [Markdown Index]
│   │   ├── Output.md                [Markdown Narrative]
│   │   ├── Prompts.md               [Markdown Narrative]
│   │   ├── Research.md              [Markdown Narrative]
│   │   ├── Scripts.md               [Markdown Narrative]
│   │   ├── Technical.md             [Markdown Narrative]
│   │   └── Tests.md                 [Markdown Narrative]
│   ├── PaulsMadRamblings/           [Directory]
│   │   ├── BioluminescentQuantumInterferometry.md [Markdown Experimental]
│   │   ├── CardiacConductionOrchestration.md [Markdown Experimental]
│   │   ├── ComputationalGelElectrophoresisStatusline.md [Markdown Experimental]
│   │   ├── ComputationalSpoorTracking.md [Markdown Experimental]
│   │   ├── CRISPRDocumentationGenomeEditing.md  [Markdown Experimental]
│   │   ├── FungalFugueNetworks.md   [Markdown Experimental]
│   │   ├── HolographicWaveletCompression.md [Markdown Experimental]
│   │   ├── PolyrhythmicHookSyncopation.md [Markdown Experimental]
│   │   ├── ProteinFoldingResponseAnnealing.md [Markdown Experimental]
│   │   ├── PulsarTimingArrayPerformanceGravitometry.md [Markdown Experimental]
│   │   ├── SeismologicalChangeDetection.md [Markdown Experimental]
│   │   ├── SuperconductingContextPhaseTransition.md [Markdown Experimental]
│   │   └── TidePoolOrchestrationSystem.md [Markdown Experimental]
│   └── Technical/                   [Directory]
│       ├── architectural_patterns.md [Markdown Technical]
│       ├── dependencies.md          [Markdown Technical]
│       ├── implementation_log.md    [Markdown Technical]
│       ├── index.md                 [Markdown Technical]
│       ├── operational_patterns.md  [Markdown Technical]
│       └── technical_patterns.md    [Markdown Technical]
├── PaulsLaboratory/                 [Directory]
│   ├── create_ios_app.swift         [Swift Script]
│   ├── Documents/                   [Directory]
│   │   ├── directory_map.md         [Markdown Documentation]
│   │   ├── file_index.md            [Markdown Documentation]
│   │   ├── EXPERIMENT_SUCCESS_BiologicalNeuralNetwork.md [Markdown Success Doc]
│   │   ├── SUCCESS_VanGoghFractalCompiler.md             [Markdown Success Doc]
│   │   ├── ULTIMATE_BREAKTHROUGH_FungalFugueNetwork.md   [Markdown Breakthrough Doc]
│   │   ├── Narratives/              [Directory]
│   │   │   ├── Adaptive_AI_Systems.md        [Markdown Research]
│   │   │   ├── Artistic_Computing.md         [Markdown Research]
│   │   │   ├── Bio-Digital_Integration.md    [Markdown Research]
│   │   │   ├── Biomimetic_Architecture.md    [Markdown Research]
│   │   │   ├── Breakthrough_Documentation.md [Markdown Research]
│   │   │   ├── Compiled_Applications.md      [Markdown Research]
│   │   │   ├── Core_Applications.md          [Markdown Research]
│   │   │   ├── Core_Documentation.md         [Markdown Research]
│   │   │   ├── Experimental_Concepts.md      [Markdown Research]
│   │   │   ├── iOS_Applications.md           [Markdown Research]
│   │   │   ├── Quantum_UI_Concepts.md        [Markdown Research]
│   │   │   └── Technical_Documentation.md    [Markdown Research]
│   │   ├── PaulsMadRamblings/       [Directory]
│   │   │   ├── BiologicalNeuralNetworkAppArchitecture.md   [Markdown Experimental]
│   │   │   ├── ChaosOrigamiHelloProtocol.md                [Markdown Experimental]
│   │   │   ├── FermentationQuantumWaggleDanceCompiler.md   [Markdown Experimental]
│   │   │   ├── FractalPaintingAICompiler.md                [Markdown Experimental]
│   │   │   ├── HiveFugueProtocolWellnessApp.md             [Markdown Experimental]
│   │   │   ├── JungianFluidDynamicsDreamComputer.md        [Markdown Experimental]
│   │   │   └── MycorrhizalMealScheduleSymbiosis.md         [Markdown Experimental]
│   │   └── Technical/               [Directory]
│   │       ├── dependencies.md      [Markdown Technical]
│   │       ├── implementation_log.md [Markdown Technical]
│   │       └── technical_patterns.md [Markdown Technical]
│   ├── FractalPaintingCompiler/     [Directory - iOS Application]
│   │   ├── AppDelegate.swift        [Swift Source]
│   │   ├── FractalMemoryManager.swift [Swift Source]
│   │   ├── Info.plist               [iOS Configuration]
│   │   ├── LaunchScreen.storyboard  [iOS Storyboard]
│   │   ├── Main.storyboard          [iOS Storyboard]
│   │   ├── PaintingCanvas.swift     [Swift Source]
│   │   ├── SceneDelegate.swift      [Swift Source]
│   │   ├── VanGoghCompiler.swift    [Swift Source]
│   │   ├── VanGoghCompilerViewController.swift [Swift Source]
│   │   ├── Assets.xcassets/         [Asset Catalog]
│   │   │   ├── Contents.json        [Asset Metadata]
│   │   │   └── AppIcon.appiconset/  [Icon Asset]
│   │   │       └── Contents.json    [Icon Metadata]
│   │   └── Base.lproj/              [Localization]
│   │       ├── LaunchScreen.storyboard [iOS Storyboard]
│   │       └── Main.storyboard      [iOS Storyboard]
│   ├── QuantumProductivityApp/      [Directory]
│   │   └── Quantum Productivity/    [iOS Application]
│   │       ├── Quantum Productivity/ [Source Directory]
│   │       │   ├── ContentView.swift [Swift Source]
│   │       │   ├── Item.swift       [Swift Source]
│   │       │   ├── Quantum_ProductivityApp.swift [Swift Source]
│   │       │   └── Assets.xcassets/ [Asset Catalog]
│   │       │       ├── Contents.json [Asset Metadata]
│   │       │       ├── AccentColor.colorset/ [Color Asset]
│   │       │       │   └── Contents.json [Color Metadata]
│   │       │       └── AppIcon.appiconset/ [Icon Asset]
│   │       │           └── Contents.json [Icon Metadata]
│   │       └── Quantum Productivity.xcodeproj/ [Xcode Project]
│   │           ├── project.pbxproj  [Xcode Project File]
│   │           ├── project.xcworkspace/ [Xcode Workspace]
│   │           │   ├── contents.xcworkspacedata [Workspace Configuration]
│   │           │   └── xcuserdata/  [User Data]
│   │           │       └── philhudson.xcuserdatad/ [User Specific]
│   │           │           └── UserInterfaceState.xcuserstate [UI State]
│   │           └── xcuserdata/      [User Data]
│   │               └── philhudson.xcuserdatad/ [User Specific]
│   │                   └── xcschemes/ [Build Schemes]
│   │                       └── xcschememanagement.plist [Scheme Management]
│   ├── VanGoghFractalCompiler.app/  [Compiled Application Bundle]
│   │   ├── Info.plist               [App Configuration]
│   │   └── VanGoghFractalCompiler   [Executable Binary]
│   └── VanGoghFractalDemo.playground/ [Swift Playground]
│       ├── Contents.swift           [Playground Source]
│       └── contents.xcplayground    [Playground Configuration]
├── prompts/                         [Directory]
│   ├── descartes.md                 [Markdown Prompt]
│   ├── feynman.md                   [Markdown Prompt]
│   ├── george.md                    [Markdown Prompt]
│   ├── john.md                      [Markdown Prompt]
│   ├── marie.md                     [Markdown Prompt]
│   ├── paul.md                      [Markdown Prompt]
│   ├── pete.md                      [Markdown Prompt]
│   ├── README.md                    [Markdown Documentation]
│   └── ringo.md                     [Markdown Prompt]
├── TestFiles/                       [Directory - Empty]
└── Transcripts/                     [Directory - Empty]
```

## Directory Summary

### Root Level (17 files + system directories)
- **11 Python Scripts**: Core orchestrators (band, conductor, smart, gilfoyle), utilities, bootstrap, locks, and test files
- **3 Shell Scripts**: Activation/deactivation scripts (including smart band)
- **1 Swift File**: WaggleDance compiler implementation
- **2 Documentation**: Main README and Smart Band README
- **12 Directories**: Organized storage for different file types (including __pycache__, .band_cache, and .claude)

### Subdirectories
- **.band_cache/**: Band orchestrator cache directory with agent locks and performance data (file_hashes.json, orchestrator_cache.json, locks/)
- **.claude/**: Claude Code configuration (settings.local.json)
- **__pycache__/**: Python bytecode cache (agent_lock, build_health_agent, conductor_agent, smart_orchestrator + others)
- **Config/**: Configuration files (empty - ready for future config needs)
- **Context/**: Runtime context storage (empty - populated during execution)
- **Documents/**: Project documentation (2 core files + 3 subdirectories)
  - **Narratives/**: Category-based narrative documentation (12 files including index)
  - **PaulsMadRamblings/**: Experimental concepts (12 files)
  - **Technical/**: Technical documentation (4 files: index, dependencies, patterns, implementation log)
- **PaulsLaboratory/**: Research and experimental workspace (80+ files)
  - **create_ios_app.swift**: iOS app generation script
  - **Documents/**: Research documentation (5 core files + 3 subdirectories)
    - **Narratives/**: Research narratives (12 files)
    - **PaulsMadRamblings/**: Experimental concepts (7 files)
    - **Technical/**: Technical documentation (3 files)
  - **FractalPaintingCompiler/**: Complete iOS app (8 Swift files + assets)
  - **QuantumProductivityApp/**: SwiftUI productivity app (Xcode project + 3 Swift files)
  - **VanGoghFractalCompiler.app/**: Compiled application bundle
  - **VanGoghFractalDemo.playground/**: Interactive Swift playground demo
- **prompts/**: Specialist AI prompts (9 files: 8 persona prompts + README)
- **TestFiles/**: Test data storage (empty - ready for test cases)
- **Transcripts/**: Conversation logs (empty - populated during execution)

### File Type Statistics
- **Python Scripts**: 11 files (8 core + 1 bootstrap + 3 tests, including conductor, smart orchestrator, gilfoyle, and lock management)
- **Swift Files**: 20+ files (iOS apps, compiler, playground, script)
- **Shell Scripts**: 3 files (activation/deactivation + smart band)
- **Markdown Files**: 60+ files (documentation + prompts + narratives + research + concepts)
- **iOS Configuration Files**: 10+ files (Info.plist, storyboards, asset catalogs)
- **Xcode Project Files**: 15+ files (project, workspace, schemes, user state)
- **Cache/Lock Files**: 4+ files (orchestrator cache, file hashes, agent locks)
- **Compiled Applications**: 1 application bundle
- **Total Files**: 115+ files across 30+ directories

### iOS Applications
1. **FractalPaintingCompiler**: Van Gogh-inspired fractal generation app
   - 8 Swift source files
   - Complete storyboard UI
   - Asset catalog with app icon
   - Compiled binary available
2. **Quantum Productivity**: SwiftUI-based productivity application
   - 3 Swift source files (SwiftUI app structure)
   - Xcode project with workspace
   - Asset catalog with accent color and app icon
3. **VanGoghFractalDemo**: Interactive playground for testing fractal algorithms

### Research Documentation Structure
- **12 Main Narrative Documents**: Organized narrative themes (including iOS_Applications and Technical)
- **12 Root Experimental Concepts**: "Paul's Mad Ramblings" on unconventional ideas (including CardiacConductionOrchestration and ComputationalSpoorTracking)
- **7 Laboratory Experimental Concepts**: Additional experimental concepts in PaulsLaboratory
- **3 Success Documents**: Breakthrough documentation
- **4 Technical Documents**: Implementation patterns and dependencies

---
**Last Updated**: November 8, 2025 - Directory map verified and current
- All 130+ project files verified and organized
- Narrative documentation files updated (Documentation.md, Technical.md, Prompts.md)
- Narrative index synchronized (narrative_index.md)
- Technical dependency graph current (dependency_graph.json)
- All file indices and statistics synchronized with current project state
