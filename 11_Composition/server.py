from fastmcp import FastMCP

add_server = FastMCP(name="AddServer")


@add_server.tool(description="Add two integers")
def add(a: int, b: int) -> int:
    print(f"Executing add tool with a={a}, b={b}")
    return a + b


subtract_server = FastMCP(name="SubtractServer")


@subtract_server.tool(description="Subtract two integers")
def subtract(a: int, b: int) -> int:
    print(f"Executing subtract tool with a={a}, b={b}")
    return a - b


main_app = FastMCP(name="MainApp")

main_app.mount("add", add_server)
main_app.mount("subtract", subtract_server)

if __name__ == "__main__":
    main_app.run(transport="streamable-http")
