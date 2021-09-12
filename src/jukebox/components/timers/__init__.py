# MIT License
#
# Copyright (c) 2021 Christian Banz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Contributing author(s):
# - Christian Banz

from jukebox.multitimer import (GenericTimerClass, GenericMultiTimerClass)
import logging
import jukebox.cfghandler
import jukebox.plugs as plugin


logger = logging.getLogger('jb.timers')
cfg = jukebox.cfghandler.get_handler('jukebox')


# ---------------------------------------------------------------------------
# Action functions for Timers
# ---------------------------------------------------------------------------
def shutdown(**ignored_kwargs):
    logger.info("Shutting down on timer request...")
    plugin.call_ignore_errors('host', 'shutdown')


def stop_player(**ignored_kwargs):
    logger.info("Stopping the player on timer request...")
    plugin.call_ignore_errors('player', 'ctrl', 'stop')


class VolumeFadeOutActionClass:
    def __init__(self, iterations):
        self.iterations = iterations
        # Get the current volume, calculate step size
        self.volume = plugin.call('volume', 'ctrl', 'get_volume')
        self.step = float(self.volume) / iterations

    def __call__(self, iteration):
        self.volume = self.volume - self.step
        logger.debug(f"Decrease volume to {self.volume} (Iteration index {iteration}/{self.iterations}-1)")
        plugin.call_ignore_errors('volume', 'ctrl', 'set_volume', args=[int(self.volume)])
        if iteration == 0:
            logger.debug("Shut down from volume fade out")
            plugin.call_ignore_errors('host', 'shutdown')


# ---------------------------------------------------------------------------
# Create the timers
# ---------------------------------------------------------------------------
timer_shutdown: GenericTimerClass
timer_stop_player: GenericTimerClass
timer_fade_volume: GenericMultiTimerClass


@plugin.finalize
def finalize():
    # TODO: Example with how to call the timers from RPC?

    # Create the various timers with fitting doc for plugin reference
    global timer_shutdown
    timeout = cfg.setndefault('timers', 'shutdown', 'default_timeout_sec', value=60 * 60)
    timer_shutdown = GenericTimerClass(timeout, shutdown)
    timer_shutdown.__doc__ = "Timer for automatic shutdown"
    timer_shutdown.name = 'TimeExit'
    # Note: Since timer_shutdown is an instance of a class from a different module,
    # auto-registration would register it with that module. Manually set package to this plugin module
    plugin.register(timer_shutdown, name='timer_shutdown', package=plugin.loaded_as(__name__))

    global timer_stop_player
    timeout = cfg.setndefault('timers', 'stop_player', 'default_timeout_sec', value=60 * 60)
    timer_stop_player = GenericTimerClass(timeout, stop_player)
    timer_stop_player.__doc__ = "Timer for automatic player stop"
    timer_stop_player.name = 'TimeStop'
    plugin.register(timer_stop_player, name='timer_stop_player', package=plugin.loaded_as(__name__))

    global timer_fade_volume
    timeout = cfg.setndefault('timers', 'volume_fade_out', 'default_time_per_iteration_sec', value=15 * 60)
    steps = cfg.setndefault('timers', 'volume_fade_out', 'number_of_steps', value=10)
    timer_fade_volume = GenericMultiTimerClass(steps, timeout, VolumeFadeOutActionClass)
    timer_fade_volume.__doc__ = "Timer step-wise volume fade out and shutdown"
    timer_fade_volume.name = 'TimeFade'
    plugin.register(timer_fade_volume, name='timer_fade_volume', package=plugin.loaded_as(__name__))

    # The idle Timer does work in a little sneaky way
    # Idle is when there are no calls through the plugin module
    # Ahh, but also when music is playing this is not idle...
    # Use setattr to replace plugin._call with a plugin._call that saves last access time

    # Two options:
    # (a) whenever a call happens -> restart timer
    # (b) save last call access time -> when timer times out, check that time with timer and restart if necessary with
    # delta time

    # MPD


@plugin.atexit
def atexit(**ignored_kwargs):
    global timer_shutdown
    timer_shutdown.cancel()