import google.generativeai as genai
from dotenv import load_dotenv
from typing import Tuple
import os

load_dotenv()

def generate_explanation(text: str) -> Tuple[list, list, list, list]:
    """
    Analyze text using Gemini model to verify truthfulness and provide explanation for each line
    
    Args:
        text (str): The input text to analyze
        predicted_true (bool): Initial truth prediction from DistilBERT
        domain (str): Domain classification from DistilBERT
        confidence_score (float): Confidence score from DistilBERT (0 to 1)
        
    Returns:
        Tuple[list, list, list, list]: (list_of_original_statements, list_of_truth_values, list_of_explanations, list_of_sources)
    """
    # Configure Gemini
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    
    # Construct the prompt with more neutral language
    prompt = f"""Given the following text, provide a rigorous fact-check analysis of each statement using only trusted sources:

Text to analyze:
{text}

Guidelines for analysis:
1. Use ONLY trusted sources for verification:
   - Government databases and official websites
   - Peer-reviewed academic publications
   - Reputable news organizations
   - Official statistics and research institutions
   - Primary source documents when available

2. For each statement:
   - Quote the exact statement
   - Classify as:
     * VERIFIABLE (TRUE): Can be proven true with reliable sources
     * INCORRECT (FALSE): Can be proven false with reliable sources
     * UNVERIFIABLE (NEUTRAL): Cannot be definitively proven or requires more context
   - Provide detailed reasoning with specific sources where possible

Response format:
STATEMENT 1:
ORIGINAL: [Exact quote of the statement]
CLASSIFICATION: [TRUE/FALSE/NEUTRAL]
REASONING: [Evidence-based explanation with sources when available]
SOURCES: [List relevant trusted sources used for verification]

STATEMENT 2:
ORIGINAL: [Exact quote of the statement]
CLASSIFICATION: [TRUE/FALSE/NEUTRAL]
REASONING: [Evidence-based explanation with sources when available]
SOURCES: [List relevant trusted sources used for verification]"""

    try:
        # Get response from Gemini with correct safety settings
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]
        model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)
        response = model.generate_content(prompt)
        
        if not response.text:
            return ([text], ["Unable to generate detailed analysis. Falling back to initial prediction."], [[]])
            
        response_text = response.text
        
        # Parse response
        truth_values = []
        explanations = []
        original_statements = []
        sources_list = []
        
        # Split response into sections for each statement
        statement_sections = response_text.split('STATEMENT')[1:]  # Skip the first empty split
        
        for section in statement_sections:
            try:
                # Extract original statement
                original_line = [line for line in section.split('\n') if 'ORIGINAL:' in line][0]
                original = original_line.replace('ORIGINAL:', '').strip()
                
                # Extract classification
                class_line = [line for line in section.split('\n') if 'CLASSIFICATION:' in line][0]
                classification = class_line.replace('CLASSIFICATION:', '').strip().upper()
                
                # Convert to boolean or None for neutral
                if 'TRUE' in classification:
                    final_truth = True
                elif 'FALSE' in classification:
                    final_truth = False
                else:
                    final_truth = None  # For NEUTRAL
                
                # Extract reasoning
                reason_line = [line for line in section.split('\n') if 'REASONING:' in line][0]
                reasoning = reason_line.replace('REASONING:', '').strip()
                
                # Extract sources
                sources_line = [line for line in section.split('\n') if 'SOURCES:' in line][0]
                sources_section = section[section.index(sources_line):]
                sources = []

                print(response_text)
                
                # Get all lines after SOURCES: that start with a dash or bullet
                for line in sources_section.split('\n')[1:]:  # Skip the SOURCES: line
                    line = line.strip()
                    if line.startswith('-') or line.startswith('•'):
                        source = line.lstrip('- •').strip()
                        if source and source != '[List relevant trusted sources used for verification]':
                            sources.append(source)
                    elif not line or line.startswith('STATEMENT'):  # Stop if we hit next statement or empty line
                        break
                
                truth_values.append(final_truth)
                explanations.append(reasoning)
                original_statements.append(original)
                sources_list.append(sources)
                
            except IndexError as e:
                print(f"Error parsing section: {str(e)}")
                continue
        
        if not truth_values:  # If no statements were successfully parsed
            return ([text], ["Unable to parse analysis. Using initial prediction."], [[]])
        
        return original_statements, truth_values, explanations, sources_list
        
    except Exception as e:
        print(f"Error in generate_explanation: {str(e)}")
        return ([text], [f"Analysis generation failed: {str(e)}. Using initial prediction."], [[]])
