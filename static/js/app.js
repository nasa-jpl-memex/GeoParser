
	$(function() {
		'use strict';

		/*
		 * The data schema used in this example is as follows:
		 * {
		 *   color:    string -- a css color name
		 *   hex:      string -- a 24bit hex value
		 *   position: object -- a correlated gaussian R.V. in R^2
		 *   exp:      number -- a random value ~ exp(0.1)
		 *   unif:     number -- a random uniform value in [0,1]
		 *   fruits:   string -- a random fruit
		 * }
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

		$.ajax({
			dataType : 'json',
			url : 'static/json/sample_data.json',
			success : function(data) {
				console.log("ajax succ");
				spec.data = data;
				$('#map').geojsMap(spec);
			},
			error : function(e){
				console.log("Eroor.." + e);
			}
		});
	});