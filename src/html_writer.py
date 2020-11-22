import subprocess
import time

from src.data_loader import get_hymn_group, get_hymn_number

html_root = "html"
html_file_pattern = f"{html_root}/%s.html"
main_html_path = html_file_pattern % "main"

languages = {
    "G": "Deutsch",
    "E": "English",
    "NS": "New-Song",
    "C": "Chinese",
    "CS": "Chinese-Supplement",
}


def write_main_page():
    body = ""
    for language in languages.values():
        body += f"<h1><a href='{language}.html'>{language}</a></h1>"

    write_html("Liederbuch", "Liederbuch", body, main_html_path)


def write_hymn_page(hymns, all_stanzas, hymn_group, hymn_group_options):
    body = get_hymn_text(hymns, all_stanzas, hymn_group, hymn_group_options)
    language = languages[hymn_group]
    write_html("", language, body, html_file_pattern % language)


def get_hymn_text(hymns, all_stanzas, hymn_group, hymn_group_options):
    language = languages[hymn_group]
    body = get_toc(hymns, hymn_group)
    for hymn_id in hymns.keys():
        hymn = hymns[hymn_id]
        stanzas = all_stanzas[hymn_id]
        title = f"<h2 id='{hymn_id}'><a href='{language}.html'>#{hymn_id}</a><br/>"
        title += f"{hymn.main_category}"
        if hymn.sub_category:
            title += f" - {hymn.sub_category}"
        title += "</h2>"
        for related_hymn_id in hymn.related_hymn_ids:
            related_hymn_group = get_hymn_group(related_hymn_id)
            if related_hymn_group in hymn_group_options:
                related_page = languages[related_hymn_group]
                title += (
                    f"<a href='{related_page}.html#{related_hymn_id}'>"
                    f"{related_hymn_id}</a>, "
                )
        if hymn.meter:
            title += f"{hymn.meter}<br/>"
        body += title

        for stanza in stanzas:
            no = stanza.no
            if no == "chorus":
                stanza_text = f"<p>{stanza.text}</p>"
            else:
                stanza_text = f"<p>{stanza.no}<br/>{stanza.text}</p>"
            body += stanza_text

    return body


def get_toc(hymns, hymn_group):
    page = languages[hymn_group]

    toc_string = ""
    body_string = ""
    hymn_ids = list(hymns.keys())

    first_indicies, last_indicies = [], []
    for index, hymn_id in enumerate(hymn_ids):
        if get_hymn_number(hymn_id) % 100 == 1:
            first_indicies.append(index)
            if first_indicies[-1] != 0:
                last_indicies.append(first_indicies[-1] - 1)
    last_indicies.append(len(hymn_ids) - 1)

    for first_index, last_index in zip(first_indicies, last_indicies):
        part_id = f"part-{hymn_ids[first_index]}"
        part_text = f"{hymn_ids[first_index]} - {hymn_ids[last_index]}"
        toc_string += f"<a href='{page}.html#{part_id}'>{part_text}</a><br>"
        body_string += f"<p id='{part_id}'>{part_text}<br/>"
        for index in range(first_index, last_index + 1):
            hymn_id = hymn_ids[index]
            body_string += f"<a href='{page}.html#{hymn_id}'>{hymn_id}</a>  "
        body_string += "</p>"

    return toc_string + body_string


def write_html(head, title, body, path):
    header = get_header(head, title)
    footer = get_footer()
    write_string(f"{header}{body}{footer}", path)


def get_header(head="", title=""):
    string = f"""<!DOCTYPE html>
<html>
<meta charset="utf-8"/>"""
    if head:
        string += f"\n<head>{head}</head>"
    if title:
        string += f"\n<header><h1>{title}</h1></header>"
    string += "<body>"
    return string


def get_footer():
    return """
</body>
</html>"""


def write_string(string, path):
    with open(path, "wb") as writer:
        writer.write(string.encode("utf-8"))


def convert_to_epub():
    arg_str = (
        f"ebook-convert {main_html_path} output/liederbuch.epub -v"
        " --title Liederbuch"
        f" --max-toc-links {len(languages)}"
        " --page-breaks-before /"
        " --chapter /"
        " --no-default-epub-cover"
    )
    popenargs = arg_str.split(" ")

    t1 = time.perf_counter()
    subprocess.run(popenargs)
    t2 = time.perf_counter()
    run_time = t2 - t1
    print(f"run_time = {run_time:.1f} s")
