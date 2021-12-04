#!/bin/bash

if [ "$TRAVIS_BRANCH" != "test" ]; then 
    exit 0;
fi

git checkout main
git merge develop
git push