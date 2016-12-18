import collections
import imp
import json
import os

PluginConfig = "./config.json"
PluginScript = "screen.py"
ScreenConf = "conf.json"


def getPlugins(inactive=False):
    plugins = []
    a = 1

    # Load in the config.json file in the root directory
    conf = json.load(open(os.path.join(PluginConfig)), object_pairs_hook=collections.OrderedDict)

    # Get the screens in the json file
    screens = conf.get("screens")

    # Loop over the screens and get their name and location
    for name, location in screens.items():

        # Ignore anything that doesn't meet our criteria
        if (not os.path.isdir(location) or PluginScript not in
            os.listdir(location)):
            continue

        # Load the module info into a variavls
        inf = imp.find_module("screen", [location])

        # Plugin needs a conf file.
        if ScreenConf in os.listdir(location):
            conf = json.load(open(os.path.join(location, ScreenConf)))

            # See if the user has disabled the plugin.
            if conf.get("enabled", False) or inactive:

                # Get the KV file text
                kvpath = os.path.join(location, conf["kv"])
                kv = open(kvpath).readlines()

                # See if there's a web config file
                webfile = os.path.join(location, "web.py")
                if os.path.isfile(webfile):
                    web = imp.find_module("web", [location])
                else:
                    web = None

                # Custom dict for the plugin
                plugin = {"name": name,
                          "info": inf,
                          "id": a,
                          "screen": conf["screen"],
                          "dependencies": conf.get("dependencies", list()),
                          "kv": kv,
                          "kvpath": kvpath,
                          "params": conf.get("params", None),
                          "enabled": conf.get("enabled", False),
                          "web": web}

                plugins.append(plugin)
                a = a + 1

    # We're done so return the list of available/enabled plugins
    return plugins
