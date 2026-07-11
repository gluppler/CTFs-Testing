#!/bin/sh
phpize && \
    ./configure --enable-php-logger && \
    make -j `nproc` && \
    strip modules/php_logger.so && \
    cp modules/php_logger.so ../challenge && \
    make clean && \
    rm -rf include && \
    phpize --clean
