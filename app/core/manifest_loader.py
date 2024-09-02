import os
import json

from app.models.manifest import Manifest


def load_manifests(directory: str) -> dict[str, Manifest]:
    manifests = {}
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), "r") as file:
                manifest_data = json.load(file)
                manifest = Manifest(**manifest_data)
                if (
                    manifest.name in manifests
                    and manifest.version > manifests[manifest.name].version
                ):
                    manifests[manifest.name] = manifest
                    continue
                manifests[manifest.name] = manifest
    return manifests


def load_all_manifests(directories: list[str]):
    manifests = {}
    for directory in directories:
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                with open(os.path.join(directory, filename), "r") as file:
                    manifest_data = json.load(file)
                    manifest = {
                        "version": manifest_data["version"],
                        "manifest": manifest_data,
                    }
                    if manifest_data["name"] not in manifests:
                        manifests[manifest_data["name"]] = []
                    manifests[manifest_data["name"]].append(manifest)
    return manifests


manifests = load_manifests("manifests")
