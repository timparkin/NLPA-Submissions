find . -type f -name '*.py' -exec grep -l "$1" {} \;
