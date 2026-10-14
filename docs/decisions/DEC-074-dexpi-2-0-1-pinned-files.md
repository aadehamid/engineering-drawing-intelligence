# DEC-074: The pinned DEXPI 2.0.1 files are the XSD, the Core and Plant models and the reference P&ID, with the models taken from the published specification

Status: Decided
Date: 2026-10-14

## Context

[DEC-062](DEC-062-vendored-model-files.md) has LIONG keep pinned copies of the 2.0.1
model files the slice needs, taken from the V2.0.1 specification repository or DEXPI's
published supporting materials. If neither source has the XML files, the agent brings
that back to the owner. Building the copies raised three questions. The agent decided
them during the night run of 2026-10-14, under the owner's delegation in
[DEC-073](DEC-073-second-night-delegation.md). The owner can reverse any of them.

On 2026-10-14 the V2.0.1 tag (commit `eef0f0c6e8edfe84582e7a45d109c396bdc544f8`) held
the XSD and the reference P&ID as XML, but the Core, Plant and Process models only as
Python source for DEXPI's build tool, `dexpi.specificator`. The published 2.0.1
specification serves `Core.xml`, `Plant.xml` and `Process.xml` under its `_static`
folder, over a valid certificate. `data.dexpi.org`, the host the imports name, served
a certificate for another host name.

## Decision

1. **Where the models come from.** `Core.xml` and `Plant.xml` come from the published
   2.0.1 specification. These are DEXPI's published supporting materials, so DEC-062
   does not require a stop. The agent built the V2.0.1 tag's model source with
   `dexpi.specificator` 1.0.1, the version the tag's CI names, and the built files
   are byte-identical to the published ones.
2. **What is pinned.** `standards/dexpi/2.0.1` holds `DEXPI_XML_Schema.xsd`,
   `Core.xml`, `Plant.xml` and `reference_pid.xml`, unmodified, with their SHA-256
   hashes, sources and CC BY 4.0 attribution. `Process.xml` is not pinned, because the
   slice writes and reads only Plant classes.
3. **MetaData.xml.** `Core.xml` and `Plant.xml` import
   `https://data.dexpi.org/models/2.0.1/MetaData.xml`. DEXPI publishes no such file:
   `dexpi.specificator` defines that model in its own code, and only the model files'
   documentation annotations use it. The manifest records it as not published, and
   `scripts/dexpi_pins.py` refuses it as an import with that reason. The pull request
   that builds the validator decides how the model stage treats those annotations.

## Alternatives considered

- Build the model XML from the tag in CI instead of pinning it. That puts a large
  tool with many dependencies into every check, to make files that are already
  published.
- Pin `Process.xml` as well. Nothing in the slice uses it.
- Stop and ask the owner, as DEC-062 says when neither source has the files. The
  published specification has them, so the stop does not apply.

## Owner's words

Given on 2026-10-14 and recorded in [DEC-073](DEC-073-second-night-delegation.md).

The owner answered:

> you have my permission to decide for me using every available data and external search of hgih quality sources to resolve any ambiquity

## Evidence

- REF-STD-001 and REF-DATA-001 in the
  [reference register](../LIONG-REF-001-reference-register.md), updated on 2026-10-14.
- `standards/dexpi/2.0.1/MANIFEST.json` and `scripts/test_dexpi_pins.py`.
