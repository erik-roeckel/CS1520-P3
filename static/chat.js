
var timeoutID;
var timeout = 1000;
var lastMessageDate = 0;
var authorUsername = "";

function setup(){
    document.getElementById("postMessage").addEventListener("click", makePost, true);
    timeoutID = window.setTimeout(poller, timeout);
}

function getAuthor(){
    var httpRequest = new XMLHttpRequest();
	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
    }
	httpRequest.onreadystatechange = function() { handleAuthor(httpRequest) };
	httpRequest.open("GET", "/author");
    httpRequest.send();
}

function handleAuthor(httpRequest){
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
            var username = JSON.parse(httpRequest.responseText);
            authorUsername = username.author;
            timeoutID = window.setTimeout(poller, timeout);
        }
        else{
            alert("There was a problem with the poll request");
        } 
    }
}

function makePost(){
    var httpRequest = new XMLHttpRequest();

    if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
    }
    
    var messageText = document.getElementById("newMessage").value
    httpRequest.onreadystatechange = function() { handlePost(httpRequest, messageText) };

    httpRequest.open("POST", "/add_message");

    httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

    var data;
    data = "text=" + messageText;

    httpRequest.send(data);
}

function handlePost(httpRequest, messageText) {
    if (httpRequest.readyState === XMLHttpRequest.DONE){
        if(httpRequest.status === 200){
            getAuthor();
            lastMessageDate = 0;
            dict = { };
            dict.author = authorUsername;
            dict.chat = null;
            dict.text = messageText;
            dict.date = Date.now();
            addMessage(dict);
            clearInput();
        }
        else{
            alert("There was a problem with the post request");
        }
    }
}

function poller() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}
	httpRequest.onreadystatechange = function() { handlePoll(httpRequest) };
	httpRequest.open("GET", "/messages?date="+lastMessageDate);
    httpRequest.send();
}

function handlePoll(httpRequest) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
            var messages = JSON.parse(httpRequest.responseText);
            for (var i = 0; i < messages.length; i++) {
                addMessage(JSON.parse(messages[i]));
            }
            timeoutID = window.setTimeout(poller, timeout);
        }
        else{
            alert("There was a problem with the poll request");
        } 
    }
}

function clearInput() {
	document.getElementById("newMessage").value = "";
}

function addMessage(messageString) {
	var messageListRef = document.getElementById("messageList");
    var newMessage = document.createElement('li');
    var content = "<p><strong>Message: </strong>" + messageString.text + "</p>";
    var author = "<p><strong>From: </strong>" + authorUsername + "</p>";
    var date = "<p><strong>Date posted: </strong>" + Date(messageString.date.toDateString).toString() + "</p>";
    newMessage.innerHTML = content + author + date;
    lastMessageDate = messageString.date;
    messageListRef.appendChild(newMessage);
}

window.addEventListener("load", setup, true);
