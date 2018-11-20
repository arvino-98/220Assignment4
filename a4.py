import networkx as nx
inputFile = 'all_in.txt'

'''
Getting raw input
////////////////////////////////////////////////////////
'''
rawInputArray = []
with open(inputFile) as f:
    for line in f:
        rawInputArray.append(line.split())
print rawInputArray
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
testCaseBudgets = []
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

    # get int values from the line
    print(rawInputArray[lineNum])
    numberOfLinks = int(rawInputArray[lineNum][1])
    numberOfParties = int(rawInputArray[lineNum][2])
    numberOfHosts = int(rawInputArray[lineNum][3])

    testCaseBudgets.append(numberOfParties)

    # slice array from first friendship link to last friendship link
    testCaseLinkSlice = rawInputArray[lineNum + 1:(lineNum + numberOfLinks + 1)]
    linkSliceLength = len(testCaseLinkSlice)

    # creating graphs and appending to graph array
    for j in range(linkSliceLength):
        person1 = testCaseLinkSlice[j][0]
        person2 = testCaseLinkSlice[j][1]
        print(person1 + " " + person2)
        # add to graph
        G.add_edge(person1, person2)
        G.add_node(person1, depth=-1)
        G.add_node(person2, depth=-1)
    testCaseGraphs.append(G)

    # moving to lines that specify host id's
    lineNum += (numberOfLinks + 1)
    testCaseHostSlice = rawInputArray[lineNum:(lineNum + numberOfHosts)]
    hostSliceLength = len(testCaseHostSlice)

    # appending host id's to array
    hostIds = []
    for k in range(hostSliceLength):
        hostIds.append(testCaseHostSlice[k][0])
        print(testCaseHostSlice[k][0])
    testCaseHostIDs.append(hostIds)

    # moving to next line that has test case specifications
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
numberOfNeighbors
Returns number of neighbors -_-
'''
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
        # break ties by lower ID
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
        # break ties by lower ID
        elif graph.nodes[node]["depth"] == maxAwkward:
            if (node < retNode):
                retNode = node
    return retNode

'''
setNodeDepths
Sets node depth on a graph for every node from root.
Since this function modifies the given graph, it is important to
work with copies if working on the same graph more than once
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
sumOfDepths
Sum of all node depths
'''
def sumOfDepths(graph):
    sumOfDepths = 0
    for node in graph.nodes:
        sumOfDepths += float(graph.nodes[node]["depth"])
    return sumOfDepths

'''
computeSocialAwkwardness
Compute social awkwardness for the case that M hosts are given
'''
def computeSocialAwkwardness(graph, hostIds):
    for id in hostIds:
        setNodeDepths(graph, id)
    return '{:.2f}'.format(round((sumOfDepths(graph) / (nx.number_of_nodes(graph) - len(hostIds))), 2))

'''
mostUniqueFriends
Find the node with most unique vertices
'''
def mostUniqueFriends(graph, adjacents):
    max = 0
    maxNode = None
    for node in graph.nodes:
        uniqueFriends = 0
        for v in list(nx.all_neighbors(graph, node)):
            if v not in adjacents:
                uniqueFriends += 1
        if uniqueFriends > max:
            max = uniqueFriends
            maxNode = node
    return maxNode

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
    # python sort is stable so sort by id, then by number of neighbors
    nodes.sort(key=lambda x: int(x), reverse=False)
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
    # use a local copy since setNodeDepths() modifes given graph
    localGraphCopy = graph
    hosts = []
    hosts.append(mostNeighbors(localGraphCopy))
    while len(hosts) < budget:
        setNodeDepths(localGraphCopy, hosts[len(hosts) - 1])
        hosts.append(mostAwkward(localGraphCopy))
    return hosts

'''
myHeuristic
Continuously pick a host who shares the least vertices (friends) with the other hosts.
So we will have hosts with the maximum amount of unique neighbors.
'''
def myHeuristic(graph, budget):
    hosts = []
    # a set of nodes that are adjacent to a host
    adjacents = set([])
    while len(hosts) < budget:
        v = mostUniqueFriends(graph, adjacents)
        if v not in hosts:
            for neighbor in list(nx.all_neighbors(graph, v)):
                adjacents.add(neighbor)
            adjacents.add(v)
            hosts.append(v)
    return hosts
'''
////////////////////////////////////////////////////////
End Heuristics
'''

'''
Writing output
////////////////////////////////////////////////////////
'''
def writeHeuristicOne(graph, budget):
    hcopy = graph.copy()
    heuristicOneHostIds = assignmentHeuristicOne(hcopy, testCaseBudgets[i])
    output.write("Heuristic 1 hosts are ")
    output.write(str(heuristicOneHostIds) + "\n")
    output.write("Average social awkwardness = ")
    output.write(str(computeSocialAwkwardness(hcopy, heuristicOneHostIds)) + "\n")

def writeHeuristicTwo(graph, budget):
    hcopy = graph.copy()
    heuristicTwoHostIds = assignmentHeuristicTwo(hcopy, testCaseBudgets[i])
    output.write("Heuristic 2 hosts are ")
    output.write(str(heuristicTwoHostIds) + "\n")
    output.write("Average social awkwardness = ")
    output.write(str(computeSocialAwkwardness(hcopy, heuristicTwoHostIds)) + "\n")

def writeMyHeuristic(graph, budget):
    hcopy = graph.copy()
    myHeuristicHostIds = myHeuristic(hcopy, testCaseBudgets[i])
    output.write("My heuristic hosts are ")
    output.write(str(myHeuristicHostIds) + "\n")
    output.write("Average social awkwardness = ")
    output.write(str(computeSocialAwkwardness(hcopy, myHeuristicHostIds)) + "\n")

output = open("output.txt", "w")
for i, graph in enumerate(testCaseGraphs):
    output.write("Test case " + str(i+1) + ".\n")
    if len(testCaseHostIDs[i]) == 0:
        writeHeuristicOne(testCaseGraphs[i], testCaseBudgets[i])
        writeHeuristicTwo(testCaseGraphs[i], testCaseBudgets[i])
        writeMyHeuristic(testCaseGraphs[i], testCaseBudgets[i])

    elif len(testCaseHostIDs[i]) >= 1:
        output.write("Average social awkwardness = ")
        output.write(str(computeSocialAwkwardness(testCaseGraphs[i], testCaseHostIDs[i])))
        output.write("\n")
'''
////////////////////////////////////////////////////////
End writing
'''
