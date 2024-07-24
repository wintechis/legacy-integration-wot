from rdflib.plugins.sparql import prepareQuery

thing_model_discovery_query = """
PREFIX tm: <https://www.w3.org/2019/wot/tm#>
PREFIX td: <https://www.w3.org/2019/wot/td#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX hctl: <https://www.w3.org/2019/wot/hypermedia#>

SELECT DISTINCT ?tm ?interactionAffordance ?interactionAffordanceForm ?target ?affordanceType
WHERE {
            ?tm a tm:ThingModel;
            ?aTR ?interactionAffordance.
        
        FILTER(?aTR in (td:hasActionAffordance, td:hasPropertyAffordance, td:hasEventAffordance))
        
        ?interactionAffordance a ?affordanceType; 
        td:hasForm ?interactionAffordanceForm.
        
        ?interactionAffordanceForm a hctl:Form;
            hctl:hasTarget ?target.        
    }
"""


thing_description_discovery_query = prepareQuery(
    """
PREFIX tm: <https://www.w3.org/2019/wot/tm#>
PREFIX td: <https://www.w3.org/2019/wot/td#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX hctl: <https://www.w3.org/2019/wot/hypermedia#>

SELECT DISTINCT ?baseUri ?interactionAffordance ?interactionAffordanceForm ?target ?affordanceType
WHERE {
    ?device a td:PartialThingDescription;
        td:baseURI ?baseUri;
        ?affordanceTypeRelation ?interactionAffordance.

    ?interactionAffordance a ?affordanceType;
        td:hasForm ?interactionAffordanceForm.
        
    

    ?interactionAffordanceForm a hctl:Form;
        hctl:hasTarget ?target.
        
    FILTER(?affordanceTypeRelation in (td:hasActionAffordance, td:hasPropertyAffordance, td:hasEventAffordance))
    FILTER (?affordanceType != td:InteractionAffordance)
    
} 
"""
)


interaction_affordance_test_query = """
PREFIX hctl: <https://www.w3.org/2019/wot/hypermedia#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tm:  <https://www.w3.org/2019/wot/tm#>
PREFIX td:  <https://www.w3.org/2019/wot/td#> 
PREFIX wotsec: <https://www.w3.org/2019/wot/security#>
PREFIX ex: <http://example.org/>

CONSTRUCT  {
    ?td a td:ThingDescription;
        td:name ?tdTitle;
        td:baseURI ?baseUri;
        td:hasSecurityConfiguration ?security;
        td:hasInstanceConfiguration "nosec_sc";
        td:hasPropertyAffordance ?affordance.

    ?affordance a td:PropertyAffordance;
    	?afTitle ?reference.
    
    ?reference td:description ?description;
        	td:type ?returnType;
    		td:hasForm ?form.
        
    ?form a hctl:Form;
        hctl:forContentType ?contentType;
        hctl:hasOperationType ?operation;
        hctl:hasTarget ?target.

    ?operation a td:OperationType. 

    ?security a td:SecurityConfiguration;
        ex:noSecurityScheme wotsec:NoSecurityScheme.
    
    wotsec:NoSecurityScheme wotsec:identity "nosec".

    
}  where {

    ?td a td:PartialThingDescription.


    
    ?form a hctl:Form;
        hctl:forContentType ?contentType;
        hctl:hasOperationType ?operation.

    ?operation a td:OperationType. 

    OPTIONAL {
        ?affordance td:type ?returnType .
    }
    
    OPTIONAL {
        ?affordance td:description ?description.
    }
    OPTIONAL {
        ?affordance td:name ?title.
    }
    
    BIND(IF(BOUND(?title), URI(CONCAT(STR(ex:),REPLACE(STR(?title), " ", ""))), URI(REPLACE(STR(?target), "./", ""))) as ?afTitle)

    BIND(URI(CONCAT(STR(?td), "/security")) AS ?security)
    BIND(URI(CONCAT(STR(?td), "/securityScheme")) AS ?securityScheme)
    BIND(URI(CONCAT(STR(?affordance), "/reference")) AS ?reference)
} 

"""


thing_model_discovery_query_ = prepareQuery(
    """
PREFIX tm: <https://www.w3.org/2019/wot/tm#>
PREFIX td: <https://www.w3.org/2019/wot/td#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX hctl: <https://www.w3.org/2019/wot/hypermedia#>

SELECT DISTINCT ?baseUri ?interactionAffordance ?interactionAffordanceForm ?tm ?interactionAffordanceModel ?interactionAffordanceFormModel ?affordanceType
WHERE {
    ?device a td:PartialThingDescription;
        td:baseURI ?baseUri;
        ?affordanceTypeRelation ?interactionAffordance.

    ?interactionAffordance a ?affordanceType;
        td:hasForm ?interactionAffordanceForm.
        
    

    ?interactionAffordanceForm a hctl:Form;
        hctl:hasTarget ?target.
        
    FILTER(?affordanceTypeRelation in (td:hasActionAffordance, td:hasPropertyAffordance, td:hasEventAffordance))
    FILTER (?affordanceType != td:InteractionAffordance)
    
    OPTIONAL {
        ?tm a tm:ThingModel;
            ?aTR ?interactionAffordanceModel.
        
        FILTER(?aTR in (td:hasActionAffordance, td:hasPropertyAffordance, td:hasEventAffordance))
        
        ?interactionAffordanceModel td:hasForm ?interactionAffordanceFormModel.
        
        ?interactionAffordanceFormModel a hctl:Form;
            hctl:hasTarget ?target.    
    }
} 
"""
)


thing_model_discovery_query__ = prepareQuery(
    """
PREFIX tm: <https://www.w3.org/2019/wot/tm#>
PREFIX td: <https://www.w3.org/2019/wot/td#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX hctl: <https://www.w3.org/2019/wot/hypermedia#>

SELECT DISTINCT ?baseUri ?interactionAffordance ?interactionAffordanceForm ?tm ?interactionAffordanceModel ?interactionAffordanceFormModel ?affordanceType
WHERE {
    {
        ?device a td:PartialThingDescription;
        td:baseURI ?baseUri;
        td:hasEventAffordance ?interactionAffordance.

        ?interactionAffordance td:hasForm ?interactionAffordanceForm.

        ?interactionAffordanceForm a hctl:Form;
        hctl:hasTarget ?target.


        OPTIONAL {
            ?tm a tm:ThingModel;
            td:hasEventAffordance ?interactionAffordanceModel.

            ?interactionAffordanceModel td:hasForm ?interactionAffordanceFormModel.

            ?interactionAffordanceFormModel a hctl:Form;
            hctl:hasTarget ?target.    
        } 
    } UNION {
        ?device a td:PartialThingDescription;
        td:baseURI ?baseUri;
        td:hasPropertyAffordance ?interactionAffordance.

        ?interactionAffordance td:hasForm ?interactionAffordanceForm.

        ?interactionAffordanceForm a hctl:Form;
        hctl:hasTarget ?target.


        OPTIONAL {
            ?tm a tm:ThingModel;
            td:hasPropertyAffordance ?interactionAffordanceModel.

            ?interactionAffordanceModel td:hasForm ?interactionAffordanceFormModel.

            ?interactionAffordanceFormModel a hctl:Form;
            hctl:hasTarget ?target.    
        }
    } UNION {
        ?device a td:PartialThingDescription;
        td:baseURI ?baseUri;
        td:hasActionAffordance ?interactionAffordance.

        ?interactionAffordance td:hasForm ?interactionAffordanceForm.

        ?interactionAffordanceForm a hctl:Form;
        hctl:hasTarget ?target.


        OPTIONAL {
            ?tm a tm:ThingModel;
            td:hasActionAffordance ?interactionAffordanceModel.

            ?interactionAffordanceModel td:hasForm ?interactionAffordanceFormModel.

            ?interactionAffordanceFormModel a hctl:Form;
            hctl:hasTarget ?target.    
        }
    }


}                          
"""
)

baseUri_and_title_query = prepareQuery(
    """ 
PREFIX td: <https://www.w3.org/2019/wot/td#>

SELECT DISTINCT ?baseUri ?title 
WHERE {
    ?device a td:PartialThingDescription;
        td:baseURI ?baseUri;
        td:title ?title.
} 
"""
)


interaction_affordance_query = prepareQuery(
    """
    PREFIX hctl: <https://www.w3.org/2019/wot/hypermedia#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX tm:  <https://www.w3.org/2019/wot/tm#>
    PREFIX td:  <https://www.w3.org/2019/wot/td#> 
    select ?title ?description ?returnType ?form ?affordanceType
    where {
        ?affordance a ?affordanceType;
        td:hasForm ?form.
        
        OPTIONAL {
            ?affordance td:type ?returnType .
        }
        
        OPTIONAL {
            ?affordance td:description ?description.
        }
        OPTIONAL {
            ?affordance td:name ?title.
        }
        
    } 
"""
)


form_query = prepareQuery(
    """
    PREFIX hctl: <https://www.w3.org/2019/wot/hypermedia#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX tm:  <https://www.w3.org/2019/wot/tm#>
    PREFIX td:  <https://www.w3.org/2019/wot/td#> 

    select ?contentType ?operation
    where {
        ?form a hctl:Form;
        hctl:forContentType ?contentType;
        hctl:hasOperationType ?operation.

        ?operation a td:OperationType. 
    } 
"""
)


thing_model_query = prepareQuery(
    """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX tm:  <https://www.w3.org/2019/wot/tm#>
    PREFIX td:  <https://www.w3.org/2019/wot/td#> 
    select ?title ?interactionAffordance ?interactionAffordanceType ?baseURI ?reference where {
        ?tm a tm:ThingModel ;
            td:title ?title.
        
        OPTIONAL {
            ?tm ?interactionAffordanceType ?interactionAffordance.
            ?interactionAffordanceType rdfs:subPropertyOf td:hasInteractionAffordance.
        }
        
        OPTIONAL {
            ?tm td:baseURI ?baseURI.
        }
        
        OPTIONAL {
            ?tm rdfs:seeAlso ?reference.
        }
}
"""
)
