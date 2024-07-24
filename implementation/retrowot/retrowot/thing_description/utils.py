import re
from copy import deepcopy
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel
from rdflib.query import Result


def camel_case(string: str) -> str:
    """
    Converts a string to camel case.

    Args:
        string (str): The input string to be converted.

    Returns:
        str: The converted string in camel case.

    Example:
        >>> camel_case("hello world")
        'helloWorld'
    """
    string_parts: List[str] = string.split(" ")

    return string_parts[0].lower() + "".join(
        [part.capitalize() for part in string_parts[1:]]
    )


def update_parameters(parameters: Dict[str, str], new_parameters: Dict[str, str]):
    """
    Updates the values of parameters in a dictionary with new values.

    Args:
        parameters (Dict[str, str]): The dictionary containing the parameters to be updated.
        new_parameters (Dict[str, str]): The dictionary containing the new parameter values.

    Returns:
        Dict[str, str]: The updated dictionary of parameters.

    Example:
        >>> parameters = {'param1': 'Hello, {{name}}!', 'param2': 'The answer is {{answer}}.'}
        >>> new_parameters = {'name': 'Alice', 'answer': '42'}
        >>> update_parameters(parameters, new_parameters)
        {'param1': 'Hello, Alice!', 'param2': 'The answer is 42.'}
    """
    for key in parameters.keys():
        if key in new_parameters.keys():
            parameters[key] = re.sub("{{.*}}", new_parameters[key], parameters[key])

    return parameters


def process_parameters(model: BaseModel) -> Dict[str, str]:
    """
    Process the parameters in the given model and return a dictionary of parameter names and values.

    Args:
        model (BaseModel): The model object to process.

    Returns:
        A dictionary containing the parameter names as keys and their values as values.

    Example:
        >>> model = BaseModel()
        >>> model.param1 = "value1"
        >>> model.param2 = "value2"
        >>> process_parameters(model)
        {'param1': 'value1', 'param2': 'value2'}
    """
    parameters = {}
    for key in model.__dict__.keys():
        is_string: bool = isinstance(model.__dict__[key], str)
        if is_string and "{{" in model.__dict__[key]:
            if "{{" in model.__dict__[key]:
                parameters[key] = model.__dict__[key]
    return parameters


def query_result_to_dict(query_result: Result) -> List[Dict[str, Optional[str]]]:
    """
    Converts an RDF query result into a list of dictionaries.

    Args:
        query_result (Result): The RDF query result.

    Returns:
        List[Dict[str, Optional[str]]]: A list of dictionaries representing the query result.
            Each dictionary contains the variable names as keys and their corresponding values as values.
            The values are optional and can be None.

    Example:
        >>> result = query_result_to_dict(query_result)
        >>> print(result)
        [{'var1': 'value1', 'var2': None}, {'var1': 'value2', 'var2': 'value3'}]
    """

    res: List[Dict[str, Optional[str]]] = []
    _result_dict: Dict[str, Optional[str]] = {}

    # print("Query Result Size: ", len(query_result))

    if query_result.vars is None:
        return res

    for row in query_result.vars:
        _result_dict[row.toPython().replace("?", "")] = None

    for row in query_result:
        result_dict = deepcopy(_result_dict)
        for num, key in enumerate(result_dict.keys()):
            if row[num] == None:
                result_dict[key] = None
            else:
                result_dict[key] = row[num].toPython()

        res.append(result_dict)
    return res


class Head(BaseModel):
    vars: List[str]


class Results(BaseModel):
    bindings: List[Dict]


class SparqlQuery(BaseModel):
    head: Head
    results: Results


class SparqlQueryResult(BaseModel):
    results: List[Dict[str, Optional[str]]]


def convert_sparql_query_to_result(query: SparqlQuery) -> SparqlQueryResult:
    """
    Converts a SPARQL query to a SPARQL query result.

    Args:
        query (SparqlQuery): The SPARQL query.

    Returns:
        SparqlQueryResult: The SPARQL query result.

    Example:
        >>> query = SparqlQuery(head=Head(vars=["s", "p", "o"]), results=Results(bindings=[Binding(s=SPO(type="uri", value="http://example.org/s"), p=SPO(type="uri", value="http://example.org/p"), o=SPO(type="uri", value="http://example.org/o"))])
        >>> result = convert_sparql_query_to_result(query)
        >>> print(result)
        SparqlQueryResult(results=[{'s': 'http://example.org/s', 'p': 'http://example.org/p', 'o': 'http://example.org/o'}])
    """
    result_entry = {}
    for binding in query.head.vars:
        result_entry[binding] = None

    result = []
    for binding in query.results.bindings:
        result_dict = deepcopy(result_entry)
        for key, value in binding.items():
            result_dict[key] = value["value"]
        result.append(result_dict)
    return SparqlQueryResult(results=result).results


def select_query(address: str, repository: str, query: str) -> any:
    """
    Sends a SPARQL SELECT query to the GraphDB repository at the given address.

    Args:
        address (str): The address of the GraphDB repository.
        repository (str): The name of the repository.
        query (str): The SPARQL SELECT query.

    Returns:
        any: The result of the query.

    Example:
        >>> select_query("http://localhost:7200", "Test", "SELECT * WHERE {?s ?p ?o} LIMIT 10")
        >>> http://localhost:7200/repositories/Test?query=select%20%2A%20where%20%7B%3Fs%20%3Fp%20%3Fo%7D%20limit%2010
        [{'s': 'http://example.org/s', 'p': 'http://example.org/p', 'o': 'http://example.org/o'}]

    """

    query = requests.utils.quote(query)

    query_url = f"{address}/repositories/{repository}?query={query}"
    headers = {"Accept": "application/sparql-results+json"}
    response = requests.get(query_url, headers=headers)

    if response.status_code == 200:
        result = SparqlQuery(**response.json())
        result = convert_sparql_query_to_result(result)
        # result = query_result_to_dict(result)
        return result
    return None
