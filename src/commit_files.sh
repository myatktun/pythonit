#!/bin/bash

source ./.env
set -e


main () {
    rst_to_html

    COMMIT_MSG="$@"

    if [[ -z $COMMIT_MSG ]]; then
        echo "Commit message not provided"
        exit 1
    fi

    cp -r $LOCAL_HTML_DIR/* $GH_REPO
    cd $GH_REPO

    check_git_status

    git add .
    git commit -m "$COMMIT_MSG"
    git push
}

rst_to_html () {
    make -C $MAKE_DIRECTORY html 2>&1 | tee -a output.log
}

check_git_status () {
    status="$(git st)"

    if [[ $status == *"nothing to commit"* ]]; then
        echo "git: Nothing to add and push"
        exit 0
    fi
}

main $1
