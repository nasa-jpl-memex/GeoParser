//Below class works together with khooshe.py to draw density bubbles on OL map
var khooshe = {
	/**
	 * OL map instance as provided during initialization
	 */
	_map : {},
	init : function(map) {
		this._map = map
	},
	/**
	 * Dictionary holding layer extents
	 */
	_dict : {},
	/**
	 * Defaults defined below<br/> They will support only one khooshe instance
	 */
	_default_color : 'red',
	_default_base_dir : 'static/tiles/',
	/**
	 * This variable holds Khooshe layer for all available instance.
	 */
	_layerKhooshe : {},
	_log: function(str){
		var DEBUG = false;
		if(DEBUG){
			console.log(str)
		}
	},

	/**
	 * delete ol.layer.Vector storing Khooshe bubbles
	 */
	deleteLayers : function(baseDir) {
		var khooshe = this
		var layers = khooshe._layerKhooshe[baseDir]
		khooshe._layerKhooshe[baseDir] = []
		
		if (!layers || !layers.length || layers.length == 0) {
			return;
		}

		for ( var i in layers) {
			khooshe._map.removeLayer(layers[i]);
		}
	},

	/**
	 * Returns current extent in -lon,-lat,lon,lat format
	 */
	_getCurrentExtent : function() {
		khooshe = this
		var currentExtent = khooshe._map.getView().calculateExtent(khooshe._map.getSize());
		currentExtent = ol.proj.transformExtent(currentExtent, 'EPSG:3857', 'EPSG:4326');
		return currentExtent
	},

	/**
	 * Adjust size array within limits of min and max size
	 */
	_adjust : function(dataPoints) {
		//console.log(dataPoints.map(function(point) {return point.label;}))
		// define max and min bubble size
		var minSize = 4
		var maxSize = 50
		var maxMinDelta = maxSize - minSize
		// get maximum sized point
		maxIpSize = Math.max.apply(Math, dataPoints.map(function(point) {
			return parseFloat(point.label);
		}))
		// adjust data points wrt max maxIpSize.
		if (maxIpSize > maxMinDelta) {
			for ( var i in dataPoints) {
				dataPoints[i].label = minSize + (maxMinDelta * (dataPoints[i].label / maxIpSize));
			}
		} else {
			for ( var i in dataPoints) {
				dataPoints[i].label = minSize + parseFloat(dataPoints[i].label);
			}
		}
		return dataPoints
	},

	/**
	 * Given khooshe points plots bubbles on a OL map
	 */
	_drawPoints : function(dataPoints, layer, color) {
		khooshe = this
		if (!dataPoints.length || dataPoints.length == 0) {
			return;
		}

		var icon_feature = [];
		// clear p from lowest level of points
		for ( var i in dataPoints) {
			if(dataPoints[i].label == 'p'){
				dataPoints[i].label = 1 
				//seed is the final location in khooshe bubble
				dataPoints[i].seed = true
			}
		}
		dataPoints = khooshe._adjust(dataPoints)

		for ( var i in dataPoints) {
			var point = dataPoints[i];
			var iconFeature = new ol.Feature({
				geometry : new ol.geom.Point([ parseFloat(point.longitude), parseFloat(point.latitude) ]).transform(
						'EPSG:4326', 'EPSG:3857'),
				name : i
			});
			var ccl = new ol.style.Circle({
				// radius : isNaN(point.label) ? 5 : point.label,
				radius : point.label,
				fill : new ol.style.Fill({
					color : color
				}),
				stroke : new ol.style.Stroke({
					color : point.seed?'white':'silver',
					width : point.seed? 2:1
				})
			})
			ccl.setOpacity(0.5)
			var iconStyle = new ol.style.Style({
				image : ccl

			});

			iconFeature.setStyle(iconStyle);
			icon_feature.push(iconFeature);
		}

		var vectorSource = new ol.source.Vector({
			features : icon_feature
		});

		var vectorLayer = new ol.layer.Vector({
			source : vectorSource
		});

		khooshe._map.addLayer(vectorLayer);

		if (!khooshe._layerKhooshe[layer]) {
			khooshe._layerKhooshe[layer] = [];
		}
		khooshe._layerKhooshe[layer].push(vectorLayer)
	},

	_drawKhoosheLayer : function(folder, fileArr, baseDir, color) {
		var csvObjArr = []
		for ( var i in fileArr) {
			$.ajax({
				type : "GET",
				url : baseDir + folder + "/" + fileArr[i] + ".csv",
				dataType : "text",
				async : false,
				success : function(data) {
					csvObjArr = csvObjArr.concat($.csv.toObjects(data));
				}
			});
		}
		khooshe._drawPoints(csvObjArr, baseDir, color)
	},

	initKhoosheLayer : function(baseDir, color) {
		var khooshe = this
		if (!baseDir) {
			baseDir = khooshe._default_base_dir
		}

		if (!color) {
			color = khooshe._default_color
		}
		if(!khooshe._layerKhooshe[baseDir]){
			khooshe._drawKhoosheLayer(0, [ 0 ], baseDir, color)
		}
		var dictOfLayer = null
		$.ajax({
			type : "GET",
			url : baseDir + "dict.csv",
			dataType : "text",
			success : function(data) {
				khooshe._dict[baseDir] = $.csv.toObjects(data)
				dictOfLayer = khooshe._dict[baseDir]
			}
		});

		/**
		 * Checks if map is changed and displays highest level bubbles available for
		 * current display
		 */
		khooshe._map.on('moveend', function() {
			var visible_layers = {}
			var min_layer = 999999
			// current extent in lat and long format
			var currentExtent = khooshe._getCurrentExtent()

			// use dictionary to get available extents
			for ( var i in dictOfLayer) {
				extent = dictOfLayer[i].extent.split(',')
				extent = extent.map(function(item) {
					return parseFloat(item);
				})
				if (ol.extent.containsExtent(currentExtent, extent)) {
					khooshe._log('Found visible: ' + dictOfLayer[i].folder + ' / ' + dictOfLayer[i].file)
					khooshe._log('currentExtent, visibleLayerExtent: ' + currentExtent.toString() + ' / ' + extent.toString())
					// update min layer if possible
					if (dictOfLayer[i].folder < min_layer) {
						min_layer = dictOfLayer[i].folder
					}
				}
				if (ol.extent.intersects(currentExtent, extent)) {
					// append in visible layer array
					if (!visible_layers[dictOfLayer[i].folder]) {
						visible_layers[dictOfLayer[i].folder] = []
					}
					visible_layers[dictOfLayer[i].folder].push(dictOfLayer[i].file)
				}
			}
			// remove existing layers
			if (visible_layers[min_layer] && visible_layers[min_layer].length != 0) {
				khooshe._log("Displaying layer: " + min_layer) 
				khooshe.deleteLayers(baseDir)
				
			}else{
				khooshe._log("No visible layers")
			}
			// display new layer
			khooshe._drawKhoosheLayer(min_layer, visible_layers[min_layer], baseDir, color)
			visible_layers = {}
		});
	}

}