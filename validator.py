import re
import os
import sys
import pathlib

# Godot Scene validator

if len(sys.argv) == 1:
    print("No arguments specified, going with defaults...")
    print("Use --help for argument help")
    print("")

if sys.argv.count("--help") == 1:
    print("Godot Scene Validator - Remove missing links in your Godot scenes")
    print("Usage - validator.py [options] --scenes [scenes to check (relative to res://)]")
    print("Help:")
    print("    --help - Display this help")
    print("    --dir <dir> - Use <dir> as res:// (Godot root)")
    print("    --debug - Prints debugging information, basically means verbose")
    print("    --scenes <scenes> - Check scenes. If not specified, checks all scenes in res://")
    exit(0)
elif sys.argv.count("--help") > 1:
    print("Arguments can only be specified once")
    exit(1)

if sys.argv.count("--dir") == 1:
    resdir = os.path.abspath(sys.argv[sys.argv.index("--dir") + 1])
    if os.path.isfile(resdir):
        resdir = os.path.dirname(resdir)
elif sys.argv.count("--dir") > 1:
    print("Arguments can only be specified once")
    exit(1)
else:
    resdir = os.getcwd()

# check if actually a Godot project

if not os.path.isfile(resdir + "/project.godot"):
    print("You need to specify/be in a Godot project root!")
    exit(1)

if sys.argv.count("--scenes") == 1:
    scenes = sys.argv[sys.argv.index("--scenes") - len(sys.argv) + 1:]
elif sys.argv.count("--scenes") > 1:
    print("Arguments can only be specified once")
    exit(1)
else:
    scenes = []
    for file in list(pathlib.Path(resdir).rglob("*.tscn")):
        filename = os.path.abspath(str(file))[len(resdir)+1:]
        scenes.append(filename)

if sys.argv.count("--debug") == 1:
    print("Debugging mode on - Verbosity increased")
    debug=True
elif sys.argv.count("--debug") > 1:
    print("Arguments can only be specified once")
    exit(1)
else:
    debug=False

if debug:
    print("res:// path - " + resdir)
    print("")

print("Checking scenes " + ", ".join(scenes) + ", is this right? [y/n]")
if not (input().lower() == "y"):
    print("Okay then!")
    exit(0)

for scene in scenes:
    # read and then delete file
    file = open(resdir + "/" + scene, "r+")
    lines = file.readlines()
    file.close()
    file = open(resdir + "/" + scene, "w").close()
    file = open(resdir + "/" + scene, "r+")
    # list broken IDs
    emptyIDs = []

    for line in lines:
        # find [ext_resource] tags
        if not re.search("\[ext_resource", line):
            # remove referenced to external resource tags that no longer exist
            resource_id = re.search("ExtResource\([^\)]*\)", line)
            if resource_id:
                # get id and check it against nonexistent ids
                resource_id = re.search("\"[^\"]*", resource_id.group(0)).group(0)[1:]
                if debug:
                    print(resource_id)
                if not resource_id in emptyIDs:
                    file.write(line)
            else:
                file.write(line)
        else:
            path = re.search("path=\"[^\"]*\"", line).group(0)
            path = re.search("res:\/\/[^\"]*", path).group(0)
            path = path[6:]
            if debug:
                print(path)
            # check if referenced resource exists
            if os.path.isfile(resdir + "/" + path):
                file.write(line)
            else:
                # else - add the id so it can be removed
                emptyIDs.append(re.search("\"[^\"]*", re.search("id=\"[^\"]*\"", line).group(0)).group(0)[1:])
