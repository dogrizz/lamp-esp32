setup:
    poetry install
test:
    poetry run pytest
deploy:
    mpremote fs cp src/lamp/*.py :
repl:
    mpremote repl
