from typing import Annotated

import dagger
from dagger import DefaultPath, Ignore, check, dag, function, object_type

# Allow project inputs, not the host checkout's Git history or local agent state.
# Everything else is small (about 4 MB tracked), so this list only drops what the
# checks do not read and what must never leave the laptop.
# Allow project inputs, not the host checkout's Git history or local agent state.
# Everything tracked is small (about 4 MB), so plain exclude patterns are enough.
SOURCE_FILTER = [
    "**/.git",
    "**/.git/**",
    "**/.entire",
    "**/.entire/**",
    "**/.venv",
    "**/__pycache__",
    "**/.pytest_cache",
    "**/.ruff_cache",
    "**/.mypy_cache",
    "**/node_modules",
    "**/.DS_Store",
    "out",
    "out/**",
]

# The vendor-style backend tests (DEC-027, DEC-056) run against throwaway service
# containers, exactly as .github/workflows/check.yml configures them. Passwords are
# throwaways for this run, not secrets.
SQLSERVER = "mcr.microsoft.com/mssql/server:2022-latest"
NEO4J = "neo4j@sha256:6f3f17e72d69bb6f26b03f6186f5afb15a201f8b460bb69b0cd8030717f9f01a"
UV = "ghcr.io/astral-sh/uv:0.12.3"


@object_type
class LiongCi:
    @function
    @check
    async def project(
        self,
        source: Annotated[dagger.Directory, DefaultPath("/"), Ignore(SOURCE_FILTER)],
    ) -> None:
        """Run scripts/check.sh with locked dependencies, an isolated Git index, and
        the SQL Server and Neo4j services the server tests expect."""
        sqlserver = (
            dag.container()
            .from_(SQLSERVER)
            .with_env_variable("ACCEPT_EULA", "Y")
            .with_env_variable("MSSQL_SA_PASSWORD", "Liong-CI-2026!")
            .with_exposed_port(1433)
            .as_service()
        )
        neo4j = (
            dag.container()
            .from_(NEO4J)
            .with_env_variable("NEO4J_AUTH", "neo4j/liong-ci-2026")
            .with_exposed_port(7687)
            .as_service()
        )
        uv = dag.container().from_(UV)
        dependencies = (
            dag.container()
            .from_("python:3.12-slim-bookworm")
            .with_exec(
                ["sh", "-c", "apt-get update && apt-get install -y --no-install-recommends git"]
            )
            .with_file("/usr/local/bin/uv", uv.file("/uv"))
            .with_workdir("/work")
            .with_file("pyproject.toml", source.file("pyproject.toml"))
            .with_file("uv.lock", source.file("uv.lock"))
            .with_exec(["uv", "sync", "--frozen", "--no-install-project"])
        )
        await (
            dependencies.with_directory("/work", source)
            .with_exec(["uv", "sync", "--frozen", "--no-install-project"])
            .with_exec(["git", "init", "--initial-branch=main"])
            .with_exec(["git", "add", "--all"])
            .with_env_variable("CI", "1")
            .with_env_variable("LIONG_SQLSERVER", "sqlserver,1433,sa,Liong-CI-2026!")
            .with_env_variable("LIONG_NEO4J", "bolt://neo4j:7687,neo4j,liong-ci-2026")
            .with_service_binding("sqlserver", sqlserver)
            .with_service_binding("neo4j", neo4j)
            .with_exec(["bash", "scripts/check.sh"])
            .sync()
        )
