# DEC-085: SmartPlant-style extraction rebuilds W-SP's segments, flows, parent and continuation from the rows, keyed by the backend's GUIDs

Status: Decided
Date: 2026-10-19

## Context

MILESTONE-001b takes W-SP through the same slice as MILESTONE-001
([DEC-042](DEC-042-w-sp-scn-001-first.md)), so source records must be extracted from
the SmartPlant-style backend without reading W-SP's answer key. [DEC-075](DEC-075-extraction-records.md) set the
record shapes and identity for the Plant 3D-style backend, whose rows state each
connection directly. The SmartPlant-style rows do not
([DEC-081](DEC-081-smartplant-style-patterns.md)): pipe segments are line depictions
of runs, a line's direction comes from its run, nozzles stand between pipes and
vessels, sheet links store only continuation, and no run stores a key to its
pipeline's line group. The
agent decided how extraction handles them during the MILESTONE-001b night run, under
the owner's delegation in [DEC-080](DEC-080-milestone-001b-night-delegation.md). The
owner can reverse any of it.

## Decision

1. **Same shapes, two readers.** `scripts/extract_sps.py` writes the records
   `scripts/extract_p3d.py` writes, from SQL Server or from a snapshot folder checked
   against its manifest. Both readers give the same records.
2. **Identity.** An item is `sps:item:<GUID>`, a pipe segment is its line depiction,
   `sps:line:<GUID>`, and a drawing is `sps:sheet:<GUID>`: the backend's own keys,
   which stay the same across snapshots. `scripts/compare_answer_key.py` maps these
   through the answer key's `keys`, and only for a key whose backend is `sps`.
3. **Objects.** Vessels, fittings, instruments and sheet links that are active become
   objects, and so does each line depiction of an active run. Runs, nozzles and
   process connections do not; they appear in the evidence of the facts that pass
   through them. A segment's tag is the text of the label on its line.
4. **Rebuilt facts are marked derived.** Relationships use extract_p3d's predicates
   so that both backends' records map to the graph the same way:
   - `starts_at` and `ends_at` for each segment, from the items its line's ends
     name, with upstream set by the run's flow sense;
   - an active nozzle at a line end counts as its parent vessel;
   - `owned_by` from an instrument to the vessel whose nozzle its process connection
     reaches;
   - `continues_to` from the "To" side of a sheet-link pair to the "From" side.
   These, and the line-number parts and size that each segment takes from its run,
   have evidence status `derived`. Facts a row states directly are `source_stated`.
5. **The pipeline.** A run belongs to the line group whose line prefix and number
   match its own; a run with either part NULL belongs to none, and a run that matches
   two groups stops extraction. No key links them, so matching is the only route.
   Each member run's segments get a derived `pipeline` assertion, `L-301` for W-SP,
   whose evidence names the line group and every member run. The pipeline is not an
   object, so the graph is the world file's.
6. **Contradictions stop extraction.** A sheet-link pair whose sides do not name each
   other, with one "To" and one "From" side, and each other's sheets, stops it. That
   covers a link that names a mate and a link that another link names, so a side that
   lost its mate is caught; only a link that no row pairs with stays unpaired, with no
   continuation. A process connection that does not join one instrument to one
   nozzle, a line whose labels have different texts, or an unknown flow sense also
   raises an error. Labels and marks are not unique in the schema, so
   extraction reads all of them: a side's sheet matches when any of its mate's marks
   is on it, and a repeated label with the same text is one tag. The result never
   depends on row order. A line end
   that reaches a missing or deleted item is kept as stated, for validation to
   reject, as DEC-075 does. A deleted nozzle counts as such an item: it is not
   collapsed into its vessel, so a segment end or an instrument parent through it
   names the nozzle.
7. **Drawing approval.** A drawing's latest revision is the row the source recorded
   last, by its recorded time; its labels are text, so they are not sorted as
   numbers. A drawing's status is `Approved` when that latest revision row
   has both an approver and an approval date, the fields
   [DEC-039](DEC-039-approval-in-vendor-fields.md) names, and empty otherwise.
8. **No answer key.** The extractor never opens one; a test records every file it
   opens and fails if any is an answer key.

## Alternatives considered

- Report only what the rows state, as DEC-075 does, and rebuild the graph in a later
  step. The MILESTONE-001b definition drafted on branch `docs/define-milestone-001b`
  asks extraction to join the run pieces and derive the pipeline, and
  `scripts/dexpi_generate.py` reads segments and their ends from the records.
- Make the pipeline an object. The graph would then hold a node the world file does
  not have.
- Keep extracting when the two sides of a sheet-link pair disagree, without the
  continuation. The comparison would then fail with a missing edge and no reason.

## Owner's words

Given on 2026-10-19 (UTC) and recorded in
[DEC-080](DEC-080-milestone-001b-night-delegation.md): the owner chose the option the
agent offered for deciding this run's open questions.

The owner answered:

> Yes, decide for me

## Evidence

- `scripts/test_extract_sps.py`. It builds a graph from the extracted records and
  scores it with `scripts/compare_answer_key.py` against W-SP's answer key: an exact
  match. Its expected edges, objects, tags, attributes and appearances are typed by
  hand from `worlds/W-SP.yaml`. Edited rows show each derivation follows the rows: a
  changed flow sense reverses run B's edges, a run whose line number changes leaves
  the group, a second group row gathers it, a run with a NULL part or a snapshot
  without the group row gives no pipeline, and a disagreeing sheet link stops
  extraction. Against SQL Server 2022
  on 2026-10-19, the database and the snapshot gave the same records.
