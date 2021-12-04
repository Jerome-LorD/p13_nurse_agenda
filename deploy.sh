#!/bin/bash

if [ "$TRAVIS_BRANCH" != "develop" ]; then 
    exit 0;
fi

git checkout origin/main
git merge origin/develop
git push