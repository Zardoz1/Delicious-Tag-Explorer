module("Module 1")

test("a basic test example", function() {
	ok(true, "test 1 works");
	var value = "hello";
	equals("hello", value, "Equals Test")
});
