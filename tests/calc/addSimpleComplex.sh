#!/bin/bash

TARGET=8
OUTPUT=$(./main add 1 2 5)

if [ "$OUTPUT" = "$TARGET" ]; then
    echo "Passed"
    exit 0
else
    echo "Failed with output: $OUTPUT"
    exit 1
fi