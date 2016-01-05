'use strict';

var csrfMiddlewareToken;
var CSRF_MIDDLEWARE_TOKEN_PARAM = "csrfmiddlewaretoken";

var getCsrfMiddlewareToken = function() {
	if (!csrfMiddlewareToken) {
		csrfMiddlewareToken = $("[name=csrfmiddlewaretoken]").val();
	}
	return csrfMiddlewareToken;
}

// to safeguard from old browser which don't support console
if (!window.console) {
	window.console = {
		error : function() {
		},
		log : function() {
		}
	};
}

// collapse "useInputDiv" on clicking +/- button
$(function() {

	$("#collapseIcon").bind('click', function(){ 
		$('#useInputDiv').toggle();
		$("#collapseIcon").toggleClass("glyphicon-minus"). toggleClass("glyphicon-plus");
	});
	
});

/**
 * Generic AJAX call to REST APIs Sample usage - callRESTApi (url, typeMethod,
 * asyncBoolean, data, successFunction)
 */
var callRESTApi = function(url, type, async, data, success, errorFn) {
	return $.ajax({
		'url' : url,
		'type' : type,
		'data' : data,
		'async' : async,
		'success' : success,
		error : function(jqXHR, textStatus, errorThrown) {
			console.error('Issue while calling API - ' + url + ' - ' + textStatus + ' - ' + errorThrown);
			if (errorFn && typeof errorFn == "function") {
				errorFn(jqXHR, textStatus, errorThrown);
			}
		}
	});
}

/**
 * Draws basic layer of map and define basic colors
 * 
 */
var colorIndex = 0
var colorArr = [ 'red', 'yellow', 'blue', 'green', 'orange', 'white', 'grey'];
var map = null;

$(function() {
	var layer = new ol.layer.Tile({
		source: new ol.source.XYZ({
      url: 'http://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
      attributions: [new ol.Attribution({ html: ['&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'] })]
    })
	});

	var view = new ol.View({
    center: ol.proj.transform([37.41, 8.82], 'EPSG:4326', 'EPSG:3857'),
	  zoom: 2
	});

	map = new ol.Map({
	  layers: [layer],
	  target: 'map',
	  view: view
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
var dataPointsAll = {};
var drawPoints = function(dataPoints) {

	if (!dataPoints.length || dataPoints.length == 0) {
		return;
	}
	
	for(var i in dataPoints){
		var point = dataPoints[i];
		var overlay = new ol.Overlay({
		  position: ol.proj.transform(
			    [point.position.y, point.position.x],
			    'EPSG:4326',
			    'EPSG:3857'
			  ),
			  element: $('<span class="glyphicon glyphicon-map-marker"><div style="display: none;">' + point.loc_name + '<br/>Extracted from: ' + point.file + '</div></span>')
			  					.css({'color':point.color})
			  					.mouseover(function() {
			  						$(this).children().show();	
			  					})
			  					.mouseout(function(){
			  						$(this).children().hide()
			  					})[0],
			  file: point.file
			});
		map.addOverlay(overlay);
		// KEEP ON APPENDING POINTS
		if( !dataPointsAll[point.file]){
			dataPointsAll[point.file] = [];
		}
		dataPointsAll[point.file].push(overlay)
	}

}

var deletePoints = function(dataPoints) {
	if (!dataPoints || !dataPoints.length || dataPoints.length == 0) {
		return;
	}
	
	for(var i in dataPoints){
		map.removeOverlay(dataPoints[i]);
	}
}


var paintDataFromAPI = function(data, docName) {
	data = [{'loc_name': 'Informationcenter', 'position': {'y': '29.98663', 'x': '31.43867'}}, {'loc_name': 'NewYork', 'position': {'y': '53.07897', 'x': '-0.14008'}}, {'loc_name': 'Ca', 'position': {'y': '-7.0877', 'x': '109.2894'}}, {'loc_name': 'Nasa', 'position': {'y': '35.35611', 'x': '129.33861'}}, {'loc_name': 'California', 'position': {'y': '-29.8804', 'x': '-51.3193'}}]

	for ( var i in data) {
		data[i].file = docName;
		data[i].color = colorArr[colorIndex];
	}
	colorIndex++;
	if (colorIndex >= colorArr.length) {
		colorIndex = 0;
	}
	
	drawPoints(data);
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
var getStatus = function(res, file) {
	// TODO: ALL API's should return json in future
	var progressTemplateCloned = progressTemplate.cloneNode();
	progressTemplateCloned.appendChild(progressTemplate.children[0].cloneNode());

	file.previewElement.appendChild(progressTemplateCloned);

	var displayArea = progressTemplateCloned.children[0];

	// AJAX 1
	callRESTApi('extract_text/' + res.file_name, 'GET', false, {}, function(data) {
		displayArea.textContent = data + '..';
	}).done(function(data) {
		setTimeout(function() {
			// AJAX 2
			callRESTApi('find_location/' + res.file_name, 'GET', false, {}, function(data) {
				displayArea.textContent = data + '..';

			}).done(function(data) {
				setTimeout(function() {
					// AJAX 3
					callRESTApi('find_latlon/' + res.file_name, 'GET', false, {}, function(data) {
						displayArea.textContent = data + '..';
					}).done(function(data) {
						// AJAX 4
						fetchAndDrawPoints(res, file, displayArea)
					});
				}, 1000);

			});
		}, 1000);

	});

}
/**
 * Fetches points for uploaded file and paint data
 */
var fetchAndDrawPoints = function(res, file, displayArea) {
	callRESTApi('return_points/' + res.file_name + '/uploaded_files', 'GET', false, {}, function(data) {
		data = eval(data);// REMOVE THIS ONCE API RETURNS JSON
		displayArea.textContent = '';

		var list = '<ol>';
		for ( var i in data) {
			list += '<li>' + data[i].loc_name + '</li>';
		}
		list += '</ol>'

		displayArea.appendChild(Dropzone.createElement(list));
		
		var fileLabels = $(file.previewElement).find('.glyphicon-minus');
		fileLabels = fileLabels.parent();
		fileLabels.append(
				Dropzone.createElement("<span class='glyphicon glyphicon-map-marker fill-bg' style='color: "+colorArr[colorIndex]+";'>"));
		
		paintDataFromAPI(data, file.name);
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

		url : '/',
		paramName : 'file',
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
		// APPEND CSRF_MIDDLEWARE_TOKEN_PARAM
		formData.append(CSRF_MIDDLEWARE_TOKEN_PARAM, getCsrfMiddlewareToken());
	});

	// Hide the total progress bar when nothing's uploading anymore
	myDropzone.on("queuecomplete", function(progress) {
		document.querySelector("#total-progress").style.opacity = "0";
	});

	myDropzone.on("success", function(file, res) {
		callRESTApi("index_file/" + res.file_name, "GET", false, {}, function(d) {
			// Start looking for geo parse status and show pointers on map if found
			getStatus(res, file);
		});
	});
	
	myDropzone.on("removedfile", function(file) {
		deletePoints(dataPointsAll[file.name]);
	});
	// Dropzone end

});

var processUploadedFile = function(name) {
	var mockFile = {
		'name' : name,
		'size' : 12345
	};
	myDropzone.options.addedfile.call(myDropzone, mockFile);

	myDropzone.emit("complete", mockFile);
	myDropzone.emit("success", mockFile, { "file_name" : name });
	myDropzone.files.push(mockFile);
}

setTimeout(function() {
	callRESTApi("/list_of_uploaded_files", 'GET', 'true', null, function(d) {
		d = eval(d);
		for ( var i in d) {
			processUploadedFile(d[i]);
		}
	});
}, 1000);

var collapseFile = function(ele){
	//get element which hold location data
	var t1 = $(ele).parent().parent().parent().siblings()[2];
	$(t1).toggle();
	$(ele).toggleClass("glyphicon-minus"). toggleClass("glyphicon-plus");
}

//Save Index functions below
$(function() {
	$("#saveIndex").bind("click", function() {
		var domain = $("#indexDomain");
		var index = $("#indexPath");
		var button = $("#saveIndex");
		var error = false;
		domain.parent().removeClass("has-error");
		index.parent().removeClass("has-error");

		error = markEmtyError(domain);
		error = markEmtyError(index) || error;

		if (error) {
			return;
		}

		// add "/" in index if not present already
		if (index.val().lastIndexOf("/") + 1 != index.val().length) {
			index.val(index.val() + "/");
		}

		toggleSpinner(button, true);
		callRESTApi("/query_crawled_index/" + index.val() + domain.val(), 'GET', 'true', null, function(d) {
			toggleSpinner(button, false);
			fillDomain();
			alert("Successfully added Index");
		}, function(d) {
			toggleSpinner(button, false);
		});

	})

})
/**
 * Toggle active class and set disabled = bool
 */
var toggleSpinner = function(ele, bool) {
	ele.toggleClass('active');
	ele.prop("disabled", bool);

}

var markEmtyError = function (inputEle){
	if (!inputEle.val() || inputEle.val().toString().trim() == "") {
		inputEle.parent().addClass("has-error");
		return true;
	}
	return false;
}

var listOfDomains;
var fillDomain = function(){
	callRESTApi("/list_of_domains/", 'GET', 'true', null, function(d) {
		listOfDomains = eval(d)[0];
		if(!listOfDomains || $.isEmptyObject(listOfDomains) ){
			$("#savedDomain").parent().parent().hide();
		}else{
			$("#savedDomain").parent().parent().show();
		}
		var domainsList = $.map(listOfDomains, function(element,index) {return "<option>"+index+"</option>"});
		
		$("#savedDomain").html(domainsList);
		
		fillURL();
		
	});	
}
var fillURL = function() {
	var selectedIndexes = listOfDomains[$("#savedDomain").val()];
	
	$("#savedIndexes").html("");
	for ( var i in selectedIndexes) {
		$("#savedIndexes").append("<option>" + selectedIndexes[i] + "</option>");
	}
}

$(function() {
	fillDomain();
	$("#savedDomain").bind("change",fillURL);
	$("#viewIndex").bind("click", function() {
		var indexDisp = $("#savedIndexes").val();
		var domainDisp = $("#savedDomain").val();
		
		callRESTApi("/return_points/" + indexDisp + "/" + domainDisp, 'GET', 'true', null, function(d) {
			d = eval(d);
			$("#resultsIndex").append("<li>"+ d.length + " found in " + domainDisp + " - " + indexDisp + "</li>");
			paintDataFromAPI(d, domainDisp + " - " + indexDisp);
		});
	})
}) 
