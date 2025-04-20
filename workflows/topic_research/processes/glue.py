

def parse_report_to_sections(report, section_markers):
    parsed_document = list()
    split_document = report.split('\n')

    current_section_idx = 0
    current_section_marker = section_markers[current_section_idx]
    current_section = [split_document[0]]

    for line_number, line in enumerate(split_document):
        if current_section_marker[1].lower() in line.lower():
            if line_number != 0:
                parsed_document.append('\n'.join(current_section))
            # current_section = list()
            current_section_idx += 1
            current_section = [line]
            if current_section_idx < len(section_markers):
                current_section_marker = section_markers[current_section_idx]
            continue
        else:
            current_section.append(line)
    parsed_document.append('\n'.join(current_section))
    return parsed_document

def parse_report(report, section_markers):
    parsed_document = parse_report_to_sections(report, section_markers)
    segmented_report = list()
    section_idx = 1
    for marker, section in zip(section_markers, parsed_document):
        segmented_report.append({'section_idx': section_idx,
                                 'section_id':marker[0],
                                 'section_title':marker[1],
                                 'section_text':section})
        section_idx += 1
    return segmented_report

