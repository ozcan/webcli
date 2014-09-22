# -*- coding: utf-8 -*-
import subprocess
import sys
import re
import json
import webbrowser
from bottle import route, run, request

PORT=8081

@route('/')
def interface():
    return """
<html>
<head>
<title>WebCli</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<script type="text/javascript" src="//code.jquery.com/jquery-2.1.1.min.js"></script>
<link href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css" rel="stylesheet">
<script type="text/javascript">
var program;

String.prototype.trim=function(){return this.replace(/^\s+|\s+$/g, '');};

function run_command() {
    $.ajax({
        type: 'POST',
        url: "/run_command?timestamp=" + new Date().getTime(),
        data: { command: $('#preview').text() },
        success: function(data) {
            $('#output').html(data);
        }
    });
}

$(document).ready(function() {
    $.ajax({
        type: 'GET',
        cache: false,
        url: '/command?timestamp=' + new Date().getTime(),
        success: function(data) {
            program = data;
        }});

    $.ajax({
        type: 'GET',
        cache: false,
        url: '/parameters?timestamp=' + new Date().getTime(),
        success: function(data) {
            data = eval(data);

            for (var i=0; i < data.length; i++)
            {
                var parameter = data[i];

                var value_box;
                if (parameter[0].indexOf('=')>-1) {
                    value_box = "<input type='text' pname='" + parameter[0] + "'/>";
                }
                else {
                    value_box = "<input type='checkbox' pname='" + parameter[0] + "' />";
                }

                var row = "<tr>" +
                "<td class='pname'>" + parameter[0] + "</td>" +
                "<td>" + value_box + "</td>" + 
                "<td>" + parameter[1] + "</td>" +
                "</tr>";

                $('#parameters').append(row);
            }


            $('#parameters input').change(function() {
                // build command line
                var use_long=$('#use_long').is(':checked');

                var output = program + " ";

                $('#parameters input').each(function() {
                    if ($(this).is('input:checkbox') && $(this).is(':checked')) 
                    {
                        var pname = $(this).attr('pname');
                        var command = pname.split('[')[0].split('=')[0].split(',');

                        if (use_long && command.length > 1) {
                            command = command[1].trim();
                        }
                        else
                        {
                            command = command[0].trim();
                        }  
                        output = output + command + " "; 
                    }
                    else if ($(this).is('input:text') && $(this).val().length > 0)
                    {
                        var pname = $(this).attr('pname');
                        var command = pname.split('[')[0].split('=')[0].split(',');

                        if (use_long && command.length > 1) {
                            command = command[1].trim();
                            output = output + command + '="' + $(this).val() + '" ';
                        }
                        else
                        {
                            command = command[0].trim();

                            if (command.indexOf('--')> -1)
                            {
                                command = command + "=";
                            }
                            else
                            {
                                command = command + " ";
                            }
                            output = output + command + '"' + $(this).val() + '" ';          
                        }
                    }
                });

                $('#preview').text(output);
            });
        }
    });

});
</script>
<style type="text/css">
body {
    padding: 10px;
}
.table {
    width: 600px;
}
textarea {
    width: 100%;
}
.left > * {
    margin: 5px;
}
#output {
    width: 100%;
    border: 1px #CCC solid;
    overflow-y: scroll;
    height: 320px;
    font-family: monospace;
    background: black;
    color: white;
}

</style>
</head>
<body>
<div class="col-xs-6 left">
<h1>WebCli</h1><br />
Command Preview:<br />
<textarea id="preview">
</textarea><br />
<button type="button" class="btn btn-success" onclick="run_command()"><i class="glyphicon glyphicon-play"></i> Run command</button>
<button type="button" class="btn btn-default" onClick="$('#output').html('');"><i class="glyphicon glyphicon-remove"></i> Clear output</button>
<input type="checkbox" id="use_long" onChange="$('.right :input').first().change()"><label for="use_long" style="font-weight: normal; ">Use double-dash parameters</label>
<br /><br />
Output:
<div id="output"></div>

</div>
</div>
<div class="col-xs-6 right" style="overflow-y: scroll; height:600;">
<table class="table table-bordered table-striped">
<thead>
<tr>
    <td>Parameter</td>
    <td>Value</td>
    <td>Description</td>
</tr>
</thead>
<tbody id="parameters">

</tbody>
</table>
</body>
</html>"""

@route('/parameters')
def parameters():
    name = sys.argv[1]

    man_file_location = subprocess.check_output(['man', '--where', name])
    manpage = subprocess.check_output(['gzip', '-dc', man_file_location.replace('\n', '')])

    tp_list = manpage.split('.TP')[1:]

    parameters = []

    for tp in tp_list:
        tp = re.sub(ur'\\(fR|fI|fB|f)?', '', tp)

        lines = tp.split('.PP')[0].split('\n')[1:]

        parameters.append([lines[0], " ".join(lines[1:])])

        if '.PP' in tp:
            break

    return json.dumps(parameters)

@route('/command')
def get_command():
    name = sys.argv[1]

    return name

@route('/run_command', method='POST')
def run_command():
    output = subprocess.check_output(request.forms.get('command'),stderr=subprocess.STDOUT, shell=True)
    return output.replace("\n", "<br />")

webbrowser.open_new("http://127.0.0.1:%d" % PORT)
run(host='127.0.0.1', port=PORT, quiet=True)

