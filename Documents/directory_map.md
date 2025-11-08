# Directory Map for CiaTc Framework

```
CiaTc/
├── Core Orchestration
│   ├── band_orchestrator_main.py         # Pre-analysis orchestrator (UserPromptSubmit hook)
│   ├── band_orchestrator_stop.py         # Stop hook orchestrator
│   ├── conductor_agent.py                # Intelligent agent selection conductor
│   ├── smart_orchestrator.py             # Adaptive orchestrator with complexity analysis & caching
│   ├── bootstrap_band.py                 # Bootstrap initialization
│   ├── agent_lock.py                     # Multi-agent lock coordination
│   ├── gilfoyle_agent.py                 # Code analysis specialist
│   ├── prompt_loader.py                  # Prompt file loader utility
│   ├── archived_janitors_orchestrator.py # Archived post-analysis janitors
│   └── WaggleDanceCompiler.swift         # Waggle dance pattern compiler
│
├── Shell Scripts
│   ├── activate_ciatc_final.sh           # Activate CiaTc framework
│   ├── deactivate_ciatc_final.sh         # Deactivate CiaTc framework
│   ├── activate_smart_band.sh            # Activate smart band mode
│   ├── band_statusline.sh                # Band statusline monitor script
│   └── demo_band_statusline.sh           # Demo of Band statusline capabilities
│
├── Testing
│   ├── test_band_debug.py                # Band orchestrator debugging
│   ├── test_band_performance.py          # Performance benchmarking
│   └── test_conductor_nuance.py          # Conductor agent testing
│
├── Prompts (Band Members & Specialists)
│   ├── conductor.md                      # Conductor orchestration logic
│   ├── john.md                           # Directory structure analyst
│   ├── george.md                         # Narrative manager
│   ├── pete.md                           # Technical specialist
│   ├── paul.md                           # Wild ideas generator
│   ├── ringo.md                          # Context synthesizer
│   ├── marie_active.md                   # Active organizational review
│   ├── README.md                         # Prompts documentation
│   └── archived/                         # Archived prompt versions
│       ├── descartes.md
│       ├── feynman.md
│       └── marie.md
│
├── Documents
│   ├── file_index.md                     # This file - categorized file index
│   ├── directory_map.md                  # Complete project structure
│   │
│   ├── Narratives/                       # Narrative documentation
│   │   ├── narrative_index.md            # Narrative index
│   │   ├── Core.md                       # Core components narrative
│   │   ├── Documentation.md              # Documentation narrative
│   │   ├── Prompts.md                    # Prompts narrative
│   │   ├── Scripts.md                    # Scripts narrative
│   │   ├── Tests.md                      # Tests narrative
│   │   ├── Config.md                     # Configuration narrative
│   │   ├── Context.md                    # Context narrative
│   │   ├── Output.md                     # Output narrative
│   │   ├── Research.md                   # Research narrative
│   │   ├── iOS_Applications.md           # iOS apps narrative
│   │   └── Technical.md                  # Technical narrative
│   │
│   ├── Technical/                        # Technical documentation
│   │   ├── index.md                      # Technical docs index
│   │   ├── dependencies.md               # External dependencies
│   │   ├── technical_patterns.md         # Design patterns
│   │   ├── implementation_log.md         # Implementation history
│   │   ├── architectural_patterns.md     # Architecture patterns
│   │   └── operational_patterns.md       # Operational patterns
│   │
│   └── PaulsMadRamblings/                # Experimental concepts
│       ├── BioluminescentQuantumInterferometry.md
│       ├── CardiacConductionOrchestration.md
│       ├── ComputationalGelElectrophoresisStatusline.md
│       ├── ComputationalSpoorTracking.md
│       ├── CRISPRDocumentationGenomeEditing.md
│       ├── FungalFugueNetworks.md
│       ├── HolographicWaveletCompression.md
│       ├── PolyrhythmicHookSyncopation.md
│       ├── ProteinFoldingResponseAnnealing.md
│       ├── PulsarTimingArrayPerformanceGravitometry.md
│       ├── SeismologicalChangeDetection.md
│       ├── SuperconductingContextPhaseTransition.md
│       └── TidePoolOrchestrationSystem.md
│
├── PaulsLaboratory/                      # Experimental research lab
│   ├── create_ios_app.swift             # iOS app generator script
│   │
│   ├── FractalPaintingCompiler/         # Van Gogh Fractal Compiler iOS App
│   │   ├── AppDelegate.swift
│   │   ├── SceneDelegate.swift
│   │   ├── VanGoghCompiler.swift        # Core compiler engine
│   │   ├── VanGoghCompilerViewController.swift
│   │   ├── PaintingCanvas.swift
│   │   ├── FractalMemoryManager.swift
│   │   ├── Info.plist
│   │   ├── LaunchScreen.storyboard
│   │   ├── Main.storyboard
│   │   ├── Base.lproj/
│   │   │   ├── LaunchScreen.storyboard
│   │   │   └── Main.storyboard
│   │   └── Assets.xcassets/
│   │       ├── Contents.json
│   │       └── AppIcon.appiconset/
│   │           └── Contents.json
│   │
│   ├── QuantumProductivityApp/          # Quantum Productivity iOS App
│   │   └── Quantum Productivity/
│   │       ├── Quantum Productivity/
│   │       │   ├── Quantum_ProductivityApp.swift
│   │       │   ├── ContentView.swift
│   │       │   ├── Item.swift
│   │       │   └── Assets.xcassets/
│   │       │       ├── Contents.json
│   │       │       ├── AccentColor.colorset/
│   │       │       │   └── Contents.json
│   │       │       └── AppIcon.appiconset/
│   │       │           └── Contents.json
│   │       └── Quantum Productivity.xcodeproj/
│   │           ├── project.pbxproj
│   │           ├── xcuserdata/
│   │           │   └── philhudson.xcuserdatad/
│   │           │       └── xcschemes/
│   │           │           └── xcschememanagement.plist
│   │           └── project.xcworkspace/
│   │               ├── contents.xcworkspacedata
│   │               └── xcuserdata/
│   │                   └── philhudson.xcuserdatad/
│   │                       └── UserInterfaceState.xcuserstate
│   │
│   ├── VanGoghFractalCompiler.app/      # Compiled application bundle
│   │   ├── VanGoghFractalCompiler       # Binary
│   │   └── Info.plist
│   │
│   ├── VanGoghFractalDemo.playground/   # Swift Playground demo
│   │   ├── Contents.swift
│   │   └── contents.xcplayground
│   │
│   └── Documents/                        # Laboratory documentation
│       ├── file_index.md
│       ├── directory_map.md
│       ├── SUCCESS_VanGoghFractalCompiler.md
│       ├── ULTIMATE_BREAKTHROUGH_FungalFugueNetwork.md
│       ├── EXPERIMENT_SUCCESS_BiologicalNeuralNetwork.md
│       │
│       ├── Narratives/                   # Research narratives
│       │   ├── Adaptive_AI_Systems.md
│       │   ├── Artistic_Computing.md
│       │   ├── Bio-Digital_Integration.md
│       │   ├── Biomimetic_Architecture.md
│       │   ├── Breakthrough_Documentation.md
│       │   ├── Compiled_Applications.md
│       │   ├── Core_Applications.md
│       │   ├── Core_Documentation.md
│       │   ├── Experimental_Concepts.md
│       │   ├── iOS_Applications.md
│       │   ├── Quantum_UI_Concepts.md
│       │   └── Technical_Documentation.md
│       │
│       ├── Technical/                    # Technical docs
│       │   ├── implementation_log.md
│       │   ├── dependencies.md
│       │   └── technical_patterns.md
│       │
│       └── PaulsMadRamblings/            # Experimental concepts
│           ├── BiologicalNeuralNetworkAppArchitecture.md
│           ├── ChaosOrigamiHelloProtocol.md
│           ├── FermentationQuantumWaggleDanceCompiler.md
│           ├── FractalPaintingAICompiler.md
│           ├── HiveFugueProtocolWellnessApp.md
│           ├── JungianFluidDynamicsDreamComputer.md
│           └── MycorrhizalMealScheduleSymbiosis.md
│
├── Cache & Runtime
│   ├── .band_cache/                      # Performance cache
│   │   └── orchestrator_cache.json       # Orchestrator state cache
│   ├── __pycache__/                      # Python bytecode cache
│   │   ├── agent_lock.cpython-312.pyc
│   │   ├── conductor_agent.cpython-312.pyc
│   │   └── smart_orchestrator.cpython-312.pyc
│   ├── Config/                           # Configuration storage
│   ├── Context/                          # Context storage
│   ├── TestFiles/                        # Test files output
│   └── Transcripts/                      # Conversation transcripts
│
└── Documentation
    ├── README.md                         # Main project documentation
    └── SMART_BAND_README.md              # Smart band system documentation
```

## Project Structure Summary

**Core Framework**: Multi-agent orchestration system with Conductor intelligence
**Band Members**: 5 specialized agents (John, George, Pete, Paul, Ringo)
**PaulsLaboratory**: Experimental iOS applications and research concepts
**Documentation**: Comprehensive narrative and technical documentation system
**Cache System**: Intelligent caching for performance optimization

**Total Files**: 140+ files organized across 9 major categories
**Main Languages**: Python, Swift, Markdown, Shell Scripts
**iOS Applications**: 2 active projects (FractalPaintingCompiler, QuantumProductivityApp)
**Statusline Monitoring**: Band orchestrator with real-time performance metrics

**Last Updated**: November 8, 2025 14:02 (Refreshed)
- Most recent changes: Technical documentation updates (implementation_log.md, index.md, technical_patterns.md, dependency_graph.json), Scripts.md narrative
- Core files verified: All 12 Python orchestration scripts operational
- Documentation: Complete narrative system (25+ files) + technical documentation (7 files) + experimental concepts (20+ files)
- iOS Development: 2 active applications with full Xcode project configuration
- Performance: Smart orchestrator with MD5-based change detection and adaptive timeouts (60-180s)
- Integration: UserPromptSubmit and Stop hook orchestration with Conductor decision-making
