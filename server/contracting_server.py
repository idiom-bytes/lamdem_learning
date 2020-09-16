# server / contracting_server.py
# Run server from the command line @ /learning/
# python3 server/contracting_server.py

from sanic import Sanic, response
from sanic_cors import CORS

import ast
import json

from contracting.db.encoder import encode

from contracting.client import ContractingClient
client = ContractingClient()

from exercises.lamdem_blog_sample import my_token
client.submit(my_token)

app = Sanic("contracting server")
CORS(app)

@app.route("ping")
async def ping(request):
    return response.json(
        {'status': 'online'}
    )

@app.route("contracts")
async def contracts(request):
    return response.json(
        {'contracts': client.get_contracts()}
    )

@app.route("/contracts/<contract>")
# Get the source code of a specific contract
async def get_contract(request, contract):
    # Use the client raw_driver to get the contract code from the db
    contract_code = client.raw_driver.get_contract(contract)

    funcs = []
    variables = []
    hashes = []

    # Parse the code into a walkable tree
    tree = ast.parse(contract_code)

    # Parse out all functions
    function_defs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    for definition in function_defs:
        func_name = definition.name
        kwargs = [arg.arg for arg in definition.args.args]

        funcs.append({'name': func_name, 'arguments': kwargs})

    # Parse out all defined state Variables and Hashes
    assigns = [n for n in ast.walk(tree) if isinstance(n, ast.Assign)]
    for assign in assigns:
        if type(assign.value) == ast.Call:
            if assign.value.func.id == 'Variable':
                variables.append(assign.targets[0].id.lstrip('__'))
            elif assign.value.func.id == 'Hash':
                hashes.append(assign.targets[0].id.lstrip('__'))

    #Return all Information
    return response.json({
        'name': contract,
        'code': contract_code,
        'methods': funcs,
        'variables': variables,
        'hashes': hashes
    }, status=200)

# Return the current state of a variable
@app.route("/contracts/<contract>/<variable>")
async def get_variable(request, contract, variable):
    # Check if contract exists. If not, return error
    contract_code = client.raw_driver.get_contract(contract)
    if contract_code is None:
        return response.json({'error': '{} does not exist'.format(contract)}, status=404)

    # Parse key from request object
    key = request.args.get('key')
    if key is not None:
        key = key.split(',')

    # Create the key contracting will use to get the value
    k = client.raw_driver.make_key(contract=contract, variable=variable, args=key)

    # Get value
    value = client.raw_driver.get(k)

    # If the variable or the value didn't exists return None
    if value is None:
        return response.json({'value': None}, status=404)

    # If there was a value, return it formatted
    return response.json({'value': value}, status=200, dumps=encode)

@app.route("/", methods=["POST",])
async def submit_transaction(request):
    # Get transaction details
    contract_name = request.json.get('contract')
    method_name = request.json.get('method')

    # I believe kwargs have to be transformed into a dict.
    # So we must import json, and call loads(string).
    kwargs = request.json.get('args')
    sender = request.json.get('sender')

    # Set the sender
    client.signer = sender

    # Get reference to contract
    contract = client.get_contract(contract_name)

    # Return error of contract does not exist
    if contract_name is None:
        return response.json({'error': '{} does not exist'.format(contract)}, status=404)

    # Get reference to the contract method to be called
    method = getattr(contract, method_name)

    # Call method with supplied arguments and return status
    try:
        method(**kwargs)
        return response.json({'status': 0})
    except Exception as err:
        # ONBOARDING FIX: Return response should dereference err.args[0]
        return response.json({'status': 1, 'error': err.args[0]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3737)