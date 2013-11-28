venv-activate() {
    source $1/bin/activate
}

forget-known-hosts() {
    rm ~/.ssh/known_hosts
}

github-clone() {
    git clone git@github.com:${1}.git "${@:2}"
}

drive-html-extract () {
    for f in *; do mv "$f"/* tempfile.html; rmdir "$f"; mv tempfile.html "$f".html; done
}
