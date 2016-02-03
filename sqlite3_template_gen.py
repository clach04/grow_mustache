#!/usr/bin/env python
# -*- coding: ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
"""Mustache template generator for sqlite3"""

from cgi import escape
import os
import sqlite3
import sys

try:
    import cherrypy
except ImportError:
    try:
        import dietcherrypy as cherrypy
    except ImportError:
        cherrypy = None

from db2template import result_to_empty_template


class SqlRunnerHtml(object):
    def __init__(self, dbname=None):
        self.dbname = dbname

    def execute_sql(self, sql_str):
        db = sqlite3.connect(self.dbname)
        try:
            c = db.cursor()
            template = result_to_empty_template(c, sql_str)
            c.close()
            return template
        finally:
            db.close()

class WebHtml(object):
    def __init__(self, sql_tm_html):
        """sql_tm_html is an instance of SqlRunnerHtml
        """
        self.sql_tm_html = sql_tm_html
        #    <TEXTAREA NAME="sql_str" ROWS="10" COLS="60">%s</TEXTAREA> 
        # <TEXTAREA NAME="sql_str" ROWS="20" style="width:100%%;">%s</TEXTAREA> 
        # <TEXTAREA NAME="sql_str" style="width:100%%;height:100%%;">%s</TEXTAREA> 
        
        # http://www.openjs.com/scripts/events/keyboard_shortcuts
        ## also see http://jonathan.tang.name/files/js_keycode/test_keycode.html
        ## TODO form has head so does sql execute!
        ## TODO auto enter/focus to form.
        self._shortcut_js_file = 'shortcut.js'
        if not os.path.exists(self._shortcut_js_file):
            self._shortcut_js_file = os.path.join(os.path.dirname(__file__), self._shortcut_js_file)
        # TODO use a Mustache template
        self._form_html = """
<head>
<title>WebTm </title>

<style>
    pre {
        background-color: lightgrey;
        border: 1px solid #5096B9;
        padding: 10 10 10 10;
    }
</style>

<script src="shortcut.js" type="text/javascript"></script>

<script type="text/javascript">
function form_setfocus() {document.sqlform.sql_str.focus();}
function init() {

    shortcut.add("Ctrl+Enter",function() {
        document.forms[0].submit();;
    });
    
    form_setfocus(); /* FIXME this isn't working, probably need body tag with onload set... */

}
window.onload=init; /* or body onload.... */
</script>

</head>

<form action="index" method="GET" id="sqlform">
<br>
    Enter SQL (SELECT) and click the Execute button (or press Ctrl+Enter).<br>
<br><br> 
 
    SQL: <br>
    <TEXTAREA id="sql_str" NAME="sql_str" ROWS="20" style="width:100%%;">%s</TEXTAREA> 
    <br> 
 
    <input type="submit"  value="Execute SQL"/> 
</form> 
"""
    def shortcut_js(self):
        # MiniFied version of http://www.openjs.com/scripts/events/keyboard_shortcuts/
        # via Minify (JSMin)
        result = 'shortcut={\'all_shortcuts\':{},\'add\':function(shortcut_combination,callback,opt){var default_options={\'type\':\'keydown\',\'propagate\':false,\'disable_in_input\':false,\'target\':document,\'keycode\':false}\r\nif(!opt)opt=default_options;else{for(var dfo in default_options){if(typeof opt[dfo]==\'undefined\')opt[dfo]=default_options[dfo];}}\r\nvar ele=opt.target;if(typeof opt.target==\'string\')ele=document.getElementById(opt.target);var ths=this;shortcut_combination=shortcut_combination.toLowerCase();var func=function(e){e=e||window.event;if(opt[\'disable_in_input\']){var element;if(e.target)element=e.target;else if(e.srcElement)element=e.srcElement;if(element.nodeType==3)element=element.parentNode;if(element.tagName==\'INPUT\'||element.tagName==\'TEXTAREA\')return;}\r\nif(e.keyCode)code=e.keyCode;else if(e.which)code=e.which;var character=String.fromCharCode(code).toLowerCase();if(code==188)character=",";if(code==190)character=".";var keys=shortcut_combination.split("+");var kp=0;var shift_nums={"`":"~","1":"!","2":"@","3":"#","4":"$","5":"%","6":"^","7":"&","8":"*","9":"(","0":")","-":"_","=":"+",";":":","\'":"\\"",",":"<",".":">","/":"?","\\\\":"|"}\r\nvar special_keys={\'esc\':27,\'escape\':27,\'tab\':9,\'space\':32,\'return\':13,\'enter\':13,\'backspace\':8,\'scrolllock\':145,\'scroll_lock\':145,\'scroll\':145,\'capslock\':20,\'caps_lock\':20,\'caps\':20,\'numlock\':144,\'num_lock\':144,\'num\':144,\'pause\':19,\'break\':19,\'insert\':45,\'home\':36,\'delete\':46,\'end\':35,\'pageup\':33,\'page_up\':33,\'pu\':33,\'pagedown\':34,\'page_down\':34,\'pd\':34,\'left\':37,\'up\':38,\'right\':39,\'down\':40,\'f1\':112,\'f2\':113,\'f3\':114,\'f4\':115,\'f5\':116,\'f6\':117,\'f7\':118,\'f8\':119,\'f9\':120,\'f10\':121,\'f11\':122,\'f12\':123}\r\nvar modifiers={shift:{wanted:false,pressed:false},ctrl:{wanted:false,pressed:false},alt:{wanted:false,pressed:false},meta:{wanted:false,pressed:false}};if(e.ctrlKey)modifiers.ctrl.pressed=true;if(e.shiftKey)modifiers.shift.pressed=true;if(e.altKey)modifiers.alt.pressed=true;if(e.metaKey)modifiers.meta.pressed=true;for(var i=0;k=keys[i],i<keys.length;i++){if(k==\'ctrl\'||k==\'control\'){kp++;modifiers.ctrl.wanted=true;}else if(k==\'shift\'){kp++;modifiers.shift.wanted=true;}else if(k==\'alt\'){kp++;modifiers.alt.wanted=true;}else if(k==\'meta\'){kp++;modifiers.meta.wanted=true;}else if(k.length>1){if(special_keys[k]==code)kp++;}else if(opt[\'keycode\']){if(opt[\'keycode\']==code)kp++;}else{if(character==k)kp++;else{if(shift_nums[character]&&e.shiftKey){character=shift_nums[character];if(character==k)kp++;}}}}\r\nif(kp==keys.length&&modifiers.ctrl.pressed==modifiers.ctrl.wanted&&modifiers.shift.pressed==modifiers.shift.wanted&&modifiers.alt.pressed==modifiers.alt.wanted&&modifiers.meta.pressed==modifiers.meta.wanted){callback(e);if(!opt[\'propagate\']){e.cancelBubble=true;e.returnValue=false;if(e.stopPropagation){e.stopPropagation();e.preventDefault();}\r\nreturn false;}}}\r\nthis.all_shortcuts[shortcut_combination]={\'callback\':func,\'target\':ele,\'event\':opt[\'type\']};if(ele.addEventListener)ele.addEventListener(opt[\'type\'],func,false);else if(ele.attachEvent)ele.attachEvent(\'on\'+opt[\'type\'],func);else ele[\'on\'+opt[\'type\']]=func;},\'remove\':function(shortcut_combination){shortcut_combination=shortcut_combination.toLowerCase();var binding=this.all_shortcuts[shortcut_combination];delete(this.all_shortcuts[shortcut_combination])\r\nif(!binding)return;var type=binding[\'event\'];var ele=binding[\'target\'];var callback=binding[\'callback\'];if(ele.detachEvent)ele.detachEvent(\'on\'+type,callback);else if(ele.removeEventListener)ele.removeEventListener(type,callback,false);else ele[\'on\'+type]=false;}}\r\n'
        cherrypy.response.headers['Content-Type'] = 'text/javascript'
        return result
        ## FIXME static shortcut.js, include in source so single jar file works standalone?
        #return cherrypy.serve_file(self._shortcut_js_file, content_type='text/javascript')
    shortcut_js.exposed = True

    def index(self, sql_str=None):
        #print repr(sql_str)
        if sql_str:
            sql_str = sql_str.strip()
            result = self.sql_tm_html.execute_sql(sql_str)
            result = 'html:' + '<pre><code>' + escape(result) + '</code></pre>'
            result += 'Python:' + '<pre><code>' + '''
sql = """%s"""
bind_params = None

c = db.cursor()
rows = select_dict_from_db_generator(c, sql, bind_params)
template_dict = {'rows': rows}  # NOTE rows is an iterator NOT a list
final = stache.Stache().render(tmp_template, template_dict)
c.close()
''' % (escape(sql_str),)            + '</code></pre>'
            return result + self._form_html % escape(sql_str)
        else:
            return self._form_html % ''
    index.exposed = True

def main(argv=None):
    if argv is None:
        argv = sys.argv

    # Horrible quick and dirty argument handling
    if len(argv) > 1:
        dbconstr = argv[1]
    else:
        dbconstr = None

    if len(argv) > 2:
        sql_filename = argv[2]
    else:
        sql_filename = None

    sql_string = None
    if sql_filename:
        #f = open(sql_filename, 'rU')
        #f = open(sql_filename, 'rb')
        f = open(sql_filename)
        sql_string = f.read()
        f.close()

    sql_tm_html = SqlRunnerHtml(dbconstr)

    if sql_string:
        result = sql_tm_html.execute_sql(sql_string)
        print result
    else:
        if cherrypy is None:
            raise ImportError('cherrypy')
        # start web app
        w = WebHtml(sql_tm_html)
        server_port = 5566
        ## CherryPy version 3.x style
        cherrypy.config.update({'server.socket_port': server_port})  # CherryPy 3.1.2
        cherrypy.quickstart(w)

        #cherrypy.dietcherry_start(root_class=w, server_port=5566)
        #cherrypy.dietcherry_start(root_class=w, server_port=5566, server_host='localhost')  # ironPython is picky about addresses
        #cherrypy.dietcherry_start(root_class=w, server_port=5566, server_host='')  # ironPython is picky about addresses (does not like '')

        """
        import webbrowser

        # style start for:
        #   CherryPy 3.1 (tested with 3.1.2)
        #   dietcherypy
        def launch_webbrowser():
            webbrowser.open(url)
        cherrypy.engine.subscribe('start', launch_webbrowser)  # CherryPy 3.1 api
        cherrypy.quickstart(mywebapp)
        """



if __name__ == "__main__":
    sys.exit(main())

