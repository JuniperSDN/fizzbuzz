$(document).ready(init)

function captializeWords(inString) {
	return inString.replace(/\b\w/g, function(l){ return l.toUpperCase() })
}

function init() {
	$("#link_traffic_stats_sidebar .close").click(function() {
		$("#link_traffic_stats_sidebar").hide("slide", { direction: "right" }, 200);
	});

	// initSocket();
	showGraph();

	// requestRedisKeys(function(data) {
	// 	console.log(data.data.filter(function(d) {
	// 		return true //d.indexOf("san francisco:") != -1 && d.indexOf("statistics") != -1
	// 	}))
	// })

	// function handle(key, data) {
	// 	// console.log(data.data[0]/*.slice(0,3)*/)
	// 	var thisStats = JSON.parse(data.data[0])['stats'][0]
	// 	console.log(key+'::output-pps:', thisStats['output-pps'][0]['data'])
	// 	console.log(key+'::output-bps:', thisStats['output-bps'][0]['data'])

	// 	console.log(key+'::input-pps:', thisStats['input-pps'][0]['data'])
	// 	console.log(key+'::input-bps:', thisStats['input-bps'][0]['data'])
	// }

	// getInterfaceStats('san francisco:ge-1/0/1:traffic statistics', handle.bind(null, 1))
	// getInterfaceStats('san francisco:ge-1/0/3:traffic statistics', handle.bind(null, 3))
	// getInterfaceStats('san francisco:ge-1/0/0:traffic statistics', handle.bind(null, 0))

	// getInterfaceStats('san francisco:chicago:latency', function(data) {
	// 	console.log(data.data.slice(0,3))
	// 	// var thisStats = JSON.parse(data.data[0])['stats'][0]
	// 	// console.log('output-pps:', thisStats['output-pps'][0]['data'])
	// 	// console.log('output-bps:', thisStats['output-bps'][0]['data'])

	// 	// console.log('input-pps:', thisStats['input-pps'][0]['data'])
	// 	// console.log('input-bps:', thisStats['input-bps'][0]['data'])
	// })

	// window.addEventListener('mousemove', function(ev) {
	// 	console.log(ev.clientX, ev.clientY)
	// })
}

// get network topology
function getNetworkTopology(cb) {
	$.get('/api/v1', {operation: 'GET_NETWORK_TOPOLOGY'}).done(function(response) {
		cb(JSON.parse(response))
	})
}

// requests all redis keys
function requestRedisKeys(cb) {
	$.get('/api/v1', {operation: 'GET_REDIS_KEYS'}).done(function(response) {
		cb(JSON.parse(response))
	})
}

// request interface stats
function getInterfaceStats(interfaceKey, cb) {
	$.get('/api/v1', {operation: 'GET_INTERFACE_STATS', interface: interfaceKey}).done(function(response) {
		cb(JSON.parse(response))
	})
}

// get links status
function getLinksStatus(cb) {
	$.get('/api/v1', {operation: 'GET_LINKS_STATUS'}).done(function(response) {
		cb(JSON.parse(response))
	})
}

// get LSPs
function getLsps(cb) {
	$.get('/api/v1', {operation: 'GET_LSPS'}).done(function(response) {
		cb(JSON.parse(response))
	})
}

function fetchAndShowLinkStats(obj) {
	$("#loading").addClass('showLoader')
	$.get('/api/v1', {operation: 'GET_LINK_TRAFFIC_STATS', from: obj.source.hostName, to: obj.target.hostName}).done(function(response) {
		$("#loading").removeClass('showLoader')
		var jsonData = JSON.parse(response)
		var endA = jsonData.data[0]
		var endZ = jsonData.data[1]
		var latency = jsonData.data[2].latency


		// Way A
		var aFromRouter = captializeWords(latency[0]['from-router'])
		var aToRouter = captializeWords(latency[0]['to-router'])
		var aLatency = latency[0]['rtt-average(ms)']
		$("#link_traffic_stats_sidebar .latency_stats .wayA").html('<i>'+aFromRouter+'</i> &mdash;> <i>'+aToRouter+'</i>: <b>('+aLatency+')ms</b>')

		// Way B
		var bFromRouter = captializeWords(latency[1]['from-router'])
		var bToRouter = captializeWords(latency[1]['to-router'])
		var bLatency = latency[1]['rtt-average(ms)']
		$("#link_traffic_stats_sidebar .latency_stats .wayB").html('<i>'+bFromRouter+'</i> <&mdash; <i>'+bToRouter+'</i>: <b>('+bLatency+')ms</b>')


		$("#link_traffic_stats_sidebar .link_name h2").text(endA.name + ' - ' + endZ.name)
		$("#link_traffic_stats_sidebar .link_name span").text(obj.name)
		
		// endA
		$(".interface.endA .name").text(endA.name)
		$(".interface.endA .interface_addr").text(endA.data.interface_address)
		$(".interface.endA .router_id").text(endA.data.router_id)
		// endA::input
		$(".interface.endA .input-bps").text(endA.data.stats[0]['input-bps'][0].data)
		$(".interface.endA .input-bytes").text(endA.data.stats[0]['input-bytes'][0].data)
		$(".interface.endA .input-packets").text(endA.data.stats[0]['input-packets'][0].data)
		$(".interface.endA .input-pps").text(endA.data.stats[0]['input-pps'][0].data)
		// endA::output
		$(".interface.endA .output-bps").text(endA.data.stats[0]['output-bps'][0].data)
		$(".interface.endA .output-bytes").text(endA.data.stats[0]['output-bytes'][0].data)
		$(".interface.endA .output-packets").text(endA.data.stats[0]['output-packets'][0].data)
		$(".interface.endA .output-pps").text(endA.data.stats[0]['output-pps'][0].data)


		// endZ
		$(".interface.endZ .name").text(endZ.name)
		$(".interface.endZ .interface_addr").text(endZ.data.interface_address)
		$(".interface.endZ .router_id").text(endZ.data.router_id)
		// endZ::input
		$(".interface.endZ .input-bps").text(endZ.data.stats[0]['input-bps'][0].data)
		$(".interface.endZ .input-bytes").text(endZ.data.stats[0]['input-bytes'][0].data)
		$(".interface.endZ .input-packets").text(endZ.data.stats[0]['input-packets'][0].data)
		$(".interface.endZ .input-pps").text(endZ.data.stats[0]['input-pps'][0].data)
		// endZ::output
		$(".interface.endZ .output-bps").text(endZ.data.stats[0]['output-bps'][0].data)
		$(".interface.endZ .output-bytes").text(endZ.data.stats[0]['output-bytes'][0].data)
		$(".interface.endZ .output-packets").text(endZ.data.stats[0]['output-packets'][0].data)
		$(".interface.endZ .output-pps").text(endZ.data.stats[0]['output-pps'][0].data)


		// show sidebar
		$("#link_traffic_stats_sidebar").show("slide", { direction: "right" }, 300);
	})
}
