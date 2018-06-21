<h2>Basic IP Control Query Using SOAP API in Python</h2>

<p>This solves a problem found here:</p>

https://stackoverflow.com/questions/29433648/soap-suds-ipcontrol-exportdevice/45201107#45201107

One problem is that the session ID you need to extract is missing from client.last_received(). I had to use some MessagePlugin code I found elsewhere to get the raw XML, then used a regex to extract the session ID. Next, I used much of your code to build the new SOAP header, but used 'sessionID' instead of 'SessionId'. Once I had all those pieces in place, it worked. Here is some basic query code that initializes and executes exportChildBlock().
