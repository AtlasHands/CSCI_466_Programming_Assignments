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
$(".friendly").on("click",function(){
	if($(this).hasClass("hit") || $(this).hasClass("miss")){

	}else{
		$(".friendly").removeClass("upNext");
		$("#enterButton").text("Confirm selection")
		$("#enterButton").addClass("ready");
		$(this).addClass("upNext");
	}
	
});
$("#enterButton").on("click",function(){
	var server = $("#serverIP").val();
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
					changeBoard(x,y,"hit")
				}
			}else if(getValueFromKey(keyValues,"miss")){
				changeBoard(x,y,"miss")
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
function changeBoard(x,y,type){
	var square = $(("#friendly-"+ x + "-" + y));
	if(square === $()){
		throw new Error("Whoops, coordinate doesn't exist");
	}
	square.addClass(type);
}