import argparse
import csv
import math
import os
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from statistics import mean

try:
    from wordfreq import zipf_frequency

    HAS_WORDFREQ = True
except ImportError:
    HAS_WORDFREQ = False

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
ICD_CODE_LETTER_PATTERN = re.compile(r"^\s*([A-Za-z])")

ICD_CHAPTER_BY_LETTER = {
    "A": "infectious_parasitic",
    "B": "infectious_parasitic",
    "C": "neoplasms",
    "D": "neoplasms_blood",
    "E": "endocrine_nutritional_metabolic",
    "F": "mental_behavioral",
    "G": "nervous_system",
    "H": "eye_ear_mastoid",
    "I": "circulatory_system",
    "J": "respiratory_system",
    "K": "digestive_system",
    "L": "skin_subcutaneous",
    "M": "musculoskeletal_connective",
    "N": "genitourinary_system",
    "O": "pregnancy_childbirth_puerperium",
    "P": "perinatal_conditions",
    "Q": "congenital_chromosomal",
    "R": "symptoms_signs_abnormal_findings",
    "S": "injury_poisoning_external_consequences",
    "T": "injury_poisoning_external_consequences",
    "U": "reserved_emergency_additions",
    "V": "external_causes",
    "W": "external_causes",
    "X": "external_causes",
    "Y": "external_causes",
    "Z": "factors_influencing_health_status",
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "without",
    "due",
    "caused",
    "cause",
    "causing",
    "other",
    "its",
    "not",
    "no",
}

ANATOMY_TOKENS = {
    "head",
    "neck",
    "chest",
    "abdomen",
    "pelvis",
    "spine",
    "arm",
    "forearm",
    "hand",
    "femur",
    "thigh",
    "knee",
    "leg",
    "ankle",
    "foot",
    "toe",
    "shoulder",
    "wrist",
    "eye",
    "ear",
    "nose",
    "mouth",
    "throat",
    "lung",
    "heart",
    "liver",
    "kidney",
    "skin",
    "bone",
    "joint",
    "nerve",
    "muscle",
    "tendon",
}

INJURY_TOKENS = {
    "fracture",
    "fx",
    "dislocation",
    "sprain",
    "strain",
    "laceration",
    "contusion",
    "puncture",
    "wound",
    "burn",
    "corrosion",
    "injury",
    "trauma",
    "avulsion",
    "rupture",
}

ENCOUNTER_TOKENS = {
    "encounter",
    "encntr",
    "initial",
    "init",
    "subsequent",
    "subs",
    "sequela",
    "sequelae",
    "sqla",
    "routine",
    "delayed",
}
ETIOLOGY_TOKENS = {"due", "caused", "induced", "related", "associated", "post", "following", "secondary"}

FRACTURE_DETAIL_TOKENS = {
    "fx",
    "open",
    "closed",
    "displaced",
    "nondisplaced",
    "disp",
    "nondisp",
    "comminuted",
    "segmental",
    "transverse",
    "oblique",
    "spiral",
    "intraarticular",
    "intra-articular",
    "extraarticular",
    "extra-articular",
    "shaft",
    "neck",
    "head",
    "base",
    "epiphysis",
    "physeal",
    "styloid",
    "trochanteric",
    "subtrochanteric",
}

HEALING_TOKENS = {"healing", "heal", "nonunion", "malunion"}

QUALIFIER_TOKENS = {
    "unspecified",
    "unsp",
    "nos",
    "nec",
    "other",
    "oth",
}

TOXIC_EVENT_TOKENS = {
    "poison",
    "poisoning",
    "toxic",
    "adverse",
    "effect",
    "eff",
    "underdosing",
    "overdose",
    "envenomation",
}

TOXIC_INTENT_TOKENS = {
    "accidental",
    "acc",
    "intentional",
    "unintentional",
    "undetermined",
    "undet",
    "assault",
    "self",
    "harm",
    "selfharm",
    "slf",
    "hrm",
}

TOXIC_AGENT_TOKENS = {
    "drug",
    "drugs",
    "substance",
    "substances",
    "agent",
    "agents",
    "compound",
    "compounds",
    "medication",
    "medications",
    "antibiotics",
    "antidepressants",
    "anesthetics",
    "neuroleptics",
    "antiepileptic",
    "vaccine",
    "vaccines",
    "venom",
    "venomous",
    "snake",
    "spider",
    "food",
    "gas",
    "gases",
    "fumes",
    "vapors",
    "tobacco",
    "alcohol",
    "carbon",
    "corrosive",
    "acid",
}

DIAGNOSTIC_EVENT_TOKENS = {
    "diagnosis",
    "finding",
    "findings",
    "history",
    "screening",
    "observation",
    "status",
    "aftercare",
    "followup",
    "follow",
    "surveillance",
    "exam",
    "examination",
}

DIAGNOSTIC_CLASSIFIER_TOKENS = {
    "type",
    "ii",
    "iii",
    "iiia",
    "iiib",
    "iiic",
    "salter",
    "harris",
    "salterharris",
    "pathological",
    "stress",
    "torus",
    "bent",
    "wedge",
    "stage",
    "primary",
    "secondary",
    "age",
    "agerelated",
}

DIAGNOSTIC_CONTEXT_TOKENS = set()

CONDITION_TOKENS = {
    "disease",
    "disorder",
    "syndrome",
    "infection",
    "inflammation",
    "lesion",
    "ulcer",
    "tumor",
    "cancer",
    "deficiency",
    "pain",
    "complication",
    "failure",
    "occlusion",
}

MECHANISM_TOKENS = {
    "collision",
    "traffic",
    "transport",
    "fall",
    "bite",
    "sting",
    "burn",
    "poisoning",
    "assault",
    "explosion",
    "fire",
    "suffocation",
}

SEVERITY_TOKENS = {
    "mild",
    "moderate",
    "severe",
    "acute",
    "chronic",
    "open",
    "closed",
    "complicated",
    "uncomplicated",
    "partial",
    "isolated",
}
LATERALITY_TOKENS = {"left", "right", "bilateral", "unilateral", "lt", "rt"}
LOCATION_TOKENS = {
    "anterior",
    "posterior",
    "medial",
    "lateral",
    "proximal",
    "distal",
    "superior",
    "inferior",
    "upper",
    "lower",
    "inner",
    "outer",
    "central",
    "peripheral",
}

PROCEDURE_TOKENS = {
    "procedure",
    "procedural",
    "postoperative",
    "operation",
    "intervention",
    "fixation",
    "implant",
    "prosthetic",
    "device",
    "graft",
    "transplant",
    "fusion",
    "arthroplasty",
    "resection",
    "insertion",
    "removal",
    "replacement",
    "surgical",
    "surgery",
}

COMPLICATION_TOKENS = {
    "complication",
    "infection",
    "hemorrhage",
    "sepsis",
    "failure",
    "reaction",
    "breakdown",
    "loosening",
    "malfunction",
    "displacement",
    "retention",
}

CONDITION_HIGH_TOKENS = set()
CONDITION_LOW_TOKENS = set()
ADJECTIVAL_CONDITION_TOKENS = set()
CONDITION_ADJECTIVE_TOKENS = set()
ANATOMY_PREFIX_TOKENS = set()

LOCATION_PREFIX_TOKENS = {
    "acro",
    "ante",
    "circum",
    "dextro",
    "dia",
    "dorsi",
    "dorso",
    "ecto",
    "endo",
    "epi",
    "exo",
    "extra",
    "infra",
    "inter",
    "intra",
    "juxta",
    "meso",
    "meta",
    "para",
    "peri",
    "post",
    "pre",
    "retro",
    "sub",
    "supra",
    "trans",
}

TEMPLATE_FAMILY_SPECS = {
    "diagnostic_event_x_condition_x_diagnostic_context": [
        ("diagnostic_event", DIAGNOSTIC_EVENT_TOKENS),
        ("condition", CONDITION_TOKENS),
        ("diagnostic_context", DIAGNOSTIC_CONTEXT_TOKENS),
    ],
    "qualifier_x_diagnostic_event_x_condition_x_diagnostic_context": [
        ("qualifier", QUALIFIER_TOKENS),
        ("diagnostic_event", DIAGNOSTIC_EVENT_TOKENS),
        ("condition", CONDITION_TOKENS),
        ("diagnostic_context", DIAGNOSTIC_CONTEXT_TOKENS),
    ],
    "diagnostic_classifier_x_anatomy_x_injury_x_diagnostic_event": [
        ("diagnostic_classifier", DIAGNOSTIC_CLASSIFIER_TOKENS),
        ("anatomy", ANATOMY_TOKENS),
        ("injury", INJURY_TOKENS),
        ("diagnostic_event", DIAGNOSTIC_EVENT_TOKENS),
    ],
    "anatomy_x_injury_x_diagnostic_event": [
        ("anatomy", ANATOMY_TOKENS),
        ("injury", INJURY_TOKENS),
        ("diagnostic_event", DIAGNOSTIC_EVENT_TOKENS),
    ],
    "injury_x_healing_x_diagnostic_event": [
        ("injury", INJURY_TOKENS),
        ("healing", HEALING_TOKENS),
        ("diagnostic_event", DIAGNOSTIC_EVENT_TOKENS),
    ],
    "anatomy_x_condition_x_diagnostic_event": [
        ("anatomy", ANATOMY_TOKENS),
        ("condition", CONDITION_TOKENS),
        ("diagnostic_event", DIAGNOSTIC_EVENT_TOKENS),
    ],
    "diagnostic_event_x_condition": [
        ("diagnostic_event", DIAGNOSTIC_EVENT_TOKENS),
        ("condition", CONDITION_TOKENS),
    ],
    "diagnostic_event_x_injury": [
        ("diagnostic_event", DIAGNOSTIC_EVENT_TOKENS),
        ("injury", INJURY_TOKENS),
    ],
    "toxic_event_x_agent_x_intent_x_encounter": [
        ("toxic_event", TOXIC_EVENT_TOKENS),
        ("toxic_agent", TOXIC_AGENT_TOKENS),
        ("toxic_intent", TOXIC_INTENT_TOKENS),
        ("encounter", ENCOUNTER_TOKENS),
    ],
    "toxic_event_x_intent_x_encounter": [
        ("toxic_event", TOXIC_EVENT_TOKENS),
        ("toxic_intent", TOXIC_INTENT_TOKENS),
        ("encounter", ENCOUNTER_TOKENS),
    ],
    "toxic_event_x_agent_x_encounter": [
        ("toxic_event", TOXIC_EVENT_TOKENS),
        ("toxic_agent", TOXIC_AGENT_TOKENS),
        ("encounter", ENCOUNTER_TOKENS),
    ],
    "qualifier_x_toxic_event_x_intent_x_encounter": [
        ("qualifier", QUALIFIER_TOKENS),
        ("toxic_event", TOXIC_EVENT_TOKENS),
        ("toxic_intent", TOXIC_INTENT_TOKENS),
        ("encounter", ENCOUNTER_TOKENS),
    ],
    "toxic_event_x_encounter": [("toxic_event", TOXIC_EVENT_TOKENS), ("encounter", ENCOUNTER_TOKENS)],
    "qualifier_x_anatomy_x_injury_x_encounter": [
        ("qualifier", QUALIFIER_TOKENS),
        ("anatomy", ANATOMY_TOKENS),
        ("injury", INJURY_TOKENS),
        ("encounter", ENCOUNTER_TOKENS),
    ],
    "qualifier_x_injury_x_encounter": [
        ("qualifier", QUALIFIER_TOKENS),
        ("injury", INJURY_TOKENS),
        ("encounter", ENCOUNTER_TOKENS),
    ],
    "qualifier_x_anatomy_x_condition": [
        ("qualifier", QUALIFIER_TOKENS),
        ("anatomy", ANATOMY_TOKENS),
        ("condition", CONDITION_TOKENS),
    ],
    "qualifier_x_condition": [("qualifier", QUALIFIER_TOKENS), ("condition", CONDITION_TOKENS)],
    "anatomy_x_injury_x_fracture_detail_x_healing_x_encounter": [
        ("anatomy", ANATOMY_TOKENS),
        ("injury", INJURY_TOKENS),
        ("fracture_detail", FRACTURE_DETAIL_TOKENS),
        ("healing", HEALING_TOKENS),
        ("encounter", ENCOUNTER_TOKENS),
    ],
    "anatomy_x_injury_x_fracture_detail_x_encounter": [
        ("anatomy", ANATOMY_TOKENS),
        ("injury", INJURY_TOKENS),
        ("fracture_detail", FRACTURE_DETAIL_TOKENS),
        ("encounter", ENCOUNTER_TOKENS),
    ],
    "anatomy_x_injury_x_healing_x_encounter": [
        ("anatomy", ANATOMY_TOKENS),
        ("injury", INJURY_TOKENS),
        ("healing", HEALING_TOKENS),
        ("encounter", ENCOUNTER_TOKENS),
    ],
    "anatomy_x_injury_x_encounter": [("anatomy", ANATOMY_TOKENS), ("injury", INJURY_TOKENS), ("encounter", ENCOUNTER_TOKENS)],
    "etiology_x_condition": [("etiology", ETIOLOGY_TOKENS), ("condition", CONDITION_TOKENS)],
    "injury_x_encounter": [("injury", INJURY_TOKENS), ("encounter", ENCOUNTER_TOKENS)],
    "anatomy_x_condition": [("anatomy", ANATOMY_TOKENS), ("condition", CONDITION_TOKENS)],
    "procedure_x_complication": [("procedure", PROCEDURE_TOKENS), ("complication", COMPLICATION_TOKENS)],
    "mechanism_x_injury": [("mechanism", MECHANISM_TOKENS), ("injury", INJURY_TOKENS)],
    "anatomy_x_condition_low": [("anatomy", ANATOMY_TOKENS), ("condition_low", CONDITION_LOW_TOKENS)],
    "condition_adjective_x_condition_high": [("condition_adjective", CONDITION_ADJECTIVE_TOKENS), ("condition_high", CONDITION_HIGH_TOKENS)],
    "anatomy_x_adjectival_condition": [("anatomy", ANATOMY_TOKENS), ("adjectival_condition", ADJECTIVAL_CONDITION_TOKENS)],
    "location_x_anatomy_x_condition": [("location", LOCATION_TOKENS), ("anatomy", ANATOMY_TOKENS), ("condition", CONDITION_TOKENS)],
    "anatomy_prefix_x_condition": [("anatomy_prefix", ANATOMY_PREFIX_TOKENS), ("condition", CONDITION_TOKENS)],
}

SLOT_TAXONOMY = {
    "qualifier": QUALIFIER_TOKENS,
    "diagnostic_event": DIAGNOSTIC_EVENT_TOKENS,
    "diagnostic_classifier": DIAGNOSTIC_CLASSIFIER_TOKENS,
    "diagnostic_context": DIAGNOSTIC_CONTEXT_TOKENS,
    "toxic_event": TOXIC_EVENT_TOKENS,
    "toxic_intent": TOXIC_INTENT_TOKENS,
    "toxic_agent": TOXIC_AGENT_TOKENS,
    "anatomy": ANATOMY_TOKENS,
    "injury": INJURY_TOKENS,
    "fracture_detail": FRACTURE_DETAIL_TOKENS,
    "healing": HEALING_TOKENS,
    "encounter": ENCOUNTER_TOKENS,
    "etiology": ETIOLOGY_TOKENS,
    "condition": CONDITION_TOKENS,
    "mechanism": MECHANISM_TOKENS,
    "severity": SEVERITY_TOKENS,
    "laterality": LATERALITY_TOKENS,
    "location": LOCATION_TOKENS,
    "procedure": PROCEDURE_TOKENS,
    "complication": COMPLICATION_TOKENS,
    "condition_high": CONDITION_HIGH_TOKENS,
    "condition_low": CONDITION_LOW_TOKENS,
    "adjectival_condition": ADJECTIVAL_CONDITION_TOKENS,
    "condition_adjective": CONDITION_ADJECTIVE_TOKENS,
    "anatomy_prefix": ANATOMY_PREFIX_TOKENS,
}

SLOT_PREFIX_TAXONOMY = {
    "anatomy_prefix": ANATOMY_PREFIX_TOKENS,
    "location": LOCATION_PREFIX_TOKENS,
}

SINGLE_SLOT_FAMILY_SPECS = {f"single_slot_{slot}": [(slot, vocab)] for slot, vocab in SLOT_TAXONOMY.items()}

XML_ENTITY_SLOT_RULES = {
    "healthcare/anatomy_singular": [("anatomy", "token")],
    "healthcare/anatomy_plural": [("anatomy", "token")],
    "healthcare/anatomical_adjectives_final": [("anatomy", "token")],
    "healthcare/prefixable_anatomical_adjectives": [("anatomy", "token")],
    "healthcare/anatomy_locations": [("anatomy", "token"), ("location", "token")],
    "healthcare/anatomical_roots": [("anatomy_prefix", "prefix")],
    "healthcare/conditions/the_big_list": [("condition", "token")],
    "healthcare/conditions/the_omas": [("condition", "token"), ("condition_high", "token")],
    "healthcare/conditions/the_emias": [("condition", "token")],
    "healthcare/prefixable_ailments": [("condition", "token")],
    "healthcare/conditions_high": [("condition", "token"), ("condition_high", "token")],
    "healthcare/conditions_low": [("condition", "token"), ("condition_low", "token")],
    "healthcare/adjectival_conditions": [("adjectival_condition", "token")],
    "healthcare/condition_adjectives": [("condition_adjective", "token"), ("severity", "token")],
    "healthcare/surgeries": [("procedure", "token")],
}

AUTO_FAMILY_SLOT_PRIORITY = [
    "qualifier",
    "diagnostic_event",
    "diagnostic_classifier",
    "diagnostic_context",
    "toxic_event",
    "toxic_intent",
    "toxic_agent",
    "anatomy",
    "injury",
    "fracture_detail",
    "healing",
    "condition",
    "encounter",
    "etiology",
    "mechanism",
    "severity",
    "laterality",
    "location",
    "procedure",
    "complication",
    "condition_high",
    "condition_low",
    "adjectival_condition",
    "condition_adjective",
    "anatomy_prefix",
]

ALL_KNOWN_CHAPTER_LETTERS = set(ICD_CHAPTER_BY_LETTER)
INJURY_CHAPTER_LETTERS = {"S", "T"}
EXTERNAL_CAUSE_CHAPTER_LETTERS = {"V", "W", "X", "Y"}
NEOPLASM_CHAPTER_LETTERS = {"C", "D"}
PREGNANCY_PERINATAL_CHAPTER_LETTERS = {"O", "P"}
CONGENITAL_CHAPTER_LETTERS = {"Q"}
SYMPTOM_CHAPTER_LETTERS = {"R"}
CONTACT_SERVICE_CHAPTER_LETTERS = {"Z"}
INFECTIOUS_CHAPTER_LETTERS = {"A", "B"}

# Phase 2 metadata: chapter compatibility policy is defined but not yet used for ranking/gating.
FAMILY_CHAPTER_POLICY: dict[str, dict[str, object]] = {
    "toxic_event_x_agent_x_intent_x_encounter": {
        "allow": INJURY_CHAPTER_LETTERS | EXTERNAL_CAUSE_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.2,
        "source": "explicit",
    },
    "toxic_event_x_intent_x_encounter": {
        "allow": INJURY_CHAPTER_LETTERS | EXTERNAL_CAUSE_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.2,
        "source": "explicit",
    },
    "toxic_event_x_agent_x_encounter": {
        "allow": INJURY_CHAPTER_LETTERS | EXTERNAL_CAUSE_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.15,
        "source": "explicit",
    },
    "qualifier_x_toxic_event_x_intent_x_encounter": {
        "allow": INJURY_CHAPTER_LETTERS | EXTERNAL_CAUSE_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.15,
        "source": "explicit",
    },
    "anatomy_x_injury_x_fracture_detail_x_healing_x_encounter": {
        "allow": INJURY_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.2,
        "source": "explicit",
    },
    "anatomy_x_injury_x_fracture_detail_x_encounter": {
        "allow": INJURY_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.2,
        "source": "explicit",
    },
    "anatomy_x_injury_x_healing_x_encounter": {
        "allow": INJURY_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.15,
        "source": "explicit",
    },
    "anatomy_x_injury_x_encounter": {
        "allow": INJURY_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.1,
        "source": "explicit",
    },
    "injury_x_encounter": {
        "allow": INJURY_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.1,
        "source": "explicit",
    },
    "diagnostic_event_x_condition_x_diagnostic_context": {
        "allow": ALL_KNOWN_CHAPTER_LETTERS - EXTERNAL_CAUSE_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.05,
        "source": "explicit",
    },
    "qualifier_x_diagnostic_event_x_condition_x_diagnostic_context": {
        "allow": ALL_KNOWN_CHAPTER_LETTERS - EXTERNAL_CAUSE_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.05,
        "source": "explicit",
    },
    "diagnostic_event_x_injury": {
        "allow": INJURY_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.1,
        "source": "explicit",
    },
    "diagnostic_event_x_condition": {
        "allow": ALL_KNOWN_CHAPTER_LETTERS - EXTERNAL_CAUSE_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.0,
        "source": "explicit",
    },
    "mechanism_x_injury": {
        "allow": INJURY_CHAPTER_LETTERS | EXTERNAL_CAUSE_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.1,
        "source": "explicit",
    },
    "condition_adjective_x_condition_high": {
        "allow": ALL_KNOWN_CHAPTER_LETTERS - EXTERNAL_CAUSE_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.0,
        "source": "explicit",
    },
    # Harden high-volume diffuse auto toxic-agent families.
    "auto_toxic_agent_x_condition": {
        "allow": INJURY_CHAPTER_LETTERS | EXTERNAL_CAUSE_CHAPTER_LETTERS | CONTACT_SERVICE_CHAPTER_LETTERS | SYMPTOM_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.08,
        "source": "explicit",
    },
    "auto_toxic_agent_x_condition_x_encounter": {
        "allow": INJURY_CHAPTER_LETTERS | EXTERNAL_CAUSE_CHAPTER_LETTERS | CONTACT_SERVICE_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.12,
        "source": "explicit",
    },
    "auto_toxic_agent_x_condition_x_condition_high": {
        "allow": INJURY_CHAPTER_LETTERS | EXTERNAL_CAUSE_CHAPTER_LETTERS | CONTACT_SERVICE_CHAPTER_LETTERS | SYMPTOM_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.08,
        "source": "explicit",
    },
    "auto_toxic_agent_x_condition_x_condition_low": {
        "allow": INJURY_CHAPTER_LETTERS | EXTERNAL_CAUSE_CHAPTER_LETTERS | CONTACT_SERVICE_CHAPTER_LETTERS | SYMPTOM_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.08,
        "source": "explicit",
    },
    "auto_diagnostic_context_x_toxic_agent_x_condition": {
        "allow": INJURY_CHAPTER_LETTERS | EXTERNAL_CAUSE_CHAPTER_LETTERS | CONTACT_SERVICE_CHAPTER_LETTERS | SYMPTOM_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.08,
        "source": "explicit",
    },
    "auto_diagnostic_event_x_toxic_agent_x_condition": {
        "allow": INJURY_CHAPTER_LETTERS | EXTERNAL_CAUSE_CHAPTER_LETTERS | CONTACT_SERVICE_CHAPTER_LETTERS | SYMPTOM_CHAPTER_LETTERS,
        "block": set(),
        "weight": 1.08,
        "source": "explicit",
    },
}

# Families allowed to bypass strict chapter blocking due to broad cross-chapter usage.
CHAPTER_POLICY_STRICT_EXCEPTIONS = {
    "diagnostic_event_x_condition",
    "diagnostic_event_x_condition_x_diagnostic_context",
    "qualifier_x_diagnostic_event_x_condition_x_diagnostic_context",
    "anatomy_x_condition",
    "qualifier_x_anatomy_x_condition",
    "single_slot_condition",
    "isolated_term",
}


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall((text or "").lower())


def _normalize_chapter_policy(policy: dict[str, object] | None, source: str) -> dict[str, object]:
    if not policy:
        return {"allow": set(), "block": set(), "weight": 1.0, "source": source}
    allow = set(policy.get("allow", set()))
    block = set(policy.get("block", set()))
    weight = float(policy.get("weight", 1.0))
    return {"allow": allow, "block": block, "weight": weight, "source": str(policy.get("source", source))}


def resolve_family_chapter_policy(family_name: str, slot_names: list[str]) -> dict[str, object]:
    explicit = FAMILY_CHAPTER_POLICY.get(family_name)
    if explicit:
        return _normalize_chapter_policy(explicit, "explicit")

    slot_set = set(slot_names)
    if "toxic_event" in slot_set:
        return _normalize_chapter_policy(
            {
                "allow": INJURY_CHAPTER_LETTERS | EXTERNAL_CAUSE_CHAPTER_LETTERS,
                "block": set(),
                "weight": 1.1,
                "source": "inferred_auto",
            },
            "inferred_auto",
        )
    if "toxic_agent" in slot_set:
        return _normalize_chapter_policy(
            {
                "allow": INJURY_CHAPTER_LETTERS | EXTERNAL_CAUSE_CHAPTER_LETTERS | CONTACT_SERVICE_CHAPTER_LETTERS | SYMPTOM_CHAPTER_LETTERS,
                "block": set(),
                "weight": 1.06,
                "source": "inferred_auto",
            },
            "inferred_auto",
        )
    if "injury" in slot_set:
        return _normalize_chapter_policy(
            {
                "allow": INJURY_CHAPTER_LETTERS,
                "block": set(),
                "weight": 1.08,
                "source": "inferred_auto",
            },
            "inferred_auto",
        )
    if "diagnostic_event" in slot_set:
        return _normalize_chapter_policy(
            {
                "allow": ALL_KNOWN_CHAPTER_LETTERS - EXTERNAL_CAUSE_CHAPTER_LETTERS,
                "block": set(),
                "weight": 1.03,
                "source": "inferred_auto",
            },
            "inferred_auto",
        )

    if "condition_high" in slot_set and ("cancer" in family_name or "neoplasm" in family_name or "tumor" in family_name):
        return _normalize_chapter_policy(
            {
                "allow": NEOPLASM_CHAPTER_LETTERS,
                "block": set(),
                "weight": 1.08,
                "source": "inferred_auto",
            },
            "inferred_auto",
        )

    if "condition" in slot_set:
        return _normalize_chapter_policy(
            {
                "allow": ALL_KNOWN_CHAPTER_LETTERS - EXTERNAL_CAUSE_CHAPTER_LETTERS,
                "block": set(),
                "weight": 1.0,
                "source": "inferred_auto",
            },
            "inferred_auto",
        )

    return _normalize_chapter_policy(None, "default")


def evaluate_chapter_policy(
    chapter_letter: str | None,
    policy: dict[str, object],
    chapter_policy_mode: str,
    family_name: str,
) -> tuple[str, float]:
    if chapter_policy_mode == "off":
        return "off", 1.0
    if not chapter_letter:
        return "unknown", 1.0

    allow = set(policy.get("allow", set()))
    block = set(policy.get("block", set()))
    weight = float(policy.get("weight", 1.0))

    strict_exempt = family_name in CHAPTER_POLICY_STRICT_EXCEPTIONS

    if chapter_letter in block:
        if chapter_policy_mode == "strict" and not strict_exempt:
            return "blocked_strict", 0.0
        return "blocked_penalized", 0.9
    if allow:
        if chapter_letter in allow:
            return "compatible", max(0.95, weight)
        if chapter_policy_mode == "strict" and not strict_exempt:
            return "blocked_strict", 0.0
        return "outside_allow_penalized", 0.93
    return "neutral", 1.0


def extract_icd_chapter_letter(code: str) -> str | None:
    match = ICD_CODE_LETTER_PATTERN.match((code or "").strip())
    if not match:
        return None
    letter = match.group(1).upper()
    if letter not in ICD_CHAPTER_BY_LETTER:
        return None
    return letter


def extract_icd_chapter_group(code: str) -> str:
    letter = extract_icd_chapter_letter(code)
    if not letter:
        return "unknown"
    return ICD_CHAPTER_BY_LETTER.get(letter, "unknown")


def is_code_like_token(token: str) -> bool:
    if token.isdigit():
        return True
    if any(ch.isdigit() for ch in token) and len(token) <= 5:
        return True
    return False


def english_zipf(term: str, cache: dict[str, float]) -> float:
    if term in cache:
        return cache[term]
    if HAS_WORDFREQ:
        score = float(zipf_frequency(term, "en"))
        score = max(0.0, min(8.0, score))
    else:
        score = 1.0
    cache[term] = score
    return score


def zipf_to_probability(zipf_value: float) -> float:
    return max(1e-12, 10 ** (zipf_value - 9.0))


def safe_log2_ratio(numerator: float, denominator: float) -> float:
    return math.log2(max(1e-12, numerator) / max(1e-12, denominator))


def normalize_match_stem(token: str) -> str:
    token = token.lower()
    if len(token) <= 4:
        return token
    if token.endswith("ies") and len(token) > 5:
        return token[:-3] + "y"
    if token.endswith("ing") and len(token) > 6:
        return token[:-3]
    if token.endswith("ed") and len(token) > 5:
        return token[:-2]
    if token.endswith("ion") and len(token) > 6:
        return token[:-3]
    if token.endswith("s") and len(token) > 5:
        return token[:-1]
    return token


def build_slot_matchers(specs: dict[str, list[tuple[str, set[str]]]]) -> dict[str, list[tuple[str, set[str], dict[str, set[str]]]]]:
    matchers = {}
    for family_name, slot_specs in specs.items():
        prepared = []
        for slot_name, vocab in slot_specs:
            stem_index = defaultdict(set)
            for token in vocab:
                stem_index[normalize_match_stem(token)].add(token)
            prepared.append((slot_name, vocab, dict(stem_index)))
        matchers[family_name] = prepared
    return matchers


def token_matches_slot(token: str, slot_name: str, vocab: set[str], stem_index: dict[str, set[str]], match_mode: str) -> bool:
    if token in vocab:
        return True
    if match_mode == "fuzzy" and normalize_match_stem(token) in stem_index:
        return True
    prefix_vocab = SLOT_PREFIX_TAXONOMY.get(slot_name, set())
    for prefix in prefix_vocab:
        if token.startswith(prefix) and len(token) >= len(prefix) + 2:
            return True
    return False


def detect_slot_fillers(tokens: list[str], slot_specs: list[tuple[str, set[str], dict[str, set[str]]]], match_mode: str):
    fillers = {}
    used_fuzzy = False
    ambiguous = False
    for slot_name, vocab, stem_index in slot_specs:
        exact = []
        seen = set()
        for token in tokens:
            if token in vocab and token not in seen:
                seen.add(token)
                exact.append(token)
        if exact:
            fillers[slot_name] = exact[0]
            continue

        if match_mode != "fuzzy":
            return None, False, False

        fuzzy = []
        seen_fuzzy = set()
        for token in tokens:
            stem = normalize_match_stem(token)
            for cand in sorted(stem_index.get(stem, set())):
                if cand not in seen_fuzzy:
                    seen_fuzzy.add(cand)
                    fuzzy.append(cand)

        if not fuzzy:
            prefix_candidates = []
            prefix_vocab = SLOT_PREFIX_TAXONOMY.get(slot_name, set())
            for token in tokens:
                if any(token.startswith(prefix) and len(token) >= len(prefix) + 2 for prefix in prefix_vocab):
                    prefix_candidates.append(token)
            if not prefix_candidates:
                return None, False, False
            fillers[slot_name] = prefix_candidates[0]
            used_fuzzy = True
            ambiguous = ambiguous or len(prefix_candidates) > 1
            continue

        fillers[slot_name] = fuzzy[0]
        used_fuzzy = True
        ambiguous = ambiguous or len(fuzzy) > 1

    return fillers, used_fuzzy, ambiguous


def term_fits_family_whole(tokens: list[str], slot_specs: list[tuple[str, set[str], dict[str, set[str]]]], match_mode: str) -> bool:
    for token in tokens:
        if token in STOPWORDS:
            continue
        covered = False
        for slot_name, vocab, stem_index in slot_specs:
            if token_matches_slot(token, slot_name, vocab, stem_index, match_mode):
                covered = True
                break
        if not covered:
            return False
    return True


def load_medical_xml_slot_tokens(xml_path: str):
    slot_tokens = {slot: set() for slot in SLOT_TAXONOMY}
    entity_counts = {slot: 0 for slot in SLOT_TAXONOMY}
    entity_token_counts = defaultdict(int)

    if not xml_path or not os.path.exists(xml_path):
        return slot_tokens, entity_counts, dict(entity_token_counts)

    entity_entries = []
    try:
        root = ET.parse(xml_path).getroot()
        for entity in root.findall(".//entity"):
            name = entity.get("name", "")
            heads = [entry.get("headword", "") for entry in entity.findall("./entry") if entry.get("headword")]
            entity_entries.append((name, heads))
    except Exception as exc:
        print(f"Warning: strict XML parse failed for '{xml_path}' ({exc}); using regex fallback parser")
        with open(xml_path, "r", encoding="utf-8", errors="ignore") as f:
            raw = f.read()
        blocks = re.findall(r'<entity\s+name="([^"]+)"[^>]*>(.*?)</entity>', raw, flags=re.IGNORECASE | re.DOTALL)
        for name, block in blocks:
            heads = re.findall(r'<entry\s+headword="([^"]+)"\s*/>', block, flags=re.IGNORECASE)
            entity_entries.append((name, heads))

    for entity_name, headwords in entity_entries:
        rules = XML_ENTITY_SLOT_RULES.get(entity_name)
        if not rules:
            continue
        added_any = False
        for headword in headwords:
            head_tokens = tokenize(headword)
            if not head_tokens:
                continue
            for slot_name, mode in rules:
                added_for_rule = 0
                if mode == "prefix":
                    for token in head_tokens:
                        if len(token) < 4:
                            continue
                        slot_tokens[slot_name].add(token)
                        SLOT_PREFIX_TAXONOMY.setdefault(slot_name, set()).add(token)
                        added_for_rule += 1
                else:
                    for token in head_tokens:
                        if token in STOPWORDS or is_code_like_token(token):
                            continue
                        slot_tokens[slot_name].add(token)
                        added_for_rule += 1
                if added_for_rule > 0:
                    entity_token_counts[entity_name] += added_for_rule
                    added_any = True
        if added_any:
            for slot_name, _ in rules:
                entity_counts[slot_name] += 1

    return slot_tokens, entity_counts, dict(entity_token_counts)


def generate_auto_template_family_specs(input_path: str, min_family_terms: int, max_slots: int, max_families: int):
    combo_counts = Counter()
    slot_priority = {slot: idx for idx, slot in enumerate(AUTO_FAMILY_SLOT_PRIORITY)}

    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tokens = [t for t in tokenize(row.get("Term", "")) if t not in STOPWORDS]
            if len(tokens) < 2:
                continue

            present_slots = set()
            all_covered = True
            for token in tokens:
                token_slots = {slot for slot, vocab in SLOT_TAXONOMY.items() if token in vocab}
                if not token_slots:
                    all_covered = False
                    break
                present_slots.update(token_slots)

            if not all_covered:
                continue
            if not (2 <= len(present_slots) <= max_slots):
                continue

            combo = tuple(sorted(present_slots, key=lambda s: (slot_priority.get(s, 999), s)))
            combo_counts[combo] += 1

    existing = {tuple(slot for slot, _ in specs) for specs in TEMPLATE_FAMILY_SPECS.values()}
    auto_specs = {}
    for combo, freq in combo_counts.most_common():
        if freq < min_family_terms or combo in existing:
            continue
        name = "auto_" + "_x_".join(combo)
        auto_specs[name] = [(slot, SLOT_TAXONOMY[slot]) for slot in combo]
        if len(auto_specs) >= max_families:
            break
    return auto_specs


def build_dynamic_toxic_agent_tokens(input_path: str, min_freq: int, max_tokens: int) -> set[str]:
    toxic_marker_tokens = TOXIC_EVENT_TOKENS | {"adverse", "effect", "poisoning", "toxic", "underdosing", "overdose"}
    excluded = STOPWORDS | QUALIFIER_TOKENS | ENCOUNTER_TOKENS | TOXIC_EVENT_TOKENS | TOXIC_INTENT_TOKENS
    excluded |= {"by", "from", "with", "without", "due", "caused", "cause", "causing", "and", "or"}

    counts = Counter()
    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tokens = tokenize(row.get("Term", ""))
            if not tokens:
                continue
            if not any(token in toxic_marker_tokens for token in tokens):
                continue
            for token in tokens:
                if token in excluded:
                    continue
                if len(token) <= 2:
                    continue
                if is_code_like_token(token):
                    continue
                counts[token] += 1

    dynamic = []
    for token, freq in counts.most_common():
        if freq < min_freq:
            break
        dynamic.append(token)
        if len(dynamic) >= max_tokens:
            break
    return set(dynamic)


def build_dynamic_diagnostic_context_tokens(input_path: str, min_freq: int, max_tokens: int) -> set[str]:
    diagnostic_markers = DIAGNOSTIC_EVENT_TOKENS | {"diagnosis", "finding", "history", "screening", "observation", "status"}
    excluded = STOPWORDS | QUALIFIER_TOKENS | ENCOUNTER_TOKENS
    excluded |= CONDITION_TOKENS | INJURY_TOKENS | ANATOMY_TOKENS | DIAGNOSTIC_EVENT_TOKENS | DIAGNOSTIC_CLASSIFIER_TOKENS
    excluded |= {"because", "caused", "due", "for", "with", "without", "and", "or", "of", "the"}

    counts = Counter()
    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tokens = tokenize(row.get("Term", ""))
            if not tokens:
                continue
            if not any(token in diagnostic_markers for token in tokens):
                continue
            for token in tokens:
                if token in excluded:
                    continue
                if len(token) <= 2:
                    continue
                if is_code_like_token(token):
                    continue
                counts[token] += 1

    dynamic = []
    for token, freq in counts.most_common():
        if freq < min_freq:
            break
        dynamic.append(token)
        if len(dynamic) >= max_tokens:
            break
    return set(dynamic)


def extract_template_family_stats(
    input_path: str,
    doc_count: int,
    unigram_df: Counter,
    zipf_cache: dict[str, float],
    match_mode: str,
    min_template_freq: int,
    include_single_slot_families: bool,
    include_isolated_terms_family: bool,
    collect_assignments: bool,
    extra_family_specs: dict[str, list[tuple[str, set[str]]]] | None,
    chapter_policy_mode: str,
):
    family_specs = dict(TEMPLATE_FAMILY_SPECS)
    if extra_family_specs:
        family_specs.update(extra_family_specs)
    if include_single_slot_families:
        family_specs.update(SINGLE_SLOT_FAMILY_SPECS)

    matchers = build_slot_matchers(family_specs)
    family_policy_cache = {
        family_name: resolve_family_chapter_policy(
            family_name, [slot for slot, _, _ in slot_specs]
        )
        for family_name, slot_specs in matchers.items()
    }

    family_term_counts = Counter()
    family_code_sets = defaultdict(set)
    family_dist_sum = defaultdict(float)
    family_instance_counts = defaultdict(Counter)
    family_instance_dist_sum = defaultdict(lambda: defaultdict(float))
    family_instance_code_sets = defaultdict(lambda: defaultdict(set))

    family_term_ids = defaultdict(set)
    family_fuzzy_ids = defaultdict(set)
    family_ambiguous_ids = defaultdict(set)
    matched_ids = set()
    fuzzy_ids = set()
    ambiguous_ids = set()
    assignment_rows = []
    blocked_chapter_candidates = 0

    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row_idx, row in enumerate(reader, start=1):
            term = row.get("Term", "")
            code = row.get("ICD10CMCode", "")
            chapter_letter = extract_icd_chapter_letter(code)
            chapter_group = extract_icd_chapter_group(code)
            tokens = tokenize(term)
            if not tokens:
                continue

            candidates = []
            for family_name, slot_specs in matchers.items():
                if family_name.startswith("single_slot_") and len(tokens) != 1:
                    continue

                fillers, used_fuzzy, ambiguous = detect_slot_fillers(tokens, slot_specs, match_mode)
                if fillers is None:
                    continue
                if not term_fits_family_whole(tokens, slot_specs, match_mode):
                    continue

                slot_scores = []
                for slot_token in fillers.values():
                    df = unigram_df.get(slot_token, 0)
                    p_domain = (df + 0.5) / (doc_count + 1.0)
                    p_english = zipf_to_probability(english_zipf(slot_token, zipf_cache))
                    slot_scores.append(safe_log2_ratio(p_domain, p_english))

                instance_key = " | ".join(f"{slot}={fillers[slot]}" for slot, _, _ in slot_specs)
                policy = family_policy_cache.get(family_name, {"allow": set(), "block": set(), "weight": 1.0, "source": "default"})
                chapter_outcome, chapter_factor = evaluate_chapter_policy(
                    chapter_letter,
                    policy,
                    chapter_policy_mode,
                    family_name,
                )
                if chapter_outcome == "blocked_strict":
                    blocked_chapter_candidates += 1
                    continue
                base_distinctiveness = mean(slot_scores)
                chapter_adjusted_distinctiveness = base_distinctiveness * chapter_factor
                candidates.append(
                    {
                        "family": family_name,
                        "specificity": len(slot_specs),
                        "distinctiveness": base_distinctiveness,
                        "chapter_adjusted_distinctiveness": chapter_adjusted_distinctiveness,
                        "chapter_policy_outcome": chapter_outcome,
                        "chapter_policy_factor": chapter_factor,
                        "instance": instance_key,
                        "used_fuzzy": used_fuzzy,
                        "ambiguous": ambiguous,
                    }
                )

            if include_isolated_terms_family and len(tokens) == 1:
                token = tokens[0]
                if token not in STOPWORDS and not is_code_like_token(token):
                    df = unigram_df.get(token, 0)
                    p_domain = (df + 0.5) / (doc_count + 1.0)
                    p_english = zipf_to_probability(english_zipf(token, zipf_cache))
                    candidates.append(
                        {
                            "family": "isolated_term",
                            "specificity": 1,
                            "distinctiveness": safe_log2_ratio(p_domain, p_english),
                            "chapter_adjusted_distinctiveness": safe_log2_ratio(p_domain, p_english),
                            "chapter_policy_outcome": "neutral",
                            "chapter_policy_factor": 1.0,
                            "instance": f"token={token}",
                            "used_fuzzy": False,
                            "ambiguous": False,
                        }
                    )

            if not candidates:
                continue

            best = max(
                candidates,
                key=lambda c: (
                    c["specificity"],
                    c["chapter_adjusted_distinctiveness"],
                    c["distinctiveness"],
                    c["family"],
                ),
            )
            ranked = sorted(
                candidates,
                key=lambda c: (
                    c["specificity"],
                    c["chapter_adjusted_distinctiveness"],
                    c["distinctiveness"],
                    c["family"],
                ),
                reverse=True,
            )
            runner = ranked[1] if len(ranked) > 1 else None

            family = best["family"]
            matched_ids.add(row_idx)
            family_term_ids[family].add(row_idx)
            if best["used_fuzzy"]:
                fuzzy_ids.add(row_idx)
                family_fuzzy_ids[family].add(row_idx)
            if best["ambiguous"]:
                ambiguous_ids.add(row_idx)
                family_ambiguous_ids[family].add(row_idx)

            family_term_counts[family] += 1
            family_dist_sum[family] += best["distinctiveness"]
            if code:
                family_code_sets[family].add(code)
            family_instance_counts[family][best["instance"]] += 1
            family_instance_dist_sum[family][best["instance"]] += best["distinctiveness"]
            if code:
                family_instance_code_sets[family][best["instance"]].add(code)

            if collect_assignments:
                policy = family_policy_cache.get(family, {"allow": set(), "block": set(), "weight": 1.0, "source": "default"})
                allow_text = "|".join(sorted(policy["allow"])) if policy["allow"] else ""
                block_text = "|".join(sorted(policy["block"])) if policy["block"] else ""
                assignment_rows.append(
                    {
                        "row_id": row_idx,
                        "icd10cm_code": code,
                        "icd_chapter_letter": chapter_letter or "",
                        "icd_chapter_group": chapter_group,
                        "term": term,
                        "assigned_family": family,
                        "specificity": best["specificity"],
                        "distinctiveness": round(best["distinctiveness"], 6),
                        "instance": best["instance"],
                        "candidate_count": len(candidates),
                        "used_fuzzy": int(best["used_fuzzy"]),
                        "ambiguous": int(best["ambiguous"]),
                        "runner_up_family": runner["family"] if runner else "",
                        "runner_up_specificity": runner["specificity"] if runner else "",
                        "runner_up_distinctiveness": round(runner["distinctiveness"], 6) if runner else "",
                        "chapter_policy_outcome": best["chapter_policy_outcome"],
                        "chapter_adjusted_score": round(best["chapter_adjusted_distinctiveness"], 6),
                        "family_chapter_allow": allow_text,
                        "family_chapter_block": block_text,
                        "family_chapter_weight": round(float(policy["weight"]), 4),
                        "family_chapter_policy_source": policy["source"],
                        "rule": "max_specificity_then_distinctiveness",
                    }
                )

    family_rows = []
    for family, count in family_term_counts.items():
        if count < min_template_freq:
            continue
        avg_dist = family_dist_sum[family] / count
        uniq_codes = len(family_code_sets[family])
        coverage_ratio = count / max(1, doc_count)
        uniq_terms = len(family_term_ids[family])
        uniq_ratio = uniq_terms / max(1, doc_count)
        fuzzy_share = len(family_fuzzy_ids[family]) / max(1, uniq_terms)
        ambiguity_share = len(family_ambiguous_ids[family]) / max(1, uniq_terms)
        score = math.log1p(count) * avg_dist * (1.0 + 0.2 * math.log1p(uniq_codes))
        top_instances = "; ".join(f"{inst} ({freq})" for inst, freq in family_instance_counts[family].most_common(5))
        family_rows.append(
            {
                "template_family": family,
                "coverage_terms": count,
                "coverage_ratio": round(coverage_ratio, 6),
                "family_unique_terms": uniq_terms,
                "family_unique_ratio": round(uniq_ratio, 6),
                "unique_codes": uniq_codes,
                "avg_distinctiveness": round(avg_dist, 5),
                "abbrev_noise_share": 0.0,
                "fuzzy_fill_share": round(fuzzy_share, 6),
                "ambiguity_share": round(ambiguity_share, 6),
                "score": round(score, 5),
                "top_instances": top_instances,
            }
        )
    family_rows.sort(key=lambda x: x["score"], reverse=True)

    instance_rows = []
    for family, instances in family_instance_counts.items():
        for instance, freq in instances.items():
            if freq < max(5, min_template_freq // 8):
                continue
            avg_dist = family_instance_dist_sum[family][instance] / freq
            uniq_codes = len(family_instance_code_sets[family][instance])
            coverage_ratio = freq / max(1, doc_count)
            score = math.log1p(freq) * avg_dist * (1.0 + 0.1 * math.log1p(uniq_codes))
            instance_rows.append(
                {
                    "template_family": family,
                    "template_instance": instance,
                    "coverage_terms": freq,
                    "coverage_ratio": round(coverage_ratio, 6),
                    "unique_codes": uniq_codes,
                    "avg_distinctiveness": round(avg_dist, 5),
                    "score": round(score, 5),
                }
            )
    instance_rows.sort(key=lambda x: x["score"], reverse=True)

    return {
        "template_family_rows": family_rows,
        "template_instance_rows": instance_rows,
        "matched_terms": len(matched_ids),
        "matched_ratio": len(matched_ids) / max(1, doc_count),
        "fuzzy_matched_terms": len(fuzzy_ids),
        "fuzzy_matched_ratio": len(fuzzy_ids) / max(1, doc_count),
        "ambiguous_terms": len(ambiguous_ids),
        "ambiguous_ratio": len(ambiguous_ids) / max(1, doc_count),
        "assignment_rows": assignment_rows,
        "blocked_chapter_candidates": blocked_chapter_candidates,
    }


def save_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def summarize_chapter_coverage(all_chapter_counts: Counter, assignment_rows: list[dict]) -> list[dict]:
    assigned_by_letter = Counter(row.get("icd_chapter_letter", "") or "unknown" for row in assignment_rows)
    rows = []
    letters = sorted(set(all_chapter_counts) | set(assigned_by_letter))
    for letter in letters:
        total = int(all_chapter_counts.get(letter, 0))
        assigned = int(assigned_by_letter.get(letter, 0))
        unmatched = max(0, total - assigned)
        ratio = assigned / max(1, total)
        group = ICD_CHAPTER_BY_LETTER.get(letter, "unknown") if letter != "unknown" else "unknown"
        rows.append(
            {
                "icd_chapter_letter": letter,
                "icd_chapter_group": group,
                "total_terms": total,
                "assigned_terms": assigned,
                "unmatched_terms": unmatched,
                "assigned_ratio": round(ratio, 6),
            }
        )
    rows.sort(key=lambda r: r["icd_chapter_letter"])
    return rows


def summarize_family_chapter_drift(assignment_rows: list[dict], min_family_terms: int = 200) -> list[dict]:
    family_letter_counts = defaultdict(Counter)
    family_total = Counter()
    for row in assignment_rows:
        family = row.get("assigned_family", "")
        letter = row.get("icd_chapter_letter", "") or "unknown"
        if not family:
            continue
        family_letter_counts[family][letter] += 1
        family_total[family] += 1

    drift_rows = []
    for family, total in family_total.items():
        if total < min_family_terms:
            continue
        letter_counts = family_letter_counts[family]
        top_letter, top_count = letter_counts.most_common(1)[0]
        concentration = top_count / max(1, total)
        top3 = ", ".join(f"{k}:{v}" for k, v in letter_counts.most_common(3))
        policy = FAMILY_CHAPTER_POLICY.get(family)
        allow = "|".join(sorted(policy.get("allow", set()))) if policy else ""
        drift_rows.append(
            {
                "template_family": family,
                "coverage_terms": total,
                "top_chapter_letter": top_letter,
                "top_chapter_share": round(concentration, 6),
                "top3_chapter_counts": top3,
                "chapter_policy_allow": allow,
            }
        )
    drift_rows.sort(key=lambda r: (r["top_chapter_share"], r["coverage_terms"]), reverse=True)
    return drift_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Family-only ICD compositional analysis.")
    parser.add_argument("--input", default="icd10cm_terms_2026_full_with_chv_core.csv")
    parser.add_argument("--output-dir", default="analysis_outputs")
    parser.add_argument(
        "--optionals",
        choices=["on", "off"],
        default="on",
        help="Enable all optional enrichments and policies (on) or disable them all (off).",
    )
    parser.add_argument("--progress-every", type=int, default=100000)
    args = parser.parse_args()

    optionals_on = args.optionals == "on"
    min_template_freq = 100
    max_template_instances = 400
    template_match_mode = "fuzzy" if optionals_on else "strict"
    include_single_slot = optionals_on
    include_isolated = optionals_on
    include_auto = optionals_on
    include_dynamic_toxic_agents = optionals_on
    include_dynamic_diagnostic_context = optionals_on
    chapter_policy_mode = "soft" if optionals_on else "off"
    medical_xml_path = "medical_conditions.xml" if optionals_on else ""
    auto_family_min_terms = 120
    auto_family_max_slots = 3
    auto_family_max_count = 25
    dynamic_toxic_agent_min_freq = 20
    dynamic_toxic_agent_max = 1500
    dynamic_diagnostic_context_min_freq = 10
    dynamic_diagnostic_context_max = 2500

    xml_added_tokens = {slot: 0 for slot in SLOT_TAXONOMY}
    xml_entity_counts = {slot: 0 for slot in SLOT_TAXONOMY}
    xml_entity_token_counts = {}
    medical_xml_loaded = False

    if medical_xml_path and os.path.exists(medical_xml_path):
        xml_slot_tokens, xml_entity_counts, xml_entity_token_counts = load_medical_xml_slot_tokens(medical_xml_path)
        for slot, tokens in xml_slot_tokens.items():
            before = len(SLOT_TAXONOMY[slot])
            SLOT_TAXONOMY[slot].update(tokens)
            xml_added_tokens[slot] = max(0, len(SLOT_TAXONOMY[slot]) - before)
        medical_xml_loaded = True

    dynamic_toxic_agent_count = 0
    if include_dynamic_toxic_agents:
        dynamic_toxic_agents = build_dynamic_toxic_agent_tokens(
            input_path=args.input,
            min_freq=max(1, dynamic_toxic_agent_min_freq),
            max_tokens=max(1, dynamic_toxic_agent_max),
        )
        before = len(TOXIC_AGENT_TOKENS)
        TOXIC_AGENT_TOKENS.update(dynamic_toxic_agents)
        dynamic_toxic_agent_count = max(0, len(TOXIC_AGENT_TOKENS) - before)

    dynamic_diagnostic_context_count = 0
    if include_dynamic_diagnostic_context:
        dynamic_diagnostic_context = build_dynamic_diagnostic_context_tokens(
            input_path=args.input,
            min_freq=max(1, dynamic_diagnostic_context_min_freq),
            max_tokens=max(1, dynamic_diagnostic_context_max),
        )
        before = len(DIAGNOSTIC_CONTEXT_TOKENS)
        DIAGNOSTIC_CONTEXT_TOKENS.update(dynamic_diagnostic_context)
        dynamic_diagnostic_context_count = max(0, len(DIAGNOSTIC_CONTEXT_TOKENS) - before)

    row_count = 0
    valid_terms = 0
    unigram_df = Counter()
    chapter_counts = Counter()
    with open(args.input, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_count += 1
            tokens = tokenize(row.get("Term", ""))
            if not tokens:
                continue
            valid_terms += 1
            unigram_df.update(set(tokens))
            chapter_letter = extract_icd_chapter_letter(row.get("ICD10CMCode", "")) or "unknown"
            chapter_counts[chapter_letter] += 1
            if args.progress_every > 0 and row_count % args.progress_every == 0:
                print(f"Processed {row_count:,} rows...")

    doc_count = max(1, valid_terms)
    zipf_cache = {}

    auto_specs = {}
    if include_auto:
        auto_specs = generate_auto_template_family_specs(
            input_path=args.input,
            min_family_terms=max(1, auto_family_min_terms),
            max_slots=max(2, auto_family_max_slots),
            max_families=max(1, auto_family_max_count),
        )

    selected = extract_template_family_stats(
        input_path=args.input,
        doc_count=doc_count,
        unigram_df=unigram_df,
        zipf_cache=zipf_cache,
        match_mode=template_match_mode,
        min_template_freq=min_template_freq,
        include_single_slot_families=include_single_slot,
        include_isolated_terms_family=include_isolated,
        collect_assignments=True,
        extra_family_specs=auto_specs,
        chapter_policy_mode=chapter_policy_mode,
    )
    baseline = extract_template_family_stats(
        input_path=args.input,
        doc_count=doc_count,
        unigram_df=unigram_df,
        zipf_cache=zipf_cache,
        match_mode=template_match_mode,
        min_template_freq=min_template_freq,
        include_single_slot_families=include_single_slot,
        include_isolated_terms_family=include_isolated,
        collect_assignments=False,
        extra_family_specs=None,
        chapter_policy_mode=chapter_policy_mode,
    )

    family_rows = selected["template_family_rows"]
    instance_rows = selected["template_instance_rows"]
    assignment_rows = selected["assignment_rows"]
    matched = selected["matched_terms"]
    matched_ratio = selected["matched_ratio"]
    unmatched = max(0, doc_count - matched)
    unmatched_ratio = unmatched / max(1, doc_count)

    baseline_matched = baseline["matched_terms"]
    baseline_ratio = baseline["matched_ratio"]
    auto_gain_terms = matched - baseline_matched
    auto_gain_ratio = matched_ratio - baseline_ratio

    assignment_count = len(assignment_rows)
    fuzzy_count = sum(int(row["used_fuzzy"]) for row in assignment_rows)
    ambiguous_count = sum(int(row["ambiguous"]) for row in assignment_rows)
    chapter_policy_distribution = Counter(row.get("chapter_policy_outcome", "unknown") for row in assignment_rows)
    blocked_chapter_candidates = int(selected.get("blocked_chapter_candidates", 0))
    chapter_coverage_rows = summarize_chapter_coverage(chapter_counts, assignment_rows)
    family_chapter_drift_rows = summarize_family_chapter_drift(assignment_rows, min_family_terms=max(200, min_template_freq))
    multi_candidate = sum(int(row["candidate_count"]) > 1 for row in assignment_rows)
    candidate_distribution = Counter(int(row["candidate_count"]) for row in assignment_rows)
    candidate_summary = ", ".join(
        f"{k}:{v}" for k, v in sorted(candidate_distribution.items(), key=lambda x: (-x[1], x[0]))[:5]
    )

    os.makedirs(args.output_dir, exist_ok=True)
    for name in os.listdir(args.output_dir):
        if name.endswith(".csv") or name.endswith(".md"):
            if name == "family_logic_guide.md":
                continue
            os.remove(os.path.join(args.output_dir, name))

    save_csv(
        os.path.join(args.output_dir, "template_families.csv"),
        family_rows,
        [
            "template_family",
            "coverage_terms",
            "coverage_ratio",
            "family_unique_terms",
            "family_unique_ratio",
            "unique_codes",
            "avg_distinctiveness",
            "abbrev_noise_share",
            "fuzzy_fill_share",
            "ambiguity_share",
            "score",
            "top_instances",
        ],
    )

    save_csv(
        os.path.join(args.output_dir, "template_instances.csv"),
        instance_rows[:max_template_instances],
        [
            "template_family",
            "template_instance",
            "coverage_terms",
            "coverage_ratio",
            "unique_codes",
            "avg_distinctiveness",
            "score",
        ],
    )

    save_csv(
        os.path.join(args.output_dir, "term_family_assignments.csv"),
        assignment_rows,
        [
            "row_id",
            "icd10cm_code",
            "icd_chapter_letter",
            "icd_chapter_group",
            "term",
            "assigned_family",
            "specificity",
            "distinctiveness",
            "instance",
            "candidate_count",
            "used_fuzzy",
            "ambiguous",
            "runner_up_family",
            "runner_up_specificity",
            "runner_up_distinctiveness",
            "chapter_policy_outcome",
            "chapter_adjusted_score",
            "family_chapter_allow",
            "family_chapter_block",
            "family_chapter_weight",
            "family_chapter_policy_source",
            "rule",
        ],
    )

    save_csv(
        os.path.join(args.output_dir, "chapter_coverage.csv"),
        chapter_coverage_rows,
        [
            "icd_chapter_letter",
            "icd_chapter_group",
            "total_terms",
            "assigned_terms",
            "unmatched_terms",
            "assigned_ratio",
        ],
    )

    save_csv(
        os.path.join(args.output_dir, "family_chapter_drift.csv"),
        family_chapter_drift_rows,
        [
            "template_family",
            "coverage_terms",
            "top_chapter_letter",
            "top_chapter_share",
            "top3_chapter_counts",
            "chapter_policy_allow",
        ],
    )

    with open(os.path.join(args.output_dir, "auto_family_comparison_report.md"), "w", encoding="utf-8") as f:
        f.write("# Auto Family Coverage Comparison\n\n")
        f.write(f"- Optionals mode: {args.optionals}\n")
        f.write(f"- Auto template families: {'on' if include_auto else 'off'}\n")
        f.write(f"- Generated auto families: {len(auto_specs)}\n")
        f.write(
            f"- Baseline matched terms: {baseline_matched} ({baseline_ratio:.6f})\n"
            f"- Matched terms with auto families: {matched} ({matched_ratio:.6f})\n"
            f"- Auto family gain: {auto_gain_terms} ({auto_gain_ratio:.6f})\n\n"
        )
        if auto_specs:
            f.write("## Generated families\n\n")
            for family, specs in auto_specs.items():
                f.write(f"- {family}: {', '.join(slot for slot, _ in specs)}\n")

    with open(os.path.join(args.output_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write("# Family-Only Compositional Analysis\n\n")
        f.write(f"Rows analyzed: {row_count}\n")
        f.write(f"Non-empty terms: {valid_terms}\n")
        f.write("Canonicalization: disabled\n")
        f.write("N-gram analysis: disabled\n")
        f.write(f"Optionals mode: {args.optionals}\n")
        f.write(f"Template match mode: {template_match_mode}\n")
        f.write(f"Chapter policy mode: {chapter_policy_mode}\n")
        f.write(f"Include single-slot families: {'on' if include_single_slot else 'off'}\n")
        f.write(f"Include isolated-term family: {'on' if include_isolated else 'off'}\n\n")
        f.write(f"Dynamic toxic agents: {'on' if include_dynamic_toxic_agents else 'off'} (added={dynamic_toxic_agent_count})\n\n")
        f.write(
            f"Dynamic diagnostic context: {'on' if include_dynamic_diagnostic_context else 'off'} "
            f"(added={dynamic_diagnostic_context_count})\n\n"
        )

        f.write("## XML ingestion\n\n")
        f.write(f"Medical XML vocabulary: {medical_xml_path if medical_xml_loaded else 'not loaded'}\n")
        if medical_xml_loaded:
            total_added = sum(xml_added_tokens.values())
            slot_summary = ", ".join(
                f"{slot}={xml_added_tokens[slot]}"
                for slot in [
                    "anatomy",
                    "condition",
                    "condition_high",
                    "condition_low",
                    "adjectival_condition",
                    "condition_adjective",
                    "anatomy_prefix",
                    "location",
                    "procedure",
                ]
                if xml_added_tokens.get(slot, 0) > 0
            )
            f.write(f"- XML slot tokens added: {total_added} | {slot_summary if slot_summary else 'none'}\n")

        f.write("\n## Coverage\n\n")
        f.write(f"- Terms matched by >=1 family: {matched} ({matched_ratio:.6f})\n")
        f.write(f"- Terms unmatched by all families: {unmatched} ({unmatched_ratio:.6f})\n")
        f.write(f"- Auto-family gain vs baseline: {auto_gain_terms} ({auto_gain_ratio:.6f})\n")

        f.write("\n## Assignment audit\n\n")
        f.write(f"- Assigned terms exported: {assignment_count}\n")
        f.write(f"- Multi-candidate rows: {multi_candidate} ({multi_candidate / max(1, assignment_count):.6f})\n")
        f.write(f"- Assigned via fuzzy slot fill: {fuzzy_count} ({fuzzy_count / max(1, assignment_count):.6f})\n")
        f.write(f"- Assigned with ambiguous slot fill: {ambiguous_count} ({ambiguous_count / max(1, assignment_count):.6f})\n")
        f.write(f"- Candidate-count distribution (top bins): {candidate_summary}\n")
        policy_summary = ", ".join(f"{k}:{v}" for k, v in chapter_policy_distribution.most_common())
        f.write(f"- Chapter-policy outcomes: {policy_summary}\n")
        f.write(f"- Chapter-policy strict blocks (candidate-level): {blocked_chapter_candidates}\n")

        f.write("\n## Chapter Coverage\n\n")
        for row in sorted(chapter_coverage_rows, key=lambda r: r["assigned_ratio"], reverse=True)[:12]:
            f.write(
                f"- {row['icd_chapter_letter']} ({row['icd_chapter_group']}) | "
                f"assigned={row['assigned_terms']}/{row['total_terms']} "
                f"({row['assigned_ratio']:.6f})\n"
            )

        f.write("\n## Family-Chapter Drift\n\n")
        for row in family_chapter_drift_rows[:10]:
            f.write(
                f"- {row['template_family']} | top_chapter={row['top_chapter_letter']} "
                f"share={row['top_chapter_share']:.6f} | {row['top3_chapter_counts']}\n"
            )

        f.write("\n## Top families\n\n")
        for row in family_rows[:12]:
            f.write(
                f"- {row['template_family']} | coverage={row['coverage_terms']} ({row['coverage_ratio']}) "
                f"| distinctiveness={row['avg_distinctiveness']} | score={row['score']}\n"
            )

    print(f"Family-only analysis complete. Outputs saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
