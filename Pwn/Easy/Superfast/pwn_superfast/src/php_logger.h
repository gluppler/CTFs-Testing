#include <stdint.h>

#define PHP_LOGGER_EXTNAME "php_logger"
#define PHP_LOGGER_VERSION "0.0.1"


zend_string* decrypt(char* buf, size_t size, uint8_t key);
PHP_FUNCTION(log_cmd);