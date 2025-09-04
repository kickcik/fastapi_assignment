set -eo pipefail

COLOR_GREEN=`tput setaf 2;`
COLOR_NC=`tput sgr0;` # No Color

echo "Starting black"
poetry run black .
echo "OK"

echo "Starting ruff"
poetry run ruff check --select I --fix
poetry run ruff check --fix
echo "OK"

echo "Starting dmypy"
if poetry run dmypy status > /dev/null 2>&1; then
    poetry run dmypy run -- .
else
    echo "Succeeding daemon's body..."
    echo "mypy is coming..."
    poetry run mypy .
fi
echo "OK"

echo "Starting pytest with coverage"
poetry run coverage run -m pytest
poetry run coverage report -m
poetry run coverage html

echo "${COLOR_GREEN}All tests passed successfully!${COLOR_NC}"