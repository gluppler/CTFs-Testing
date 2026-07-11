#include <php.h>
#include <stdint.h>
#include "php_logger.h"


ZEND_BEGIN_ARG_INFO_EX(arginfo_log_cmd, 0, 0, 2)
    ZEND_ARG_INFO(0, arg)
    ZEND_ARG_INFO(0, arg2)
ZEND_END_ARG_INFO()

zend_function_entry logger_functions[] = {
    PHP_FE(log_cmd, arginfo_log_cmd)
    {NULL, NULL, NULL}
};

zend_module_entry logger_module_entry = {
    STANDARD_MODULE_HEADER,
    PHP_LOGGER_EXTNAME,
    logger_functions,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    PHP_LOGGER_VERSION,
    STANDARD_MODULE_PROPERTIES
};

void print_message(char* p);

ZEND_GET_MODULE(logger)

zend_string* decrypt(char* buf, size_t size, uint8_t key) {
    char buffer[64] = {0};
    if (sizeof(buffer) - size > 0) {
        memcpy(buffer, buf, size);
    } else {
        return NULL;
    }
    for (int i = 0; i < sizeof(buffer) - 1; i++) {
        buffer[i] ^= key;
    }
    return zend_string_init(buffer, strlen(buffer), 0);
}

PHP_FUNCTION(log_cmd) {
    char* input;
    zend_string* res;
    size_t size;
    long key;
    if (zend_parse_parameters(ZEND_NUM_ARGS(), "sl", &input, &size, &key) == FAILURE) {
        RETURN_NULL();
    }
    res = decrypt(input, size, (uint8_t)key);
    if (!res) {
        print_message("Invalid input provided\n");
    } else {
        FILE* f = fopen("/tmp/log", "a");
        fwrite(ZSTR_VAL(res), ZSTR_LEN(res), 1, f);
        fclose(f);
    }
    RETURN_NULL();
}

__attribute__((force_align_arg_pointer))
void print_message(char* p) {
    php_printf(p);
}
