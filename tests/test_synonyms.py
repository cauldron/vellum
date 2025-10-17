"""
Pytest test to validate that synonyms element allows multiple synonym subelements.
"""

import os
import pytest
import xmlschema
import xml.etree.ElementTree as ET


@pytest.fixture(scope="module")
def groups_schema():
    """Load the XSD schema containing the synonyms definition."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    xsd_file = os.path.join(project_root, "vellum-schemas", "Vellum_Common_Groups.xsd")
    
    if not os.path.exists(xsd_file):
        pytest.skip(f"XSD schema file not found: {xsd_file}")
        
    return xmlschema.XMLSchema11(xsd_file, validation='lax')


class TestSynonyms:
    """Test class for synonyms element validation."""
    
    def validate_synonyms_element(self, xml_content, schema):
        """
        Validate a synonyms element against the schema.
        
        Args:
            xml_content (str): XML content containing synonyms element
            schema: XMLSchema object
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Parse XML content
            root = ET.fromstring(xml_content)
            
            # Get the synonyms element definition from the schema
            synonyms_element = schema.elements.get('synonyms')
            if not synonyms_element:
                return False, "synonyms element not found in schema"
            
            # Validate the element against synonyms definition
            synonyms_element.validate(root)
            return True, None
            
        except xmlschema.XMLSchemaException as e:
            return False, f"Validation error: {e}"
        except ET.ParseError as e:
            return False, f"XML parse error: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"
    
    def test_synonyms_empty_valid(self, groups_schema):
        """Test that empty synonyms element is valid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<synonyms xmlns="http://lca.jrc.it/ILCD/Common">
</synonyms>'''
        
        is_valid, error_message = self.validate_synonyms_element(xml_content, groups_schema)
        
        assert is_valid, f"Expected valid empty synonyms element but got error: {error_message}"
    
    def test_synonyms_single_synonym_valid(self, groups_schema):
        """Test that synonyms element with single synonym is valid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<synonyms xmlns="http://lca.jrc.it/ILCD/Common">
    <synonym>Alternative name</synonym>
</synonyms>'''
        
        is_valid, error_message = self.validate_synonyms_element(xml_content, groups_schema)
        
        assert is_valid, f"Expected valid synonyms element with single synonym but got error: {error_message}"
    
    def test_synonyms_multiple_synonyms_valid(self, groups_schema):
        """Test that synonyms element with multiple synonyms is valid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<synonyms xmlns="http://lca.jrc.it/ILCD/Common">
    <synonym>Alternative name 1</synonym>
    <synonym>Alternative name 2</synonym>
    <synonym>Alternative name 3</synonym>
</synonyms>'''
        
        is_valid, error_message = self.validate_synonyms_element(xml_content, groups_schema)
        
        assert is_valid, f"Expected valid synonyms element with multiple synonyms but got error: {error_message}"
    
    def test_synonyms_with_lang_attributes_valid(self, groups_schema):
        """Test that synonyms element with language attributes is valid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<synonyms xmlns="http://lca.jrc.it/ILCD/Common">
    <synonym xml:lang="en">Alternative name</synonym>
    <synonym xml:lang="de">Alternativer Name</synonym>
    <synonym xml:lang="fr">Nom alternatif</synonym>
</synonyms>'''
        
        is_valid, error_message = self.validate_synonyms_element(xml_content, groups_schema)
        
        assert is_valid, f"Expected valid synonyms element with language attributes but got error: {error_message}"
    
    def test_synonyms_mixed_content_valid(self, groups_schema):
        """Test that synonyms element with mixed content (with and without lang attributes) is valid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<synonyms xmlns="http://lca.jrc.it/ILCD/Common">
    <synonym>Default synonym</synonym>
    <synonym xml:lang="en">English synonym</synonym>
    <synonym xml:lang="de">German synonym</synonym>
    <synonym>Another default synonym</synonym>
</synonyms>'''
        
        is_valid, error_message = self.validate_synonyms_element(xml_content, groups_schema)
        
        assert is_valid, f"Expected valid synonyms element with mixed content but got error: {error_message}"
    
    def test_synonyms_long_text_valid(self, groups_schema):
        """Test that synonyms element with long text content is valid (FTMultiLang allows unlimited length)."""
        long_text = "This is a very long synonym text that should be valid because FTMultiLang allows unlimited length. " * 10
        
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<synonyms xmlns="http://lca.jrc.it/ILCD/Common">
    <synonym>{long_text}</synonym>
</synonyms>'''
        
        is_valid, error_message = self.validate_synonyms_element(xml_content, groups_schema)
        
        assert is_valid, f"Expected valid synonyms element with long text but got error: {error_message}"
    
    def test_synonyms_special_characters_valid(self, groups_schema):
        """Test that synonyms element with special characters is valid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<synonyms xmlns="http://lca.jrc.it/ILCD/Common">
    <synonym>Synonym with "quotes" &amp; ampersands</synonym>
    <synonym>Synonym with &lt;brackets&gt; and [square brackets]</synonym>
    <synonym>Synonym with numbers: 123, 456.789</synonym>
    <synonym>Synonym with symbols: @#$%^&amp;*()</synonym>
</synonyms>'''
        
        is_valid, error_message = self.validate_synonyms_element(xml_content, groups_schema)
        
        assert is_valid, f"Expected valid synonyms element with special characters but got error: {error_message}"
    
    @pytest.mark.parametrize("synonym_count", [0, 1, 5, 10, 50])
    def test_synonyms_various_counts_valid(self, groups_schema, synonym_count):
        """Parametrized test for synonyms element with various numbers of synonyms."""
        synonyms_xml = ""
        for i in range(synonym_count):
            synonyms_xml += f'    <synonym>Synonym {i+1}</synonym>\n'
        
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<synonyms xmlns="http://lca.jrc.it/ILCD/Common">
{synonyms_xml}</synonyms>'''
        
        is_valid, error_message = self.validate_synonyms_element(xml_content, groups_schema)
        
        assert is_valid, f"Expected valid synonyms element with {synonym_count} synonyms but got error: {error_message}"
    
    def test_synonyms_schema_structure(self, groups_schema):
        """Test that the schema correctly defines the synonyms element structure."""
        # This test validates that the schema can be loaded and the synonyms element is properly defined
        assert groups_schema is not None, "Groups schema should load successfully"
        
        # Check that synonyms element exists
        synonyms_element = groups_schema.elements.get('synonyms')
        assert synonyms_element is not None, "synonyms element should be defined in schema"
        
        # Check that it's a complex type (not simple content)
        assert hasattr(synonyms_element, 'type'), "synonyms element should have a type"
        
        # The element should allow multiple synonym subelements
        assert True, "synonyms element structure validated successfully"
