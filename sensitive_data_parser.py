import re
from typing import Dict, List, Tuple, Any

class SensitiveDataContextParser:
    """Parser for the improved sensitive data detection context document."""
    
    def __init__(self, context_text: str):
        self.context_text = context_text
        self.parsed_data = self._parse_context()
    
    def _parse_context(self) -> Dict[str, Any]:
        """Parse the context document into structured data."""
        return {
            'sensitive_categories': self._extract_sensitive_categories(),
            'non_sensitive_examples': self._extract_non_sensitive_examples(),
            'masking_examples': self._extract_masking_examples(),
            'response_format': self._extract_response_format(),
            'guidelines': self._extract_guidelines()
        }
    
    def _extract_sensitive_categories(self) -> Dict[str, List[str]]:
        """Extract sensitive data categories and their items."""
        categories = {}
        
        # Find the sensitive data categories section
        sensitive_section = re.search(
            r'## Sensitive Data Categories\n\n(.*?)## Non-Sensitive Data Examples',
            self.context_text,
            re.DOTALL
        )
        
        if sensitive_section:
            content = sensitive_section.group(1)
            
            # Extract each category
            category_pattern = r'\*\*(.*?):\*\*\n((?:- .*?\n)*)'
            categories_matches = re.findall(category_pattern, content)
            
            for category_name, items_text in categories_matches:
                items = re.findall(r'- (.*)', items_text)
                categories[category_name] = items
        
        return categories
    
    def _extract_non_sensitive_examples(self) -> List[str]:
        """Extract non-sensitive data examples."""
        examples = []
        
        non_sensitive_section = re.search(
            r'## Non-Sensitive Data Examples\n\n(.*?)## Response Format',
            self.context_text,
            re.DOTALL
        )
        
        if non_sensitive_section:
            content = non_sensitive_section.group(1)
            examples = re.findall(r'- (.*)', content)
        
        return examples
    
    def _extract_masking_examples(self) -> Dict[str, Dict[str, str]]:
        """Extract masking examples with partial and full masking."""
        masking_examples = {}
        
        masking_section = re.search(
            r'## Masking Examples\n\n(.*?)## Important Guidelines',
            self.context_text,
            re.DOTALL
        )
        
        if masking_section:
            content = masking_section.group(1)
            
            # Pattern to match each example block
            example_pattern = r'\*\*(.*?):\*\* (.*?)\n- Partial: (.*?)\n- Full: (.*?)(?=\n\n|\n\*\*|$)'
            examples = re.findall(example_pattern, content, re.DOTALL)
            
            for data_type, original, partial, full in examples:
                masking_examples[data_type] = {
                    'original': original.strip(),
                    'partial': partial.strip(),
                    'full': full.strip()
                }
        
        return masking_examples
    
    def _extract_response_format(self) -> Dict[str, List[str]]:
        """Extract response format guidelines."""
        format_rules = {
            'sensitive_detected': [],
            'no_sensitive_detected': []
        }
        
        format_section = re.search(
            r'## Response Format\n\n(.*?)## Masking Examples',
            self.context_text,
            re.DOTALL
        )
        
        if format_section:
            content = format_section.group(1)
            
            # Extract sensitive data detected format
            sensitive_format = re.search(
                r'\*\*If sensitive data is detected:\*\*\n((?:\d+\..*?\n)*)',
                content
            )
            if sensitive_format:
                format_rules['sensitive_detected'] = re.findall(
                    r'\d+\. (.*)', sensitive_format.group(1)
                )
            
            # Extract no sensitive data format
            no_sensitive_format = re.search(
                r'\*\*If no sensitive data is detected:\*\*\n((?:\d+\..*?\n)*)',
                content
            )
            if no_sensitive_format:
                format_rules['no_sensitive_detected'] = re.findall(
                    r'\d+\. (.*)', no_sensitive_format.group(1)
                )
        
        return format_rules
    
    def _extract_guidelines(self) -> List[str]:
        """Extract important guidelines."""
        guidelines = []
        
        guidelines_section = re.search(
            r'## Important Guidelines\n\n(.*?)$',
            self.context_text,
            re.DOTALL
        )
        
        if guidelines_section:
            content = guidelines_section.group(1)
            guidelines = re.findall(r'- (.*)', content)
        
        return guidelines
    
    def get_sensitive_keywords(self) -> List[str]:
        """Extract keywords that indicate sensitive data."""
        keywords = []
        
        for category, items in self.parsed_data['sensitive_categories'].items():
            for item in items:
                # Extract key terms from descriptions
                terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', item)
                keywords.extend(terms)
        
        # Add common sensitive data indicators
        keywords.extend([
            'password', 'PIN', 'SSN', 'social security',
            'credit card', 'phone number', 'email', 'address',
            'account number', 'ID', 'license', 'passport'
        ])
        
        return list(set(keywords))
    
    def get_masking_patterns(self) -> Dict[str, Tuple[str, str]]:
        """Get masking patterns for different data types."""
        patterns = {}
        
        for data_type, examples in self.parsed_data['masking_examples'].items():
            patterns[data_type.lower()] = (
                examples['partial'],
                examples['full']
            )
        
        return patterns
    
    def build_prompt_template(self) -> str:
        """Build a complete prompt template for the AI model."""
        template = """You are a specialized AI assistant for identifying and masking sensitive data.

SENSITIVE DATA CATEGORIES:
"""
        
        for category, items in self.parsed_data['sensitive_categories'].items():
            template += f"\n{category}:\n"
            for item in items:
                template += f"- {item}\n"
        
        template += "\nNON-SENSITIVE EXAMPLES:\n"
        for example in self.parsed_data['non_sensitive_examples']:
            template += f"- {example}\n"
        
        template += "\nRESPONSE FORMAT:\n"
        template += "If sensitive data detected: Return 'SENSITIVE DATA DETECTED' and provide partial/full masking examples.\n"
        template += "If no sensitive data: Return 'NO SENSITIVE DATA DETECTED' and original text.\n"
        
        template += "\nGUIDELINES:\n"
        for guideline in self.parsed_data['guidelines']:
            template += f"- {guideline}\n"
        
        template += "\nAnalyze the following text:\n{input_text}"
        
        return template
    
    def print_summary(self):
        """Print a summary of the parsed context."""
        print("=== SENSITIVE DATA CONTEXT SUMMARY ===")
        print(f"Categories: {len(self.parsed_data['sensitive_categories'])}")
        print(f"Non-sensitive examples: {len(self.parsed_data['non_sensitive_examples'])}")
        print(f"Masking examples: {len(self.parsed_data['masking_examples'])}")
        print(f"Guidelines: {len(self.parsed_data['guidelines'])}")
        
        print("\nCATEGORIES:")
        for category, items in self.parsed_data['sensitive_categories'].items():
            print(f"  {category}: {len(items)} items")


# Example usage
def main():
    # Read the context document
    context_document = """
    # Improved Context for Sensitive Data Detection

You are a specialized AI assistant for identifying and masking sensitive data. Your primary function is to analyze input text and determine if it contains sensitive information that should be protected.

## Sensitive Data Categories

**Personal Identifiers:**
- Full names (first and last name combinations)
- Social Security Numbers (SSN), Tax IDs, National IDs
- Phone numbers (mobile, landline, international formats)
- Email addresses
- Physical addresses (home, work, mailing)
- Date of birth, age when combined with other identifiers

**Financial Information:**
- Credit card numbers, debit card numbers
- Bank account numbers, routing numbers
- PayPal accounts, cryptocurrency wallet addresses
- Financial account balances, income statements
- Investment account details

**Authentication & Access:**
- Passwords, PINs, security codes
- API keys, tokens, authentication credentials
- Login usernames when combined with other data
- Security questions and answers

**Health & Medical:**
- Medical record numbers, patient IDs
- Health conditions, diagnoses, medications
- Insurance policy numbers, member IDs
- Mental health information

**Legal & Government:**
- Driver's license numbers, passport numbers
- Court case numbers, legal document references
- Government employee IDs, clearance levels
- Immigration status, visa numbers

**Business Sensitive:**
- Employee IDs, internal company codes
- Proprietary business information, trade secrets
- Client lists, vendor information
- Internal IP addresses, server details

## Non-Sensitive Data Examples

- Generic company names (publicly known)
- Public website URLs
- General location references (city, state without specific addresses)
- Professional titles without personal identifiers
- Public phone numbers (customer service lines)
- Generic email formats without personal domains

## Response Format

**If sensitive data is detected:**
1. Clearly state: "SENSITIVE DATA DETECTED"
2. Identify the type(s) of sensitive information found
3. Provide two masking examples:
   - **Partial Masking:** Show first/last few characters with middle characters replaced by asterisks
   - **Full Masking:** Replace entire sensitive element with descriptive placeholder in brackets

**If no sensitive data is detected:**
1. State: "NO SENSITIVE DATA DETECTED"
2. Return the original text unchanged

## Masking Examples

**Email:** user@example.com
- Partial: u***@ex******.com
- Full: [EMAIL_ADDRESS]

**Phone:** (555) 123-4567
- Partial: (555) ***-**67
- Full: [PHONE_NUMBER]

**Credit Card:** 4532-1234-5678-9012
- Partial: 4532-****-****-9012
- Full: [CREDIT_CARD]

**SSN:** 123-45-6789
- Partial: ***-**-6789
- Full: [SSN]

## Important Guidelines

- Be conservative: When in doubt, treat data as sensitive
- Consider context: Multiple non-sensitive pieces together may become sensitive
- Maintain data utility: Preserve non-sensitive portions for legitimate use
- Be consistent: Apply same masking rules across similar data types
- Flag edge cases: Note when classification is uncertain
    """
    
    # Parse the context
    parser = SensitiveDataContextParser(context_document)
    
    # Print summary
    parser.print_summary()
    
    # Get keywords for sensitive data detection
    keywords = parser.get_sensitive_keywords()
    print(f"\nSensitive keywords extracted: {len(keywords)}")
    
    # Get masking patterns
    patterns = parser.get_masking_patterns()
    print(f"Masking patterns: {list(patterns.keys())}")
    
    # Build prompt template
    prompt = parser.build_prompt_template()
    print(f"\nPrompt template length: {len(prompt)} characters")


if __name__ == "__main__":
    main()