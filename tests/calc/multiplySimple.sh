#!/bin/bash

TARGET=42
OUTPUT=$(./main mul 7 6)

if [ "$OUTPUT" = "$TARGET" ]; then
    echo "Passed"
    exit 0
else
    echo "Failed with output: $OUTPUT"
    exit 1
fi