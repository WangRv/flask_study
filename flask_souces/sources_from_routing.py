# encoding:UTF-8
import werkzeug.routing as rout

#
test_url = "/www.baidu.com/abc/<int(12):year>"
s = rout._fast_url_quote("abcdefgh".encode("utf8"))
print(s)
