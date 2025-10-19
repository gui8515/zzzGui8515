# KSP1 Contract Packs - Repository Structure

This repository contains 18 Contract Packs for Kerbal Space Program, all refactored to follow a consistent, standardized structure based on official KSP conventions.

## Repository Structure

All mods now follow this standard directory layout:

```
ContractPacks/
└── <ModName>/
    ├── Agencies/                      # Agency configurations and logos
    │   ├── <ModName>_Agency.cfg
    │   └── agency_logo.png
    │
    ├── Contracts/
    │   ├── Groups/                    # Contract group definitions
    │   │   └── <ModName>_Groups.cfg
    │   ├── Types/                     # Individual contract definitions
    │   │   └── <ModName>_Contract.cfg
    │   └── Icons/                     # Contract icons
    │       └── icon.png
    │
    ├── Localization/                  # Multi-language support
    │   ├── en-us.cfg                  # English
    │   ├── pt-br.cfg                  # Portuguese (Brazil)
    │   └── es-es.cfg                  # Spanish (Spain)
    │
    ├── Patches/
    │   ├── ModuleManager/             # General MM patches
    │   │   └── MM_Patch.cfg
    │   └── Compatibility/             # Mod compatibility patches
    │       ├── Strategia.cfg
    │       └── Kerbalism.cfg
    │
    ├── Plugins/                       # DLL files (if applicable)
    │   └── <ModName>.dll
    │
    ├── Flags/                         # Custom flags (if applicable)
    ├── Textures/                      # Additional textures
    │   ├── UI/
    │   └── Logos/
    │
    ├── README.md                      # Mod documentation
    └── LICENSE.txt                    # License information
```

## Included Mods

### 1. AdvancedProgression
Progressive contract chain for career mode from early orbital missions to advanced planetary exploration.

### 2. AnomalySurveyor
Contracts for discovering and surveying anomalies including monoliths, pyramids, and UFOs.

### 3. CC-CP-SCANSat
SCANsat-based scanning contracts for orbital surveys, multispectral scanning, and biome identification.

### 4. CleverSat
Satellite constellation contracts including probe malfunctions and rogue AI scenarios.

### 5. CommNetRelays
Communication relay network contracts for Lagrange points and orbital constellations.

### 6. Constellations
Comprehensive satellite constellation contracts including relay networks and station-keeping.

### 7. ExplorationPlus
Exploration-focused contracts including first steps, orbital maneuvers, and landing missions.

### 8. FieldResearch
Science-focused contracts for biome studies, climate research, and geological surveys.

### 9. GAP (Giving Aircraft Purpose)
Aviation contracts including milestones, rescue missions, deliveries, and stunts.

### 10. HistoricalProgression
Historical space mission contracts from early space age through Apollo, Gemini, and ISS.

### 11. InterplanetaryMountaineer
Challenge contracts for landing on highest peaks and lowest valleys across the solar system.

### 12. KerbalAcademy
Training contracts including boot camp, flight school, and engineering courses.

### 13. KerbinSpaceStation
Station and base construction contracts including resupply, crew rotation, and expansion.

### 14. RAD
Research and development contracts for various celestial bodies.

### 15. Spacetux
Collection including Grand Tours, Rover Missions, and Unmanned Contracts.

### 16. Tourism
Comprehensive tourism system with suborbital flights, moon tours, and attraction sites.

### 17. Tourism Overhaul
Extensive tourism overhaul with local, interplanetary, and interstellar destinations.

### 18. TourismExpanded
Expanded tourism including grand tours, flyby missions, and rover tours.

## Localization Support

All mods now include localization framework for:
- **English (en-us)** - Full support
- **Portuguese/Brazil (pt-br)** - Framework in place
- **Spanish/Spain (es-es)** - Framework in place

Contract-specific strings can be added to localization files as needed following the format:
```
#LOC_<ModName>_<Contract>_<Field> = Localized text
```

## Dependencies

All mods require:
- **Contract Configurator** (minimum version varies by mod)

Some mods have additional dependencies:
- **SCANsat** - Required for CC-CP-SCANSat
- **Station Science** - Optional for some mods
- **Strategia** - Optional integration for many mods

## Installation

1. Install Contract Configurator (required)
2. Download desired contract packs
3. Extract to `GameData/ContractPacks/` directory

## Credits

These contract packs were created by various authors in the KSP community:
- nightingale - Tourism, FieldResearch, and others
- inigma - GAP
- Kerbas_ad_astra - CommNetRelays
- And many other talented modders

## License

Each mod has its own license (see individual LICENSE.txt files). Most use MIT License, some use GPL v3.

## Contributing

To add localized strings to any mod:
1. Navigate to the mod's `Localization/` folder
2. Edit the appropriate language file (en-us.cfg, pt-br.cfg, or es-es.cfg)
3. Add localization keys following the pattern: `#LOC_<ModName>_<ID> = <Text>`

## Changelog

### 2025-10-19 - Major Structure Refactoring
- Reorganized all 18 mods to follow standard KSP structure
- Added localization framework (en-us, pt-br, es-es) to all mods
- Organized contract files into Groups and Types subdirectories
- Consolidated patches into ModuleManager and Compatibility folders
- Added README.md to all mods
- Added LICENSE.txt where missing
- Preserved all existing functionality and compatibility
