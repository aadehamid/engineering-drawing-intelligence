-- The SmartPlant-style vendor-style backend (DEC-020, DEC-029), schema sps.
--
-- It follows how Smart P&ID stores a plant's saved data (DEC-031), using this
-- project's own names: no vendor table, column, class or code-list name, and no
-- vendor tag-format string. DEC-081 sets the seven borrowed patterns; each is cited
-- below by its register entry in docs/LIONG-REF-001-reference-register.md. DEC-082
-- records the choices this file makes under the owner's delegation (DEC-080).
--
-- It lives in the same database as schema p3d (DEC-028). No table has a foreign key
-- (DEC-043). Every key is a GUID that stays the same in every snapshot of a world,
-- and no other backend shares it (DEC-044). Run this file once on a database without
-- schema sps; it creates schema sps.

CREATE SCHEMA sps;
GO

-- Pattern 1: design items and depictions. Every engineering object is one design item,
-- keyed by a GUID, with a state that says whether it is active or deleted. One table
-- per class shares that key. Items carry no sheet key: each appearance on a sheet is
-- a depiction row (REF-TECH-019; the shared key, the GUID form and the sheet key's
-- place come from REF-TECH-029, a secondary source).
CREATE TABLE sps.DesignItem (
    ItemGuid  UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    ItemKind  NVARCHAR(32)     NOT NULL,  -- the class table that holds the item's columns
    ItemState NVARCHAR(16)     NOT NULL   -- select list ItemState: 'Active' or 'Deleted'
);

-- Pattern 6: tagged classes store the tag's parts next to the composed tag. The
-- composed tag is unique for vessels and instruments (REF-TECH-025, REF-TECH-027);
-- the nozzle and pipe-run rules are at their tables.
CREATE TABLE sps.Vessel (
    ItemGuid    UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    ItemTag     NVARCHAR(64)     NULL,
    TagLead     NVARCHAR(16)     NULL,
    TagNumber   NVARCHAR(16)     NULL,
    TagTail     NVARCHAR(8)      NULL,
    Description NVARCHAR(128)    NULL
);
CREATE UNIQUE INDEX UX_Vessel_ItemTag ON sps.Vessel (ItemTag) WHERE ItemTag IS NOT NULL;

-- An instrument tag's lead is its function letters, as in LT-302.
CREATE TABLE sps.Instrument (
    ItemGuid    UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    ItemTag     NVARCHAR(64)     NULL,
    TagLead     NVARCHAR(16)     NULL,
    TagNumber   NVARCHAR(16)     NULL,
    TagTail     NVARCHAR(8)      NULL,
    Unit        NVARCHAR(16)     NULL,
    Description NVARCHAR(128)    NULL
);
CREATE UNIQUE INDEX UX_Instrument_ItemTag ON sps.Instrument (ItemTag) WHERE ItemTag IS NOT NULL;

-- Pattern 2 and pattern 4: a pipe run is one design item. Its tag parts are the
-- line-number parts, and its composed tag may repeat: runs that share them form one
-- pipeline (REF-TECH-019, REF-TECH-022, REF-TECH-028). FlowSense says which end of each of the run's line depictions is
-- upstream (REF-TECH-019).
CREATE TABLE sps.PipeRun (
    ItemGuid      UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    ItemTag       NVARCHAR(64)     NULL,
    TagLead       NVARCHAR(16)     NULL,
    TagNumber     NVARCHAR(16)     NULL,
    TagTail       NVARCHAR(8)      NULL,
    NominalSizeMm INT              NULL,
    FlowSense     NVARCHAR(16)     NOT NULL  -- select list FlowSense: 'End1Upstream' or 'End2Upstream'
);

-- Pattern 4: a line group is the pipeline's row. It holds only the line key values;
-- no run stores a key to it. A run belongs to the group whose key values its own line
-- parts match, and a run with a NULL key part belongs to none (REF-TECH-022: the
-- application adds a pipeline entry as runs are drawn, and the relationship between
-- pipeline and run is implicit).
CREATE TABLE sps.LineGroup (
    GroupGuid UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    TagLead   NVARCHAR(16)     NOT NULL,
    TagNumber NVARCHAR(16)     NOT NULL
);

-- A piping fitting, such as a hand valve. Its tag is one plain column: piping
-- components are outside tag calculation (REF-TECH-025).
CREATE TABLE sps.PipingFitting (
    ItemGuid    UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    ItemTag     NVARCHAR(64)     NULL,
    Description NVARCHAR(128)    NULL
);

-- Pattern 7: a nozzle stores its parent vessel. Piping reaches a vessel through a
-- nozzle (REF-TECH-021, REF-TECH-027). Pattern 6: a nozzle's tag is unique within its
-- vessel and may repeat on another vessel (REF-TECH-022).
CREATE TABLE sps.Nozzle (
    ItemGuid   UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    ItemTag    NVARCHAR(64)     NULL,
    ParentItem UNIQUEIDENTIFIER NOT NULL
);
CREATE UNIQUE INDEX UX_Nozzle_ParentItem_ItemTag ON sps.Nozzle (ParentItem, ItemTag) WHERE ItemTag IS NOT NULL;

-- Pattern 7: an instrument on a vessel reaches the vessel's nozzle through a process
-- connection, a design item drawn as a line depiction (REF-TECH-027).
CREATE TABLE sps.ProcessConnection (
    ItemGuid    UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    Description NVARCHAR(128)    NULL
);

-- Pattern 5: each off-page connector of a pair stores its mate and its mate's sheet,
-- with a to or from orientation. No row stores the flow between them (REF-TECH-019,
-- REF-TECH-024).
CREATE TABLE sps.SheetLink (
    ItemGuid  UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    LinkLabel NVARCHAR(64)     NOT NULL,
    LinkSense NVARCHAR(8)      NOT NULL,  -- select list LinkSense: 'To' or 'From'
    MateItem  UNIQUEIDENTIFIER NULL,
    MateSheet UNIQUEIDENTIFIER NULL
);

-- Pattern 1: each appearance of an item on a sheet. A mark is a symbol, a line is a
-- drawn piece of a run or a process connection, and a label is text placed on
-- another depiction. A label belongs to no item, so its ItemGuid is NULL
-- (REF-TECH-019).
CREATE TABLE sps.Depiction (
    DepictionGuid UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    ItemGuid      UNIQUEIDENTIFIER NULL,
    SheetGuid     UNIQUEIDENTIFIER NOT NULL,
    DepictionKind NVARCHAR(8)      NOT NULL  -- select list DepictionKind: 'Mark', 'Line' or 'Label'
);

-- Pattern 2: a line depiction shares its key with a Depiction row and names the mark
-- depiction at each end, in the order the line was drawn. A free end is NULL. Each
-- inline fitting splits a line in two (REF-TECH-019).
CREATE TABLE sps.LineDepiction (
    DepictionGuid UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    End1Mark      UNIQUEIDENTIFIER NULL,
    End2Mark      UNIQUEIDENTIFIER NULL
);

-- A label depiction's text and the depiction it labels (REF-TECH-019).
CREATE TABLE sps.LabelDepiction (
    DepictionGuid     UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    LabelledDepiction UNIQUEIDENTIFIER NOT NULL,
    LabelText         NVARCHAR(64)     NOT NULL
);

-- Pattern 3: a fitting's membership in its run is a row of its own, not a column on
-- the fitting (REF-TECH-019).
CREATE TABLE sps.InlinePlacement (
    PlacementGuid UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    ItemGuid      UNIQUEIDENTIFIER NOT NULL UNIQUE,
    RunGuid       UNIQUEIDENTIFIER NOT NULL
);

-- Pattern 3: numbered connection points on a fitting, instrument or nozzle,
-- unique within their owner (REF-TECH-019).
CREATE TABLE sps.PortPoint (
    PointGuid UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    OwnerItem UNIQUEIDENTIFIER NOT NULL,
    PointNo   INT              NOT NULL,
    CONSTRAINT UQ_PortPoint_Owner UNIQUE (OwnerItem, PointNo)
);

-- Sheets. A sheet number is unique (REF-TECH-019).
CREATE TABLE sps.Sheet (
    SheetGuid UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    SheetNo   NVARCHAR(64)     NOT NULL UNIQUE
);

-- Revision rows, many to one sheet, with a major and a minor number unique together
-- on their sheet (REF-TECH-019, REF-TECH-026). ApprovalState is the source approval
-- (DEC-039); RevisedOn is when the source recorded the revision (DEC-045).
CREATE TABLE sps.SheetRevision (
    RevisionGuid  UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    SheetGuid     UNIQUEIDENTIFIER NOT NULL,
    MajorRev      NVARCHAR(8)      NOT NULL,
    MinorRev      NVARCHAR(8)      NOT NULL,
    RevisedOn     DATETIME2(0)     NOT NULL,
    ApprovalState NVARCHAR(32)     NOT NULL,
    CONSTRAINT UQ_SheetRevision_Number UNIQUE (SheetGuid, MajorRev, MinorRev)
);

-- The data dictionary, for W-SP's classes only (DEC-032): item types, their
-- properties, and the select lists that coded columns draw from (REF-TECH-019).
CREATE TABLE sps.ItemType (
    ItemKind    NVARCHAR(32)  NOT NULL PRIMARY KEY,
    ParentKind  NVARCHAR(32)  NULL,
    TableName   NVARCHAR(64)  NOT NULL,
    DisplayName NVARCHAR(128) NOT NULL,
    TagFormat   NVARCHAR(64)  NULL
);

CREATE TABLE sps.ItemProperty (
    ItemKind     NVARCHAR(32)  NOT NULL,
    PropertyName NVARCHAR(64)  NOT NULL,
    DataType     NVARCHAR(32)  NOT NULL,
    DisplayName  NVARCHAR(128) NOT NULL,
    TagPart      INT           NULL,  -- position in the tag format, or NULL
    SelectList   NVARCHAR(32)  NULL,  -- the select list its values come from, or NULL
    PRIMARY KEY (ItemKind, PropertyName)
);

CREATE TABLE sps.SelectEntry (
    ListName    NVARCHAR(32)  NOT NULL,
    EntryValue  NVARCHAR(32)  NOT NULL,
    DisplayName NVARCHAR(128) NOT NULL,
    PRIMARY KEY (ListName, EntryValue)
);
GO

INSERT INTO sps.ItemType (ItemKind, ParentKind, TableName, DisplayName, TagFormat) VALUES
    (N'DesignItem',        NULL,          N'DesignItem',        N'Design item',        NULL),
    (N'Vessel',            N'DesignItem', N'Vessel',            N'Vessel',             N'Lead-Number Tail'),
    (N'Instrument',        N'DesignItem', N'Instrument',        N'Instrument',         N'Lead-Number Tail'),
    (N'PipeRun',           N'DesignItem', N'PipeRun',           N'Pipe run',           N'Lead-Number Tail'),
    (N'PipingFitting',     N'DesignItem', N'PipingFitting',     N'Piping fitting',     NULL),
    (N'Nozzle',            N'DesignItem', N'Nozzle',            N'Nozzle',             NULL),
    (N'ProcessConnection', N'DesignItem', N'ProcessConnection', N'Process connection', NULL),
    (N'SheetLink',         N'DesignItem', N'SheetLink',         N'Off-page connector', NULL);

INSERT INTO sps.ItemProperty (ItemKind, PropertyName, DataType, DisplayName, TagPart, SelectList) VALUES
    (N'DesignItem',        N'ItemKind',      N'String',  N'Item kind',         NULL, NULL),
    (N'DesignItem',        N'ItemState',     N'String',  N'Item state',        NULL, N'ItemState'),
    (N'Vessel',            N'ItemTag',       N'String',  N'Tag',               NULL, NULL),
    (N'Vessel',            N'TagLead',       N'String',  N'Tag lead',          1,    NULL),
    (N'Vessel',            N'TagNumber',     N'String',  N'Tag number',        2,    NULL),
    (N'Vessel',            N'TagTail',       N'String',  N'Tag tail',          3,    NULL),
    (N'Vessel',            N'Description',   N'String',  N'Description',       NULL, NULL),
    (N'Instrument',        N'ItemTag',       N'String',  N'Tag',               NULL, NULL),
    (N'Instrument',        N'TagLead',       N'String',  N'Function letters',  1,    NULL),
    (N'Instrument',        N'TagNumber',     N'String',  N'Loop number',       2,    NULL),
    (N'Instrument',        N'TagTail',       N'String',  N'Tag tail',          3,    NULL),
    (N'Instrument',        N'Unit',          N'String',  N'Unit',              NULL, NULL),
    (N'Instrument',        N'Description',   N'String',  N'Description',       NULL, NULL),
    (N'PipeRun',           N'ItemTag',       N'String',  N'Line tag',          NULL, NULL),
    (N'PipeRun',           N'TagLead',       N'String',  N'Line prefix',       1,    NULL),
    (N'PipeRun',           N'TagNumber',     N'String',  N'Line number',       2,    NULL),
    (N'PipeRun',           N'TagTail',       N'String',  N'Line suffix',       3,    NULL),
    (N'PipeRun',           N'NominalSizeMm', N'Integer', N'Nominal size (mm)', NULL, NULL),
    (N'PipeRun',           N'FlowSense',     N'String',  N'Flow sense',        NULL, N'FlowSense'),
    (N'PipingFitting',     N'ItemTag',       N'String',  N'Tag',               NULL, NULL),
    (N'PipingFitting',     N'Description',   N'String',  N'Description',       NULL, NULL),
    (N'Nozzle',            N'ItemTag',       N'String',  N'Tag',               NULL, NULL),
    (N'Nozzle',            N'ParentItem',    N'Guid',    N'Parent vessel',     NULL, NULL),
    (N'ProcessConnection', N'Description',   N'String',  N'Description',       NULL, NULL),
    (N'SheetLink',         N'LinkLabel',     N'String',  N'Connector label',   NULL, NULL),
    (N'SheetLink',         N'LinkSense',     N'String',  N'To or from',        NULL, N'LinkSense'),
    (N'SheetLink',         N'MateItem',      N'Guid',    N'Mate connector',    NULL, NULL),
    (N'SheetLink',         N'MateSheet',     N'Guid',    N'Mate sheet',        NULL, NULL);

INSERT INTO sps.SelectEntry (ListName, EntryValue, DisplayName) VALUES
    (N'ItemState',     N'Active',       N'Active'),
    (N'ItemState',     N'Deleted',      N'Deleted'),
    (N'FlowSense',     N'End1Upstream', N'Flow from end 1 to end 2'),
    (N'FlowSense',     N'End2Upstream', N'Flow from end 2 to end 1'),
    (N'LinkSense',     N'To',           N'To another sheet'),
    (N'LinkSense',     N'From',         N'From another sheet'),
    (N'DepictionKind', N'Mark',         N'Symbol'),
    (N'DepictionKind', N'Line',         N'Line'),
    (N'DepictionKind', N'Label',        N'Label');
GO
