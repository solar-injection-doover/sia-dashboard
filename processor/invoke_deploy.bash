#!/bin/bash

export PYTHONDONTWRITEBYTECODE=1
python3.11 -m pydoover invoke_local_task on_deploy . --profile staging --agent ce515920-25ea-4829-9a2c-d47c1fb05b64 --enable-traceback