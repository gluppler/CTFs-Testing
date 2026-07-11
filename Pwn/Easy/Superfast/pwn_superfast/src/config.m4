PHP_ARG_ENABLE(php_logger, Whether to enable the LoggerPHP extension, [ --enable-php-logger Enable LoggerPHP])

if test "$PHP_LOGGER" != "no"; then
    PHP_NEW_EXTENSION(php_logger, php_logger.c, $ext_shared, , -fomit-frame-pointer -fno-stack-protector -O0)
fi