import os
import json
import argparse
from pprint import pprint
from rag import RAG

def retrieval(query):
    print("\nRetrieving...")

    # Initialize the RAG object
    rag = RAG()

    # Read profiles from data.json
    with open('data.json', 'r') as f:
        db = json.load(f)

    # Retrieve the IDs of people
    retrieved = rag.retrieve(query)
    
    found = []
    for result in retrieved["results"]:
        #TODO: Query from the actual database using the IDs
        found.append(db[int(result["id"])-1])

    print("\nResults:")
    pprint(found)

def db_sync():
    print("\nUpserting...")

    # Initialize the RAG object
    rag = RAG()

    # Read profiles from data.json
    with open('data.json', 'r') as f:
        profiles = json.load(f)

    # Upsert the profiles to Pinecone
    rag.upsert(profiles)

if __name__ == "__main__":
    os.environ['GRPC_VERBOSITY'] = 'ERROR'

    parser = argparse.ArgumentParser(description='This is argparse example python program.')
    parser.add_argument('--sync', action='store_true', help='Please enter a flag for database synchronization.')

    # 3. parse arguments
    args = parser.parse_args()

    if args.sync is True:
        db_sync()
    else:
        while(True):
            query = input("\nPlease input a query to retrieve (or type 'exit' to quit): ")
    
            if query.lower() == 'exit':
                print("\nExiting the program.")
                break

            retrieval(query)