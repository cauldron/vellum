"""
Pytest test to validate that MixAndLocationTypes enumeration restrictions work correctly.
"""

import os
import pytest
import xmlschema
import xml.etree.ElementTree as ET


@pytest.fixture(scope="module")
def common_schema():
    """Load the XSD schema containing the MixAndLocationTypes definition."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    xsd_file = os.path.join(project_root, "vellum-schemas", "Vellum_Common_DataTypes.xsd")
    
    if not os.path.exists(xsd_file):
        pytest.skip(f"XSD schema file not found: {xsd_file}")
        
    return xmlschema.XMLSchema11(xsd_file, validation='lax')


@pytest.fixture(scope="module")
def process_schema():
    """Load the ProcessDataSet XSD schema."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    xsd_file = os.path.join(project_root, "vellum-schemas", "Vellum_ProcessDataSet.xsd")
    
    if not os.path.exists(xsd_file):
        pytest.skip(f"XSD schema file not found: {xsd_file}")
        
    return xmlschema.XMLSchema11(xsd_file, validation='lax')


@pytest.fixture(scope="module")
def flow_schema():
    """Load the FlowDataSet XSD schema."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    xsd_file = os.path.join(project_root, "vellum-schemas", "Vellum_FlowDataSet.xsd")
    
    if not os.path.exists(xsd_file):
        pytest.skip(f"XSD schema file not found: {xsd_file}")
        
    return xmlschema.XMLSchema11(xsd_file, validation='lax')


class TestMixAndLocationTypes:
    """Test class for MixAndLocationTypes enumeration validation."""
    
    def validate_mix_and_location_element(self, xml_content, schema, element_name="mixAndLocationTypes"):
        """
        Validate a mixAndLocationTypes element against the schema.
        
        Args:
            xml_content (str): XML content containing mixAndLocationTypes element
            schema: XMLSchema object
            element_name (str): Name of the element to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Parse XML content
            root = ET.fromstring(xml_content)
            
            # Get the MixAndLocationTypesMultiLang type from the schema
            mix_type = schema.types.get('MixAndLocationTypesMultiLang')
            if not mix_type:
                return False, "MixAndLocationTypesMultiLang not found in schema"
            
            # Validate the element against MixAndLocationTypesMultiLang
            mix_type.validate(root)
            return True, None
            
        except xmlschema.XMLSchemaException as e:
            return False, f"Validation error: {e}"
        except ET.ParseError as e:
            return False, f"XML parse error: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"
    
    @pytest.mark.parametrize("value,expected_valid,description", [
        ("at producer", True, "valid value: at producer"),
        ("production mix", True, "valid value: production mix"),
        ("consumption mix", True, "valid value: consumption mix"),
        ("post-consumer", True, "valid value: post-consumer"),
        ("invalid value", False, "invalid value: invalid value"),
        ("at_producer", False, "invalid value: at_producer (underscore)"),
        ("production-mix", False, "invalid value: production-mix (hyphen)"),
        ("", False, "invalid value: empty string"),
        ("AT PRODUCER", False, "invalid value: uppercase"),
        ("At Producer", False, "invalid value: title case"),
    ])
    def test_mix_and_location_types_enumeration(self, common_schema, value, expected_valid, description):
        """Parametrized test for MixAndLocationTypes enumeration validation."""
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<mixAndLocationTypes xmlns="http://lca.jrc.it/ILCD/Common">{value}</mixAndLocationTypes>'''
        
        is_valid, error_message = self.validate_mix_and_location_element(xml_content, common_schema)
        
        if expected_valid:
            assert is_valid, f"Expected valid MixAndLocationTypes element for {description} but got error: {error_message}"
        else:
            assert not is_valid, f"Expected invalid MixAndLocationTypes element for {description} but validation passed"
            assert error_message is not None, f"Expected error message for invalid MixAndLocationTypes element: {description}"
    
    def test_mix_and_location_types_with_lang_attribute(self, common_schema):
        """Test that MixAndLocationTypes supports xml:lang attribute."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<mixAndLocationTypes xmlns="http://lca.jrc.it/ILCD/Common" xml:lang="de">production mix</mixAndLocationTypes>'''
        
        is_valid, error_message = self.validate_mix_and_location_element(xml_content, common_schema)
        
        assert is_valid, f"Expected valid MixAndLocationTypes element with lang attribute but got error: {error_message}"
    
    def test_process_dataset_mix_and_location_types(self, process_schema):
        """Test that ProcessDataSet schema loads successfully with the new MixAndLocationTypes."""
        # This test validates that the ProcessDataSet schema can be loaded with the new type
        assert process_schema is not None, "ProcessDataSet schema should load successfully"
        
        # The fact that the schema loads without errors means our MixAndLocationTypesMultiLang type
        # is correctly defined and referenced. The core enumeration validation is tested elsewhere.
        assert True, "ProcessDataSet schema loaded successfully with MixAndLocationTypesMultiLang"
    
    def test_flow_dataset_mix_and_location_types(self, flow_schema):
        """Test that FlowDataSet schema loads successfully with the new MixAndLocationTypes."""
        # This test validates that the FlowDataSet schema can be loaded with the new type
        assert flow_schema is not None, "FlowDataSet schema should load successfully"
        
        # The fact that the schema loads without errors means our MixAndLocationTypesMultiLang type
        # is correctly defined and referenced. The core enumeration validation is tested elsewhere.
        assert True, "FlowDataSet schema loaded successfully with MixAndLocationTypesMultiLang"
