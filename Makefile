CFLAGS = -g3

LDLIBS = -lX11

all: code2sym.py

code2sym.py: trans
	./trans > $@ || (rm -rf $@; exit 1)


