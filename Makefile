

all: README.html

README.html : README.md
	markdown $^ > $@

