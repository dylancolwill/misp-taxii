### Conversion

#### UUID

MISP uses tag identification through incremental numerical values and string names. TAXII requires collections to have a version 4 UUID, we have chosen to use tag names as the seed for this conversion. 

MISP tag names are put through `functions/conversion.str_to_uuid()`, to generate a UUID, used to identify the corresponding TAXII Collection. Returned in string format.

UUID version 4 does not take an input field, this function utlises version 5 for deterministic mapping. Since a database is not used in this project, a seed is required to ensure consistency.

#### MISP-STIX

The function `functions/misp.misp_to_stix()` is called to convert MISP event data into a STIX 2.1 bundle. Utilising the `MISPtoSTIX21Parser` function from the [`misp_stix_converter`](https://github.com/MISP/misp-stix) library to perform the conversion. 

#### STIX-MISP

The function `functions/conversion.stix_to_misp()` is used to convert STIX 2.1 bundles back into MISP event format. Utilising the `InternalSTIX2toMISPParser` function from the [`misp_stix_converter`](https://github.com/MISP/misp-stix) library to parse the STIX bundle and reconstruct the corresponding MISP events.

##### Mapping

| MISP Datastructure | STIX Object |
| :---- | :---- |
| Event | Report or Grouping |
| Attribute | Indicator, Observable, Vulnerability,Campaign, Custom Object |
| Object | Indicator, Observable  Vulnerability, Threat Actor, Course of Action, Custom Object |
| Galaxy | Vulnerability, Threat Actor, Course of Action |


The conversion table was acquired from the library's [official repository](https://github.com/MISP/misp-stix). However, it will not be listed here due to size and possibility of library updates.
