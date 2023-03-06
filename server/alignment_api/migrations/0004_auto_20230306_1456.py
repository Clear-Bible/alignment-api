# Generated by Django 4.1.7 on 2023-03-06 14:56
import csv
import json
from django.conf import settings
from django.db import migrations

from tqdm import tqdm

DATA_PATH = settings.BASE_DIR / "../data/data"


def import_resource(resource_model, name, lang):
    resource = resource_model(name=name, lang=lang)
    resource.save()
    return resource


def import_tokens(
    source_token_model, target_token_model, tsv_path, related_resource, type
):
    # count = 0
    source_to_create = {}
    target_to_create = {}
    with open(tsv_path) as file:
        tsv_file = csv.reader(file, delimiter="\t")
        for line in tqdm(tsv_file):
            # count = count + 1
            # if count == 100:
            # break
            if type == "source":
                source_to_create[line[0]] = source_token_model(
                    token_id=line[0], resource=related_resource, text=line[6]
                )
            if type == "target":
                target_to_create[line[0]] = target_token_model(
                    token_id=line[0], resource=related_resource, text=line[2]
                )
    source_token_model.objects.bulk_create(source_to_create.values())
    target_token_model.objects.bulk_create(target_to_create.values())
    return source_to_create, target_to_create


def import_alignment(alignment_model, name, source, target):
    new_alignment = alignment_model(name=name, source=source, target=target)
    new_alignment.save()
    return new_alignment


def import_links(
    link_model,
    source_token_model,
    target_token_model,
    alignment,
    alignment_data_path,
    na27_resource,
    ylt_resource,
):
    print(f"Importing alignment: {alignment_data_path}")
    source_tokens_lu = {t.token_id: t for t in na27_resource.sourcetoken_set.all()}
    target_tokens_lu = {t.token_id: t for t in ylt_resource.targettoken_set.all()}
    with open(alignment_data_path, "r") as f:
        alignment_data = json.load(f)
        print(len(alignment_data))
        for link in tqdm(alignment_data):
            id = list(link.keys())[0]
            extracted_link = list(link.values())[0]
            source_token_ids = extracted_link["NA27"]
            target_token_ids = extracted_link["YLT"]
            source_tokens = []
            target_tokens = []
            for the_id in source_token_ids:
                # print(f"retrieving source token: {the_id}")
                token = source_tokens_lu[the_id]
                source_tokens.append(token)

            for the_id in target_token_ids:
                # print(f"retrieving target token: {the_id}")
                token = target_tokens_lu[the_id]
                target_tokens.append(token)

            # print(f"Creating link for alignment {alignment.name}")
            # TODO: Bulkify this too
            new_link = link_model(alignment=alignment)
            new_link.save()
            # print(f"saved link {new_link.id} {new_link.alignment.name}")
            # print("add tokens")
            for source_token in source_tokens:
                # print(
                #     f"adding source_token to link {source_token} {source_token.token_id}"
                # )
                new_link.source_tokens.add(source_token)

            # print(f"source token count: {new_link.source_tokens.count()}")

            for target_token in target_tokens:
                # print(
                #     f"adding target_token to link {target_token} {target_token.token_id}"
                # )
                new_link.target_tokens.add(target_token)
            # print(f"target token count: {new_link.target_tokens.count()}")

            # print("second save")
            # new_link.save()


def populate_data(apps, schema_editor):
    if not DATA_PATH.exists():
        return
    # FIXME: deploy data
    resource_model = apps.get_model(app_label="alignment_api", model_name="Resource")
    source_token_model = apps.get_model(
        app_label="alignment_api", model_name="SourceToken"
    )
    target_token_model = apps.get_model(
        app_label="alignment_api", model_name="TargetToken"
    )
    alignment_model = apps.get_model(app_label="alignment_api", model_name="Alignment")
    link_model = apps.get_model(app_label="alignment_api", model_name="Link")

    # Import NA27
    # - Resource
    # - Token(s)
    print("import na27")
    na27_resource = import_resource(resource_model, "na27", "grk")
    import_tokens(
        source_token_model,
        target_token_model,
        DATA_PATH / "sources/NA27-YLT.tsv",
        na27_resource,
        "source",
    )

    # Import YLT
    # - Resource
    # - Token(s)
    print("import ylt")
    ylt_resource = import_resource(resource_model, "ylt", "eng")
    import_tokens(
        source_token_model,
        target_token_model,
        DATA_PATH / "targets/NA27-YLT.tsv",
        ylt_resource,
        "target",
    )

    # Import NA27 / YLT Alignment
    # - Alignment
    # - Link(s)
    print("import na27-ylt alignment")
    na27_ylt_alignment = import_alignment(
        alignment_model, "NA27-YLT", na27_resource, ylt_resource
    )
    print(f"import na27-ylt links with alignment {na27_ylt_alignment}")
    import_links(
        link_model,
        source_token_model,
        target_token_model,
        na27_ylt_alignment,
        DATA_PATH / "alignments/eng/YLT/NA27-YLT-manual.json",
        na27_resource,
        ylt_resource,
    )


def backwards(apps, schema_editor):
    resource_model = apps.get_model(app_label="alignment_api", model_name="Resource")
    resource_model.objects.all().delete()

    source_token_model = apps.get_model(
        app_label="alignment_api", model_name="SourceToken"
    )
    source_token_model.objects.all().delete()

    target_token_model = apps.get_model(
        app_label="alignment_api", model_name="TargetToken"
    )

    target_token_model.objects.all().delete()

    alignment_model = apps.get_model(app_label="alignment_api", model_name="Alignment")
    alignment_model.objects.all().delete()

    link_model = apps.get_model(app_label="alignment_api", model_name="Link")
    link_model.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("alignment_api", "0003_alter_link_source_tokens_alter_link_target_tokens"),
    ]

    operations = [migrations.RunPython(populate_data, backwards)]
