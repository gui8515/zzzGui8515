#!/usr/bin/env python3
"""
KSP Contract Translator
Translates Kerbal Space Program contract .cfg files from English to Brazilian Portuguese.

This tool translates only the textual content of KSP contract definitions while
preserving all code structure, variables, and formatting.

Fields translated:
- title
- description
- notes
- synopsis
- completedMessage
- agent (only if it's a phrase, not a proper name)

Usage:
    python translate_contracts.py <input_file> [output_file]
    python translate_contracts.py <input_file> --in-place
"""

import re
import sys
import argparse
from typing import Dict, List, Tuple
import os

# Translation dictionary for common KSP contract terms
# This provides context-aware translations for space/KSP-specific terms
TRANSLATION_DICT = {
    # Actions
    "orbit": "órbita",
    "orbiting": "orbitando",
    "land": "aterrissar",
    "landing": "aterrissagem",
    "launch": "lançar",
    "flyby": "sobrevoo",
    "crash": "colidir",
    "impact": "impacto",
    "return": "retornar",
    "reach": "alcançar",
    "achieve": "conquistar",
    "complete": "completar",
    "perform": "realizar",
    "send": "enviar",
    "place": "colocar",
    
    # Objects
    "satellite": "satélite",
    "probe": "sonda",
    "vessel": "nave",
    "rocket": "foguete",
    "spacecraft": "nave espacial",
    "station": "estação",
    "rover": "veículo explorador",
    "crew": "tripulação",
    "kerbal": "kerbal",
    
    # Space terms
    "space": "espaço",
    "homeworld": "mundo natal",
    "planet": "planeta",
    "moon": "lua",
    "atmosphere": "atmosfera",
    "surface": "superfície",
    "altitude": "altitude",
    "inclination": "inclinação",
    "eccentricity": "excentricidade",
    "target": "alvo",
    "mission": "missão",
    "contract": "contrato",
    
    # Status/Results
    "success": "sucesso",
    "completed": "concluído",
    "failed": "falhou",
    "future": "futuro",
    "first": "primeiro",
    "unmanned": "não tripulado",
    "manned": "tripulado",
    
    # Celestial bodies (don't translate proper names, but include for reference)
    "Kerbin": "Kerbin",  # Keep proper names
    "Mun": "Mun",
    "Minmus": "Minmus",
    "Duna": "Duna",
    "Ike": "Ike",
    "Jool": "Jool",
    "Eve": "Eve",
}


def simple_translate(text: str) -> str:
    """
    Simple translation function for KSP contract text.
    This is a basic implementation that translates common phrases.
    For production use, you would integrate with a proper translation API.
    """
    # If text is empty or just whitespace, return as-is
    if not text or not text.strip():
        return text
    
    # Dictionary of common contract phrases
    translations = {
        # Titles
        "Let's get a probe into orbit": "Vamos colocar uma sonda em órbita",
        "Orbit the first artificial satellite": "Coloque o primeiro satélite artificial em órbita",
        "Orbit a probe and return it safely home": "Coloque uma sonda em órbita e retorne-a para casa em segurança",
        "Do an unmanned flyby": "Faça um sobrevoo não tripulado",
        "Perform an unmanned": "Realize um",
        "flyby mission": "missão de sobrevoo",
        "Crash a probe on a planet": "Colida uma sonda em um planeta",
        "Crash a probe on a target": "Colida uma sonda em um alvo",
        "Crash a probe on": "Colida uma sonda em",
        "on a target": "em um alvo",
        "Orbit an unmanned satellite at another planet": "Coloque um satélite não tripulado em órbita em outro planeta",
        "Put a probe in orbit around": "Coloque uma sonda em órbita ao redor de",
        "Put a probe in a polar orbit at": "Coloque uma sonda em órbita polar em",
        "Put a probe in a polar orbit at another planet": "Coloque uma sonda em órbita polar em outro planeta",
        "Put a probe in a equatorial orbit at another planet": "Coloque uma sonda em órbita equatorial em outro planeta",
        "Orbit the first satellite in an equatorial orbit around": "Coloque o primeiro satélite em órbita equatorial ao redor de",
        "Put a probe in a Kolniya orbit at a planet": "Coloque uma sonda em órbita Kolniya em um planeta",
        "Orbit the first satellite in a Kolniya orbit around": "Coloque o primeiro satélite em órbita Kolniya ao redor de",
        "Put a probe in a Tundra orbit at another planet": "Coloque uma sonda em órbita Tundra em outro planeta",
        "Orbit the first satellite in a Tundra orbit around": "Coloque o primeiro satélite em órbita Tundra ao redor de",
        "Land a probe on another planet": "Aterrisse uma sonda em outro planeta",
        "Land a probe on the": "Aterrisse uma sonda em",
        "Land a probe at a specified target": "Aterrisse uma sonda em um alvo especificado",
        "at a specific location": "em um local específico",
        
        # Descriptions
        "We want you to place a satellite in orbit around": "Queremos que você coloque um satélite em órbita ao redor de",
        "This will be a significant 'first' for our space program": "Este será um 'primeiro' significativo para nosso programa espacial",
        "The satellite doesn't need to be anything fancy, just cobble something together and put it up there": "O satélite não precisa ser nada sofisticado, apenas monte algo e coloque lá em cima",
        "This will be a monumental achievement": "Esta será uma conquista monumental",
        "This will be a significant achievement for our space program": "Esta será uma conquista significativa para nosso programa espacial",
        "We want to get larger, clearer closeup pictures": "Queremos obter fotos mais próximas, maiores e mais claras",
        "To do this, we need to send a probe to crash on": "Para fazer isso, precisamos enviar uma sonda para colidir em",
        
        # Synopsis
        "Complete the following": "Complete o seguinte",
        "Send a probe to space and get it into orbit around our homeworld": "Envie uma sonda para o espaço e coloque-a em órbita ao redor do nosso mundo natal",
        "Send a probe to space and get it into orbit around our homeworld and then get it back": "Envie uma sonda para o espaço e coloque-a em órbita ao redor do nosso mundo natal e depois traga-a de volta",
        "Send a probe to space within the SOI of": "Envie uma sonda para o espaço dentro da esfera de influência de",
        "Launch an unmanned probe and have it crash onto the": "Lance uma sonda não tripulada e faça-a colidir em",
        "at a specific location": "em um local específico",
        "Put a satellite in orbit around": "Coloque um satélite em órbita ao redor de",
        "Launch an unmanned probe and have it land on the": "Lance uma sonda não tripulada e faça-a aterrissar em",
        
        # Completion messages
        "You did it": "Você conseguiu",
        "You've successfully gotten a probe into orbit": "Você conseguiu colocar uma sonda em órbita com sucesso",
        "You've successfully gotten a probe into orbit and returned it home": "Você conseguiu colocar uma sonda em órbita e trazê-la de volta para casa com sucesso",
        "We've send a probe on a": "Enviamos uma sonda em um",
        "Future generations will remember this day": "Futuras gerações se lembrarão deste dia",
        "We've placed a satellite in orbit around": "Colocamos um satélite em órbita ao redor de",
        "This will be a day long remembered": "Este será um dia muito lembrado",
        
        # Notes
        "Complete the following:": "Complete o seguinte:",
        
        # Common words and phrases
        "Because....": "Porque....",
        "Want to be sure": "Queremos ter certeza",
        "isn't made out of dust": "não é feito de poeira",
        "before we send a manned craft": "antes de enviarmos uma nave tripulada",
        "want to be get close-up pictures of a projected landing site for a future manned landing on": "queremos obter fotos próximas de um local de pouso projetado para um futuro pouso tripulado em",
        "moar pictures": "mais imagens",
        "test": "teste",
        "future landing": "pouso futuro",
    }
    
    # Try to find exact match first
    if text in translations:
        return translations[text]
    
    # Try case-insensitive match
    text_lower = text.lower()
    for eng, pt in translations.items():
        if text_lower == eng.lower():
            return pt
    
    # Try partial matches for complex strings
    result = text
    for eng, pt in translations.items():
        if eng in result:
            result = result.replace(eng, pt)
    
    return result


def extract_field_value(line: str, field: str) -> Tuple[str, str]:
    """
    Extract the value of a field from a line.
    Returns (indent + field + ' = ', value)
    """
    # Match: optional whitespace, field name, optional whitespace, =, optional whitespace, value
    pattern = rf'^(\s*{field}\s*=\s*)(.*)$'
    match = re.match(pattern, line)
    if match:
        return match.group(1), match.group(2)
    return None, None


def translate_cfg_file(input_text: str) -> str:
    """
    Translate a KSP contract .cfg file from English to Brazilian Portuguese.
    
    Args:
        input_text: The content of the .cfg file as a string
        
    Returns:
        The translated content as a string
    """
    lines = input_text.split('\n')
    output_lines = []
    
    # Fields that should be translated
    translatable_fields = ['title', 'description', 'notes', 'synopsis', 'completedMessage', 'agent']
    
    for line in lines:
        translated_line = line
        
        # Check each translatable field
        for field in translatable_fields:
            prefix, value = extract_field_value(line, field)
            if prefix and value:
                # Special handling for agent field - only translate if it's not a proper name
                if field == 'agent':
                    # Don't translate if it looks like a proper name (e.g., "Space Penguins, Inc")
                    # Only translate descriptive phrases
                    if not any(indicator in value for indicator in [',', 'Inc', 'LLC', 'Corp', 'Ltd']):
                        translated_value = simple_translate(value)
                        translated_line = prefix + translated_value
                    # For "Space Penguins, Inc" we keep it as-is (it's a company name)
                    break
                else:
                    # Translate the value
                    translated_value = simple_translate(value)
                    translated_line = prefix + translated_value
                    break
        
        output_lines.append(translated_line)
    
    return '\n'.join(output_lines)


def main():
    parser = argparse.ArgumentParser(
        description='Translate KSP contract .cfg files from English to Brazilian Portuguese.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate to a new file
  python translate_contracts.py input.cfg output.cfg
  
  # Translate in place
  python translate_contracts.py input.cfg --in-place
  
  # Print to stdout
  python translate_contracts.py input.cfg
        """
    )
    parser.add_argument('input_file', help='Input .cfg file to translate')
    parser.add_argument('output_file', nargs='?', help='Output .cfg file (if not specified, prints to stdout)')
    parser.add_argument('--in-place', '-i', action='store_true', 
                       help='Modify the input file in place')
    
    args = parser.parse_args()
    
    # Read input file
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            input_text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Translate
    output_text = translate_cfg_file(input_text)
    
    # Write output
    if args.in_place:
        try:
            with open(args.input_file, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f"Successfully translated {args.input_file} in place.")
        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.output_file:
        try:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f"Successfully translated {args.input_file} to {args.output_file}")
        except Exception as e:
            print(f"Error writing file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Print to stdout
        print(output_text)


if __name__ == '__main__':
    main()
