import webbrowser
from threading import Timer
import copy
import flask
import time
from datetime import datetime
import subprocess

app = flask.Flask(__name__, static_url_path='/static')


@app.route("/index")
def main_page():
    return app.send_static_file('index.html')


@app.route("/generate")
@app.route("/generate/<run_id>")
def generate(run_id=str(time.time())[-5:], date=datetime.now().strftime("%m_%d_%y_")):
    return flask.render_template('generate.html', run_id=date + run_id)


@app.route("/edit")
def edit():
    return app.send_static_file('')

@app.route("/load_config")
def load_config():
    return flask.render_template('load_config.html')

@app.route("/overview")
def overview():
    tools = copy.deepcopy(dict(flask.request.args))
    parsed_tools = {}
    for i in tools:
        if tools[i] != '':
            if i.startswith('tool_'):
                parsed_tools['_'.join(i.split('_')[1:])] = {''.join(tools[i].split('_')[0]): {}}
                for j in tools:
                    if j.startswith(tools[i] + '_param') and tools[j] == "on":
                        parsed_tools['_'.join(i.split('_')[1:])][''.join(tools[i].split('_')[0])].update(
                            {''.join(j.split('!')[-1]): ''})
                    elif j.startswith(tools[i] + '_param') and tools[j] != '':
                        parsed_tools['_'.join(i.split('_')[1:])][''.join(tools[i].split('_')[0])].update(
                            {''.join(j.split('!')[-1]): tools[j]})
    appendage = {i: {} for i in parsed_tools}
    for i in parsed_tools:
        for j in parsed_tools[i]:
            params = []
            for key, value in parsed_tools[i][j].items():
                if j == "TRIMMOMATIC":
                    params.append(str(key) + ':' + str(value))
                else:
                    params.append(str(key) + ' ' + str(value))
            appendage[i].update({j: ' '.join(params)})
    request_args.update({'tools': appendage})
    with open('../config_files/' + request_args['run_id'] + '.json', 'w') as f:
        f.write(flask.json.dumps(request_args, separators=(',\n', ':')))
    return flask.render_template('overview.html', run_id=request_args['run_id'] + '.json')


@app.route("/tools")
def tools():
    global request_args
    request_args = copy.deepcopy(dict(flask.request.args))
    if request_args['run_type'] == "complete_analysis":
        return flask.render_template('complete_analysis.html')

    elif request_args['run_type'] == "sequence_prefiltering":
        return flask.render_template('sequence_prefiltering.html')

    elif request_args['run_type'] == "analysis":
        return flask.render_template('analysis.html')


@app.route("/progress")
def progress():
    bashCommand = 'python3 DRAW.py ' + request_args['run_id'] + '.json'
    subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

@app.route("/run_from_load")
def run_from_load():
    load_args = copy.deepcopy(dict(flask.request.args))
    bashCommand = 'python3 DRAW.py ' + load_args['run_id'] + '.json'
    subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

def open_browser():
    webbrowser.open_new('http://127.0.0.1:2000/index')


if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(port=2000, debug=False)
