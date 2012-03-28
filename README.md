为sleepy.mongoose增加了wsgi的支持，试过用nginx+uwsgi来部署没有问题。

nginx+uwsgi快速部署方法：
uwsgi --http :9090 --wsgi-file  mongo_uwsgi.py

更多文档还是看
 [the wiki](http://wiki.github.com/kchodorow/sleepy.mongoose/) for documentation.
