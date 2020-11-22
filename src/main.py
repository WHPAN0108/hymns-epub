from src import data_loader, html_writer

hymn_group_options = ("G", "E", "NS", "C", "CS")


def main():
    html_writer.write_main_page()

    cursor = data_loader.connect_db()
    related_hymn_list = data_loader.find_related_hymn_list(cursor)
    for hymn_group in hymn_group_options:
        hymns, all_stanzas = data_loader.run(cursor, related_hymn_list, hymn_group)
        html_writer.write_hymn_page(hymns, all_stanzas, hymn_group, hymn_group_options)
    cursor.close()

    html_writer.convert_to_epub()


if __name__ == "__main__":
    main()
