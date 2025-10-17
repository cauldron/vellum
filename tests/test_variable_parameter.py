"""
Pytest test to validate that VariableParameterType requires meanValue element.
"""

import os
import pytest
import xmlschema
import xml.etree.ElementTree as ET


@pytest.fixture(scope="module")
def process_schema():
    """Load the XSD schema containing the VariableParameterType definition."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    xsd_file = os.path.join(project_root, "vellum-schemas", "Vellum_ProcessDataSet.xsd")
    
    if not os.path.exists(xsd_file):
        pytest.skip(f"XSD schema file not found: {xsd_file}")
        
    return xmlschema.XMLSchema11(xsd_file, validation='lax')


class TestVariableParameterType:
    """Test class for VariableParameterType meanValue requirement."""
    
    def validate_variable_parameter_element(self, xml_content, schema):
        """
        Validate a variableParameter element against the schema.
        
        Args:
            xml_content (str): XML content containing variableParameter element
            schema: XMLSchema object
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Parse XML content
            root = ET.fromstring(xml_content)
            
            # Get the VariableParameterType from the schema
            variable_param_type = schema.types.get('VariableParameterType')
            if not variable_param_type:
                return False, "VariableParameterType not found in schema"
            
            # Validate the element against VariableParameterType
            variable_param_type.validate(root)
            return True, None
            
        except xmlschema.XMLSchemaException as e:
            return False, f"Validation error: {e}"
        except ET.ParseError as e:
            return False, f"XML parse error: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"
    
    def test_variable_parameter_with_mean_value_valid(self, process_schema):
        """Test that variableParameter element with meanValue is valid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<variableParameter xmlns="http://lca.jrc.it/ILCD/Process" name="test_variable">
    <meanValue>42.5</meanValue>
</variableParameter>'''
        
        is_valid, error_message = self.validate_variable_parameter_element(xml_content, process_schema)
        
        assert is_valid, f"Expected valid variableParameter element but got error: {error_message}"
    
    def test_variable_parameter_with_formula_and_mean_value_valid(self, process_schema):
        """Test that variableParameter element with both formula and meanValue is valid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<variableParameter xmlns="http://lca.jrc.it/ILCD/Process" name="test_variable">
    <formula>x * 2</formula>
    <meanValue>85.0</meanValue>
</variableParameter>'''
        
        is_valid, error_message = self.validate_variable_parameter_element(xml_content, process_schema)
        
        assert is_valid, f"Expected valid variableParameter element but got error: {error_message}"
    
    def test_variable_parameter_missing_mean_value_invalid(self, process_schema):
        """Test that variableParameter element missing meanValue is invalid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<variableParameter xmlns="http://lca.jrc.it/ILCD/Process" name="test_variable">
    <formula>x * 2</formula>
</variableParameter>'''
        
        is_valid, error_message = self.validate_variable_parameter_element(xml_content, process_schema)
        
        assert not is_valid, "Expected invalid variableParameter element (missing meanValue) but validation passed"
        assert "meanvalue" in error_message.lower() or "expected" in error_message.lower(), \
            f"Expected meanValue/expected error, got: {error_message}"
    
    def test_variable_parameter_empty_element_invalid(self, process_schema):
        """Test that empty variableParameter element is invalid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<variableParameter xmlns="http://lca.jrc.it/ILCD/Process" name="test_variable">
</variableParameter>'''
        
        is_valid, error_message = self.validate_variable_parameter_element(xml_content, process_schema)
        
        assert not is_valid, "Expected invalid variableParameter element (empty) but validation passed"
        assert "meanvalue" in error_message.lower() or "expected" in error_message.lower(), \
            f"Expected meanValue/expected error, got: {error_message}"
    
    def test_variable_parameter_with_optional_elements_valid(self, process_schema):
        """Test that variableParameter element with all optional elements is valid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<variableParameter xmlns="http://lca.jrc.it/ILCD/Process" name="test_variable">
    <formula>x * 2</formula>
    <meanValue>85.0</meanValue>
    <minimumValue>10.0</minimumValue>
    <maximumValue>100.0</maximumValue>
    <uncertaintyDistributionType>log-normal</uncertaintyDistributionType>
    <relativeStandardDeviation95In>0.1</relativeStandardDeviation95In>
</variableParameter>'''
        
        is_valid, error_message = self.validate_variable_parameter_element(xml_content, process_schema)
        
        assert is_valid, f"Expected valid variableParameter element but got error: {error_message}"
    
    @pytest.mark.parametrize("mean_value,expected_valid,description", [
        ("42.5", True, "positive decimal value"),
        ("0.0", True, "zero value"),
        ("-15.3", True, "negative decimal value"),
        ("1000000.0", True, "large positive value"),
        ("-1000000.0", True, "large negative value"),
        ("", False, "empty meanValue"),
        ("invalid", False, "non-numeric meanValue"),
    ])
    def test_variable_parameter_mean_value_values(self, process_schema, mean_value, expected_valid, description):
        """Parametrized test for variableParameter meanValue validation."""
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<variableParameter xmlns="http://lca.jrc.it/ILCD/Process" name="test_variable">
    <meanValue>{mean_value}</meanValue>
</variableParameter>'''
        
        is_valid, error_message = self.validate_variable_parameter_element(xml_content, process_schema)
        
        if expected_valid:
            assert is_valid, f"Expected valid variableParameter element for {description} but got error: {error_message}"
        else:
            assert not is_valid, f"Expected invalid variableParameter element for {description} but validation passed"
            assert error_message is not None, f"Expected error message for invalid variableParameter element: {description}"
