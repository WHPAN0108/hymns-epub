import re
import sqlite3
from collections import namedtuple

Hymn = namedtuple("Hymn", "id, main_category, sub_category, related_hymn_ids, meter")
Stanza = namedtuple("Stanza", "parent_hymn, no, text")


def connect_db():
    conn = sqlite3.connect("database/hymns.sqlite")
    cursor = conn.cursor()
    return cursor


def find_related_hymn_list(cursor):
    cursor.execute("SELECT _id, parent_hymn FROM hymns WHERE parent_hymn IS NOT NULL")
    related_hymn_list = []
    for hymn_id, parent_hymn_id in cursor.fetchall():
        new_set = {hymn_id, parent_hymn_id}
        repeated_index = [i for i, s in enumerate(related_hymn_list) if s & new_set]
        if repeated_index:
            assert len(repeated_index) == 1
            related_hymn_list[repeated_index[0]] |= new_set
        else:
            related_hymn_list.append(new_set)

    return related_hymn_list


def run(cursor, related_hymn_list, hymn_group):
    hymns = load_hymns(cursor, related_hymn_list, hymn_group)
    all_stanzas = load_stanzas(cursor, hymns)
    return hymns, all_stanzas


def load_hymns(cursor, related_hymn_list, hymn_group):
    cursor.execute(
        "SELECT _id, main_category, sub_category, meter FROM hymns "
        f"WHERE hymn_group == '{hymn_group}'"
    )
    hymns = {}
    for hymn_id, main_category, sub_category, meter in cursor.fetchall():
        sub_category = sub_category or ""
        meter = meter or ""
        related_hymn_set = [s for s in related_hymn_list if hymn_id in s]
        if related_hymn_set:
            related_hymn_ids = sorted(related_hymn_set[0] - {hymn_id})
        else:
            related_hymn_ids = []
        hymns[hymn_id] = Hymn(
            hymn_id, main_category, sub_category, related_hymn_ids, meter
        )

    hymns = dict(sorted(hymns.items(), key=lambda item: get_hymn_number(item[0])))
    return hymns


def load_stanzas(cursor, hymns):
    hymn_ids = list(hymns.keys())
    all_stanzas = {hymn_id: [] for hymn_id in hymn_ids}
    all_chorus = {hymn_id: None for hymn_id in hymn_ids}
    cursor.execute("SELECT parent_hymn, no, text FROM stanza")
    rows = list(map(Stanza._make, cursor.fetchall()))
    for stanza in rows:
        hymn_id = stanza.parent_hymn
        if hymn_id in hymn_ids:
            chorus = all_chorus[hymn_id]
            if stanza.no != "chorus":
                all_stanzas[hymn_id].append(stanza)
                if chorus is not None:
                    all_stanzas[hymn_id].append(chorus)
            else:
                if chorus is None:
                    all_stanzas[hymn_id].append(stanza)
                else:
                    all_stanzas[hymn_id][-1] = stanza
                all_chorus[hymn_id] = stanza

    return all_stanzas


def get_hymn_group(hymn_id):
    return re.findall("\D+", hymn_id)[0]


def get_hymn_number(hymn_id):
    return int(re.findall("\d+", hymn_id)[0])
