#!/bin/bash

if [ "$TRAVIS_BRANCH" != "develop" ]; then 
    exit 0;
fi

git checkout main
git merge develop
git push