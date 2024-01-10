#!/bin/bash

TARGET=1
OUTPUT=$(./main div 5 5)

if [ "$OUTPUT" = "$TARGET" ]; then
    echo "Passed"
    exit 0
else
    echo "Failed with output: $OUTPUT"
    exit 1
fi