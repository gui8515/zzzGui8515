# KSP Contract Translator

This tool translates Kerbal Space Program contract .cfg files from English to Brazilian Portuguese while preserving all code structure, variables, and formatting.

## Features

- Translates only textual content fields: `title`, `description`, `notes`, `synopsis`, `completedMessage`, and `agent` (when it's a phrase, not a proper name)
- Preserves all code structure, indentation, brackets, and parameter names
- Maintains all KSP-specific syntax and variables
- Keeps comments, body names, and technical parameters unchanged
- Outputs valid KSP contract .cfg files

## Installation

No installation required. Just ensure you have Python 3.6 or later installed.

## Usage

### Basic Usage

Translate a file and output to stdout:
```bash
python translate_contracts.py input.cfg
```

### Save to a new file:
```bash
python translate_contracts.py input.cfg output.cfg
```

### Translate in place (overwrites the original file):
```bash
python translate_contracts.py input.cfg --in-place
# or
python translate_contracts.py input.cfg -i
```

## Example

**Input** (`input.cfg`):
```
CONTRACT_TYPE
{
    name = First Orbit
    title = Orbit the first artificial satellite.
    description = We want you to place a satellite in orbit around Kerbin.
    notes = Complete the following:
    synopsis = Send a probe to space and get it into orbit
    completedMessage = You did it! Mission accomplished.
    agent = Space Penguins, Inc
    
    PARAMETER
    {
        name = Orbit
        type = Orbit
        situation = ORBITING
    }
}
```

**Output** (translated):
```
CONTRACT_TYPE
{
    name = First Orbit
    title = Coloque o primeiro satélite artificial em órbita.
    description = Queremos que você coloque um satélite em órbita ao redor de Kerbin.
    notes = Complete o seguinte:
    synopsis = Envie uma sonda para o espaço e coloque-a em órbita
    completedMessage = Você conseguiu! Missão cumprida.
    agent = Space Penguins, Inc
    
    PARAMETER
    {
        name = Orbit
        type = Orbit
        situation = ORBITING
    }
}
```

## What Gets Translated

The tool translates only these fields:
- `title` - Contract title
- `description` - Contract description
- `notes` - Contract notes
- `synopsis` - Contract synopsis
- `completedMessage` - Message shown when contract is completed
- `agent` - Only if it's a descriptive phrase (proper names like "Space Penguins, Inc" are preserved)

## What Is Preserved

Everything else remains unchanged:
- All code structure and syntax
- Variable names and function calls
- Indentation and formatting
- Comments
- Celestial body names (Kerbin, Mun, Duna, etc.)
- Technical parameters (maxCompletions, rewardScience, etc.)
- Parameter names (CONTRACT_TYPE, PARAMETER, REQUIREMENT, etc.)

## Testing

Run the test suite to ensure everything is working correctly:
```bash
python test_translator.py
```

## Batch Processing

To translate multiple files:
```bash
# Translate all .cfg files in a directory
for file in ContractPacks/ModName/*.cfg; do
    python translate_contracts.py "$file" --in-place
done
```

## Limitations

- The translation dictionary is currently limited to common KSP contract phrases
- For production use, integration with a professional translation API (like Google Translate API or DeepL) would provide better translations
- Custom or mod-specific terms may not be translated optimally

## Contributing

To improve translations:
1. Edit the `TRANSLATION_DICT` in `translate_contracts.py`
2. Add new phrase translations to the `translations` dictionary in the `simple_translate()` function
3. Run tests to ensure no regressions: `python test_translator.py`

## License

This tool is provided as-is for translating KSP contract files. The original contract files maintain their respective licenses.
