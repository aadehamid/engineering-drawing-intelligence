# DEXPI 2.0.1 files

These files are unmodified copies of material from the DEXPI Specification 2.0.1,
released on 2026-09-30 by the DEXPI Initiative under the
[Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/legalcode).

- `DEXPI_XML_Schema.xsd` and `reference_pid.xml` come from the
  [specification repository](https://gitlab.com/dexpi/Specification) at tag `V2.0.1`.
- `Core.xml` and `Plant.xml` come from the
  [published 2.0.1 specification](https://dexpi.org/specification/2.0.1/html/). The tag holds
  these models as source, not XML. Building that source with DEXPI's own tool,
  `dexpi.specificator` 1.0.1, gives byte-identical files.

`MANIFEST.json` gives each file's SHA-256 and source. `scripts/dexpi_pins.py check` verifies them.
