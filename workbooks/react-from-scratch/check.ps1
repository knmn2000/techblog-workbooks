# Checks one checkpoint. Run `.\check` with no arguments for the options.
py -P "$PSScriptRoot/tools/check.py" @args
exit $LASTEXITCODE
