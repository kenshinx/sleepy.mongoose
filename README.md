原来的sleep.mongoose实现了一个单线程的http server，但是无法配合nginx，apache等web服务器在线上部署。

我在原来基础上增加了wsgi的支持，可以通过python wsgi.py来调试。

另外通过nginx+uwsgi部署也没有问题,Quick Start：

uwsgi --http :9090 --wsgi-file  mongo_uwsgi.py

更多使用方法请看项目原来的wiki
 [the wiki](http://wiki.github.com/kchodorow/sleepy.mongoose/) 
