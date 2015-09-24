'use strict';

//to safeguard from old browser which don't support console 
if (!window.console) {
	window.console = {
		error : function() {
		},
		log : function() {
		}
	};
}
/*
 * The data schema used in this example is as follows: { color: string -- a
 * css color name hex: string -- a 24bit hex value position: object -- a
 * correlated gaussian R.V. in R^2 exp: number -- a random value ~ exp(0.1)
 * unif: number -- a random uniform value in [0,1] fruits: string -- a
 * random fruit }
 */
var spec = {
	center : {
		x : -100,
		y : 40
	},
	zoom : 4,
	layers : [ {
		renderer : 'd3',
		features : [ {
			type : 'point',
			size : function(d) {
				return d.exp;
			},
			position : function(d) {
				return {
					x : d.position.x,
					y : d.position.y
				};
			},
			fill : true,
			fillColor : function(d) {
				return d.fruits;
			},
			fillOpacity : function(d) {
				return 0.5 + d.unif / 2;
			},
			stroke : true,
			strokeColor : function(d) {
				return d.color;
			},
			strokeOpacity : 1,
			strokeWidth : 2
		} ]
	} ]
};

$(function() {
    geo.map({'node': '#map'}).createLayer('osm');

});

/**
 * Polls /status API to get parsing status of file and show pointers on map if found.
 * TODO: To implement recursive polling after every 5 seconds. Below function will only be called once
 */
var getStatus = function (uploadResponse){
	
	if(uploadResponse){
		//TODO Design a template and apply to this rather than just appending text 
		$("#uploadedFiles").append("<li>" + uploadResponse + "</li>");
	}
	$.ajax({
		dataType : 'json',
		url : 'static/json/sample_data.json',//needs to be changed to actual API
		success : function(data) {
			//TODO Append data instead of removing existing data
			spec.data = data;//might become data.parsedInfo
			$('#map').geojsMap(spec);//spec filled with pointers data
		},
		error : function(e) {
			console.error("Eroor.." + e.responseText);
		}
	});
}

// Dropzone configurations start
Dropzone.options.dropzoneForm = {
	init : function() {
		this.on("success", function(file, responseText) {
			//console.log(file.name);//file details can be found here 
            //console.log(responseText); // API response can be accessed here
			this.removeFile(file);//removes icon from box
            getStatus(responseText);//Start looking for geo parse status and show pointers on map if found
        });
	},
	maxFilesize : 1024, // MB
	parallelUploads : 2,
	addRemoveLinks : true //For users to remove file upload icons in case unsuccessful 
};
//Dropzone configurations ended

