from contracting.client import ContractingClient
client = ContractingClient()

# Make sure mongdob is running
# docker run -d -p 27017–27019:27017–27019 — name mongodb mongo:4.2

def my_token() :

    # SC State
    S = Hash(default_value=0)

    # Initialize SC
    @construct
    def seed():
        # Award 50 tokens to self
        S['me'] = 50

    # Exported methods can be executed by users
    # Exported methods must be typesafe
    @export
    def transfer(amount: int, receiver: str):
        # Contracting ctx.caller ~= Solidity msg.sender
        sender = ctx.caller

        # Get the sender's balance from State
        balance = S[sender]

        # Assert the sender has the appropriate balance to send
        # If this assert fails, the method will fail here
        # Everything reverts, no more code is executed
        assert balance >= amount, "Transfer amount exceeds available token balance"

        # subtract the tokens from the sender's balance
        S[sender] -= amount

        # add tokens to the receiver's balance
        S[receiver] += amount
