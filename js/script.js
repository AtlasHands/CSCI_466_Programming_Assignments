makeBattleShipTable();
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
$("#connectFriendlyIP").on("click",function(){
	var ip = $("#friendlyIP").val();
	var ajaxSettings ={
		url: "http://" + ip + "/api/getBoard",
		method: "GET",
	}
	var request = $.ajax(ajaxSettings);
	request.always(function(data,status){
		if(status === "success"){
			var keyValues = parseResponse(data);
			var hitMap = getValueFromKey(keyValues,"hitmap");
			parseHitMap(hitMap,"friendly");
		}
	});
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
			}
		}
	}
}
$("#enterButton").on("click",function(){
	var server = $("#friendlyIP").val();
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
			$("#enterButton").text("Select Tile")
			$("#enterButton").removeClass("ready");
			if(hasKey(keyValues,"hit")){
				if(getValueFromKey(keyValues,"hit") === "1"){
					changeBoard(x,y,"hit","enemy")
				}
			}else if(getValueFromKey(keyValues,"miss")){
				changeBoard(x,y,"miss","enemy")
			}
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
	square.addClass(type);
}