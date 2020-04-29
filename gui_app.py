import webbrowser
from threading import Timer
import copy
from flask import Flask, request, json

app = Flask(__name__)

@app.route("/")
def main_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {
        background-image: url('/static/images/bg.png');
        background-attachment: fixed;
        background-repeat: no-repeat;
        background-position: center;
    }
    .content {
    border-radius: 25px;
    padding: 10px;
    position: absolute;
    top:  50%;
    left: 50%;
    transform: translate(-50%,-50%);
    background: HoneyDew;
    }
    </style>
    </head>
    <body>
    <div class="content">
    <center>
    <h1>Conifg file generator for DRAW</h1>
    <form action="/tools">
        <label for="run_type">Run type</label><br>
        <select id="run_type" name="run_type">
            <option value="complete_analysis">Complete</option>
            <option value="sequence_prefiltering">Sequence prefiltering</option>
            <option value="analysis">Analysis</option>
        </select><br><br>
        <label for="seq_type">Input sequences type</label><br>
        <select id="seq_type" name="seq_type">
            <option value="single_end">Single end</option>
            <option value="paired_end">Paired end</option>
        </select><br><br>
        <label for="annotation_file_path">Path to annotation file</label><br>
        <input type="text" id="annotation_file_path" name="annotation_file_path" value=""><br><br>
        <label for="input_file_dir">Absolute path to directory containing files</label><br>
        <input type="text" id="input_file_dir" name="input_file_dir" value=""><br><br>
        <label for="input_file_prefix">Prefix of sample file names</label><br>
        <input type="text" id="input_file_prefix" name="input_file_prefix" value=""><br><br>
        <label for="control_file_prefix">Prefix of control file names</label><br>
        <input type="text" id="control_file_prefix" name="control_file_prefix" value=""><br><br>
        <label for="output_dir">Select path for all output files</label><br>
        <input type="text" id="output_dir" name="output_dir" value=""><br><br>
        <label for="threads_number">Number of threads used for the analysis</label><br>
        <input type="number" id="threads_number" name="threads_number" value=""><br><br>
        
        <label for="run_downstream_analysis">Run downstream analysis</label><br>
        <input type="checkbox" id="run_downstream_analysis" name="run_downstream_analysis"><br><br>
        
        <input type="submit" value="Continue">
    </form>
    </center>
    </div>
    </body>
    </html>
    """


@app.route("/tools")
def tools():
    global request_args
    request_args = copy.deepcopy(dict(request.args))
    if request_args['run_type'] == "complete_analysis":
        return """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body {
            background-image: url('/static/images/bg.png');
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }
        .content {
        border-radius: 25px;
        padding: 10px;
        position: absolute;
        top:  50%;
        left: 50%;
        transform: translate(-50%,-50%);
        background: AliceBlue;
        }
        </style>
        </head>
        <body>
        <div class="content">
        <center>
        <h1>Tools</h1>
        <form action="/send_form">
        <label for="INITIAL_QUALITY_CONTROL">Initial quality check</label><br>
        <select id="INITIAL_QUALITY_CONTROL" name="INITIAL_QUALITY_CONTROL">
            <option value="FastQC">FastQC</option>
        </select><br><br>
        <label for="QC_params">Input parameters for chosen tool</label><br>
        <input type="text" id="QC_params" name="QC_params" value=""><br><br>
        
        <label for="TRIMMING">Trimming tool</label><br>
        <select id="TRIMMING" name="TRIMMING">
            <option value="TRIMMOMATIC">Trimmomatic</option>
        </select><br><br>
        <label for="TRIMMING_params">Input parameters for chosen tool</label><br>
        <input type="text" id="TRIMMING_params" name="TRIMMING_params" value=""><br><br>
        
        <label for="AFTER_TRIMMING_CONTROL">After-trimming quality check</label><br>
        <select id="AFTER_TRIMMING_CONTROL" name="AFTER_TRIMMING_CONTROL">
            <option value="FastQC">FastQC</option>
        </select><br><br>
        <label for="AFTER_TRIMMING_CONTROL_params">Input parameters for chosen tool</label><br>
        <input type="text" id="AFTER_TRIMMING_CONTROL_params" name="AFTER_TRIMMING_CONTROL_params" value=""><br><br>
        
        <label for="MAPPING"></label>Mapping<br>
        <select id="MAPPING" name="MAPPING">
            <option value="Bowtie2">Bowtie2</option>
        </select><br><br>
        <label for="MAPPING_params">Input parameters for chosen tool</label><br>
        <input type="text" id="MAPPING_params" name="MAPPING_params" value=""><br><br>
        
        <label for="COUNTING">Counting</label><br>
        <select id="COUNTING" name="COUNTING">
            <option value="HT-seq">HT-seq</option>
        </select><br><br>
        <label for="COUNTING_params">Input parameters for chosen tool</label><br>
        <input type="text" id="COUNTING_params" name="COUNTING_params" value=""><br><br>
        <input type="submit" value="Generate">
        </form>
        </center>
        </div>
        </body>
        </html>
        """
    else:
        return """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body {
            background-image: url('/static/images/bg.png');
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }
        .content {
        border-radius: 25px;
        padding: 10px;
        position: absolute;
        top:  50%;
        left: 50%;
        transform: translate(-50%,-50%);
        background: HoneyDew;
        }
        </style>
        </head>
        <body>
        <div class="content">
        <center>
        <h1>**Not ready yet - choose complete run option**</h1>
            <button onclick="goBack()">Go Back</button>
            <script>
            function goBack() {
              window.history.back();
            }
            </script>
        </center>
        </div>
        </body>
        </html>
        """


@app.route("/send_form")
def send_form():
    tools = copy.deepcopy(dict(request.args))
    request_args.update({'tools': tools})
    with open('config.json', 'w') as f:
        f.write(json.dumps(request_args, separators=(',\n', ':')))
    return """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        body {
            background-image: url('/static/images/bg.png');
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }
        .content {
        border-radius: 25px;
        padding: 10px;
        position: absolute;
        top:  50%;
        left: 50%;
        transform: translate(-50%,-50%);
        background: MintCream;
        }
        </style>
        </head>
        <body>
        <div class="content">
        <center>
        <h1>Congrats, you've successfully generated config file!</h1>
        </center>
        </div>
        </body>
        </html>
        """


def open_browser():
    webbrowser.open_new('http://127.0.0.1:2000/')


if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(port=2000, debug=False)
