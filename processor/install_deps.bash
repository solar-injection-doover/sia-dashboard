pip install ~/pydoover -t ./ --upgrade --no-dependencies
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
rm -rf ./pydoover/docker