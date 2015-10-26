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
 * Initialize variables needed to call girder API's<br/> Call Girder Auth to
 * get <br/> 1. Auth token <br/> 2. Folder ID
 */
var authToken = null;// GLOBAL VARIABLE TO STORE AUTH TOKEN
var folderId = null;// GLOBAL VARIABLE TO STORE UPLOAD FOLDER ID
var FOLDER_NAME = 'uploaded_files'; // constant storing name of folder
$(function() {
	// get auth token
	/*
	 * $.ajax({ 'url' : '/girder/api/v1/user/authentication', 'type' : 'GET',
	 * headers : { 'Girder-Authorization' : 'Basic Z2lyZGVyOmdpcmRlcg==' }, async :
	 * false, success : function(data) { if (data && data.authToken &&
	 * data.authToken.token) { authToken = data.authToken.token; } }, error :
	 * function(jqXHR, textStatus, errorThrown) { alert('Issue while logging into
	 * Girder - ' + textStatus + ' - ' + errorThrown); } });
	 */
	// get folder id
	if (authToken) {
		callGirderWithAuth('girder/api/v1//folder?parentType=collection&text=' + FOLDER_NAME + '&limit=50', 'GET', false,
				{}, function(data) {
					for ( var ele in data) {
						if (data[ele].name == FOLDER_NAME) {
							folderId = data[ele]._id;
							break;
						}
					}
				});
	}
});

/**
 * Generic AJAX call to girder APIs Sample usage - callGirderWithAuth (url,
 * typeMethod, asyncBoolean, data, successFunction)
 */
var callGirderWithAuth = function(url, type, async, data, success) {
	$.ajax({
		'url' : url,
		'type' : type,
		'data' : data,
		headers : {
			'Girder-Token' : authToken
		},
		'async' : async,
		'success' : success,
		error : function(jqXHR, textStatus, errorThrown) {
			alert('Issue while calling Girder API - ' + url + ' - ' + textStatus + ' - ' + errorThrown);
		}
	});
}

/**
 * Draws basic layer of map
 */
var map = null;
$(function() {
	map = geo.map({
		'node' : '#map'
	});
	map.createLayer('osm');

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
var dataPoints = {};
var drawPoints = function() {
	// var map = geo.map({
	// 'node' : '#map'
	// });
	// map.createLayer('osm');

	var featureLayer = map.createLayer('feature', {
		renderer : 'vgl'
	});
	var uiLayer = map.createLayer('ui');

	featureLayer.createFeature('point', {
		selectionAPI : true
	}).data(dataPoints).position(function(d) {
		return {
			x : d.x,
			y : d.y
		};
	}).geoOn(
			geo.event.feature.mouseover,
			function(evt) {
				$(uiLayer.node()).append(
						'<div id="example-overlay">' + evt.data.location + '<br/> Reference: ' + evt.data.content
								+ '<br/> Extracted from: ' + evt.data.file + '</div>');

				var pos = map.gcsToDisplay({
					x : evt.data.x,
					y : evt.data.y
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

	callGirderWithAuth('extract_text/geoparser_app/static/uploaded_files/' + file.name, 'GET', false, {}, function(data) {
		displayArea.textContent = 'Extracted Text..';
	});

	// ALL SET TIMEOUTS NEED TO BE REMOVED ONCE APIS START RESPONDING AFTER ACTUAL
	// PROCESSING
	setTimeout(function() {
		callGirderWithAuth('find_location/' + file.name, 'GET', false, {}, function(data) {
			displayArea.textContent = 'Finding location..';
		});
	}, 3000);

	setTimeout(function() {
		callGirderWithAuth('find_latlon/' + file.name, 'GET', false, {}, function(data) {
			displayArea.textContent = 'Finding lat lon';
		});
	}, 6000);

	setTimeout(function() {
		callGirderWithAuth('return_points/' + file.name, 'GET', false, {}, function(data) {
			data = eval(data);// REMOVE THIS ONCE API RETURNS JSON
			displayArea.textContent = '';
			var list = '<ol>';
			for ( var i in data) {
				data[i].file = file.name;
				list += '<li>' + data[i].location + '</li>';
			}
			list += '</ol>'
			displayArea.appendChild(Dropzone.createElement(list));

			// KEEP ON APPENDING POINTS
			dataPoints = data.concat(dataPoints);
			drawPoints();
		});
	}, 9000);

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
		// Set the url for Girder multipart file upload
		url : 'upload_file',
		paramName : 'chunk',
		parallelUploads : 2,
		previewTemplate : previewTemplate,
		maxFilesize : 1024, // MB
		autoQueue : true,
		headers : {
			'Girder-Token' : authToken
		// Girder Auth token as received
		},
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

	setTimeout(function() {
		var mockFile = {
			name : "File1.txt",
			size : 12345
		};
		myDropzone.options.addedfile.call(myDropzone, mockFile);
		myDropzone.emit("complete", mockFile);
		myDropzone.emit("success", mockFile, 'Uploaded File');

		myDropzone.files.push(mockFile);
	}, 100);

	setTimeout(function() {
		var mockFile = {
			name : "File2.txt",
			size : 42345
		};
		myDropzone.options.addedfile.call(myDropzone, mockFile);
		myDropzone.emit("complete", mockFile);
		myDropzone.emit("success", mockFile, 'Uploaded File');

		myDropzone.files.push(mockFile);
	}, 10000);

});