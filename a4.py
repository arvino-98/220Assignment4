import networkx as nx
inputFile = 'sample_in.txt'

'''
Getting raw input
////////////////////////////////////////////////////////
'''
rawInputArray = []
with open(inputFile) as f:
    for line in f:
        rawInputArray.append(line.split())
'''
////////////////////////////////////////////////////////
End raw input
'''

'''
Parsing input into graphs
////////////////////////////////////////////////////////
'''
# all arrays map 1-1 to each other, and hold graphs, budgets, and host Id's respectively
testCaseGraphs = []
testCaseBudget = []
testCaseHostIDs = []

# number of test cases is always first line of input
numOfTestCases = int(rawInputArray[0][0])

# we will iterate in such a way that the value of lineNum always
# represents a line number that gives test case specifications
# we init is as 1 to start from the second line (since the first line specifies # of test cases)
lineNum = 1
for i in range(numOfTestCases):
    print("test case " + str(i + 1))
    G = nx.Graph()

    # get int value from the line
    print(rawInputArray[lineNum])
    numberOfLinks = int(rawInputArray[lineNum][1])
    numberOfParties = int(rawInputArray[lineNum][2])
    numberOfHosts = int(rawInputArray[lineNum][3])

    testCaseBudget.append(numberOfParties)

    # slice array from first friendship link to last freindship link
    testCaseLinkSlice = rawInputArray[lineNum + 1:(lineNum + numberOfLinks + 1)]
    linkSliceLength = len(testCaseLinkSlice)

    # for each row of input in a slice
    for j in range(linkSliceLength):
        person1 = testCaseLinkSlice[j][0]
        person2 = testCaseLinkSlice[j][1]
        print(person1 + " " + person2)
        # add to graph
        G.add_edge(person1, person2)
        G.add_node(person1, depth=-1)
        G.add_node(person2, depth=-1)

    testCaseGraphs.append(G)

    lineNum += (numberOfLinks + 1)
    testCaseHostSlice = rawInputArray[lineNum:(lineNum + numberOfHosts)]
    hostSliceLength = len(testCaseHostSlice)

    hostIds = []
    for k in range(hostSliceLength):
        hostIds.append(testCaseHostSlice[k][0])
        print(testCaseHostSlice[k][0])

    testCaseHostIDs.append(hostIds)

    lineNum += numberOfHosts

    print("End test case")
'''
////////////////////////////////////////////////////////
End Parsing
'''

'''
Utilities
////////////////////////////////////////////////////////
'''
'''
neighbors
Returns the number of neighbers of a node in a graph
'''
def neighbors(graph, root):
    return list(nx.all_neighbors(graph, root))

def numberOfNeighbors(graph, root):
    return len(list(nx.all_neighbors(graph, root)))

'''
mostNeighbors
Returns the node with most neighbors
'''
def mostNeighbors(graph):
    maxNeighbors = 0
    retNode = None
    for node in graph.nodes:
        if numberOfNeighbors(graph, node) > maxNeighbors:
            maxNeighbors = numberOfNeighbors(graph, node)
            retNode = node
        elif numberOfNeighbors(graph, node) == maxNeighbors:
            if (node < retNode):
                retNode = node
    return retNode

'''
mostAwkward
Returns the most awkward (highest depth) node
'''
def mostAwkward(graph):
    maxAwkward = 0
    retNode = None
    for node in graph.nodes:
        if graph.nodes[node]["depth"] > maxAwkward:
            maxAwkward = graph.nodes[node]["depth"]
            retNode = node
        elif graph.nodes[node]["depth"] == maxAwkward:
            if (node < retNode):
                retNode = node
    return retNode

'''
setNodeDepths
Sets node depth on a graph for every node from root
'''
def setNodeDepths(graph, root):
    for node in graph.nodes:
        shortestPath = nx.shortest_path_length(graph, source=root, target=node)
        # -1 is what all node depths are initialized at
        # if depth is == -1 then we just set it to the shortestPath
        if (graph.nodes[node]["depth"] == -1):
            graph.nodes[node]["depth"] = shortestPath
        # elif there is an actual value and we need to check if the new shortestPath
        # is less than it
        elif (shortestPath < graph.nodes[node]["depth"]):
            graph.nodes[node]["depth"] = shortestPath
'''
sumDepths
Sum of all node depths
'''
def sumDepths(graph):
    sumDepths = 0
    for node in graph.nodes:
        sumDepths += float(graph.nodes[node]["depth"])
    return sumDepths
'''
////////////////////////////////////////////////////////
End Utilities
'''

'''
Heuristics for Part 4
////////////////////////////////////////////////////////
'''
'''
assignmentHeuristicOne
Find the person with the most friends and make them a party host. Repeat until M
party hosts have been assigned. Ties should be resolved by choosing the person with a
lower numerical ID.
'''
def assignmentHeuristicOne(graph, budget):
    nodes = list(graph.nodes)
    nodes.sort(key=lambda x: numberOfNeighbors(graph, x), reverse=True)
    return nodes[:budget]

'''
assignmentHeuristicTwo
First pick the person with the most friends and make them a party host. On subsequent
rounds, find the person with the maximum current social awkwardness and make
them a party host. Repeat until M party hosts have been assigned. Ties should be
resolved by choosing the person with a lower numerical ID.
'''
def assignmentHeuristicTwo(graph, budget):
    hosts = []
    hosts.append(mostNeighbors(graph))
    while len(hosts) < budget:
        setNodeDepths(graph, hosts[len(hosts) - 1])
        hosts.append(mostAwkward(graph))
    return hosts

'''
myHeuristic
TODO
Maybe: first pick host with most friends. then continuously pick a host who shares
the least vertices (friends) with the other hosts
'''
'''
////////////////////////////////////////////////////////
End Heuristics
'''

'''
computeHostsAssigned
Compute social awkwardness for the case that M hosts are given
'''
def computeHostsAssigned(graph, hostIds):
    for id in hostIds:
        setNodeDepths(graph, id)
    return round((sumDepths(graph) / (nx.number_of_nodes(graph) - len(hostIds))), 2)

'''
computeFixedBudget
Compute social awkwardness for the case with a fixed budget and assigned
hosts are not yet set
'''
def computeFixedBudget(graph, budget):
    hostIds = assignmentHeuristicTwo(graph, budget)
    #print(hostIds)
    return computeHostsAssigned(graph, hostIds)

'''
Main social awkwardness calculator that checks the number of host Id's
and calls proper compute function
'''
def computeSocialAwkwardness(graph, budget, hostIds):
    numberOfHosts = len(hostIds)
    if numberOfHosts == 0:
        return computeFixedBudget(graph, budget)
    elif numberOfHosts >= 1:
        return computeHostsAssigned(graph, hostIds)

'''
Testing
////////////////////////////////////////////////////////
'''
print("TESTS--------------------------------")
print(computeSocialAwkwardness(testCaseGraphs[0], testCaseBudget[0],testCaseHostIDs[0]))
print(computeSocialAwkwardness(testCaseGraphs[1], testCaseBudget[1], testCaseHostIDs[1]))
print(computeSocialAwkwardness(testCaseGraphs[2], testCaseBudget[2], testCaseHostIDs[2]))
print(computeSocialAwkwardness(testCaseGraphs[3], testCaseBudget[3], testCaseHostIDs[3]))
