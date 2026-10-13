-- The Plant 3D-style vendor-style backend (DEC-020, DEC-030), schema p3d.
--
-- It follows how AutoCAD Plant 3D and AutoCAD P&ID store a project's saved data
-- (DEC-031), using this project's own names (DEC-033). DEC-040 sets the six borrowed
-- patterns; each is cited below by its register entry in
-- docs/LIONG-REF-001-reference-register.md. DEC-049 records the choices this file
-- makes under the owner's delegation (DEC-048).
--
-- No table has a foreign key (DEC-043): as far as the research shows, the product
-- keeps integrity in the application, and LIONG-006's checks belong to the pipeline.
-- Keys stay the same in every snapshot of a world, and no other backend shares them
-- (DEC-044). Run this file once on an empty database; it creates schema p3d.

CREATE SCHEMA p3d;
GO

-- Pattern 1: one table per class under a shared base table, with one project-wide
-- key and a GUID on every row (REF-TECH-016: PnPBase holds PnPID, PnPClassName,
-- PnPStatus, PnPGuid and PnPTimestamp for every object).
-- Revision and Status are the vendor's own revision and status columns on each row
-- (DEC-037); Status 'Approved' is the source approval (DEC-039).
CREATE TABLE p3d.PlantObject (
    ObjectId    INT              NOT NULL PRIMARY KEY,
    ObjectGuid  UNIQUEIDENTIFIER NOT NULL UNIQUE,
    ClassName   NVARCHAR(64)     NOT NULL,
    Revision    NVARCHAR(16)     NOT NULL,
    Status      NVARCHAR(32)     NOT NULL,
    RowStamp    BIGINT           NOT NULL
);

-- The class tables. Each row shares its ObjectId with one PlantObject row.
-- Pattern 5: a tag is stored as its format's subparts next to the composed tag, and
-- the composed tag is unique in its class (REF-TECH-017: "Equipment Tag
-- [Type-Number]"; REF-TECH-016: Equipment rows carry Tag, Type and Number).
CREATE TABLE p3d.Equipment (
    ObjectId    INT           NOT NULL PRIMARY KEY,
    Tag         NVARCHAR(64)  NULL,
    TagType     NVARCHAR(16)  NULL,
    TagNumber   NVARCHAR(16)  NULL,
    Description NVARCHAR(128) NULL
);
CREATE UNIQUE INDEX UX_Equipment_Tag ON p3d.Equipment (Tag) WHERE Tag IS NOT NULL;

CREATE TABLE p3d.Valve (
    ObjectId    INT           NOT NULL PRIMARY KEY,
    Tag         NVARCHAR(64)  NULL,
    TagType     NVARCHAR(16)  NULL,
    TagNumber   NVARCHAR(16)  NULL,
    Description NVARCHAR(128) NULL
);
CREATE UNIQUE INDEX UX_Valve_Tag ON p3d.Valve (Tag) WHERE Tag IS NOT NULL;

-- An instrument tag is its function letters and loop number, as in "PI-102".
CREATE TABLE p3d.Instrument (
    ObjectId    INT           NOT NULL PRIMARY KEY,
    Tag         NVARCHAR(64)  NULL,
    TagType     NVARCHAR(16)  NULL,
    LoopNumber  NVARCHAR(16)  NULL,
    Unit        NVARCHAR(16)  NULL,
    Description NVARCHAR(128) NULL
);
CREATE UNIQUE INDEX UX_Instrument_Tag ON p3d.Instrument (Tag) WHERE Tag IS NOT NULL;

-- A line segment tag is a prefix, a line number and a segment suffix, as in "L-101-1".
-- NominalSizeMm is the only engineering attribute R0 gives a segment.
CREATE TABLE p3d.LineSegment (
    ObjectId      INT          NOT NULL PRIMARY KEY,
    Tag           NVARCHAR(64) NULL,
    LinePrefix    NVARCHAR(8)  NULL,
    LineNumber    NVARCHAR(16) NULL,
    SegmentSuffix NVARCHAR(8)  NULL,
    NominalSizeMm INT          NULL
);
CREATE UNIQUE INDEX UX_LineSegment_Tag ON p3d.LineSegment (Tag) WHERE Tag IS NOT NULL;

-- A junction where lines meet. It has no tag.
CREATE TABLE p3d.Junction (
    ObjectId    INT           NOT NULL PRIMARY KEY,
    Description NVARCHAR(128) NULL
);

-- An off-page connector. Its label, such as "TO-S2/A", is a drawing label, not a tag.
CREATE TABLE p3d.SheetConnector (
    ObjectId  INT          NOT NULL PRIMARY KEY,
    Label     NVARCHAR(64) NOT NULL,
    Direction NVARCHAR(8)  NOT NULL  -- 'Out' or 'In'
);

-- Pattern 2: connections are rows of their own (REF-TECH-016: LineStartAsset and
-- LineEndAsset, each a Line and an Asset; ConnectorsRelationship, a Connector1 and a
-- Connector2). Flow runs from a segment's start object into the segment and out to
-- its end object.
CREATE TABLE p3d.SegmentStart (
    RowId     INT              NOT NULL PRIMARY KEY,
    RowGuid   UNIQUEIDENTIFIER NOT NULL UNIQUE,
    SegmentId INT              NOT NULL,
    ObjectId  INT              NOT NULL
);

CREATE TABLE p3d.SegmentEnd (
    RowId     INT              NOT NULL PRIMARY KEY,
    RowGuid   UNIQUEIDENTIFIER NOT NULL UNIQUE,
    SegmentId INT              NOT NULL,
    ObjectId  INT              NOT NULL
);

CREATE TABLE p3d.ConnectorPair (
    RowId      INT              NOT NULL PRIMARY KEY,
    RowGuid    UNIQUEIDENTIFIER NOT NULL UNIQUE,
    Connector1 INT              NOT NULL,
    Connector2 INT              NOT NULL
);

-- An instrument's parent equipment, as its own relationship row (REF-TECH-016 lists
-- an AssetOwnership table among the relationship tables).
CREATE TABLE p3d.Ownership (
    RowId   INT              NOT NULL PRIMARY KEY,
    RowGuid UNIQUEIDENTIFIER NOT NULL UNIQUE,
    OwnerId INT              NOT NULL,
    OwnedId INT              NOT NULL
);

-- Pattern 4: off-page connector links (REF-TECH-016: LineOffPageConnector, and the
-- relationship "between two Off-Page connectors"). R0's cross-sheet pair X1 and X2
-- is one row: flow leaves through OutConnector and enters through InConnector.
CREATE TABLE p3d.SheetConnectorLink (
    RowId        INT              NOT NULL PRIMARY KEY,
    RowGuid      UNIQUEIDENTIFIER NOT NULL UNIQUE,
    OutConnector INT              NOT NULL,
    InConnector  INT              NOT NULL
);

-- Drawings. A drawing is not a plant object; its revision and status are the
-- vendor's drawing fields (DEC-037), and Status 'Approved' is the source approval
-- (DEC-039).
CREATE TABLE p3d.Drawing (
    DrawingId INT          NOT NULL PRIMARY KEY,
    FileName  NVARCHAR(64) NOT NULL UNIQUE,
    Revision  NVARCHAR(16) NOT NULL,
    Status    NVARCHAR(32) NOT NULL
);

-- Pattern 3: a table links each object to the drawings it appears on, with the
-- drawing handle of its symbol. Objects carry no drawing ID (REF-TECH-016:
-- PnPDataLinks, the system table that links database rows to drawing objects).
CREATE TABLE p3d.DrawingAppearance (
    RowId         INT          NOT NULL PRIMARY KEY,
    ObjectId      INT          NOT NULL,
    DrawingId     INT          NOT NULL,
    DrawingHandle NVARCHAR(16) NOT NULL
);

-- The work history: one row for each change a revision makes (DEC-037). The time
-- is when the source recorded the change (DEC-045).
CREATE TABLE p3d.WorkHistory (
    HistoryId  INT           NOT NULL PRIMARY KEY,
    ObjectId   INT           NULL,
    DrawingId  INT           NULL,
    Revision   NVARCHAR(16)  NOT NULL,
    ChangeKind NVARCHAR(16)  NOT NULL,  -- 'Created', 'Modified' or 'Deleted'
    Detail     NVARCHAR(256) NULL,
    RecordedAt DATETIME2(0)  NOT NULL
);

-- Pattern 6: class-definition metadata, for R0's classes only (DEC-032; REF-TECH-016:
-- PnPColumnAttributes describes each class's columns).
CREATE TABLE p3d.ClassDefinition (
    ClassName   NVARCHAR(64)  NOT NULL PRIMARY KEY,
    ParentClass NVARCHAR(64)  NULL,
    TableName   NVARCHAR(64)  NOT NULL,
    DisplayName NVARCHAR(128) NOT NULL,
    TagFormat   NVARCHAR(64)  NULL
);

CREATE TABLE p3d.PropertyDefinition (
    ClassName    NVARCHAR(64)  NOT NULL,
    PropertyName NVARCHAR(64)  NOT NULL,
    DataType     NVARCHAR(32)  NOT NULL,
    DisplayName  NVARCHAR(128) NOT NULL,
    TagSubpart   INT           NULL,  -- position in the tag format, or NULL
    PRIMARY KEY (ClassName, PropertyName)
);
GO

INSERT INTO p3d.ClassDefinition (ClassName, ParentClass, TableName, DisplayName, TagFormat) VALUES
    (N'PlantObject',    NULL,           N'PlantObject',    N'Plant object',         NULL),
    (N'Equipment',      N'PlantObject', N'Equipment',      N'Equipment',            N'Type-Number'),
    (N'Valve',          N'PlantObject', N'Valve',          N'Valve',                N'Type-Number'),
    (N'Instrument',     N'PlantObject', N'Instrument',     N'Instrument',           N'Type-Loop'),
    (N'LineSegment',    N'PlantObject', N'LineSegment',    N'Line segment',         N'Prefix-Line-Suffix'),
    (N'Junction',       N'PlantObject', N'Junction',       N'Junction',             NULL),
    (N'SheetConnector', N'PlantObject', N'SheetConnector', N'Off-page connector',   NULL);

INSERT INTO p3d.PropertyDefinition (ClassName, PropertyName, DataType, DisplayName, TagSubpart) VALUES
    (N'PlantObject',    N'Revision',      N'String',  N'Revision',            NULL),
    (N'PlantObject',    N'Status',        N'String',  N'Status',              NULL),
    (N'Equipment',      N'Tag',           N'String',  N'Tag',                 NULL),
    (N'Equipment',      N'TagType',       N'String',  N'Type',                1),
    (N'Equipment',      N'TagNumber',     N'String',  N'Number',              2),
    (N'Equipment',      N'Description',   N'String',  N'Description',         NULL),
    (N'Valve',          N'Tag',           N'String',  N'Tag',                 NULL),
    (N'Valve',          N'TagType',       N'String',  N'Type',                1),
    (N'Valve',          N'TagNumber',     N'String',  N'Number',              2),
    (N'Valve',          N'Description',   N'String',  N'Description',         NULL),
    (N'Instrument',     N'Tag',           N'String',  N'Tag',                 NULL),
    (N'Instrument',     N'TagType',       N'String',  N'Function',            1),
    (N'Instrument',     N'LoopNumber',    N'String',  N'Loop',                2),
    (N'Instrument',     N'Unit',          N'String',  N'Unit',                NULL),
    (N'Instrument',     N'Description',   N'String',  N'Description',         NULL),
    (N'LineSegment',    N'Tag',           N'String',  N'Tag',                 NULL),
    (N'LineSegment',    N'LinePrefix',    N'String',  N'Prefix',              1),
    (N'LineSegment',    N'LineNumber',    N'String',  N'Line number',         2),
    (N'LineSegment',    N'SegmentSuffix', N'String',  N'Segment',             3),
    (N'LineSegment',    N'NominalSizeMm', N'Integer', N'Nominal size (mm)',   NULL),
    (N'Junction',       N'Description',   N'String',  N'Description',         NULL),
    (N'SheetConnector', N'Label',         N'String',  N'Connector label',     NULL),
    (N'SheetConnector', N'Direction',     N'String',  N'Direction',           NULL);
GO
