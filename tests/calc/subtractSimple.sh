#!/bin/bash

TARGET=0
OUTPUT=$(./main sub 1 1)

if [ "$OUTPUT" = "$TARGET" ]; then
    echo "Passed"
    exit 0
else
    echo "Failed with output: $OUTPUT"
    exit 1
fi