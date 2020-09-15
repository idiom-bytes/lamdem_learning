import unittest

from contracting.client import ContractingClient
from exercises.lamdem_blog_sample import my_token
client = ContractingClient()

# SC's get added to DB with each call
# You should either verify before submitting, or wrapping in a try/catch block
running_contracts = client.get_contracts()
if 'my_token' not in running_contracts :
    client.submit(my_token)

# Running into errors when loading it like this.
# I think it might be because of extra headers, and imports
# with open('../exercises/lamdem_blog_sample.py') as f:
#     code = f.read()
#     client.submit(code, name='my_token')

class MyTestCase(unittest.TestCase):

    def test_supply(self):
        my_token = client.get_contract('my_token')
        self.assertEqual(my_token.quick_read('S', 'me'), 50)

    def test_transfer(self):
        # set transaction sender
        client.signer = 'me'

        # get contract reference
        my_token = client.get_contract('my_token')

        # call transfer method
        # remember to properly define the parameters
        my_token.transfer(
            amount=10,
            receiver='you'
        )

        # Assert token balances for 'me'
        self.assertEqual(my_token.quick_read('S', 'me'), 40)
        # Assert token balances for 'you'
        self.assertEqual(my_token.quick_read('S', 'you'), 10)

    def test_transfer_neg_insufficient_funds(self):
        # set transaction sender
        client.signer = 'you'

        # get contract reference
        my_token = client.get_contract('my_token')

        # get balances
        me_balance_before = my_token.quick_read('S', 'me')
        you_balance_before = my_token.quick_read('S', 'you')

        # Set transfer amount to X + 1
        transfer_amount = you_balance_before + 1

        # Test that the transfer method rases an Assertion
        self.assertRaises(
            AssertionError,
            lambda: my_token.transfer(
                amount=transfer_amount,
                receiver='me'
            )
        )

        # Assert token balance for 'me' has not changed
        self.assertEqual(my_token.quick_read('S', 'me'), me_balance_before)
        # Assert token balance for 'you' has not changed
        self.assertEqual(my_token.quick_read('S', 'you'), you_balance_before)

if __name__ == '__main__':
    unittest.main()
