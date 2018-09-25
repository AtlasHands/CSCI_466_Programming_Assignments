makeBattleShipTable();
updated = true;
function makeBattleShipTable(height, width){
	for(var x = 0;x<height;x++){
		var row = $(document.createElement("tr"));
		for(var y =0;y<width;y++){
			var column = $(document.createElement("td"));
			column.attr("id","friendly-" + x + "-"+ y);
			row.append(column);
		}
		var table = $(document.getElementById("battleShipTable"));
		table.append(row);
	}
}
getUpdate(true)
//setInterval(function(){
	//getUpdate(false);
//},500);
function getUpdate(firstGrab){
	var ajaxSettings = {
		method: "GET",
		url: "http://" + window.location.host + "/api/getBoard"
	}
	var request = $.ajax(ajaxSettings);
	request.always(function(data,status){
		if(status === "success"){
			var keyValues = parseResponse(data);
			var hitMap = getValueFromKey(keyValues,"hitmap");
			parseHitMap(hitMap,"friendly");
			if(updated){
				$("#enterButton").text("Select Tile")
			}
		}
	});
	if(firstGrab){
		var positionSettings = {
			method: "GET",
			url: "http://" + window.location.host + "/api/getPositions"
		}
		var positionRequest = $.ajax(positionSettings)
		positionRequest.always(function(data,status){
		if(status === "success"){
			var keyValues = parseResponse(data);
			var positions = getValueFromKey(keyValues,"positions");
			parsePositions(positions);
		}
	});
	}
}
function parsePositions(positions){
	var split = positions.split("\n");
	for(var x = 0;x<split.length;x++){
		for(var y =0;y<split[0].length;y++){
			if(split[x][y] != "_"){
				addShip(x,y,split[x][y],"friendly")
			}
		}
	}
}
function addShip(x,y,name,board){
	var square = $(("#" + board + "-"+ x + "-" + y));
	if(square === $()){
		throw new Error("Whoops, coordinate doesn't exist");
	}
	square.text(name);
}
$(".enemy").on("click",function(){
	if($(this).hasClass("hit") || $(this).hasClass("miss")){

	}else{
		if($(this).hasClass("upNext")){
			$(this).removeClass("upNext");
			$("#enterButton").text("Select Tile")
			$("#enterButton").removeClass("ready");
		}else{
			$(".enemy").removeClass("upNext");
			$("#enterButton").text("Confirm selection")
			$("#enterButton").addClass("ready");
			$(this).addClass("upNext");
		}	
	}
});
$("#connectEnemyIP").on("click",function(){
	var ip = $("#enemyIP").val();
	var ajaxSettings ={
		url: "http://" + ip + "/api/getBoard",
		method: "GET"
	}
	$.ajax(ajaxSettings);
	var request = $.ajax(ajaxSettings);
	request.always(function(data,status){
		if(status === "success"){
			var keyValues = parseResponse(data);
			var hitMap = getValueFromKey(keyValues,"hitmap");
			parseHitMap(hitMap,"enemy");
		}
	});
})
function parseHitMap(hitMap,board){
	var split = hitMap.split("\n");
	for(var x = 0;x<split.length;x++){
		for(var y =0;y<split[0].length;y++){
			if(split[x][y] == "H"){
				changeBoard(x,y,"hit",board);
			}else if(split[x][y] == "M"){
				changeBoard(x,y,"miss",board);
			}else{
				changeBoard(x,y,"none",board);
			}
		}
	}
}
$("#enterButton").on("click",function(){
	if($(this).text() === "Waiting for turn"){
		return;
	}
	var server = $("#enemyIP").val();
	var selected = $(".upNext");
	var id = selected.attr("id");
	coords = id.split("-");
	x = coords[1];
	y = coords[2];
	var ajaxSettings ={
		url: "http://" + server + "?x=" + x + "&y=" + y,
		method: "POST"
	}
	var request = $.ajax(ajaxSettings);
	request.always(function(data,status,xhr){
		if(status === "success"){
			var keyValues = parseResponse(data)
			selected.removeClass("upNext");
			$("#enterButton").text("Waiting for turn")
			$("#enterButton").removeClass("ready");
			if(hasKey(keyValues,"hit")){
				if(getValueFromKey(keyValues,"hit") === "1"){
					changeBoard(x,y,"hit","enemy")
				}
			}else if(getValueFromKey(keyValues,"miss")){
				changeBoard(x,y,"miss","enemy")
			}
			if(hasKey(keyValues,"sink")){
				var letter = getValueFromKey(keyValues,"sink") 
				var getPositionSettings = {
					url: "http://" + server + "/api/getPositions",
					method: "GET"
				}
				console.log(getPositionSettings);
				console.log("Yay!")
				var positionRequest = $.ajax(getPositionSettings)
				positionRequest.always(function(data,status){
					if(status === "success"){
						var keyValues = parseResponse(data);
						var positioning = getValueFromKey(keyValues,"positions")
						var positioning = positioning.split("\n");
						console.log(positioning);
						for(var x = 0;x<positioning.length;x++){
							for(var y = 0;y<positioning[0].length;y++){
								if(positioning[x][y] == letter){
									addShip(x,y,letter,"enemy");
								}
							}
						}
					}
				});
			}
			updated = false;
		}
	});
})
function hasKey(array,key){
	for(var x = 0;x<array.length;x=x+2){
		if(array[x] == key){
			return true
		}
	}
	return false;
}
function getValueFromKey(array,key){
	for(var x = 0;x<array.length;x=x+2){
		if(array[x] == key){
			return array[x+1]
		}
	}
	return "";
}
function parseResponse(response){
	var pairs = response.split("&")
	var keyValues = []
	for(var x = 0;x<pairs.length;x++){
		var tempSplit = pairs[x].split("=");
		for(var y = 0;y<tempSplit.length;y++){
			keyValues.push(tempSplit[y]);
		}
	}
	return keyValues;
}
function changeBoard(x,y,type,board){
	var square = $(("#" + board + "-"+ x + "-" + y));
	if(square === $()){
		throw new Error("Whoops, coordinate doesn't exist");
	}
	if(type == "none"){
		if(square.hasClass("miss")){
			square.removeClass("miss");
			updated = true;
		}
		if(square.hasClass("hit")){
			square.removeClass("hit");
			updated = true;
		}
		
	}else{
		if(!square.hasClass(type)){
			square.addClass(type);
			updated = true;
		}	
	}
	
}