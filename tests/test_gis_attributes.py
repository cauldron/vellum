"""
Pytest test to validate that GIS type requires latitude and longitude attributes.
"""

import os
import pytest
import xmlschema
import xml.etree.ElementTree as ET


@pytest.fixture(scope="module")
def gis_schema():
    """Load the XSD schema containing the GIS type definition."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    xsd_file = os.path.join(project_root, "vellum-schemas", "Vellum_Common_DataTypes.xsd")
    
    if not os.path.exists(xsd_file):
        pytest.skip(f"XSD schema file not found: {xsd_file}")
        
    return xmlschema.XMLSchema11(xsd_file, validation='lax')


class TestGISAttributes:
    """Test class for GIS attribute requirements."""
    
    def validate_gis_element(self, xml_content, schema):
        """
        Validate a GIS element against the schema.
        
        Args:
            xml_content (str): XML content containing GIS element
            schema: XMLSchema object
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Parse XML content
            root = ET.fromstring(xml_content)
            
            # Get the GIS type from the schema
            gis_type = schema.types.get('GIS')
            if not gis_type:
                return False, "GIS type not found in schema"
            
            # Validate the element against GIS type
            gis_type.validate(root)
            return True, None
            
        except xmlschema.XMLSchemaException as e:
            return False, f"Validation error: {e}"
        except ET.ParseError as e:
            return False, f"XML parse error: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"
    
    def test_gis_with_both_attributes_valid(self, gis_schema):
        """Test that GIS element with both required attributes is valid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<gis xmlns="http://lca.jrc.it/ILCD/Common" latitude="42.5" longitude="-73.8">42.5;-73.8</gis>'''
        
        is_valid, error_message = self.validate_gis_element(xml_content, gis_schema)
        
        assert is_valid, f"Expected valid GIS element but got error: {error_message}"
    
    def test_gis_missing_latitude_attribute(self, gis_schema):
        """Test that GIS element missing latitude attribute is invalid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<gis xmlns="http://lca.jrc.it/ILCD/Common" longitude="-73.8">42.5;-73.8</gis>'''
        
        is_valid, error_message = self.validate_gis_element(xml_content, gis_schema)
        
        assert not is_valid, "Expected invalid GIS element (missing latitude) but validation passed"
        assert "latitude" in error_message.lower() or "required" in error_message.lower(), \
            f"Expected latitude/required error, got: {error_message}"
    
    def test_gis_missing_longitude_attribute(self, gis_schema):
        """Test that GIS element missing longitude attribute is invalid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<gis xmlns="http://lca.jrc.it/ILCD/Common" latitude="42.5">42.5;-73.8</gis>'''
        
        is_valid, error_message = self.validate_gis_element(xml_content, gis_schema)
        
        assert not is_valid, "Expected invalid GIS element (missing longitude) but validation passed"
        assert "longitude" in error_message.lower() or "required" in error_message.lower(), \
            f"Expected longitude/required error, got: {error_message}"
    
    def test_gis_missing_both_attributes(self, gis_schema):
        """Test that GIS element missing both attributes is invalid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<gis xmlns="http://lca.jrc.it/ILCD/Common">42.5;-73.8</gis>'''
        
        is_valid, error_message = self.validate_gis_element(xml_content, gis_schema)
        
        assert not is_valid, "Expected invalid GIS element (missing both attributes) but validation passed"
        assert ("latitude" in error_message.lower() or "longitude" in error_message.lower() or 
                "required" in error_message.lower()), \
            f"Expected latitude/longitude/required error, got: {error_message}"
    
    def test_gis_invalid_latitude_range(self, gis_schema):
        """Test that GIS element with latitude outside valid range is invalid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<gis xmlns="http://lca.jrc.it/ILCD/Common" latitude="95.0" longitude="-73.8">95.0;-73.8</gis>'''
        
        is_valid, error_message = self.validate_gis_element(xml_content, gis_schema)
        
        assert not is_valid, "Expected invalid GIS element (latitude > 90) but validation passed"
        assert "latitude" in error_message.lower() or "90" in error_message.lower(), \
            f"Expected latitude/90 error, got: {error_message}"
    
    def test_gis_invalid_longitude_range(self, gis_schema):
        """Test that GIS element with longitude outside valid range is invalid."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<gis xmlns="http://lca.jrc.it/ILCD/Common" latitude="42.5" longitude="185.0">42.5;185.0</gis>'''
        
        is_valid, error_message = self.validate_gis_element(xml_content, gis_schema)
        
        assert not is_valid, "Expected invalid GIS element (longitude > 180) but validation passed"
        assert "longitude" in error_message.lower() or "180" in error_message.lower(), \
            f"Expected longitude/180 error, got: {error_message}"
    
    @pytest.mark.parametrize("latitude,longitude,expected_valid,description", [
        (42.5, -73.8, True, "valid coordinates"),
        (0.0, 0.0, True, "equator and prime meridian"),
        (-90.0, -180.0, True, "minimum valid coordinates"),
        (90.0, 180.0, True, "maximum valid coordinates"),
        (95.0, -73.8, False, "latitude too high"),
        (-95.0, -73.8, False, "latitude too low"),
        (42.5, 185.0, False, "longitude too high"),
        (42.5, -185.0, False, "longitude too low"),
    ])
    def test_gis_coordinate_ranges(self, gis_schema, latitude, longitude, expected_valid, description):
        """Parametrized test for GIS coordinate range validation."""
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<gis xmlns="http://lca.jrc.it/ILCD/Common" latitude="{latitude}" longitude="{longitude}">{latitude};{longitude}</gis>'''
        
        is_valid, error_message = self.validate_gis_element(xml_content, gis_schema)
        
        if expected_valid:
            assert is_valid, f"Expected valid GIS element for {description} but got error: {error_message}"
        else:
            assert not is_valid, f"Expected invalid GIS element for {description} but validation passed"
            assert error_message is not None, f"Expected error message for invalid GIS element: {description}"
