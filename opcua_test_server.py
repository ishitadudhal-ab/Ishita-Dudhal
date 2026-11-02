"""Small local OPC UA server for testing the WMS machine interface."""

import argparse
import asyncio
import os

from asyncua import Server

from app.logic.machine_interface import NAMESPACE_URI


DEFAULT_ENDPOINT = "opc.tcp://127.0.0.1:4840/wms-test/server/"


async def create_server(endpoint_url):
    """Create the WMS test address space and return the configured server."""
    server = Server()
    await server.init()
    server.set_endpoint(endpoint_url)
    namespace_index = await server.register_namespace(NAMESPACE_URI)

    lager = await server.nodes.objects.add_object(namespace_index, "Lager")
    functions = await lager.add_object(namespace_index, "Funktionen")
    controls = await lager.add_object(namespace_index, "Steuerung allgemein")
    safety = await lager.add_object(namespace_index, "Sicherheitsfunktionen")

    variables = {
        "Einlagern": (functions, False),
        "Auslagern": (functions, False),
        "Umlagern": (functions, False),
        "Referenzieren": (functions, False),
        "Steuerung Ein": (controls, True),
        "Hand Automatik": (controls, True),
        "Not Aus": (safety, False),
        "Kollisionen": (safety, False),
    }
    for name, (parent, initial_value) in variables.items():
        variable = await parent.add_variable(namespace_index, name, initial_value)
        await variable.set_writable()

    return server


async def run_server(endpoint_url):
    server = await create_server(endpoint_url)
    await server.start()
    print(f"OPC UA test server listening at {endpoint_url}")
    print("Control enabled; emergency stop and collision are clear.")
    try:
        await asyncio.Event().wait()
    finally:
        await server.stop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("OPCUA_TEST_ENDPOINT", DEFAULT_ENDPOINT),
        help=f"OPC UA endpoint (default: {DEFAULT_ENDPOINT})",
    )
    args = parser.parse_args()
    try:
        asyncio.run(run_server(args.endpoint))
    except KeyboardInterrupt:
        print("OPC UA test server stopped.")


if __name__ == "__main__":
    main()