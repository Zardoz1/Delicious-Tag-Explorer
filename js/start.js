/*
 * Basic js for controlling the start html page and its form and control
 *	Version 2. 03May2011.
*/


/*
 * Basic validation logic for the starter form.
 *   
*/

$(document).ready(function(){
	
	$('#starter').submit(function() {
		
		var user = $('#starter input').val();
		if (user && user.length > 1) {
			$('#starter').hide();
			$('#loading').show();
		}
		else {
			$('#comments').show();
		}
		return true;
	});
	
	$('#starter input').focus(function() {
		
		$('#comments').hide();
	});
});
// eof
