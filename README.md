# ninja-taisen

This repo contains back-end code related to the 2-player board game [Ninja Taisen](https://iellogames.com/jeux/ninja-taisen). The aims of this project are:
- to develop a winning strategy for playing Ninja Taisen
- to allow humans to play against this strategy
- to have some fun along the way and learn new skills

This project was initially written in Python, then re-written in Rust with a Python API - this has proven to make it several hundred times faster!

## Developing a strategy

This is an open-ended question. As of September 2024, the approach has been:
- Use human intuition to write a strategy, or improve an existing strategy
- Run the `batch_simulate.py` script to play this new strategy against existing strategies and see how the results compare
- Iterate and repeat based on the results

When developing a strategy you are consuming the code in `ninja-taisen` as a Python library. To this end the library code is structured as a Python pacakge:
- Methods & classes intended for public usage are in either [api.py](https://github.com/luke-chapman/ninja-taisen/blob/master/ninja_taisen/api.py) or [dtos.py](https://github.com/luke-chapman/ninja-taisen/blob/master/ninja_taisen/dtos.py)
- There are tests, including regression tests. These have been invaluable in developing a reliable game simulator 
- The code is linted with `ruff` and `mypy`, including checking for type annotations

While the library is young and changing fast, it's not yet published to a pypi repository. You'll need to `git clone` this repo and `pip install -e ninja-taisen` into a virtual environment for the time being.

So far, developing a strategy has been difficult. Just encoding a new strategy in reliable code is pretty hard. I've had several experiences of either getting the code wrong, or the idea turning out to not work, or both. Rome wasn't built in a day; I recommend a large dose of patience and humour.

As of September 2024 the "metric_strength" strategy beats the "random" strategy [96% of the time](https://github.com/luke-chapman/ninja-taisen/blob/9a8f6de6fd521aaf3df90f1663ad3a114c2ff20c/analysis/ninja-taisen-20240916_104134/metric_strength.csv#L2) - not a bad start. My next goal is to write a strategy which does the following:
- Almost always beats "random" - let's say 99% of the time
- Reliably beats "metric_strength" - let's say 70% of the time

If you're happy to develop the library broadly in the style described above, please do get involved / get in touch. I've raised [issues](https://github.com/luke-chapman/ninja-taisen/issues) for my current ideas here - consider them a [starter for ten](https://en.wiktionary.org/wiki/starter_for_ten).

## Local environment setup
You'll need both a Python and Rust development environment work on this project. Getting this working is non-trivial and there are different ways to go about it - my approach is detailed below.

### Pre-requisites
Clone this repo: 
```
git clone https://github.com/luke-chapman/ninja-taisen
```

Install Python 3.12 or newer on your machine (NB I'm sticking to 3.12, as matplotlib crashes on 3.13 for me). I recommend the [official, canonical versions](https://www.python.org/downloads/). 

Install Rust on your machine. I did this by installing [RustRover](https://www.jetbrains.com/rust/) on my machine. I'd really recommend this IDE and it's free for non-commercial use.

### Building the package

Now we need to make a Python [virtual environment](https://docs.python.org/3/library/venv.html) with some additional packages on top of the core installation. Open a terminal, `cd` to your location of choice, then run:
```
python -m venv virtual-environment-name --system-site-packages
```
Next, we `activate` our Python virtual environment. Commands vary according to your operating system. Either:
```
.\virtual-environment-name\Scripts\activate       # Windows
source ./virtual-environment-name/bin/activate    # Mac / Linux

deactivate                                        # Useful command to deactivate the environment after activation
```
Now we're ready to install extra packages into our environment. `cd` to the folder containing this Readme file, and run
```
pip install -r dev_requirements.txt
pip install -e .
```
The second of these commands is expected to take several minutes, as it compiles the Rust code into a binary before packaging it into the Python wheel.

Your local environment is now ready with ninja-taisen and all of its dependencies.

### Python development
The Python code is structured as a Python library, using `maturin` to do a magic which links Rust and Python together via the magic `maturin develop` command. 

As far as the Python code goes:
- `ninja_taisen` has source code
- `tests` has the tests
- `typing` provides type hints for the methods exposed from Rust

I'm using `ruff`, `mypy` and `black` for linting and `pytest` for testing. A few settings are encoded in the `pyproject.toml` file.

I use the `dev.py` script to launch useful linting operations, e.g.
```
python dev.py lint
python dev.py test
```
You can also commit to a branch using
```
python dev.py yeehaw "Commit message"
```
This will format, lint & test the code before committing to git if all is well.

### Rust development
For pure Rust development, we can use `cargo`:
```
cargo build    # Compile the code (in debug)
cargo test     # Compile the code & run unit tests
```

## Showcasing a strategy

You can ask the code to:
- `choose` a move, using the `choose_move` method in `api.py`
- `execute` a move, using the `execute_move` method in `api.py`

These methods are packaged up behind a json api using [flask](https://flask.palletsprojects.com). This json api allows the front end (coming soon!) to communicate with the back end without either needing to know any fine details of how the other operates.

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
The commands below work on Windows using Command Prompt; minor variants should work in other environments.

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
