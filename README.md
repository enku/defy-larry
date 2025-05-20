# defy-larry

defy-larry is a [larry](https://github.com/enku/larry) plugin to change the
LED colors on the Dygma (Defy) keyboard.

<p align="center">
<img src="https://raw.githubusercontent.com/enku/screenshots/refs/heads/master/defy-larry/defy-larry1.png" alt="screenshot" width="100%">
</p>

### Usage

Install [larry](https://github.com/enku/larry).

Install defy-larry:

```console
$ pip install git+https://github.com/enku/defy-larry
```

Add `defy_larry` to your list of larry plugins, e.g.:

```
# ~/.config/larry.cfg

[larry]
...
plugins = vim defy_larry

In addition you can add configuration for the plugin::

[plugins:defy_larry]
# Defy keyboard devices (separated by whitespace)
devices = /dev/ttyACM0

# What effect to use to enhance the colors. Valid values are "soften",
"pastelize" and "none". The default is "none".
effect = pastelize

# Increase the intensity (saturation) of the colors by this amount (between -1
and 1).  A value of 0, the default, does not alter the colors. Values greater
than 0 increase saturation. Values less than 0 decrease the saturation.
intensity = 0.6
```

Restart larry and enjoy!


# Warning

The keyboard's flash memory is written whenever larry changes colors. This
flash memory has a limited lifespan, so care should be taken not to run this
too much on your keyboard (don't use this to simulate animation, for example).

This plugin has been tested on the Dygma Defy keyboard, but other Dygma (or
non-Dygma) keyboards may work as well.
