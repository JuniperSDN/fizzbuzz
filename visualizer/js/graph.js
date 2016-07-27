function showGraph() {
	var allLSPs = [];
	var editingLSPName = null;
	var newLSPNodes = [];

	var highlightedLSP = [];

	var NODE_LOCATIONS = {
		'SF': {x: 100, y: 374},
		'Dallas': {x: 711, y: 594},
		'Miami': {x: 1161, y: 776},
		'LA': {x: 158, y: 485},
		'Houston': {x: 750, y: 688},
		'Tampa': {x: 1091, y: 708},
		'NY': {x: 1231, y: 300},
		'Chicago': {x: 912, y: 295},
	}

	var width = window.innerWidth
    var height = window.innerHeight

	var outer = d3.select("div#graph").append("svg")
		.call(d3.behavior.zoom().on("zoom", rescale))
		.on("dblclick.zoom", null)
		.attr("width", width)
		.attr("height", height)
		.attr("pointer-events", "all")

	var svg = outer.append("svg:g")
	    .attr("width", width)
	    .attr("height", height)

	// add the map
	svg.append("image")
			.attr("xlink:href","../assets/usmap.svg")
			.attr("width", window.innerWidth)
			.attr("height", window.innerHeight)

	var node = svg.selectAll(".node"),
	    link = svg.selectAll(".link")
	var nodes = [],
	    links = []

	var color = d3.scale.category20b()

	var force = d3.layout.force()
	    .nodes(nodes)
	    .links(links)
	    .charge(-400)
	    .linkDistance(10)
	    .size([width, height]);

	function update() {
		link = link.data(force.links())
		link.exit().remove()
		
		link.enter().insert("line", ".node");

		link.attr("class", function(d) {
			return d.isUp ? "link" : "link error"
		})
		.attr('stroke', function (d) {
			// console.log(d, highlightedLSP)
			var ff = highlightedLSP.filter(function(lsp) {
				return d.name.indexOf(lsp.address) != -1
			})
			// console.log(ff)
			return ff.length != 0 ? '#0f0' : '#99c1ea'
		})
		.style({'stroke-width': '8px'})
		.on("click", fetchAndShowLinkStats)

		node = node.data(force.nodes())
		node.enter().insert("g").attr("class", "node");
		node.exit().remove()

		var nodeCircles = node.selectAll("circle")
		if (nodeCircles.empty()) {
			nodeCircles = node.insert("circle")
		}
		nodeCircles.attr("r", function() { return 15 });
		nodeCircles.on("click", function(obj) {
			if (editingLSPName != null) {
				newLSPNodes.push(obj.name)
			}
		})

		var nodeTexts = node.selectAll("text")
		if (nodeTexts.empty()) {
			nodeTexts = node.insert("text")
		}

		nodeTexts
			.attr("dx", 20)
			.attr("dy", ".35em")
			.text(function(d) { return d.hostName + ' - ' + d.name });


		force.on("tick", function() {
			node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

			link.attr("x1", function(d) { return d.source.x })
				.attr("y1", function(d) { return d.source.y })
				.attr("x2", function(d) { return d.target.x })
				.attr("y2", function(d) { return d.target.y });

			// linkText.attr("x", function(d) { return ((d.source.x + d.target.x) / 2) - 15 })
			// 	.attr("y", function(d) { return (d.source.y + d.target.y) / 2 })
		});

		force.start()
	}

	// Rescale function, called on zoom event
	function rescale() {
		trans = d3.event.translate
		scale = d3.event.scale
		svg.attr("transform", "translate(" + trans + ")" + " scale(" + scale + ")")
	}

	// fetch and update link status every 5 seconds
	setInterval(function() {
		getLinksStatus(function(data) {
			// clear links array
			links.length = 0

			for (l in data.data) {
				var thisLink = data.data[l]

				var fromIndex = nodes.findIndex(function(node) {
					return node.name === thisLink.endA.node.name
				})
				var toIndex = nodes.findIndex(function(node) {
					return node.name === thisLink.endZ.node.name
				})

				links.push({
					source: fromIndex,
					target: toIndex,
					isUp: (thisLink['operationalStatus'].toLowerCase() === "up"),
					name: thisLink.name
				})
			}

			update()
		})
	}, 5000)


	/// draw initial map
	getNetworkTopology(function(json) {
		for (n_I in json.data.nodes) {
			var thisNode = json.data.nodes[n_I]
			nodes.push({
				id: parseInt(thisNode.nodeIndex),
				name: thisNode.name,
				fixed: true,
				hostName: thisNode.hostName,
				x: NODE_LOCATIONS[thisNode.hostName].x,
				y: NODE_LOCATIONS[thisNode.hostName].y,
				loc_Coords: thisNode.topology.coordinates.coordinates,
			})
		}

		for (l in json.data.links) {
			var thisLink = json.data.links[l]
			var fromIndex = json.data.nodes.findIndex(function(node) {
				return node.name === thisLink.endA.node.name
			})
			var toIndex = json.data.nodes.findIndex(function(node) {
				return node.name === thisLink.endZ.node.name
			})

			links.push({
				source: fromIndex,
				target: toIndex,
				isUp: (thisLink['operationalStatus'].toLowerCase() === "up"),
				name: thisLink.name
			})
		}

		update()

		/// Next step:: fetch LSPs
		getLsps(function(json) {
			// console.log(json.data)
			allLSPs = json.data
			for(lsp_idx in json.data) {
				// console.log(json.data[lsp_idx])
				var thisLsp = json.data[lsp_idx]
				
				var lsp_eros_html = ''
				for (propIdx in thisLsp['liveProperties']['ero']) {
					var thisEro = thisLsp['liveProperties']['ero'][propIdx]
					lsp_eros_html += '<li class="list-group-item">\
							<p>'+thisEro.address+'</p>\
						</li>'
				}

				$("#lsps_sidebar .lsps_list").append('<li class="list-group-item">\
						<h5 data-name="'+thisLsp.name+'"><span class="lsp_name">'+thisLsp.name+'</span> <i class="fa fa-pencil editLSP" aria-hidden="true"></i><i class="fa fa-save saveLSP" style="display:none" aria-hidden="true"></i></h5>\
						<ul class="list-group">'+lsp_eros_html+'</ul>\
					</li>')
			}

			$("#lsps_sidebar .lsp_name").click(function() {
				// console.log('lsp click', )
				var el = this;
				var lsp_filtered = allLSPs.filter(function(lsp) {
					return $(el).parent().attr('data-name') == lsp['name']
				});

				// console.log(lsp_filtered[0]['liveProperties']['ero'])
				highlightedLSP = lsp_filtered[0]['liveProperties']['ero'];
				update()
			})

			$("#lsps_sidebar .lsps_list i.editLSP").click(function() {
				editingLSPName = $(this).parent().attr('data-name');
				$(this).hide();
				$(this).siblings(".saveLSP").show()
			})
			$("#lsps_sidebar .lsps_list i.saveLSP").click(function() {
				console.log('saving', newLSPNodes)
				// $.post('/api/v1', {operation})
				$.post('/api/v1', {operation: 'CREATE_NEW_LSP', eros: newLSPNodes, lspName: editingLSPName}).done(function(response) {
					console.log(response)
				});
				
				// toggles
				editingLSPName = null;
				newLSPNodes = [];
				$(this).hide();
				$(this).siblings(".editLSP").show()
			})
		})
	})
}