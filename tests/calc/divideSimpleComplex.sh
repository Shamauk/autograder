#!/bin/bash

TARGET=10
OUTPUT=$(./main div 100 2 5)

if [ "$OUTPUT" = "$TARGET" ]; then
    echo "Passed"
    exit 0
else
    echo "Failed with output: $OUTPUT"
    exit 1
fi