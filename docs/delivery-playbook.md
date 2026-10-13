# Delivery playbook: engineering data to a validated graph

Status: Draft, version 0.1. Started 2026-10-13.

This playbook is for a team building a pipeline that turns engineering source data,
such as a P&ID authoring database or an exchange file, into a validated, queryable
graph. It records what to do, what worked, and what did not. It describes
engineering practice only. How the work itself flows (pull requests, reviews,
decision records and checks) is in the
[way-of-working standard](https://github.com/aadehamid/personal-agent-skills/tree/main/skills/engineering/way-of-working).

## How to read an entry

Each practice carries one status, and says what the status rests on.

| Status | Meaning |
| --- | --- |
| Proven | A merged test or a recorded run shows that the practice works. |
| Proposed | The team decided on it, but has not built or tested it yet. |
| Didn't work | The team tried it and dropped it. The entry says why. |

Worked examples come from the project that started this playbook, a synthetic
P&ID pipeline that generates DEXPI files from a vendor-style backend and publishes
a graph. They are there to make a practice concrete. Adapt them; do not copy them.

## 1. Choose and pin the exchange standard

Status: Proposed. It rests on a review of the standard's releases and of the
tools available for it.

1. **Pick the newest release that fixes known errors.** A fix release that replaces
   an earlier one is the target, unless something is already built on the earlier
   release. Check the standard's own announcements, not a third-party summary.
2. **Pin the exact artifacts by hash.** For each artifact the pipeline reads or
   writes against (the schema, the information-model files, a reference example),
   record its source URL, release tag and SHA-256. A version name alone does not
   identify the bytes.
3. **Record the license of each artifact.** A specification's license may not
   cover separately packaged downloads. Record which statement covers which file.
4. **Survey the tools before choosing to write your own.** For each candidate
   library, record the release it supports, its license and its maintenance state.
   Exclude a tool that supports only an older release. Reading a newer format
   through an older-release tool is a silent downgrade.
5. **Pin every dependency exactly.** Pin libraries in the lock file and container
   images by digest. Choose the latest release that is at least 14 days old, which
   gives the release time to show problems. Record each version with its license.

Worked example: the project found that the standard's newest release replaced the
previous one weeks earlier, and that no library in its language supported either.
The one mature library supported only an older release, under a copyleft license.
The team chose to write a small generator and parser for only the classes it
needed.

## 2. Keep pinned copies of files from an unreliable host

Status: Proposed. It rests on repeated failures to fetch the standard's
model files from their published host.

1. **Do not fetch at validation time.** If a schema or model file imports others
   from a remote host, a check that fetches them depends on that host's uptime and
   certificate.
2. **Keep a pinned copy in the repository.** Take it from the standard's release
   tag or official supporting materials. Store its SHA-256, its source and its
   attribution next to it.
3. **Map each import to its local copy.** Have the validator resolve imports
   through a table of pinned files, and turn off network access in the XML parser.
4. **Never disable certificate checks.** If a host fails TLS verification, record
   the failure and use the pinned copy.
5. **Do not generate a missing official file.** If no official source has the
   file, stop and escalate. A file you wrote yourself is not the standard.

Worked example: the standard's example files import their model files from a host
that first failed certificate checks and later did not respond. The team decided
to keep pinned copies and validate offline.

## 3. Validate in named stages

Status: Proposed. It rests on the absence of any official validator for the
release, and on a review of what XML schema validation can and cannot detect.

An XML file can be valid against its schema and still describe an impossible
engineering model. Validate in stages, in this order, and make every failure name
its stage:

| Stage | What it checks | What a failure means |
| --- | --- | --- |
| 1. Schema | The file validates against the pinned XSD. | The file is not well-formed exchange XML. |
| 2. References | Every import maps to a pinned file, and every local and named reference resolves. | The file points at something that is not there. |
| 3. Model | Every class exists and is not abstract. Every property is declared for its class, with the right kind and data type. Every property has an allowed number of values. | The file breaks the standard's information model. |
| 4. Project rules | Rules that are yours and not the standard's, such as unique tags or required units. | The file breaks your project's rules, not the standard. |

Then add a round trip: generate, parse and generate again, and require the two
files to match exactly.

Practices that go with the stages:

1. **Keep stage 4 separate from stages 1 to 3.** A duplicated tag breaks a project
   rule. A dangling reference breaks the standard. A report that mixes them tells
   the reader the wrong thing.
2. **Give every negative fixture its expected stage.** A bad file that fails at the
   wrong stage shows the validator is wrong, even when the file fails.
3. **Parse a file you did not write.** Run the parser on the standard's own
   reference example. Extract the classes you support, and report the rest as
   unsupported without failing. Your own generator's output cannot catch a parser
   that only reads its own dialect.
4. **Report unsupported content.** Anything outside the classes and properties
   you support is listed, never dropped silently.
5. **Claim only the stages that ran.** If stages 1, 2 and 4 ran, the claim is
   "passes the schema and the project's rules". Never write "conformant" or
   "certified" unless an official conformance test exists and passed.

Worked example: the team's first plan had three checks: the schema, its own subset
rules, and a round trip. Its subset rules mixed standard failures with project
failures, so the plan moved to the four stages above.

## 4. Build synthetic worlds with hidden answer keys

Status: Proposed for the graph comparison. A synthetic backend, its generator and
its loader are built and tested, and the end-to-end comparison is not built yet.

1. **Hand-author one small, complete world first.** Write it as a data file checked
   against a schema. It holds the full engineering truth, including its intended
   errors.
2. **Generate each source view from the world.** A source view is one way a
   source presents the world, such as a vendor-style backend database. The
   generator writes files, and a separate loader applies them.
3. **Write the answer key separately from the source views.** The pipeline under
   test must never read it.
4. **Include bad revisions on purpose.** Each bad revision has one named defect, and
   the test expects that defect's exact rejection message. A rejected revision must
   leave the published graph unchanged.
5. **Compare exactly.** Normalize the published graph into the answer key's form
   and require equality. A synthetic world is fully known, so any difference is a
   defect.

Worked example: the team's first world is a small two-sheet P&ID with one
cross-sheet connection. One of its revisions has a flow line whose endpoint is
missing. The loader loads it, and the pipeline must reject it with a message that
names the missing endpoint.

## Appendix: notes on DEXPI as of 2026-10

These are facts about the standard as checked on 2026-10-13. Check them again
before you rely on them.

- **Releases.** DEXPI 2.0.0 was released on 2025-10-10. DEXPI 2.0.1 was released
  on 2026-09-30 as the update replacing 2.0. Its announcement says it fixes a small
  number of issues in the Plant model and improves the Process model.
- **Format.** DEXPI 2.0 uses DEXPI XML, with a `Model` root, in place of the older
  Proteus XML. No other encoding was found.
- **Source of truth.** The specification repository is
  [gitlab.com/dexpi/Specification](https://gitlab.com/dexpi/Specification). The
  V2.0.1 tag holds the XSD and a 2.0.1 reference P&ID. The HTML specification is
  at [dexpi.org/specification/2.0.1/html](https://dexpi.org/specification/2.0.1/html/).
- **License.** The specification states CC BY 4.0.
- **Model files.** Example files import `Core.xml` and `Plant.xml` from
  `data.dexpi.org`. That host failed certificate checks and later did not respond.
- **Validators.** No official 2.0 validator was found. The open-source
  [bpmn2dexpi](https://github.com/skhella/bpmn2dexpi) (MIT, TypeScript) validates
  2.0 files against the XSD and the information models, but it targets 2.0, not
  2.0.1.
- **Python libraries.** None reads or writes 2.0. pyDEXPI supports DEXPI 1.3, under
  AGPL-3.0-or-later. Its maintainer has said 2.0 support will come, without a date.
