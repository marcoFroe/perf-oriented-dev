CC := gcc
CFLAGS := -Wall -Wextra

.PHONY: all clean

all: my_allocator.so malloctest

my_allocator.so: my_allocator.c
	$(CC) -shared -fPIC $(CFLAGS) -O3 -o $@ $<

malloctest: malloctest.c
	$(CC) $(CFLAGS) -O2 -o $@ $<

CC := gcc
CFLAGS := -Wall -Wextra

clean:
	rm -f my_allocator.so malloctest