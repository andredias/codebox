from httpx import AsyncClient
from pydantic import parse_obj_as
from pytest import fixture

from app.models import Command, ProjectCore, Response


@fixture
def run_rust(client: AsyncClient):
    async def _run_rust(code: str) -> list[Response]:
        sources = {'test.rs': code}
        commands = [
            Command(command='/venv/rust/bin/rustc test.rs', timeout=1, cgroups_enabled=False),
            Command(command='./test', timeout=0.1, mem_max=350_000_000),
        ]
        resp = await client.post(
            '/execute', json=ProjectCore(sources=sources, commands=commands).dict()
        )
        return parse_obj_as(list[Response], resp.json())

    return _run_rust


async def test_get_version(client: AsyncClient):
    command = Command(command='/venv/rust/bin/rustc --version', timeout=1, mem_max=512_000_000)
    resp = await client.post('/execute', json=ProjectCore(sources={}, commands=[command]).dict())
    response = Response(**(resp.json()[0]))
    assert response.exit_code == 0
    assert len(response.stdout)


async def test_hello_world(run_rust):
    code = '''
fn main() {
    println!("Hello World!");
}
'''
    assert (await run_rust(code))[1] == Response(stdout='Hello World!\n', stderr='', exit_code=0)


async def test_fizz_buzz(run_rust):
    code = '''// ref: https://doc.rust-lang.org/rust-by-example/fn.html?highlight=fizz#functions

fn main() {
    // We can use this function here, and define it somewhere later
    fizzbuzz_to(100);
}

// Function that returns a boolean value
fn is_divisible_by(lhs: u32, rhs: u32) -> bool {
    // Corner case, early return
    if rhs == 0 {
        return false;
    }

    // This is an expression, the `return` keyword is not necessary here
    lhs % rhs == 0
}

// Functions that "don't" return a value, actually return the unit type `()`
fn fizzbuzz(n: u32) -> () {
    if is_divisible_by(n, 15) {
        println!("fizzbuzz");
    } else if is_divisible_by(n, 3) {
        println!("fizz");
    } else if is_divisible_by(n, 5) {
        println!("buzz");
    } else {
        println!("{}", n);
    }
}

// When a function returns `()`, the return type can be omitted from the
// signature
fn fizzbuzz_to(n: u32) {
    for n in 1..n + 1 {
        fizzbuzz(n);
    }
}'''
    responses = await run_rust(code)
    assert responses[0].exit_code == responses[1].exit_code == 0
    assert responses[0].stderr == responses[1].stderr == ''
    assert len(responses[1].stdout.splitlines()) == 100
