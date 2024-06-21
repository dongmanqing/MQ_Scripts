"""
Log all the events which occurs in the short term.
"""

import json
from typing import List

from tritium.world import World


def generate_state_string(recognised_people, n_people):
    if n_people == 0:
        return "Ameca is not sure who it is speaking to."
    else:
        out_str = "Ameca is talking to "
        n_unrecognised_people = n_people - len(recognised_people)
        if len(recognised_people) > 0:
            out_str += ", ".join(recognised_people)
            if n_unrecognised_people == 1:
                out_str += " and one person it does not recognise."
            elif n_unrecognised_people > 1:
                out_str += " and {n_unrecognised_people} people it does not recognise."
            else:
                out_str += "."
        else:
            if n_people == 1:
                out_str += "one person it does not recognise."
            else:
                out_str += "{n_unrecognised_people} people it does not recognise."
    return out_str


class WorldState:
    def __init__(self):
        self.world = World("world transient memory")
        self.sub = self.world.watch(self.world.get_features("faces"))

    def get_world_state_str(self):
        s = self.sub.latest("faces")
        if s is not None:
            n_people = 0
            recognised_people = []
            for face in s.detections:
                if face.name is not None and face.name != "Unknown":
                    recognised_people.append(face.name)
                n_people += 1

            state = generate_state_string(recognised_people, n_people)
            return state
        else:
            return "Ameca cannot see anything around it."

    def identify_speaker(self):
        s = self.sub.latest("faces")
        if s is not None:
            return " or ".join((f"Person {face.identifier}" for face in s.detections))
        else:
            return "Unknown Person"

    def get_profiles(self, person_identifier=None):
        s = self.sub.latest("faces")
        if not s and person_identifier is None:
            return {}
        if person_identifier is None:
            return json.dumps(
                {
                    f"Person {face.identifier}": json.loads(face._info)
                    if face._info is not None
                    else None
                    for face in s.detections
                }
            )
        else:
            faces = [
                face for face in s.detections if face.identifier == person_identifier
            ]
            if len(faces) == 1 and faces[0]._info is not None:
                return json.loads(faces[0]._info)
            else:
                return {}


world_state = WorldState()
get_world_state = world_state.get_world_state_str
get_speaker = world_state.identify_speaker
get_profiles = world_state.get_profiles