#!/bin/bash

cd $(dirname $0)
echo "Running $(pwd)/git_backup.sh ..."

if [ -n "$(git status --porcelain)" ]; then
	echo "commit all staged changes and push branch master to backup!"

	git add --all
	git commit -m "automatic backup commit"
	git push -u backup master
else
	echo "no staged changes - nothing to commit/backup!"
fi
