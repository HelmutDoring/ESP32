The ESP32-S3-Zero is a little bit of a problem. It doesn't have a toplevel board directory. Not even /pyboard/. I was able to use rshell to upload directories named 'bin' and 'lib', but it doesn't seem to like any other directory names I've tried.
People have raised the issue of boards with toplevel directories named '[]' with the author of rshell. He doesn't seem too interested in the problem.
