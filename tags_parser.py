import re
import sys
import json


def main():
    parsed_tags = []
    if len(sys.argv) < 2:
        return
    with open(sys.argv[1], "r") as input_file:
        all_tags = input_file.readlines()
        for tag in all_tags:
            tag_parts = re.split(
                r"(</td>|<td>|<tr>|</tr>)", tag)
            # Get tag parts.
            filtered_tag_parts = []
            for tag_part in tag_parts:
                if tag_part.strip() not in ["", "</td>", "<td>", "<tr>", "</tr>"]:
                    filtered_tag_parts.append(tag_part)
            # Construct the parsed tags.
            parsed_tags.append({'number': int(filtered_tag_parts[0]),
                                'name': re.search(r"href=\"[a-zA-Z0-9_. -]*\">(?P<name>[a-zA-Z0-9 _-]*)</a>",
                                                  filtered_tag_parts[2]).group('name'),
                                'desc': filtered_tag_parts[3]})
        # Dump the tags to a json file.
        with open('private_tags.json', 'w') as tags_json:
            json.dump(parsed_tags, tags_json)


if __name__ == '__main__':
    main()
