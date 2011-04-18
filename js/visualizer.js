var labelType, useGradients, nativeTextSupport, animate;

(function() {
  var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport 
        && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
  //I'm setting this based on the fact that ExCanvas provides text support for IE
  //and that as of today iPhone/iPad current text support is lame
  labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
  nativeTextSupport = labelType == 'Native';
  useGradients = nativeCanvasSupport;
  animate = !(iStuff || !nativeCanvasSupport);
})();

var Log = {
  elem: false,
  write: function(text){
    if (!this.elem) 
      this.elem = document.getElementById('log');
	if (this.elem) {
		this.elem.innerHTML = text;
		this.elem.style.left = (500 - this.elem.offsetWidth / 2) + 'px';
	}
  }
};


function init(){
  // init ForceDirected
  var fd = new $jit.ForceDirected({
    //id of the visualization container
    injectInto: 'infovis',
	width: window.innerWidth,
	height: window.innerHeight,
    //Enable zooming and panning
    //by scrolling and DnD
    Navigation: {
      enable: true,
      //Enable panning events only if we're dragging the empty
      //canvas (and not a node).
      panning: 'avoid nodes',
      zooming: 10 //zoom speed. higher is more sensible
    },
    // Change node and edge styles such as
    // color and width.
    // These properties are also set per node
    // with dollar prefixed data-properties in the
    // JSON structure.
    Node: {
      overridable: false,
	  type: 'rectangle',
	  color: '#DEAB1F',
	  autoHeight: true,
	  autoWidth: true//,
	  //alpha: 0.8
    },
    Edge: {
      overridable: true,
      color: '#23A4FF',
      lineWidth: 0.4
    },
    //Native canvas text styling
    Label: {
	  overridable: false,  
      type: 'Native', //Native or HTML
	  //type: 'HTML',
      size: 12,
      style: 'bold',
	  color: '#000000',
	  textAlign: 'center',
	  textBaseline: 'bottom'
    },
    //Add Tips
    Tips: {
      enable: true,
      onShow: function(tip, node) {
        //count connections
        var count = 0;
		var links = "";
        node.eachAdjacency(function(adj) { 
				count++;
				links = links + "<li><b>'" + adj.nodeTo.id + "'</b> " + adj.data.count 
							  + (adj.data.count == 1 ? " time" : " times") + ".</li>" 
		});
        //display node info in tooltip
        tip.innerHTML = "<div class=\"tip-title\"><p>Tag: '" + node.name 
			+ "'. Used " + node.data.count + (node.data.count == 1 ? " time." : " times.") + "</p></div>"
	  	  		+ "<div class=\"tip-text\"><p><em>Appears with " + count + (count == 1 ? " tag:" : " tags:") + "</em></p>"
		  		+ "<ul>" + links + "</ul></div>";
      }
    },
    // Add node events
    Events: {
      enable: true,
      //Change cursor style when hovering a node
      onMouseEnter: function() {
        fd.canvas.getElement().style.cursor = 'move';
      },
      onMouseLeave: function() {
        fd.canvas.getElement().style.cursor = '';
      },
      //Update node positions when dragged
      onDragMove: function(node, eventInfo, e) {
          var pos = eventInfo.getPos();
          node.pos.setc(pos.x, pos.y);
          fd.plot();
      },
      //Implement the same handler for touchscreens
      onTouchMove: function(node, eventInfo, e) {
        $jit.util.event.stop(e); //stop default touchmove event
        this.onDragMove(node, eventInfo, e);
      },
      //Add also a click handler to nodes
      onClick: function(node) {
        if(!node) return;
			
		url = "http://localhost:8080/tags/branch?parent=" + encodeURIComponent(node.name)
		window.location.replace(url)	
      }
    },
    //Number of iterations for the FD algorithm
    iterations: 200,
    //Edge length
    levelDistance: 130,
    // Add text to the labels. This method is only triggered
    // on label creation and only for DOM labels (not native canvas ones).
    onCreateLabel: function(domElement, node){
      domElement.innerHTML = '<p>Tag: "' + node.name + '"</p><p>Count: ' + node.data.count + '</p>';
      var style = domElement.style;
      style.fontSize = "0.8em";
      style.color = "#070707";
    },
    // Change node styles when DOM labels are placed
    // or moved.
    onPlaceLabel: function(domElement, node){
      var style = domElement.style;
      var left = parseInt(style.left);
      var top = parseInt(style.top);
      var w = domElement.offsetWidth;
	  var h = domElement.offsetHeight
      style.left = (left - w/2) + 'px';
      style.top = (top - h/2) + 'px';
    },
	onBeforePlotNode: function(node) {
		var pos = node.getPos('end')
	},
	onAfterPlotNode: function(node) {
		var pos = node.getPos('current')
	}
  });
  // load JSON data.
  fd.loadJSON(json);
  // compute positions incrementally and animate.
  fd.computeIncremental({
    iter: 40,
    property: 'end',
    onStep: function(perc){
      Log.write(perc + '% loaded...');
    },
    onComplete: function(){
      Log.write('done');
      fd.animate({
        modes: ['linear'],
        transition: $jit.Trans.Elastic.easeOut,
        duration: 2500
      });
    }
  });
  // end
}
