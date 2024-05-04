from rdflib import Graph
from pyshacl import validate
from thing_description.thing_description import ThingDescription
from functools import cache

@cache
def get_protocol_linkings():
    return Graph(store="Oxigraph").parse("./retrowot/protocol_linkings.ttl")

@cache
def get_shacl_graph():
    return Graph(store="Oxigraph").parse("./retrowot/servicetranslation.ttl")
    
    

def align_capabilities(device, emitter = None, performance_test = False):
    
    
    g_device = device.to_rdf()
    
    #g_device.serialize("device.ttl", format="turtle")
    #g_device.serialize("zigbee_test_device.ttl", format="turtle")

    g_linkings = get_protocol_linkings()

    g_device = g_device + g_linkings

    shacl_graph = get_shacl_graph()

    validate(g_device, shacl_graph=shacl_graph, advanced=True, inplace=True)

    g_device.serialize("linkings.ttl", format="turtle")
    
    if performance_test:
        return g_device
    

    generate_thing_description(device, g_device, emitter)
    




def prRed(skk): print("\033[91m {}\033[00m" .format(skk))




def generate_thing_description(device, graph):
    
    prRed("generate_thing_description")
    deviceNames = [
        _.deviceName.toPython() for _ in graph.query(SELECT_QUERY_GET_DEVICE_NAME)
    ]

    if len(deviceNames) < 1:
        deviceNames = [
            _.deviceName.toPython() for _ in graph.query(SELECT_QUERY_GET_DEVICE_NAME_2)
        ]

    deviceName = deviceNames[0]

    deviceAddress = [
        _.deviceName.toPython() for _ in graph.query(SELECT_QUERY_GET_DEVICE_ADDRESS)
    ][0]

    print("DeviceNames: ", deviceNames)
    graph.serialize(f"{deviceName}.ttl", format="turtle")

    print(deviceName)
    td = ThingDescription(title=deviceName)

    for _ in graph.query(
        SELECT_QUERY_SERVICE_TO_PROPERTY_AFFORDANCE.replace(
            "DEVICE_NAME", deviceAddress
        )
    ):
        print(_)
        form = Form(
            href=deviceAddress + "/" + _.affordanceId.toPython(),
            op=_.interactionType.toPython(),
        )
        affordance = PropertyAffordance(
            title=_.capabilityName.toPython(),
            forms=[form],
        )
        td.properties.append(affordance)

    for _ in graph.query(
        SELECT_QUERY_SERVICE_TO_ACTION_AFFORDANCE.replace("DEVICE_NAME", deviceAddress)
    ):
        print(_)
        form = Form(
            href=deviceAddress + "/" + _.affordanceId.toPython(),
            op=_.interactionType.toPython(),
        )
        affordance = ActionAffordance(
            title=_.capabilityName.toPython(),
            forms=[form],
        )
        td.properties.append(affordance)

    for _ in graph.query(
        SELECT_QUERY_SERVICE_TO_EVENT_AFFORDANCE.replace("DEVICE_NAME", deviceAddress)
    ):
        print(_)
        form = Form(
            href=deviceAddress + "/" + _.affordanceId.toPython(),
            op=_.interactionType.toPython(),
        )

        affordance = EventAffordance(
            title=_.capabilityName.toPython(),
            forms=[form],
        )
        td.events.append(affordance)

    device.thing_description = td
def enrich_capability_name(capability_name: str):
    prRed("enrich_capability_name")
    pass

def generate_thing_description(device, graph, emitter):
    device.thing_description = ThingDescription(graph=graph)

    if emitter is not None:    
        emitter.emit("thing_description_created", device)
        emitter.emit("add_thing_description_to_thing_directory", device)
    
    
def enrich_affordance(device, g_device, emitter):
    prRed("enrich_affordance")
    enriched_capabilities = Graph().parse("./servicecapability.ttl")

    select_capability_query = """
    
    SELECT ?affordanceId ?protocolStack 
    WHERE {
        
        ?device a capability:Device;
            capability:hasProtocolStack ?protocolStack;
            capability:hasAffordance ?affordance.
        
        
        ?affordance capability:hasAffordanceID ?affordanceId;
        capability:hasInteraction ?interactionType.
        
        }
    """

    output_query = """
    PREFIX capability: <http://purl.org/serviceCapability#>
    PREFIX prof: <http://www.w3.org/ns/dx/prof/>
    PREFIX td: <https://www.w3.org/2022/wot/td#>
    
    SELECT ?capabilityName ?outputFormat ?outputUnit ?decodingRule ?ruleConformance
    WHERE {
        
        ?capability a capability:ServiceCapability;
        capability:represents ?capabilityName;
        capability:hasProtocolStack ?protocolStack;
        capability:hasInteraction [capability:hasAffordanceId "AFFORDANCE_ID"];
        capability:hasDataModel [
            capability:hasOutputFormat ?outputFormat;
            capability:hasOutputUnit ?outputUnit;
            capability:hasDecodingRule [
                prof:hasArtifact ?decodingRule;
                dct:conformsTo ?ruleConformance
        ].
    }
    
    """

    g_device
    emitter.emit("generate_thing_description", device, g_device)





if __name__ == "__main__":
    graph = Graph().parse("./BBC micro:bit [geto.ttl", format="turtle")
    
    shacl_graph = Graph().parse("./servicetranslation.ttl")

    validate(graph, shacl_graph=shacl_graph, advanced=True, inplace=True)
    graph.serialize("enriched_test.ttl", format="turtle")
    td = ThingDescription(graph)
