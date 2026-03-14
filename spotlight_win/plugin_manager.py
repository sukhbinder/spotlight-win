import pluggy

HOOK_NAMESPACE = "spotlight"

# Create hookspec and hookimpl markers
hookspec = pluggy.HookspecMarker(HOOK_NAMESPACE)
hookimpl = pluggy.HookimplMarker(HOOK_NAMESPACE)

class SpotlightSpec:
    """A hook specification namespace."""

    @hookspec
    def match(self, text):
        """
        Determine if a plugin can handle the given text.
        Should return (score, display_text) or None.
        """

    @hookspec
    def activate(self, text):
        """
        Perform the action associated with the plugin.
        """

# Create a PluginManager
plugin_manager = pluggy.PluginManager(HOOK_NAMESPACE)
plugin_manager.add_hookspecs(SpotlightSpec)