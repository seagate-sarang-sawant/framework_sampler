venv37_py\Scripts\activate
set CWD=C:\Users\755344\codebase\proj\framework_sampler
set PYTHONPATH=%CWD%;%CWD%\perf;%PYTHONPATH%
python perf\locust_runner.py --file_path=locustfile_step_users.py
venv_py\Scripts\deactivate