````
sudo apt-get install mecab mecab-ipadic-utf8 libmecab-dev
````

* it requires python 2.x, cause mecab-python bindings does not officially support python 3.x yet.
* also, need mecab-python v.0.993, instead of later release like v.0.996.
    * with later release, it seems we get gcc compile error at pip install.

````
pyenv install 2.7.8
pyenv virtualenv 2.7.8 kubota-news-2.7.8
pip install http://sourceforge.net/projects/pychecker/files/pychecker/0.8.19/pychecker-0.8.19.tar.gz/download
pip install https://mecab.googlecode.com/files/mecab-python-0.993.tar.gz
pip install -r requirements.txt
````

