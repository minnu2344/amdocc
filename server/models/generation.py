def generate_explanation(text: str):
    """
    Analyze text using Gemini model and return a structured fact-checking response.

    Returns:
        Tuple[list, list, list, list]: 
        (original_statements, truth_values, explanations, sources_list)
    """
    original_statements = []
    truth_values = []
    explanations = []
    sources_list = []

    try:
        # Make API request to Gemini (Assume response.text contains the output)
        response = model.generate_content(prompt)
        if not response.text:
            return [text], ["No response generated"], ["No explanation available"], [[]]

        response_text = response.text

        # Parse response into structured lists
        statement_sections = response_text.split('STATEMENT')[1:]  # Skip first empty split

        for section in statement_sections:
            try:
                original = extract_field(section, 'ORIGINAL:')
                classification = extract_field(section, 'CLASSIFICATION:')
                reasoning = extract_field(section, 'REASONING:')
                sources = extract_sources(section)

                original_statements.append(original)
                truth_values.append(parse_classification(classification))
                explanations.append(reasoning)
                sources_list.append(sources)

            except Exception as e:
                print(f"Error parsing section: {str(e)}")
                original_statements.append("Could not parse statement")
                truth_values.append(None)
                explanations.append("Parsing error")
                sources_list.append([])

    except Exception as e:
        print(f"Error in generate_explanation: {str(e)}")
        return [text], ["Error occurred"], ["Unable to generate analysis"], [[]]

    return original_statements, truth_values, explanations, sources_list


def extract_field(text: str, field_name: str) -> str:
    """Extracts a field value from a text block."""
    for line in text.split("\n"):
        if line.startswith(field_name):
            return line.replace(field_name, "").strip()
    return "Not available"


def parse_classification(classification: str):
    """Converts classification text to a boolean or None."""
    if "TRUE" in classification:
        return True
    elif "FALSE" in classification:
        return False
    return None  # For NEUTRAL


def extract_sources(section: str) -> list:
    """Extracts sources from a text block."""
    sources = []
    if 'SOURCES:' in section:
        sources_section = section.split('SOURCES:')[-1]
        for line in sources_section.split("\n")[1:]:
            line = line.strip()
            if line.startswith("-") or line.startswith("•"):
                sources.append(line.lstrip("- •").strip())
            elif not line or "STATEMENT" in line:
                break
    return sources if sources else ["No sources provided"]
