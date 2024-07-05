find . -type f -name '*.html' -exec grep -l "$1" {} \;
