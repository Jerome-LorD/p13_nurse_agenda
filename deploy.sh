#!/bin/bash

if [ "$TRAVIS_BRANCH" != "develop" ]; then 
    exit 0;
fi

git checkout $TRAVIS_BRANCH
git merge develop
git push