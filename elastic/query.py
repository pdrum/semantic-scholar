from pprint import pprint

from elasticsearch import Elasticsearch


def _get_should_clause(title_query=None, title_weight=1,
                       abstract_query=None, abstract_weight=1,
                       year_query=None, year_weight=None):
    result = []
    if title_query:
        result.append({
            "match": {
                "title": {
                    "query": title_query,
                    "boost": title_weight,
                }
            }
        })
    if abstract_query:
        result.append({
            "match": {
                "abstract": {
                    "query": abstract_query,
                    "boost": abstract_weight,
                }
            }
        })
    if year_query is not None:
        result.append({
            "range": {
                "date": {
                    "gte": year_query,
                    "boost": year_weight
                }
            }
        })
    if not result:
        return [{'match_all': {}}]
    return result


def search(title_query=None, title_weight=1,
           abstract_query=None, abstract_weight=1,
           year_query=None, year_weight=None):
    es = Elasticsearch()
    return es.search(index='paper_index', doc_type='paper', body={
        "query": {
            "bool": {
                "should": _get_should_clause(
                    title_query=title_query, title_weight=title_weight,
                    abstract_query=abstract_query, abstract_weight=abstract_weight,
                    year_query=year_query, year_weight=year_weight
                )
            }
        }
    })['hits']


if __name__ == '__main__':
    res = search(
        title_query='The Comparison Geometry of Ricci Curvature',
        year_query=2000,
        year_weight=20000
    )
    pprint(res)
