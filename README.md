# jinja2gv

Small tools for create UML diagrams from jinja2 templates. 
jinja2gv output gv file to stdout. For visualization can be used [Graphviz](http://www.graphviz.org/)

### Example of use

python jinja2gv.py modulename:app.jinja2_env | dot -T png  > scr.png

![diagram](https://raw.githubusercontent.com/maxim-s-barabash/jinja2gv/master/scr.png)
