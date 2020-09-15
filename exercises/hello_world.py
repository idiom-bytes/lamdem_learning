from contracting.client import ContractingClient
client = ContractingClient()

# Make sure mongdob is running
# docker run -d -p 27017–27019:27017–27019 — name mongodb mongo:4.2

def hello_world():

    @export
    def hello():
        return 'World!'

    # @export must be typesafe
    @export
    def add(a: int, b: int):
        return private_add(a, b)

    # @private functions do not require to be typesafe
    def private_add(a, b):
        return a + b