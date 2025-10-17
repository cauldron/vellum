"""
Pytest test to validate that CASNumber pattern validation works correctly.
"""

import os
import xml.etree.ElementTree as ET

import pytest
import xmlschema


@pytest.fixture(scope="module")
def common_schema():
    """Load the XSD schema containing the CASNumber definition."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    xsd_file = os.path.join(project_root, "vellum-schemas", "Vellum_Common_DataTypes.xsd")
    
    if not os.path.exists(xsd_file):
        pytest.skip(f"XSD schema file not found: {xsd_file}")
        
    return xmlschema.XMLSchema11(xsd_file, validation='lax')


class TestCASNumber:
    """Test class for CASNumber pattern validation."""
    
    def validate_cas_number_element(self, xml_content, schema):
        """
        Validate a CASNumber element against the schema.
        
        Args:
            xml_content (str): XML content containing CASNumber element
            schema: XMLSchema object
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Parse XML content
            root = ET.fromstring(xml_content)
            
            # Get the CASNumber type from the schema
            cas_type = schema.types.get('CASNumber')
            if not cas_type:
                return False, "CASNumber not found in schema"
            
            # Extract the text content from the XML element
            text_content = root.text if root.text else ""
            
            # Validate the text content against CASNumber
            cas_type.validate(text_content)
            return True, None
            
        except xmlschema.XMLSchemaException as e:
            return False, f"Validation error: {e}"
        except ET.ParseError as e:
            return False, f"XML parse error: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"
    
    @pytest.mark.parametrize("cas_number,expected_valid,description", [
        # Valid cases - 2 to 7 digits before first hyphen
        ("12-34-5", True, "minimum valid CAS number (2 digits)"),
        ("123-45-6", True, "3 digits before hyphen"),
        ("1234-56-7", True, "4 digits before hyphen"),
        ("12345-67-8", True, "5 digits before hyphen"),
        ("123456-78-9", True, "6 digits before hyphen (old minimum)"),
        ("1234567-89-0", True, "maximum valid CAS number (7 digits)"),
        
        # Invalid cases - too few digits before first hyphen
        ("1-23-4", False, "too few digits before first hyphen (1 digit)"),
        
        # Invalid cases - too many digits before first hyphen
        ("12345678-90-1", False, "too many digits before first hyphen (8 digits)"),
        ("123456789-01-2", False, "too many digits before first hyphen (9 digits)"),
        
        # Invalid cases - wrong pattern structure
        ("12-345-6", False, "too many digits in middle section (3 digits)"),
        ("12-3-456", False, "too many digits in last section (3 digits)"),
        ("12-3-45", False, "too few digits in middle section (1 digit)"),
        ("12-34-5", True, "correct pattern structure"),
        
        # Invalid cases - non-numeric characters
        ("12a-34-5", False, "non-numeric character in first section"),
        ("12-3a-5", False, "non-numeric character in middle section"),
        ("12-34-a", False, "non-numeric character in last section"),
        
        # Invalid cases - missing hyphens
        ("12345", False, "missing hyphens"),
        ("12-345", False, "missing second hyphen"),
        ("123-45", False, "missing first hyphen"),
        
        # Invalid cases - extra characters
        ("12-34-5-6", False, "extra hyphen"),
        (" 12-34-5", False, "leading space"),
        ("12-34-5 ", False, "trailing space"),
        ("12 -34-5", False, "space in middle"),
        
        # Edge cases
        ("", False, "empty string"),
        ("-", False, "only hyphen"),
        ("--", False, "only hyphens"),
        ("123--45", False, "double hyphen"),
        ("12-34--5", False, "double hyphen in middle"),
    ])
    def test_cas_number_pattern_validation(self, common_schema, cas_number, expected_valid, description):
        """Parametrized test for CASNumber pattern validation."""
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<casNumber xmlns="http://lca.jrc.it/ILCD/Common">{cas_number}</casNumber>'''
        
        is_valid, error_message = self.validate_cas_number_element(xml_content, common_schema)
        
        if expected_valid:
            assert is_valid, f"Expected valid CASNumber element for {description} but got error: {error_message}"
        else:
            assert not is_valid, f"Expected invalid CASNumber element for {description} but validation passed"
            assert error_message is not None, f"Expected error message for invalid CASNumber element: {description}"
    
    def test_cas_number_with_real_examples(self, common_schema):
        """Test CASNumber validation with real-world CAS number examples."""
        # Real CAS numbers that should be valid with the new pattern
        real_cas_numbers = [
            "50-00-0",    # Formaldehyde (2 digits)
            "000050-00-0",    # Formaldehyde (2 digits, zero padded)
            "64-17-5",    # Ethanol (2 digits)
            "108-88-3",   # Toluene (3 digits)
            "1002-43-3",  # 1,2-Dichloroethane (4 digits)
            "10041-05-5", # 1,1,1-Trichloroethane (5 digits)
            "100414-06-2", # Example with 6 digits
            "1004140-07-3", # Example with 7 digits
        ]
        
        for cas_number in real_cas_numbers:
            xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<casNumber xmlns="http://lca.jrc.it/ILCD/Common">{cas_number}</casNumber>'''
            
            is_valid, error_message = self.validate_cas_number_element(xml_content, common_schema)
            assert is_valid, f"Expected valid CASNumber '{cas_number}' but got error: {error_message}"
    
    def test_cas_number_boundary_values(self, common_schema):
        """Test CASNumber validation at boundary values."""
        # Test minimum valid length (2 digits)
        min_valid = "12-34-5"
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<casNumber xmlns="http://lca.jrc.it/ILCD/Common">{min_valid}</casNumber>'''
        
        is_valid, error_message = self.validate_cas_number_element(xml_content, common_schema)
        assert is_valid, f"Expected valid CASNumber '{min_valid}' (minimum length) but got error: {error_message}"
        
        # Test maximum valid length (7 digits)
        max_valid = "1234567-89-0"
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<casNumber xmlns="http://lca.jrc.it/ILCD/Common">{max_valid}</casNumber>'''
        
        is_valid, error_message = self.validate_cas_number_element(xml_content, common_schema)
        assert is_valid, f"Expected valid CASNumber '{max_valid}' (maximum length) but got error: {error_message}"
        
        # Test just below minimum (1 digit)
        below_min = "1-23-4"
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<casNumber xmlns="http://lca.jrc.it/ILCD/Common">{below_min}</casNumber>'''
        
        is_valid, error_message = self.validate_cas_number_element(xml_content, common_schema)
        assert not is_valid, f"Expected invalid CASNumber '{below_min}' (below minimum) but validation passed"
        
        # Test just above maximum (8 digits)
        above_max = "12345678-90-1"
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<casNumber xmlns="http://lca.jrc.it/ILCD/Common">{above_max}</casNumber>'''
        
        is_valid, error_message = self.validate_cas_number_element(xml_content, common_schema)
        assert not is_valid, f"Expected invalid CASNumber '{above_max}' (above maximum) but validation passed"
    
    def test_cas_number_pattern_consistency(self, common_schema):
        """Test that the pattern is consistently applied across different valid lengths."""
        # Test all valid lengths from 2 to 7 digits
        for length in range(2, 8):  # 2 to 7 inclusive
            # Create a CAS number with the specified length
            first_part = "1" * length
            cas_number = f"{first_part}-23-4"
            
            xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<casNumber xmlns="http://lca.jrc.it/ILCD/Common">{cas_number}</casNumber>'''
            
            is_valid, error_message = self.validate_cas_number_element(xml_content, common_schema)
            assert is_valid, f"Expected valid CASNumber with {length} digits '{cas_number}' but got error: {error_message}"
