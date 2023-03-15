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
alignment_targets = ["YLT", "CUVMP"]
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

    # TODO: support language ingestion
    print(f"\t create {resource_name}")
    new_resource = Resource(name=resource_name, lang=lang)
    new_resource.save()
    return new_resource


def import_source_tokens(path, resource):
    to_create = {}
    count = SourceToken.objects.filter(resource=resource).count()

    if count == 0 and os.path.isfile(path):
        with open(path) as file:
            tsv_file = csv.reader(file, delimiter="\t")
            for line in tqdm(tsv_file, desc=f"\t source tokens for {resource.name}"):
                to_create[line[0]] = SourceToken(
                    token_id=line[0],
                    resource=resource,
                    gloss=line[4],
                    lemma=line[6],
                    text=line[6],
                )

        SourceToken.objects.bulk_create(to_create.values())


def import_target_tokens(path, resource):
    to_create = {}
    count = TargetToken.objects.filter(resource=resource).count()

    if count == 0 and os.path.isfile(path):
        with open(path) as file:
            tsv_file = csv.reader(file, delimiter="\t")
            for line in tqdm(tsv_file, desc=f"\t target tokens for {resource.name}"):
                to_create[line[0]] = TargetToken(
                    token_id=line[0],
                    text=line[2],
                    is_punc=bool(line[4]),
                    resource=resource,
                )

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

            # TODO: Bulkify this too

            # new_link.save()
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

                # for source_token in source_tokens:
                # print(
                #     f"adding source_token to link {source_token} {source_token.token_id}"
                # )
                created_links[idx].source_tokens.add(*source_tokens)

                # for target_token in target_tokens:
                # print(
                #     f"adding target_token to link {target_token} {target_token.token_id}"
                # )
                created_links[idx].target_tokens.add(*target_tokens)

                # new_link.save()


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

    for entry in [CATALOG[1]]:
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

    # for alignment_pair in alignment_pairs:

    # for target_name in alignment_targets:
    #     print(f"INGEST {target_name}")
    #     source_names = determine_source_names_for_target(target_name)

    #     source_resources = []
    #     for source_name in source_names:
    #         source_resources.append(get_or_create_resource(source_name))

    #     for source_resource in source_resources:
    #         import_source_tokens(
    #             f"{DATA_PATH}/sources/{source_resource.name}-{target_name}.tsv",
    #             source_resource,
    #         )

    # source_token_path = DATA_PATH / "sources/NA27-YLT.tsv"
    # target_token_path = DATA_PATH / "targets/NA27-YLT.tsv"

    # source_resource = get_or_create_resource()

    # Import NA27
    # - Resource
    # - Token(s)
    # print("import na27")
    # na27_resource = import_resource(resource_model, "na27", "grk")
    # import_tokens(
    #     source_token_model,
    #     target_token_model,
    #     DATA_PATH / "sources/NA27-YLT.tsv",
    #     na27_resource,
    #     "source",
    # )

    # Import YLT
    # - Resource
    # - Token(s)
    # print("import ylt")
    # ylt_resource = import_resource(resource_model, "ylt", "eng")
    # import_tokens(
    #     source_token_model,
    #     target_token_model,
    #     DATA_PATH / "targets/NA27-YLT.tsv",
    #     ylt_resource,
    #     "target",
    # )

    # Import NA27 / YLT Alignment
    # - Alignment
    # - Link(s)
    # print("import na27-ylt alignment")
    # na27_ylt_alignment = import_alignment(
    #     alignment_model, "NA27-YLT", na27_resource, ylt_resource
    # )
    # print(f"import na27-ylt links with alignment {na27_ylt_alignment}")
    # import_links(
    #     link_model,
    #     source_token_model,
    #     target_token_model,
    #     na27_ylt_alignment,
    #     DATA_PATH / "alignments/eng/YLT/NA27-YLT-manual.json",
    #     na27_resource,
    #     ylt_resource,
    # )


if __name__ in {"__main__", "django.core.management.commands.shell"}:
    if not settings.DEBUG:
        raise ImproperlyConfigured("This command can only be ran if DEBUG=True")
    load_alignments()
