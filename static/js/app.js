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
	$.ajax({
		'url' : '/girder/api/v1/user/authentication',
		'type' : 'GET',
		headers : {
			'Girder-Authorization' : 'Basic Z2lyZGVyOmdpcmRlcg=='
		},
		async : false,
		success : function(data) {
			if (data && data.authToken && data.authToken.token) {
				authToken = data.authToken.token;
			}
		},
		error : function(jqXHR, textStatus, errorThrown) {
			alert('Issue while logging into Girder - ' + textStatus + ' - ' + errorThrown);
		}
	});
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
$(function() {
	geo.map({
		'node' : '#map'
	}).createLayer('osm');

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
var drawPoints = function(dataPoints) {
	var map = geo.map({
		'node' : '#map'
	});
	map.createLayer('osm');

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
	}).geoOn(geo.event.feature.mouseover, function(evt) {
		$(uiLayer.node()).append('<div id="example-overlay">' + evt.data.location + '<br/>' + evt.data.content + '</div>');

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
 * Polls /status API to get parsing status of file and show pointers on map if
 * found. <br/> TODO: To implement recursive polling after every 5 seconds.
 * Below function will only be called once
 */
var getStatus = function(uploadResponse) {

	// TODO Design a template to show response after file upload 
	// TODO Move it in Dropzone

	$.ajax({
		dataType : 'json',
		url : 'static/json/sample_data.json',// needs to be changed to actual
		// API
		success : function(data) {
			// TODO Append data instead of removing existing data
			drawPoints(data);
		},
		error : function(e) {
			console.error("Error.." + e.responseText);
		}
	});
}

// Dropzone start
// TODO truncate big file names
$(function() {
	// Get the template HTML and remove it from the document template HTML and
	// remove it from the document
	var previewNode = document.querySelector("#template");
	previewNode.id = "";
	var previewTemplate = previewNode.parentNode.innerHTML;
	previewNode.parentNode.removeChild(previewNode);

	var myDropzone = new Dropzone(document.body, {// Whole body is a drop zone
		// Set the url for Girder multipart file upload
		url : 'girder/api/v1/file/chunk',
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

		// Make sync call to create new item
		var itemId = null;
		callGirderWithAuth('girder/api/v1/item?folderId=' + folderId + '&name=' + file.name, 'POST', false, {}, function(
				data) {
			itemId = data._id;
		});

		var uploadFileId = null;
		if (itemId) {
			// Make sync call to create new place holder file
			callGirderWithAuth('girder/api/v1/file', 'POST', false, {
				'parentType' : 'item',
				'parentId' : itemId,
				'name' : file.name,
				'size' : file.size,
				'mimeType' : file.type
			}, function(data) {
				uploadFileId = data._id;
			});
		} else {
			// throw exception to stop further upload
			throw 'Unable to create item in Girder';
		}

		// Add additional formData as required by girder
		formData.append('offset', 0);
		formData.append('uploadId', uploadFileId);

	});

	// Hide the total progress bar when nothing's uploading anymore
	myDropzone.on("queuecomplete", function(progress) {
		document.querySelector("#total-progress").style.opacity = "0";
	});

	document.querySelector("#actions .cancel").onclick = function() {
		myDropzone.removeAllFiles(true);
	};

	myDropzone.on("success", function(file, responseText) {
		getStatus(responseText);// Start looking for geo parse status and show
		// pointers on map if found

	});

	// Dropzone end

});
