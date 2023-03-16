"""
Usage: python manage.py shell < alignment_api/pipelines/load_alignments.py
"""
import os
import csv
import json

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from tqdm import tqdm

from alignment_api.models import SourceToken, TargetToken, Resource, Alignment, Link

DATA_PATH = settings.BASE_DIR / "data/data"
SOURCES_PATH = DATA_PATH / "sources"
TARGETS_PATH = DATA_PATH / "targets"
CATALOG = []


def load_catalog():
    CATALOG_PATH = DATA_PATH / "catalog.tsv"
    with open(CATALOG_PATH) as file:
        tsv_file = csv.reader(file, delimiter="\t")
        next(tsv_file)  # skip header
        for line in tqdm(tsv_file, desc=f"import catalog"):
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
    CATALOG.pop(2)  # Ditch NET.


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
                    text=line[6],
                )

    token_ids = list(to_create.keys())
    first_token_id = token_ids[0]
    token_exists = SourceToken.objects.filter(
        token_id=first_token_id, resource=resource
    ).exists()

    if not token_exists:
        print(f"\t bulk save")
        SourceToken.objects.bulk_create(to_create.values())


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
                    is_punc=bool(line[4]),
                    resource=resource,
                )

        # TargetToken.objects.bulk_create(to_create.values())
    token_ids = list(to_create.keys())
    first_token_id = token_ids[0]
    token_exists = TargetToken.objects.filter(
        token_id=first_token_id, resource=resource
    ).exists()

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
    print("source token sample: ", list(source_tokens_lu.items())[0])
    target_tokens_lu = {t.token_id: t for t in target_resource.targettoken_set.all()}
    print("target token sample: ", list(target_tokens_lu.items())[0])
    links = []
    with open(ALIGNMENT_DATA_PATH, "r") as f:
        alignment_data = json.load(f)
        for link in tqdm(alignment_data, desc=f"\t create links"):
            new_link = Link(alignment=alignment)
            links.append(new_link)

        created_links = Link.objects.bulk_create(links)

        with transaction.atomic():
            for idx, link in enumerate(
                tqdm(alignment_data, desc=f"\t create link relationships")
            ):

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


def load_alignments(reset=True):
    if not DATA_PATH.exists():
        return

    if reset:
        print(f"Reset...")

        print(f"\t Resource")
        Resource.truncate()

        print(f"\t SourceToken")
        SourceToken.truncate()

        print(f"\t TargetToken")
        TargetToken.truncate()

        print(f"\t Alignment")
        Alignment.truncate()

        print(f"\t Link")
        Link.truncate()

    load_catalog()

    for entry in CATALOG:
        name = f"{entry['source']}-{entry['target']}"
        print(f"INGEST {name}")
        source_resource = get_or_create_resource(entry["source"], entry["lang"])
        target_resource = get_or_create_resource(entry["target"], entry["lang"])

        import_source_tokens(
            f"{DATA_PATH}/sources/{entry['source']}-{entry['target']}.tsv",
            source_resource,
        )
        import_target_tokens(
            f"{DATA_PATH}/targets/{entry['source']}-{entry['target']}.tsv",
            target_resource,
        )

        alignment = import_alignment(
            name, source_resource, target_resource, entry["type"]
        )

        import_links(alignment, source_resource, target_resource)


if __name__ in {"__main__", "django.core.management.commands.shell"}:
    if not settings.DEBUG:
        raise ImproperlyConfigured("This command can only be ran if DEBUG=True")
    load_alignments()
