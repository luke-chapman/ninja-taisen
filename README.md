# ninja-taisen

This repo contains back-end code related to the 2-player board game [Ninja Taisen](https://iellogames.com/jeux/ninja-taisen). The aims of this project are:
- to develop an excellent strategy for playing Ninja Taisen
- to allow humans to play against this strategy for fun
- to have some fun along the way and learn new skills

## Developing a strategy

This is done by running multiple games end-to-end, using the results to iterate as you go. I recommend running a locally-modified variant of the script `play_all_strategies.py` to generate a batch of results. These can then be analysed with the associated Jupyter notebooks to see how they fair against each other.

When developing a strategy you are implicitly consuming the code in ninja-taisen as a Python library. You'll need to do a `pip install -e ninja-taisen` of the library to use it. Publically available methods are visible in either `api.py` and `dtos.py`. There are also tests and linting.

Developing a strategy is really hard. Just encoding a new idea for a strategy in code is difficult. I've had several experiences of either getting the code wrong, or the idea turning out to not work, or both. Patience and humour is key! As of August 2024 the best strategy `metric_strength` beats a random strategy 95%+ of the time - not bad!

## Showcasing a strategy

You can ask the code to:
- `choose` a sample move, using the `choose_move` method in `api.py`
- `execute` a sample move, using the `execute_move` method in `api.py`

These methods are packaged up behind a json api using [flask](https://flask.palletsprojects.com). This json api allows a front end to communicate with the back end without either needing to know any fine details of how the other operates.

## Local environment setup
First clone this repo:
```
git clone https://github.com/luke-chapman/ninja-taisen
```
Next, install Python 3.12 or newer on your machine. I recommend the [official, canonical versions](https://www.python.org/downloads/). 

Now we need to make a Python [virtual environment](https://docs.python.org/3/library/venv.html) with some additional packages on top of the core installation. Open a terminal, `cd` to your location of choice, then run:
```
python -m venv virtual-environment-name --system-site-packages
```
Next, we activate our Python virtual environment. Commands slightly vary according to your OS. Either:
```
# Activation - Mac / Linux
source ./virtual-environment-name/bin/activate

# Activation - Windows
.\virtual-environment-name\Scripts\activate

# Deactivation - Windows / Mac / Linux
deactivate
```
Now we're ready to install extra packages into our environment. We're going to get ninja-taisen itself from local code, but other stuff will be pulled from an internet-based packaged repository:
```
# Everyone needs this: ninja-taisen and its dependencies
... 'cd' to the folder containing this ninja-taisen repo ...
pip install -e ./ninja-taisen

# If you want to run the Jupyter notebooks 
pip install -I jupyter ipython

# If you want to run testing / linting
pip install hatch pytest ruff black mypy requests
```

## Querying the json endpoint
### Launch server
You can launch the Python server like this:
```
python -m flask --app ./ninja-taisen/src/ninja_taisen/flask_entrypoint.py run
```
You should see output such as:
```
2024-09-13 15:11:59 - INFO - flask_entrypoint - Setting up Flask server 'ninja_taisen.flask_entrypoint'
2024-09-13 15:11:59 - INFO - flask_entrypoint - Added /choose POST url rule
2024-09-13 15:11:59 - INFO - flask_entrypoint - Added /execute POST url rule
 * Serving Flask app '.\src\ninja_taisen\flask_entrypoint.py'
 * Debug mode: off
2024-09-13 15:11:59 - INFO - _internal - WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
2024-09-13 15:11:59 - INFO - _internal - Press CTRL+C to quit
```
There are now two `url`s to query:
```
http://127.0.0.1:5000/choose
http://127.0.0.1:5000/execute
```

### Submit a curl command
The commands below work on Windows using Command Prompt. They may need some bashing-into-shape to get them to work in other contexts

#### choose
```
curl -X POST http://127.0.0.1:5000/choose -H "Content-Type: application/json" -d "{\"board\":{\"monkey\":{\"0\":[\"MJ4\",\"MR3\",\"MP2\",\"MS1\"],\"1\":[\"MP3\",\"MS2\",\"MR1\"],\"2\":[\"MS3\",\"MR2\"],\"3\":[\"MP1\"]},\"wolf\":{\"7\":[\"WP3\"],\"8\":[\"WS1\",\"WR2\"],\"9\":[\"WP1\",\"WS2\",\"WR3\"],\"10\":[\"WJ4\",\"WR1\",\"WP2\",\"WS3\"]}},\"dice\":{\"rock\":1,\"paper\":3,\"scissors\":2},\"team\":\"monkey\",\"strategy\":\"random\",\"seed\":42}"

{"moves":[{"card":"MP1","diceCategory":"paper"},{"card":"MS2","diceCategory":"scissors"},{"card":"MR2","diceCategory":"rock"}]}
```
#### execute
```
curl -X POST http://127.0.0.1:5000/execute -H "Content-Type: application/json" -d "{\"board\":{\"monkey\":{\"0\":[\"MJ4\",\"MR3\",\"MP2\",\"MS1\"],\"1\":[\"MP3\",\"MS2\",\"MR1\"],\"2\":[\"MS3\",\"MR2\"],\"3\":[\"MP1\"]},\"wolf\":{\"7\":[\"WP3\"],\"8\":[\"WS1\",\"WR2\"],\"9\":[\"WP1\",\"WS2\",\"WR3\"],\"10\":[\"WJ4\",\"WR1\",\"WP2\",\"WS3\"]}},\"dice\":{\"rock\":1,\"paper\":3,\"scissors\":2},\"team\":\"monkey\",\"moves\":[{\"diceCategory\":\"paper\",\"card\":\"MP1\"},{\"diceCategory\":\"scissors\",\"card\":\"MS2\"},{\"diceCategory\":\"rock\",\"card\":\"MR2\"}]}"

{"board":{"monkey":{"0":["MJ4","MR3","MP2","MS1"],"1":["MP3"],"2":["MS3"],"3":["MS2","MR1","MR2"],"6":["MP1"]},"wolf":{"7":["WP3"],"8":["WS1","WR2"],"9":["WP1","WS2","WR3"],"10":["WJ4","WR1","WP2","WS3"]}}}
```

## Development work
This project uses `hatch` to structure the project. Hatch invokes `ruff`, `mypy` and `black` for linting and `pytest` for testing.

Linting and tests should pass before hitting master. There are some useful commands in the pyproject.toml file for aid with this:

```
hatch run format
hatch run lint
hatch run test
```

You can also commit to a branch using
```
hatch run yeehaw -- "Commit message"
```
This will format, lint & test the code before committing to git if all is well.

## Issues
This project started in August 2024 and is still in its infancy. Writing a bot to play a board game is not an easy task - this will take time!

Open issues can be seen on this page: https://github.com/luke-chapman/ninja-taisen/issues
