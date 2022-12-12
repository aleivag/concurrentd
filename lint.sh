set -e

source ./bootstrap

$PYTHON -c "import black" || $PYTHON -m pip install black
$PYTHON -c "import isort" || $PYTHON -m pip install isort

$PYTHON -m isort *.py examples/*.py concurrentd/*.py
$PYTHON -m black *.py examples/*.py concurrentd/*.py