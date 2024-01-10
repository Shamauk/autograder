#!/bin/bash

TARGET=168
OUTPUT=$(./main mul 7 6 4 1)

if [ "$OUTPUT" = "$TARGET" ]; then
    echo "Passed"
    exit 0
else
    echo "Failed with output: $OUTPUT"
    exit 1
fi