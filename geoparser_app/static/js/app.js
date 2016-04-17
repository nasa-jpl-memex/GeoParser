'use strict';

var SUB_DOMAIN = "/"
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

	$("#collapseIcon").bind('click', function() {
		$('#useInputDiv').toggle();
		$("#collapseIcon").toggleClass("glyphicon-minus").toggleClass("glyphicon-plus");
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
var colorArr = [ 'red', 'yellow', 'blue', 'green', 'orange', 'white', 'grey' ];
var map = null;
var view = null;
/**
 * layerToIndexMap has key as base directory for khooshe tiles and value as actual solr index.
 * {'static/tiles/test1/':'http://localhost:8983/solr/test'}
 */
var layerToIndexMap = {}
var d3_data;
$(function() {
	var layer = new ol.layer.Tile(
			{
				source : new ol.source.XYZ(
						{
							url : 'http://{a-c}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
							attributions : [ new ol.Attribution(
									{
										html : [ '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>' ]
									}) ]
						})
			});

	view = new ol.View({
		center : ol.proj.transform([ -98.5, 39.76 ], 'EPSG:4326', 'EPSG:3857'),
		zoom : 2
	});

	map = new ol.Map({
		layers : [ layer ],
		target : 'map',
		view : view
	});

	var element = $('<span></span>')[0];

	var popup = new ol.Overlay({
		element : element,
		positioning : 'bottom-center',
		stopEvent : false
	});
	map.addOverlay(popup);

	//Below is disabled for now, need to enable it for files only
	// display popup on hover
	map.on('pointermove', function(evt) {
		var feature = map.forEachFeatureAtPixel(evt.pixel, function(feature, layer) {
			return feature;
		});
		if (feature) {
			// close any existing popovers
			$(element).popover('destroy');
			var popupData = $.csv.toArray(feature.get('popup_content'))
			var metadataFields = layerToIndexMap[feature.get('layer')].metadataFields
			
			var docLink = layerToIndexMap[feature.get('layer')].indexURL + "/select?q=id:%22" + eval(popupData[1])
					+ "%22&wt=json&indent=true"

			var popup_content = '';
            d3_data = {"name": eval(popupData[0]), "children": []};
            
            jQuery.ajax({
                url: docLink,
                data: '',
                beforeSend: function() {
                    $(element).popover({
                        trigger: 'manual',
                        'placement': 'top',
                        'html': true,
                        'content': function () {
                            if (popupData[1]) {
                                popup_content = "<p><a href='" + docLink + "' target = '_blank' style='word-wrap: break-word;'>"+docLink+"</a></p>";
                                popup_content += '<div class="progress"><div class="progress-bar progress-bar-striped active"role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"><span class="sr-only">Indeterminate</span></div></div>'
                                return popup_content;
                            } else {
                                return ""
                            }
                        },
                        container: $(element), // This makes popover part of element
                        'title': eval(popupData[0])
                    });
                    $(element).popover('show');
                },
                success:  function(res) {
//                    console.log(JSON.stringify(res, null, 2));
                        $(element).popover('destroy');
                        $(element).popover({
                        trigger: 'manual',
                        'placement': 'top',
                        'html': true,
                        'content': function () {
                            if (popupData[1]) {
                                popup_content = ''
                                if (res.hasOwnProperty('response')) {
                                    if (res.response.hasOwnProperty('docs')) {
                                        var doc = res.response.docs[0];
                                        var count = 0;
                                        for (var key in doc) {
                                            if (doc.hasOwnProperty(key)) {
                                                count+=1;
                                                var value = doc[key];
                                                // Ellipsing the string if its too long
                                                if(value.toString().length > 145) {
                                                    value = value.toString().substring(0,144)+"...";
                                                }
                                                var child = {"name": key, "children": [{"name": value,"size": 1}]};
                                                d3_data['children'].push(child);
                                                // Max num of default keys to be shown in the popup
                                                if(count <= 4){
                                                    popup_content += "<p>" + key + ": " + value + "</p>";
                                                }
                                            }
                                        }
//                                        popup_content += "<p><a href='" + docLink + "' target = '_blank' style='word-wrap: break-word;'>More...</a></p>";
                                        popup_content += "<p><a class='more' href='' data-toggle='modal' data-target='#moreModal' style='word-wrap: break-word;'>More...</a></p>";
                                    }
                                }
                                return popup_content;
                            } else {
                                return ""
                            }
                        },
                        container: $(element), // This makes popover part of element
                        'title': eval(popupData[0])
                    })
                    $(element).popover('show');
                },
                error: function(xhr, textStatus, errorThrown){
                    $(element).popover({
                        trigger: 'manual',
                        'placement': 'top',
                        'html': true,
                        'content': function () {
                            if (popupData[1]) {
                                popup_content = "<p><a href='" + docLink + "' target = '_blank' style='word-wrap: break-word;'>"+docLink+"</a></p>";
                                return popup_content;
                            } else {
                                return ""
                            }
                        },
                        container: $(element), // This makes popover part of element
                        'title': eval(popupData[0])
                    })
                    $(element).popover('show');
                },
                dataType: 'jsonp',
                jsonp: 'json.wrf'
            });
            
			popup.setPosition(evt.coordinate);
            $(document).click(function (e) {
                if ($(e.target).is('.more')) {
                    $(element).popover('destroy');
                    $('#modal-title').text(eval(popupData[0]));
                    $('#d3-iframe').attr("src","static/html/collapsible_indented_tree.html");
                }
            });
		} else {

			// On mouse leave close popover after 3 seconds
			setTimeout(function() {
        if (!$(".popover:hover").length) { 
       // This check ensure we close popover only if mouse is not hovered over
				// .popover
        	$(element).popover('destroy');
        }
			}, 3000)
		
		}
	});
	// initialize khooshe
	khooshe.init(map, false)

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

// checks is ends with slash
var notEndsWithSlash = function(string) {
	return string.lastIndexOf("/") + 1 != string.length
}

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

	var icon_feature = [];
	for ( var i in dataPoints) {
		var point = dataPoints[i];
		var iconFeature = new ol.Feature({
			geometry : new ol.geom.Point([ parseFloat(point.position.y), parseFloat(point.position.x) ]).transform(
					'EPSG:4326', 'EPSG:3857'),
			name : point.loc_name + '<br/>Extracted from: ' + point.file
		});

		var iconStyle = new ol.style.Style({
			image : new ol.style.Circle({
				radius : 6,
				fill : new ol.style.Fill({
					color : point.color
				}),
				stroke : new ol.style.Stroke({
					color : 'silver',
					width : 1
				})
			})
		});

		iconFeature.setStyle(iconStyle);
		icon_feature.push(iconFeature)
	}

	var maxFeatureCount;
	function calculateClusterInfo(resolution) {
		maxFeatureCount = 0;
		var features = vectorLayer.getSource().getFeatures();
		var feature, radius;
		for (var i = features.length - 1; i >= 0; --i) {
			feature = features[i];
			var originalFeatures = feature.get('features');
			var extent = ol.extent.createEmpty();
			for (var j = 0, jj = originalFeatures.length; j < jj; ++j) {
				ol.extent.extend(extent, originalFeatures[j].getGeometry().getExtent());
			}
			maxFeatureCount = Math.max(maxFeatureCount, jj);
		}
		return maxFeatureCount
	}
	var styleCache = {};
	var s = function(feature, resolution) {
		var max = calculateClusterInfo(resolution);
		console.log(max);
		var size = feature.get('features').length;
		console.log(size);
		console.log("---");
		var style = styleCache[size];
		if (!style) {
			style = [ new ol.style.Style({
				image : new ol.style.Circle({
					radius : (size / max) + 10,
					stroke : new ol.style.Stroke({
						color : '#fff'
					}),
					fill : new ol.style.Fill({
						color : '#3399CC'
					})
				}),
				text : new ol.style.Text({
					text : size.toString(),
					fill : new ol.style.Fill({
						color : '#fff'
					})
				})
			}) ];
			styleCache[size] = style;
		}
		return style;
	}

	var vectorSource = new ol.source.Vector({
		features : icon_feature
	});

	var vectorLayer = new ol.layer.Vector({
		source : new ol.source.Cluster({
			distance : 40,
			source : vectorSource
		}),
		style : s
	});

	map.addLayer(vectorLayer);

	// KEEP ON APPENDING POINTS
	if (!dataPointsAll[point.file]) {
		dataPointsAll[point.file] = [];
	}
	vectorLayer.color = point.color
	dataPointsAll[point.file].push(vectorLayer)

}

var deletePoints = function(dataPoints) {
	if (!dataPoints || !dataPoints.length || dataPoints.length == 0) {
		return;
	}

	for ( var i in dataPoints) {
		map.removeLayer(dataPoints[i]);
	}
}

var getNewColor = function() {
	var color = colorArr[colorIndex];
	colorIndex++;
	if (colorIndex >= colorArr.length) {
		colorIndex = 0;
	}
	return color;
}

var paintDataFromKhooshe = function (khoosheData, indexURL) {
		var khoosheBaseDir = khoosheData.khooshe_tile
		var metadataFields = $.csv.toArray(khoosheData.popup_fields)
	
    if (notEndsWithSlash(khoosheBaseDir)) {
        khoosheBaseDir = khoosheBaseDir + "/"
    }
    khoosheBaseDir = SUB_DOMAIN + khoosheBaseDir

    layerToIndexMap[khoosheBaseDir] = {'indexURL' : indexURL, 'metadataFields' : metadataFields}

    khooshe.initKhoosheLayer(khoosheBaseDir, getNewColor())

}

var paintDataFromAPI = function(data, docName) {
	var color;
	if (dataPointsAll[docName] && dataPointsAll[docName][0].color) {
		color = dataPointsAll[docName][0].color
	} else {
		color = getNewColor()
	}
	for ( var i in data) {
		data[i].file = docName;
		data[i].color = color;
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
	callRESTApi(SUB_DOMAIN + 'extract_text/' + res.file_name, 'GET', false, {}, function(data) {
		displayArea.textContent = data + '..';
	}).done(function(data) {
		setTimeout(function() {
			// AJAX 2
			callRESTApi(SUB_DOMAIN + 'find_location/' + res.file_name, 'GET', false, {}, function(data) {
				displayArea.textContent = data + '..';

			}).done(function(data) {
				setTimeout(function() {
					// AJAX 3
					callRESTApi(SUB_DOMAIN + 'find_latlon/' + res.file_name, 'GET', false, {}, function(data) {
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
	callRESTApi(SUB_DOMAIN + 'return_points/' + res.file_name + '/uploaded_files', 'GET', false, {}, function(d) {
		d = eval(d)[0];// REMOVE THIS ONCE API RETURNS JSON
		var data = d.points
		displayArea.textContent = '';

		var list = '<ol>';
		for ( var i in data) {
			list += '<li>' + data[i].loc_name + '</li>';
		}
		list += '</ol>'

		displayArea.appendChild(Dropzone.createElement(list));

		var fileLabels = $(file.previewElement).find('.glyphicon-minus');
		fileLabels = fileLabels.parent();
		fileLabels.append(Dropzone.createElement("<span class='glyphicon glyphicon-map-marker fill-bg' style='color: "
				+ colorArr[colorIndex] + ";'>"));

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

		url : SUB_DOMAIN ,
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
		callRESTApi(SUB_DOMAIN + "index_file/" + res.file_name, "GET", false, {}, function(d) {
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
	myDropzone.emit("success", mockFile, {
		"file_name" : name
	});
	myDropzone.files.push(mockFile);
}

setTimeout(function() {
	callRESTApi(SUB_DOMAIN + "list_of_uploaded_files", 'GET', 'true', null, function(d) {
		d = eval(d);
		for ( var i in d) {
			processUploadedFile(d[i]);
		}
	});
}, 1000);

var collapseFile = function(ele) {
	// get element which hold location data
	var t1 = $(ele).parent().parent().parent().siblings()[2];
	$(t1).toggle();
	$(ele).toggleClass("glyphicon-minus").toggleClass("glyphicon-plus");
}

// Save Index functions below
var timer;
$(function() {
	$("#saveIndex").bind(
			"click",
			function() {
				var domain = $("#indexDomain");
				var index = $("#indexPath");
				var username = $("#indexUsername");
				var passwd = $("#indexPasswd");
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
				if (notEndsWithSlash(index.val())) {
					index.val(index.val() + "/");
				}

				toggleSpinner(button, true);
				callRESTApi(SUB_DOMAIN + "query_crawled_index/" + index.val() + domain.val() + "/" + username.val() + "/"
						+ passwd.val(), 'GET', 'true', null, function(d) {
					toggleSpinner(button, false);
					fillDomain();
					alert("Successfully Geotagged Index");
				}, function(d) {
					alert("Error while GeoTagging Index: " + d.status + " - " + d.responseText);
					toggleSpinner(button, false);
				});

				timer = setInterval(function() {
					callRESTApi(SUB_DOMAIN + "return_points_khooshe/" + index.val() + domain.val(), 'GET', 'true', null,
							function(d) {
								d = eval(d)[0];
								var progress = 0
								if (d.total_docs && d.rows_processed) {
									progress = (d.rows_processed / d.total_docs) * 100
								}
								var ele = $("#indexProgress")
								ele.show();
								ele.find(".progress-bar").css('width', progress + '%').attr('aria-valuenow', progress).html(
										d.rows_processed + ' / ' + d.total_docs);

								paintDataFromKhooshe(d, index.val());
								if (d.total_docs == d.rows_processed) {
									clearInterval(timer);
								}
							});
				}, 10000)
			})

})

/**
 * Toggle active class and set disabled = bool
 */
var toggleSpinner = function(ele, bool) {
	ele.toggleClass('active');
	ele.prop("disabled", bool);

}
var hideOtherChild = function(ele) {
	// get element which hold location data
	var t1 = $(ele).parent().siblings()[0];
	var t2 = $(ele).parent().siblings()[1];
	$(t1).toggle();
	$(t2).toggle();
	$(ele).toggleClass("glyphicon-minus").toggleClass("glyphicon-plus");
}

var markEmtyError = function(inputEle) {
	if (!inputEle.val() || inputEle.val().toString().trim() == "") {
		inputEle.parent().addClass("has-error");
		return true;
	}
	return false;
}

var listOfDomains;
var fillDomain = function() {
	callRESTApi(SUB_DOMAIN + "list_of_domains/", 'GET', 'true', null, function(d) {
		listOfDomains = eval(d)[0];
		if (!listOfDomains || $.isEmptyObject(listOfDomains)) {
			$("#savedDomain").parent().parent().hide();
		} else {
			$("#savedDomain").parent().parent().show();
		}
		var domainsList = $.map(listOfDomains, function(element, index) {
			return "<option>" + index + "</option>"
		});

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
	$("#savedDomain").bind("change", fillURL);
	var viewindexButton = $("#viewIndex")
	viewindexButton.bind("click", function() {
		var indexDisp = $("#savedIndexes").val();
		var domainDisp = $("#savedDomain").val();
		toggleSpinner(viewindexButton, true);

		callRESTApi(SUB_DOMAIN + "return_points_khooshe/" + indexDisp + "/" + domainDisp, 'GET', 'true', null, function(d) {
			try {
				d = eval(d)[0];
				$("#resultsIndex").append(
						"<li>" + d.points_count + " points found in domain-" + domainDisp + " - " + indexDisp + " - " + d.rows_processed + ' / '
								+ d.total_docs + "</li>");
				
                paintDataFromKhooshe(d, indexDisp);
			} catch (e) {
				console.error(e.stack)
				alert("Error while displaying co-ordinates: " + e)
			}
			toggleSpinner(viewindexButton, false);
		}, function(d) {
			alert("Error while retrieving co-ordinates: " + d.status + " - " + d.responseText);
			toggleSpinner(viewindexButton, false);
		});
	})
})
