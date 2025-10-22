### Conversion

#### *UUID*

The Tag ID of MISP Event Tags, is put through the str\_to\_uuid() function, which then generates a UUID for the Event Tag. After which a TAXII Collection is made using the Tag UUID.

#### *MISP-STIX*

The function misp\_to\_stix() is called to convert the retrieved MISP data after it has been converted into JSON. 

##### **Mapping**

| MISP Datastructure | STIX Object |
| :---- | :---- |
| Event | Report or Grouping |
| Attribute | Indicator, Observable, Vulnerability,Campaign, Custom Object |
| Object | Indicator, Observable  Vulnerability, Threat Actor, Course of Action, Custom Object |
| Galaxy | Vulnerability, Threat Actor, Course of Action |

The conversion table was acquired from the library's official repository, further detailed mapping for attributes can be acquired from the repository \[1\]. However, it will not be listed here due to size and possibility of library updates.