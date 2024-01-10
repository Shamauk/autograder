This is where tests are to be placed.
Tests are to be placed under a folder of the assignment name.
Each test should return 0 if passed, otherwise any other number if failed.
Under each assignment directory should be a grading.json which will have each test name and the points as the attribute.
{
"<test-name>": {
"points": <num-points>
"exec": <exec-file>
"compile": <compile-command>
}
}
