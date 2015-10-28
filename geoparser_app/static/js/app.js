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

/**
 * Generic AJAX call to REST APIs Sample usage - callRESTApi (url, typeMethod,
 * asyncBoolean, data, successFunction)
 */
var callRESTApi = function(url, type, async, data, success) {
	return $.ajax({
		'url' : url,
		'type' : type,
		'data' : data,
		'async' : async,
		'success' : success,
		error : function(jqXHR, textStatus, errorThrown) {
			console.error('Issue while calling API - ' + url + ' - ' + textStatus + ' - ' + errorThrown);
		}
	});
}

/**
 * Draws basic layer of map and define basic colors
 * 
 */
var colorIndex = 0
var colorArr = [ 'black','red', 'yellow', 'blue', 'green', 'orange' ];
var map = null;
$(function() {
	map = geo.map({
		'node' : '#map', zoom: 2
	});
	map.createLayer('osm', {
		baseUrl : 'http://a.basemaps.cartocdn.com/light_all/'
	});
});

/**
 * Nav icons to control views. Views supported<br/> 1. Add Index<br/> 2.
 * Upload files<br/> 3. Search Index.
 */
$(function() {
	$("#navButtons :input").change(function() {
		var boxToBeDisplayed;
		// variable this points to the clicked input button
		var buttonClicked = $(this);
		buttonClicked.parent().addClass('active').siblings().removeClass('active');

		// switch case on this.id to control corresponding div
		switch (buttonClicked.attr("id")) {
		case 'navUploadFiles':
			boxToBeDisplayed = $('#fileUploadBox');
			break;
		case 'navAddIndex':
			boxToBeDisplayed = $('#addIndexBox');
			break;
		case 'navSearchIndex':
			boxToBeDisplayed = $('#searchIndexBox');
			break;
		default:
			console.error("Error while navigating ");
		}
		boxToBeDisplayed.removeClass('hide').siblings().addClass('hide');

	});
});

/**
 * Dropdown text change bindings. Dropdown is used in #addIndexBox
 */
$(function() {
	$(".dropdown-menu li a").click(function() {
		$(this).parents(".dropdown").find('.btn').html($(this).text() + ' <span class="caret"></span>');
		$(this).parents(".dropdown").find('.btn').val($(this).data('value'));
	});
});

/**
 * Function to draw points on #map
 */
var dataPointsAll = {
	position : {}
};
var drawPoints = function(dataPoints) {
	if (!dataPoints.length || dataPoints.length == 0) {
		return;
	}

	var featureLayer = map.createLayer('feature', {
		renderer : 'vgl'
	});
	var uiLayer = map.createLayer('ui');

	featureLayer.createFeature('point', {
		selectionAPI : true
	}).data(dataPoints).position(function(d) {
		return {
			'x' : d.position.x,
			'y' : d.position.y
		};
	}).style('fillColor', function(d) {
		if (d.color)
			return d.color;
		return 'yellow'
	}).geoOn(
			geo.event.feature.mouseover,
			function(evt) {
				$(uiLayer.node()).append(
						'<div id="example-overlay">' + evt.data.loc_name + '<br/> Extracted from: ' + evt.data.file + '</div>');

				var pos = map.gcsToDisplay({
					x : evt.data.position.x,
					y : evt.data.position.y
				});

				$('#example-overlay').css('position', 'absolute');
				$('#example-overlay').css('left', pos.x + 'px');
				$('#example-overlay').css('top', pos.y + 'px');
			}).geoOn(geo.event.feature.mouseout, function(evt) {
		$('#example-overlay').remove();
	}).geoOn(geo.event.pan, function(evt) {
		// Do something on pan
	});

	map.draw();
}

/**
 * Below code stores #progress-template once and removes it from DOM
 */
var progressTemplate;
$(function() {
	progressTemplate = document.querySelector("#progress-template-sucess");
	progressTemplate.id = "";
	progressTemplate.parentNode.removeChild(progressTemplate);
});

/**
 * Polls /status API to get parsing status of file and show pointers on map if
 * found. <br/> progressTemplate shows progress on UI
 */
var getStatus = function(uploadResponse, file) {
	console.log('Started processing file');

	// TODO: ALL API's should return json in future
	var progressTemplateCloned = progressTemplate.cloneNode();
	progressTemplateCloned.appendChild(progressTemplate.children[0].cloneNode());

	file.previewElement.appendChild(progressTemplateCloned);

	var displayArea = progressTemplateCloned.children[0];

	// AJAX 1
	callRESTApi('extract_text/' + file.name, 'GET', false, {}, function(data) {
		displayArea.textContent = data + '..';
	}).done(function(data) {
		setTimeout(function() {
			// AJAX 2
			callRESTApi('find_location/' + file.name, 'GET', false, {}, function(data) {
				displayArea.textContent = data + '..';

			}).done(function(data) {
				setTimeout(function() {
					// AJAX 3
					callRESTApi('find_latlon/' + file.name, 'GET', false, {}, function(data) {
						displayArea.textContent = data + '..';
					}).done(function(data) {
						// AJAX 4
						fetchAndDrawPoints(file, displayArea)
					});
				}, 1000);

			});
		}, 1000);

	});

}

var fetchAndDrawPoints = function(file, displayArea) {
	callRESTApi('return_points/' + file.name, 'GET', false, {}, function(data) {
		data = eval(data);// REMOVE THIS ONCE API RETURNS JSON
		displayArea.textContent = '';

		var list = '<ol>';
		for ( var i in data) {
			data[i].file = file.name;
			data[i].color = colorArr[colorIndex];
			list += '<li>' + data[i].loc_name + '</li>';
		}
		list += '</ol>'

		colorIndex++;
		if (colorIndex >= colorArr.length) {
			colorIndex = 0;
		}

		displayArea.appendChild(Dropzone.createElement(list));

		// KEEP ON APPENDING POINTS
		dataPointsAll = data.concat(dataPointsAll);
		drawPoints(data);
	});
}

var myDropzone;
// Dropzone start
// TODO truncate big file names
$(function() {
	// Get the template HTML and remove it from the document template HTML and
	// remove it from the document
	var previewNode = document.querySelector("#template");
	previewNode.id = "";
	var previewTemplate = previewNode.parentNode.innerHTML;
	previewNode.parentNode.removeChild(previewNode);

	myDropzone = new Dropzone(document.body, {// Whole body is a drop zone

		url : 'upload_file',
		paramName : 'chunk',
		parallelUploads : 2,
		previewTemplate : previewTemplate,
		maxFilesize : 1024, // MB
		autoQueue : true,
		previewsContainer : '#previews', // Container to display the previews
		clickable : '.fileinput-button' // class for click trigger to select files.
	});

	// Update the total progress bar
	myDropzone.on('totaluploadprogress', function(progress) {
		document.querySelector("#total-progress .progress-bar").style.width = progress + "%";
	});

	myDropzone.on("sending", function(file, xhr, formData) {
		// Show the total progress bar when upload starts
		document.querySelector("#total-progress").style.opacity = "1";
	});

	// Hide the total progress bar when nothing's uploading anymore
	myDropzone.on("queuecomplete", function(progress) {
		document.querySelector("#total-progress").style.opacity = "0";
	});

	document.querySelector("#actions .cancel").onclick = function() {
		myDropzone.removeAllFiles(true);
	};

	myDropzone.on("success", function(file, responseText) {
		getStatus(responseText, file);// Start looking for geo parse status and show
		// pointers on map if found

	});

	// Dropzone end

});

// TEMP code TODO: REMOVE BELOW
$(function() {

	var mockFile = {
		name : "polar.txt",
		size : 12345
	};
	myDropzone.options.addedfile.call(myDropzone, mockFile);

	setTimeout(function() {
		myDropzone.emit("complete", mockFile);
		myDropzone.emit("success", mockFile, 'Uploaded File');
		myDropzone.files.push(mockFile);
	}, 100);

	setTimeout(function() {
		mockFile = {
			name : "simple.txt",
			size : 12345
		};
		myDropzone.options.addedfile.call(myDropzone, mockFile);
		setTimeout(function() {
			myDropzone.emit("complete", mockFile);
			myDropzone.emit("success", mockFile, 'Uploaded File');
			myDropzone.files.push(mockFile);
		}, 100);
	}, 10000);

});