-- The outbox: a third, non-vendor schema in the backend database (DEC-047).
--
-- The loader that applies a backend snapshot writes the snapshot's rows and one
-- PendingEvent row in a single transaction, so a committed revision always has its
-- event and an uncommitted one has none (LIONG-006 "Recovery fixtures"). The vendor
-- schemas hold only what each application saves (DEC-031). A delivery worker reads
-- pending events; its attempts and outcomes belong to the pipeline's own records.

CREATE SCHEMA outbox;
GO

CREATE TABLE outbox.PendingEvent (
    EventId       UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    LoadSequence  BIGINT           NOT NULL IDENTITY(1, 1) UNIQUE,  -- the order revisions were loaded
    Backend       NVARCHAR(16)     NOT NULL,  -- the vendor schema, such as 'p3d'
    World         NVARCHAR(16)     NOT NULL,
    Revision      NVARCHAR(16)     NOT NULL,
    PayloadSha256 CHAR(64)         NOT NULL,  -- digest of the snapshot's files
    RecordedAt    DATETIME2(0)     NOT NULL,  -- when the source recorded the revision
    CommittedAt   DATETIME2(3)     NOT NULL DEFAULT SYSUTCDATETIME(),
    Status        NVARCHAR(16)     NOT NULL DEFAULT N'Pending',
    -- One event per source revision: reloading a revision cannot raise a second event.
    CONSTRAINT UQ_PendingEvent_Revision UNIQUE (Backend, World, Revision)
);
GO
