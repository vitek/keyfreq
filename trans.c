#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/keysym.h>
#include <X11/extensions/XTest.h>

int main(void) {
    Display *display;
    KeySym ksym;
    KeyCode kcode;
    int i;

    display = XOpenDisplay(0);

    printf("KEYCODE_TO_KEYSYM = {\n");
    for (i = 0; i< 256; i++) {
        KeySym ksym = XKeycodeToKeysym(display, i, 0);
        if (ksym)
            printf("    %d: \"%s\",\n", i, XKeysymToString(ksym));
    }
    printf("}\n");
    XCloseDisplay(display);

    return 0;
}
