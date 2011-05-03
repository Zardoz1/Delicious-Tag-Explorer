describe("Start Page", function() {
	
	// start up state..
	it("should start with name field empty", function() {

		expect($('#Starter :input[name="getUserName"]')).toExist();
		expect($('#Starter :input[name="getUserName"]')).toBeEmpty();
		expect($('#Starter :input[name="getUserName"]')).not.toBeDisabled();
		expect($('#Starter :submit')).toExist();
		expect($('#Starter :submit')).toBeDisabled();
		expect($('#Starter #tags')).toExist();
		expect($('#Starter #tags')).toBeDisabled();
	});	
});
