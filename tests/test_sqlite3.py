from httpx import AsyncClient
from pytest import fixture

from app.models import Command, ProjectCore, Response


@fixture
def run_sqlite3(client: AsyncClient):
    async def _run_sqlite3(sql: str) -> Response:
        filename = 'database.sql'
        sources = {filename: sql}
        commands = [
            Command(
                command=f'/usr/bin/sqlite3 temp.db -bail -init {filename} ".exit"', timeout=0.1
            ),
        ]
        resp = await client.post(
            '/execute', json=ProjectCore(sources=sources, commands=commands).model_dump()
        )
        return Response(**(resp.json()[0]))

    return _run_sqlite3


async def test_sqlite3(run_sqlite3):
    sql = """
-- tabelas

create table building (
    id smallint not null,
    name       varchar(30) not null,

    primary key (id)
);

create index idx_building_1 on building(name);

-- Dados

insert into building values (1, 'Hilton');
insert into building values (2, 'Plazza');

-- Consults

-- a) Get all buildings

select * from building;
"""
    resp = await run_sqlite3(sql)
    assert resp.exit_code == 0
    assert 'Hilton' in resp.stdout
    assert len(resp.stdout.splitlines()) == 2
