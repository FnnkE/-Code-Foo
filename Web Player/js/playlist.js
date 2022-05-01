callData(0, false)

var card1 = document.getElementById("card1")
var card2 = document.getElementById("card2");
var card3 = document.getElementById("card3");
var card4 = document.getElementById("card4");
var card5 = document.getElementById("card5");

card1.addEventListener("click", function() {
    callData(1, true)
}, false);
card2.addEventListener("click", function() {
    callData(2, true)
}, false);
card3.addEventListener("click", function() {
    callData(3, true)
}, false);
card4.addEventListener("click", function() {
    callData(4, true)
}, false);
card5.addEventListener("click", function() {
    callData(5, true)
}, false);