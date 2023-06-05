"""Load alignment data.

Usage: python manage.py shell < alignment_api/pipelines/load_alignments.py
"""
import os
import csv
import json

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from tqdm import tqdm

from alignment_api.models import (
    SourceToken,
    TargetToken,
    Resource,
    Alignment,
    Link,
    MediaAsset,
    Subject,
)

INTERNAL_DATA_PATH = settings.BASE_DIR / "data/internal-alignments/data"
DATA_PATH = settings.BASE_DIR / "data/alignments/data"
TEST_DATA_PATH = settings.BASE_DIR / "test_data"
CATALOG_PATH = DATA_PATH / "catalog.tsv"

SOURCES_PATH = INTERNAL_DATA_PATH / "sources"
TARGETS_PATH = INTERNAL_DATA_PATH / "targets"
CATALOG = []


def load_catalog():
    with open(CATALOG_PATH) as file:
        tsv_file = csv.reader(file, delimiter="\t")
        next(tsv_file)  # skip header
        for line in tqdm(tsv_file, desc=f"IMPORT catalog"):
            identifier = line[0]
            format = line[1]
            alignment_license = line[2]
            scope = line[3]
            source_license = line[4]
            target_license = line[5]

            id_pieces = identifier.split("+")
            pair = id_pieces[2].split("-")

            new_entry = {}
            new_entry["lang"] = id_pieces[0]
            new_entry["source"] = pair[0]
            new_entry["target"] = pair[1]
            new_entry["type"] = pair[2]
            new_entry["alignment_license"] = alignment_license
            new_entry["source_license"] = source_license
            new_entry["target_license"] = target_license
            CATALOG.append(new_entry)

    CATALOG.sort(key=lambda x: x["target"])
    CATALOG.reverse()  # Load YLT alignments first.


def get_alignment_pairs_for_target(target_name):
    source_oriented_pairs = os.listdir(SOURCES_PATH)
    target_oriented_pairs = os.listdir(TARGETS_PATH)


def determine_source_names_for_target(target_name):
    source_target_pairs = os.listdir(TARGETS_PATH)
    source_names = []
    for source_target_pair in source_target_pairs:
        cleaned_pair = source_target_pair.split(".")[0].split("-")
        if cleaned_pair[1] == target_name:
            source_names.append(cleaned_pair[0])
    return source_names


def get_or_create_resource(resource_name, lang):
    exists = Resource.objects.filter(name=resource_name).exists()
    if exists:
        print(f"\t get {resource_name}")
        return Resource.objects.get(name=resource_name)

    print(f"\t create {resource_name}")
    new_resource = Resource(name=resource_name, lang=lang)
    new_resource.save()
    return new_resource


def import_source_tokens(path, resource):
    to_create = {}

    if os.path.isfile(path):
        with open(path) as file:
            tsv_file = csv.reader(file, delimiter="\t")
            next(tsv_file)  # skip header
            for line in tqdm(tsv_file, desc=f"\t source tokens for {resource.name}"):
                to_create[line[0]] = SourceToken(
                    token_id=line[0],
                    resource=resource,
                    gloss=line[4],
                    lemma=line[6],
                    text=line[2],
                )

    token_ids = list(to_create.keys())
    first_token_id = token_ids[0]
    token_exists = SourceToken.objects.filter(token_id=first_token_id, resource=resource).exists()

    if not token_exists:
        print(f"\t bulk save")
        SourceToken.objects.bulk_create(to_create.values())


def import_source_token_subjects():
    SUBJECT_TOKEN_REFS_DATA_PATH = f"{TEST_DATA_PATH}/subject_token_refs.json"

    with open(SUBJECT_TOKEN_REFS_DATA_PATH, "r") as f:
        subject_token_ref_data = json.load(f)

        for subject_token_ref in tqdm(
            subject_token_ref_data["subject_token_refs"],
            desc=f"\t create subject_token_refs",
        ):
            subject = Subject.objects.get(subject_id=subject_token_ref["subject_id"])
            source_token = SourceToken.objects.get(token_id=subject_token_ref["token_id"])
            source_token.subjects.add(subject)


def import_target_tokens(path, resource):
    to_create = {}

    if os.path.isfile(path):
        with open(path) as file:
            tsv_file = csv.reader(file, delimiter="\t")
            next(tsv_file)  # skip header
            for line in tqdm(tsv_file, desc=f"\t target tokens for {resource.name}"):
                to_create[line[0]] = TargetToken(
                    token_id=line[0],
                    text=line[2],
                    is_punc=bool(line[4] == "True"),
                    resource=resource,
                )

        # TargetToken.objects.bulk_create(to_create.values())
    token_ids = list(to_create.keys())
    first_token_id = token_ids[0]
    token_exists = TargetToken.objects.filter(token_id=first_token_id, resource=resource).exists()

    if not token_exists:
        print(f"\t bulk save")
        TargetToken.objects.bulk_create(to_create.values())


def import_alignment(name, source, target, type):
    print(f"\t create alignment {name}")
    new_alignment = Alignment(name=name, source=source, target=target, type=type)
    new_alignment.save()
    return new_alignment


def import_links(alignment, source_resource, target_resource):
    print(f"\t links for {alignment.name}")
    ALIGNMENT_DATA_PATH = f"{DATA_PATH}/alignments/{target_resource.lang}/{target_resource.name}/{alignment.name}-{alignment.type}.json"
    source_tokens_lu = {t.token_id: t for t in source_resource.sourcetoken_set.all()}
    target_tokens_lu = {t.token_id: t for t in target_resource.targettoken_set.all()}
    links = []
    with open(ALIGNMENT_DATA_PATH, "r") as f:
        alignment_data = json.load(f)
        for link in tqdm(alignment_data, desc=f"\t create links"):
            new_link = Link(alignment=alignment)
            links.append(new_link)

        created_links = Link.objects.bulk_create(links)

        with transaction.atomic():
            for idx, link in enumerate(tqdm(alignment_data, desc=f"\t create link relationships")):
                id = list(link.keys())[0]
                extracted_link = list(link.values())[0]
                source_token_ids = extracted_link[source_resource.name]
                target_token_ids = extracted_link[target_resource.name]
                source_tokens = []
                target_tokens = []

                for the_id in source_token_ids:
                    token = source_tokens_lu[the_id]
                    source_tokens.append(token)

                for the_id in target_token_ids:
                    token = target_tokens_lu[the_id]
                    target_tokens.append(token)

                created_links[idx].source_tokens.add(*source_tokens)
                created_links[idx].target_tokens.add(*target_tokens)


def import_subjects():
    SUBJECTS_DATA_PATH = f"{TEST_DATA_PATH}/subjects.json"

    with open(SUBJECTS_DATA_PATH, "r") as f:
        subjects_data = json.load(f)
        new_subjects = []

        for subject in tqdm(subjects_data["subjects"], desc=f"\t create subjects"):
            new_subject = Subject(
                subject_id=subject["subject_id"],
                name=subject["name"],
                description=subject["description"],
            )
            new_subjects.append(new_subject)

        created_subjects = Subject.objects.bulk_create(new_subjects)


def import_media_assets():
    MEDIA_ASSETS_DATA_PATH = f"{TEST_DATA_PATH}/media_assets.json"

    with open(MEDIA_ASSETS_DATA_PATH, "r") as f:
        media_assets_data = json.load(f)
        new_media_assets = []

        for media_asset in tqdm(media_assets_data["media_assets"], desc=f"\t create media assets"):
            related_subject = Subject.objects.get(subject_id=media_asset["subject"])
            new_media_asset = MediaAsset(
                media_asset_id=media_asset["media_asset_id"],
                dam_id=media_asset["dam_id"],
                title=media_asset["title"],
                subtitle=media_asset["subtitle"],
                description=media_asset["description"],
                asset_type=media_asset["asset_type"],
                subject=related_subject,
            )
            new_media_assets.append(new_media_asset)

        created_media_assets = MediaAsset.objects.bulk_create(new_media_assets)


def load_alignments(reset=True):
    if not DATA_PATH.exists():
        return

    if reset:
        print(f"Reset...")

        print(f"\t Resource")
        Resource.objects.all().delete()

        print(f"\t SourceToken")
        SourceToken.objects.all().delete()

        print(f"\t TargetToken")
        TargetToken.objects.all().delete()

        print(f"\t Alignment")
        Alignment.objects.all().delete()

        print(f"\t Link")
        Link.objects.all().delete()

        print(f"\t Subject")
        Subject.objects.all().delete()

        print(f"\t MediaAsset")
        MediaAsset.objects.all().delete()

    load_catalog()

    print(f"IMPORT Subject(s)")
    import_subjects()

    print(f"IMPORT MediaAsset(s)")
    import_media_assets()

    for entry in CATALOG[0:2]:
        name = f"{entry['source']}-{entry['target']}"
        print(f"INGEST {name}")
        source_resource = get_or_create_resource(entry["source"], entry["lang"])
        target_resource = get_or_create_resource(entry["target"], entry["lang"])

        import_source_tokens(
            f"{SOURCES_PATH}/{entry['source']}-{entry['target']}.tsv",
            source_resource,
        )
        import_target_tokens(
            f"{TARGETS_PATH}/{entry['source']}-{entry['target']}.tsv",
            target_resource,
        )

        alignment = import_alignment(name, source_resource, target_resource, entry["type"])

        import_links(alignment, source_resource, target_resource)

    print(f"IMPORT SourceToken.Subject")
    import_source_token_subjects()


if __name__ in {"__main__", "django.core.management.commands.shell"}:
    if not settings.DEBUG:
        raise ImproperlyConfigured("This command can only be ran if DEBUG=True")
    load_alignments()
