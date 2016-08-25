from pprint import pprint

# since None < 1 in python, for ease of program
# we just use an arbitarily large value as edge dist representing inf.
EDGE_INF=100000

# initial edge weight, ie. [2] is based on distance only
graph=[
	['a','c',4],
	['a','b',2],
	['a','e',5],
	['c','e',2],
	['b','e',4],
	['b','f',3],
	['e','d',4],
	['e','f',2],
	['f','d',3],
	['c','d',3],
]

def djks(graph, src='a', to='d'):

	''' helper function '''
	def _getNodeEdges(node):
		return [e for e in graph if e[0] == node or e[1] == node]

	''' helper function '''
	def _getOtherNode(edge, currentNode):
		if currentNode == edge[0]:
			return edge[1]
		else: return edge[0]

	prev={}; visited=[]; distTbl={}

	for e in graph:
		distTbl[e[0]]=EDGE_INF
		distTbl[e[1]]=EDGE_INF

	distTbl[src]=0

	for _ in xrange(len(distTbl.keys())):
		minDistNodeInGraph=min([(k,v) for (k,v) in distTbl.iteritems() if k not in visited], key=lambda x: x[1])[0]
		unvisitedEdges = filter(lambda e: _getOtherNode(e, minDistNodeInGraph) not in visited , _getNodeEdges(minDistNodeInGraph))

		# recompute distances
		for ue in unvisitedEdges:
			currDist = distTbl[_getOtherNode(ue, minDistNodeInGraph)]
			newDist = ue[2] + distTbl[minDistNodeInGraph]
			if currDist > newDist:
				distTbl[_getOtherNode(ue, minDistNodeInGraph)] = newDist
				prev[_getOtherNode(ue, minDistNodeInGraph)] = minDistNodeInGraph # how we got here...

		visited.append(minDistNodeInGraph)

	# retrace path back to `src`
	path = [to]
	while src not in path:
		path.append(prev[path[-1]])

	return path[::-1]

# this function is valid because once dijkstra computes a path
# there will be traffic flowing through the path and we need to
# take that traffic in account for the edge weights
def makePathHeavy(graph, path):
	for x in xrange(len(path)-1):
		for y in xrange(len(graph)):
			e=graph[y]
			if e[0] == path[x] and e[1] == path[x+1] or e[0] == path[x+1] and e[1] == path[x]:
				# this here is the 'traffic' being added to edge weight
				# the actual number can be computed many different ways
				# it just needs to be significantly different than the real world distances between the nodes
				graph[y][2] += 1000

if __name__ == "__main__":
	connectedNodes=[]

	# here would be a while loop, and we keep on looping until all nodes are connected
	# ie. `connectedNodes` list contains all nodes in the graph
	p0=djks(graph)
	makePathHeavy(graph, p0)

	p1=djks(graph)
	makePathHeavy(graph, p1)

	p2=djks(graph)
	makePathHeavy(graph, p2)

	# p0, p1, p2 are the three optimal 'paths' or in SDN terms, `LSPs` connecting all nodes
	print p0, p1, p2




