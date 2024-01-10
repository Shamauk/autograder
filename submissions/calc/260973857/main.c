#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("Usage: %s <operator> <operand1> <operand2> ...\n", argv[0]);
        return 1;
    }

    char *operator = argv[1];
    int result = atoi(argv[2]);

    for (int i = 3; i < argc; i++) {
        if (strcmp(operator, "add") == 0) {
            result += atoi(argv[i]);
        } else if (strcmp(operator, "sub") == 0) {
            result -= atoi(argv[i]);
        } else if (strcmp(operator, "mul") == 0) {
            result *= atoi(argv[i]);
        } else if (strcmp(operator, "div") == 0) {
            if (atoi(argv[i]) != 0) {
                result /= atoi(argv[i]);
            } else {
                printf("Error: Division by zero\n");
                return 1;
            }
        } else {
            printf("Error: Unknown operator '%s'\n", operator);
            return 1;
        }
    }

    printf("%d\n", result);
    return 0;
}