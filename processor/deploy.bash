#!/bin/bash

export PYTHONDONTWRITEBYTECODE=1
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
python3.11 -m pydoover deploy_config ../doover_config.json --profile staging --agent ce515920-25ea-4829-9a2c-d47c1fb05b64