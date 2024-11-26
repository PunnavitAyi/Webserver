from elasticsearch import Elasticsearch, helper
import ndjson
import argparse
import uuid

es = Elasticsearch("http://localhost:9200", basic_auth=("elastic","9HMU4fD9jc33EvBd51z0"), verify_certs=False)

parser = argparse.ArgumentParser()
parser.add_argument('--file')
parser.add_argument('--index')

args = parser.parse_args()

index = args.index
file = args.file

with open(file) as json_file:
    json_docs = ndjson.load(json_file)

def bulk_json_data(json_list, _index):
    for doc in json_list:

        if '{"index"' not in doc:
            yield{
                "_index": _index,
                "_id": uuid.uuid4(),
                "_source": doc
            }

try:
    # make the bulk call, and get a response
    response = helpers.bulk(es, bulk_json_data(json_docs, index))
    print ("\nRESPONSE:", response)
except Exception as e:
    print("\nERROR:", e)
