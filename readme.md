![Vellum logo](https://github.com/cauldron/vellum/blob/main/img/logo.png)

Vellum is [ILCD](https://eplca.jrc.ec.europa.eu/ilcd.html), but better. Every Vellum document is a valid ILCD document, but has the follow improvements over ILCD 1.1:

Vellum is made by [Cauldron Solutions](https://www.cauldron.ch/) with funding from the [International Zinc Association](https://www.zinc.org/)

# Problem Statement

The ILCD format is large and complex. Though the format contains many potentially useful fields, trying to fill out every field for every graph node (process, flow) and edge is effectively impossible - there are at least 150 fields just for a process data set, for example.

To see how ILCD is being used, we looked at the following dataset providers:

* Blonk (PEF AGROFOOD, FEED, and RENEWABLES): Retrieved from https://lcdn.blonkconsultants.nl/ on 28.05.2025
* Cobalt Institute: Retrieved from https://lca-data.cobaltinstitute.org/ on 28.05.2025
* ecosystem WEEE: Retrieved from https://weee-lci.ecosystem.eco/ on 28.05.2025
* ESIG (PEF): Retrieved from https://data.esig.org on 02.05.2025
* Hydrogen (PEF): Retrieved from https://eplca.jrc.ec.europa.eu/EF-SDP/ on 02.05.2025
* Hyguide: Retrieved from https://fc-hyguide.eu/lca-data-sets.html on 12.05.2025
* JRC EF Representative Products (PEF): Retrieved from https://eplca.jrc.ec.europa.eu/EF-node/ on 28.05.2025
* KEITI (Korea Environmental Industry & Technology Institute): Retrieved from http://133.186.241.65/ on 28.05.2025
* KRICT (Korea Research Institute on Chemical Technology): Retrieved from https://lcdn-krictlci.com/ on 28.05.2025
* TianGong: Retrieved from https://github.com/linancn/TianGong-LCA-Data on 02.05.2025 (Last commit from 05.04.2025)

Overall, we examined 10259 processes, 134700 flows, and 1212 flow properties, which to the best of our knowledge were produced by at least three different ILCD-generating software systems. As an indication of the difficulty in correctly complying with the ILCD standards, we note that many of these data files are *not valid* when validating against the ILCD 1.1 schemas:

* Processes: 5088 of 10259 (49.6%) invalid
* Flows: 107308 of 134700 (79.6%) invalid
* Flow properties: 0 of 1212 (0%) invalid

# Vellum Approach

We are building a 100% ILCD-compliant (**as ILCD is being used**, not as specified) schema as an example of how ILCD could be updated.

## Sane unit handling

In ILCD, you can easily get the unit label for an `exchange` in a process data set. You just have to:

- Parse the file indicated by the `referenceToFlowDataSet`, which is a `GlobalReferenceType`. This is normally included together with the package, but doesn't have to be. Load this new file.
- Read the `referenceToReferenceFlowProperty` (it's an integer)
- Iterate through the flow properties, and find the one whose `dataSetInternalID` matches the `referenceToReferenceFlowProperty`
- Parse the file indicated by the `referenceToFlowPropertyDataSet`, which is a `GlobalReferenceType`. This is normally included together with the package, but doesn't have to be. Load this new file.
- Parse the file indicated by the `referenceToReferenceUnitGroup`, which is a `GlobalReferenceType`. This is normally included together with the package, but doesn't have to be. Load this new file.
- Read the `referenceToReferenceUnit` (it's an integer)
- Iterate through the units, and find the one whose `dataSetInternalID` matches the `referenceToReferenceUnit`.
- Read the `name` field from this element

In Vellum, it's much less structured:

- The `unitName` is a required attribute of an `exchange`.

## Variables should require an amount

The point of variables is to give numeric values which can be used in formulas or calculations. However, the field `meanValue` is currently optional: `<xs:element name="meanValue" type="common:Real" minOccurs="0">`. Vellum removes the `minOccurs="0"` to guarantee that variables can actually be used.

## Schema documentation that agrees with formal restrictions

This isn't great:

```xml
<xs:simpleType name="String">
    <xs:annotation>
        <xs:documentation>String with a maximum length of 500 characters. Must have a minimum length of 1.</xs:documentation>
    </xs:annotation>
    <xs:restriction base="xs:string">
        <xs:minLength value="0"/>
        <xs:maxLength value="500"/>
    </xs:restriction>
</xs:simpleType>
```

Vellum correctly puts the restrictions back into the description.

## Some free text fields should be chosen from a list of pre-selected options

There are some fields where ILCD users are providing the same information with slightly different phrasing. In vellum, `ProcessDataSet.mixAndLocationTypes` is reduced to a choice between:

* `at producer`
* `production mix`
* `consumption mix`
* `post-consumer`

In normal LCA practice, the production mix is what is produced within the region of interest, whereas the consumption mix include production and imports.

These choices are not exhaustive, but in all the data we have reviewed, providers are using the general comment field to give more detail on exactly what is included (e.g. transport and loss across the distribution change), so duplicating that information in `mixAndLocationTypes` isn't valuable.

### CAS regular expression is outdated

The regular expression for Chemical Abstract Service (CAS) numbers enforce exactly six digits in the first section (before the first hyphen): `\d{6}-\d{2}-\d`. However, around 2008 the American Chemical Society added a seventh digit to the first section. Therefore, the regular expression should be updated to `\d{7}-\d{2}-\d`. As this formulation would require zero-padding (i.e. _exactly_ seven digits), it might be more sensible to remove the requirement of zero-padding altogether; in that case, the regular expression would be `\d{2,7}-\d{2}-\d`.

### No use of semicolons or commas to separate distinct values

For some reason the following was accepted into the ILCD format:

```xml
<synonyms>this;is;a;terrible;idea</synonyms>
```

Instead of the much more sensible:

```xml
<synonyms>
    <synonym>this</synonym>
    <synonym>is</synonym>
    <synonym>much</synonym>
    <synonym>better</synonym>
</synonyms>
```

In Vellum, `synonyms` allows for `synonym` subelements.

The same problem shows up in GIS coordinates. Our format is already verbose; there is no reason to have:

```xml
<latitudeAndLongitude>36.504;128.103</latitudeAndLongitude>
```

Instead of:

```xml
<latitude>36.504</latitude>
<longitude>128.103</longitude>
```

The second option would also allow for proper typing (float with constraints instead of string with the following regular expression of death: `"\s*([\-+]?(([0-8]?\d)(\.\d*)?)|(90(\.0{0,2})?))\s*;\s*(([\-+]?(((1[0-7]\d)(\.\d*)?)|([0-9]\d(\.\d*)?)|(\d(\.\d*)?)|(180(\.[0]*)?))))\s*"`).

In Vellum, the attributes `latitude` and `longitude` (as floats) are allowed for the element `latitudeAndLongitude`.

# Possible Additional Future Improvements in ILCD/Vellum

## Simplify multilingual string types

The file `ILCD_Common_DataTypes.xsd` defines three version of a multilingual string: `FTMultiLang`, `STMultiLang`, and `StringMultiLang`. Having three different string types with arbitrary length restrictions introduces complexity without providing any value. In our analysis of real ILCD use, these length restrictions are routinely ignored, and we expect that all ILCD-consuming programs also accept strings outside these length limits. We can therefore safely simplify the schema documentation to use a single multilingual string type.

### `GlobalReferenceType` should require that reference resources be available

The `GlobalReferenceType` is used extensively in ILCD to refer to data in other files. However, the current standard doesn't require that these other files are actually available. This is especially problematic for defining exchanges, as this is a perfectly valid exchange:

```xml
<exchange dataSetInternalID="0">
    <referenceToFlowDataSet
        type="flow data set"
        uri="../flows/you-will-never-find-me.xml"
        refObjectId="12345678-1111-2222-aaaa-abcdefghijkl">
 </referenceToFlowDataSet>
 <exchangeDirection>Output</exchangeDirection>
 <meanAmount>1.0</meanAmount>
</exchange>
```

However, this completely breaks any use of this process - we don't know anything about the flow or even the unit associated with the value `1.0`.

This isn't easy to fix in the XSD files, as in ILCD most of these references are relative file paths, but file URIs [do not allow for relative paths](https://en.wikipedia.org/wiki/File_URI_scheme), so using the XPath `doc-available` call doesn't seem like it would work. In this case I think validation outside the XSD should be specified.
