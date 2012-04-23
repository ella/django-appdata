#!/bin/bash

set -e
set -x

APP_NAME=${1:?brand.sh APP_NAME}

cd $(dirname $(which "$0"))

echo "Moving directories"
find . -type d -not -name "brand.sh" -not -path './.git/*' | tac | grep 'APP_NAME' | while read d
do
    echo "$d -> ${d//APP_NAME/$APP_NAME}"
    git mv "$d" "${d//APP_NAME/$APP_NAME}"
done

echo "Editting files"
find . -type f -not -name "brand.sh" -not -path './.git/*' | xargs sed -i -e "s;APP_NAME;$APP_NAME;g"

echo "Done"
