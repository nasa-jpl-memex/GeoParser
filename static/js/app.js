'use strict';

// to safeguard from old browser which don't support console
if (!window.console) {
	window.console = {
		error : function() {
		},
		log : function() {
		}
	};
}
/*
 * The data schema used in this example is as follows: { color: string -- a css
 * color name hex: string -- a 24bit hex value position: object -- a correlated
 * gaussian R.V. in R^2 exp: number -- a random value ~ exp(0.1) unif: number --
 * a random uniform value in [0,1] fruits: string -- a random fruit }
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
	geo.map({
		'node' : '#map'
	}).createLayer('osm');

});

/**
 * Polls /status API to get parsing status of file and show pointers on map if
 * found. TODO: To implement recursive polling after every 5 seconds. Below
 * function will only be called once
 */
var getStatus = function(uploadResponse) {

	if (uploadResponse) {
		// TODO Design a template and apply to this rather than just appending
		// text
		$("#uploadedFiles").append("<li>" + uploadResponse + "</li>");
	}
	$.ajax({
		dataType : 'json',
		url : 'static/json/sample_data.json',// needs to be changed to actual
												// API
		success : function(data) {
			// TODO Append data instead of removing existing data
			spec.data = data;// might become data.parsedInfo
			$('#map').geojsMap(spec);// spec filled with pointers data
		},
		error : function(e) {
			console.error("Error.." + e.responseText);
		}
	});
}

//Dropzone start
$(function() {
// Get the template HTML and remove it from the document template HTML and
// remove it from the document
var previewNode = document.querySelector("#template");
previewNode.id = "";
var previewTemplate = previewNode.parentNode.innerHTML;
previewNode.parentNode.removeChild(previewNode);

var myDropzone = new Dropzone(document.body, { // Make the whole body a
												// dropzone
	url : "/upload", // Set the url
	parallelUploads : 2,
	previewTemplate : previewTemplate,
	maxFilesize : 1024, // MB
	autoQueue : true, 
	previewsContainer : "#previews", // Define the container to display the previews
	clickable : ".fileinput-button" // Define the element that should be used as click trigger to select files.
});

//myDropzone.on("addedfile", function(file) {
//	// Hookup the start button
//	file.previewElement.querySelector(".start").onclick = function() {
//		myDropzone.enqueueFile(file);
//	};
//});

// Update the total progress bar
myDropzone.on(
				"totaluploadprogress",
				function(progress) {
					document.querySelector("#total-progress .progress-bar").style.width = progress
							+ "%";
				});

myDropzone.on("sending", function(file) {
	// Show the total progress bar when upload starts
	document.querySelector("#total-progress").style.opacity = "1";
//	// And disable the start button
//	file.previewElement.querySelector(".start").setAttribute("disabled",
//			"disabled");
});

// Hide the total progress bar when nothing's uploading anymore
myDropzone.on("queuecomplete", function(progress) {
	document.querySelector("#total-progress").style.opacity = "0";
});

document.querySelector("#actions .cancel").onclick = function() {
	myDropzone.removeAllFiles(true);
};

myDropzone.on("success", function(file, responseText) {
	getStatus(responseText);// Start looking for geo parse status and show pointers on map if found
	
});


// Dropzone end

});
