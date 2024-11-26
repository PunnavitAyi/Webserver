from flask import Flask, request
from markupsafe import escape
from flask import render_template
from elasticsearch import Elasticsearch
import math


# Change pasword
ELASTIC_PASSWORD = "9HMU4fD9jc33EvBd51z0"

es = Elasticsearch("https://localhost:9200", http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


# # Check index name before perform "flask run"
# @app.route('/search')
# def search():
#     page_size = 10
#     keyword = request.args.get('keyword')
#     if request.args.get('page'):
#         page_no = int(request.args.get('page'))
#     else:
#         page_no = 1

#     # modify body 

#     body = {
#     'size': page_size,
#     'from': page_size * (page_no - 1),
#     'query': {
#         'bool': {
#             'should': [
#                 {
#                     'multi_match': {
#                         'query': keyword,
#                         'fields': ["Author^3", "Title^2", "Genre", "Publication Year"],
#                         'fuzzy_transpositions': True,
#                         'fuzziness': 'AUTO'
#                     }
#                 },
#                 {
#                     'wildcard': {
#                         'Author.keyword': f"*{keyword.lower()}*"
#                     }
#                 },
#                 {
#                     'match_phrase': {
#                         'Author': keyword
#                     }
#                 }
#             ]
#             # ,
#             # 'minimum_should_match': 1
#         }
#     }
# }


#     res = es.search(index='book_illust', body=body)
#     hits = [{'name': doc['_source']['Title'], 'description': doc['_source']['Description'], 'author': doc['_source']['Author'], 'year': doc['_source']['Publication Year'],'picture': doc['_source']['Picture'], 'created': doc['_source']['Genre']} for doc in res['hits']['hits']]
#     page_total = math.ceil(res['hits']['total']['value']/page_size)
#     return render_template('search.html',keyword=keyword, hits=hits, page_no=page_no, page_total=page_total)

@app.route('/search')
def search():
    page_size = 10
    keyword = request.args.get('keyword', '').strip()
    page_no = int(request.args.get('page', 1))

    # Modify the body for more accurate search results
    body = {
        'size': page_size,
        'from': page_size * (page_no - 1),
        'query': {
            'bool': {
                'should': [
                    {
                        'multi_match': {
                            'query': keyword,
                            'fields': [
                                "Title^4",         # Boost Title field importance
                                "Author^3",        # Boost Author field importance
                                "Genre^2",         # Genre gets moderate importance
                                "Publication Year" # Publication year is also searched
                            ],
                            'fuzziness': 'AUTO',     # Enable fuzziness for typos
                            'fuzzy_transpositions': True,  # Allow fuzzy transpositions
                            'type': 'best_fields'
                        }
                    },
                    {
                        'wildcard': {
                            'Title': f"*{keyword.lower()}*"
                        }
                    },
                    {
                        'wildcard': {
                            'Author': f"*{keyword.lower()}*"
                        }
                    },
                    {
                        'match_phrase': {
                            'Title': keyword
                        }
                    },
                    {
                        'match_phrase': {
                            'Author': keyword
                        }
                    }
                ],
                'minimum_should_match': 1  # At least one should match
            }
        }
    }

    # Execute search query
    try:
        res = es.search(index='book_illust', body=body)
        hits = [
            {
                'name': doc['_source'].get('Title', 'N/A'),
                'description': doc['_source'].get('Description', 'No description available'),
                'author': doc['_source'].get('Author', 'Unknown'),
                'picture': doc['_source'].get('Picture', ''),
                'genre': doc['_source'].get('Genre', 'N/A'),
                'year': doc['_source'].get('Publication Year', 'N/A')
            }
            for doc in res['hits']['hits']
        ]
        page_total = math.ceil(res['hits']['total']['value'] / page_size)
    except Exception as e:
        hits = []
        page_total = 0
        print(f"Error occurred: {e}")

    # Render the search results
    return render_template(
        'search.html',
        keyword=keyword,
        hits=hits,
        page_no=page_no,
        page_total=page_total
    )
