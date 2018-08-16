#!/usr/bin/env bash

# This script identifies the unit test modules that do not correspond
# directly with a module in the code tree.  See TESTING.rst for the
# intended structure.

project_path=$(dirname $(dirname $(realpath "$0")))
base_test_path=networking_ansible/tests/unit
test_path=$project_path/$base_test_path

test_files=$(find ${test_path} -iname 'test_*.py')

ignore_regexes=(
    # Nothing here so far
)

wrong_files=()
ignore_count=0
total_count=0
for test_file in ${test_files[@]}; do
    relative_path=${test_file#$test_path/}
    expected_path=$(dirname $project_path/networking_ansible/$relative_path)
    test_filename=$(basename "$test_file")

    expected_filename=${test_filename#test_}
    # Module filename (e.g. foo/bar.py -> foo/test_bar.py)
    filename=$expected_path/$expected_filename
    # Package dir (e.g. foo/ -> test_foo.py)
    package_dir=${filename%.py}
    if [ ! -f "$filename" -a ! -d "$package_dir" ]; then
        for ignore_regex in ${ignore_regexes[@]}; do
            if [[ "$relative_path" =~ $ignore_regex ]]; then
                ignore_count=$((ignore_count + 1))
                continue 2
            fi
        done
        wrong_files+=($base_test_path/$relative_path)
    fi
    total_count=$((total_count + 1))
done

if [ $ignore_count -ne 0 ]; then
    echo "$ignore_count unmatched test modules were ignored"
fi

if [ ${#wrong_files[@]} -eq 0 ]; then
    echo 'Success!  All test modules match targets in the code tree.'
    exit 0
else
    echo "Failure! ${#wrong_files[@]} of $total_count test modules do not match targets in the code tree. Wrong files are:"
    for wrong_file in ${wrong_files[@]}; do
        echo -e "\t$wrong_file"
    done
    exit 1
fi
