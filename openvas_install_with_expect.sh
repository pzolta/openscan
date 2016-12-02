#!/bin/expect
set timeout 15

spawn apt-get -Y install openvas

expect {
	timeout { send "\n\r" }
}
close