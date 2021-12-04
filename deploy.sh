#!/bin/bash

if [ "$TRAVIS_BRANCH" != "develop" ]; then 
    exit 0;
fi

git checkout refs/remotes/origin/main
git merge refs/remotes/origin/develop
git push