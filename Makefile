.PHONY: build clean rebuild serve

build:
	python3 build.py

clean:
	rm -rf site

rebuild: clean build

serve: build
	cd site && python3 -m http.server 8000
