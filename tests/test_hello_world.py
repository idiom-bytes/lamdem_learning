import unittest

from contracting.client import ContractingClient
from exercises.hello_world import hello_world
client = ContractingClient()

# SC's get added to DB with each call
# You should either verify before submitting, or wrapping in a try/catch block
running_contracts = client.get_contracts()
if 'hello_world' not in running_contracts :
    client.submit(hello_world)

class MyTestCase(unittest.TestCase):

    def test_hello_world(self):
        hw_contract = client.get_contract('hello_world')
        self.assertEqual(hw_contract.hello(), 'World!')

        # You must specify the parameters being passed in
        self.assertEqual(hw_contract.add(a=2, b=3), 5)

if __name__ == '__main__':
    unittest.main()