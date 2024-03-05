def definition_xml(id_definition):
    import xml.etree.ElementTree as ET
    import re
    import sys
    import os
    import textwrap
    
    output_file = f"data/filtered_txts/definitions/{id_definition}.txt"

    output_variable = ""

    if os.path.exists(output_file):
        # If the file exists, delete it
        os.remove(output_file)

    # Specify the path to your XML file
    xml_file_path = f"data/raw_xmls/definitions/{id_definition}.xml"

    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Now you can access elements in the XML file using ElementTree methods
    for main_element in root.iter('main'):
        # Extract data from specific tags
        if (main_element.find('id') is not None):
            artist_id = main_element.find('id').text
            output_variable += f'''Id : {artist_id}
Source Link : https://www.theartstory.org/definition/{re.sub('_', '-', artist_id)}/
Dynamic Card Iframe Link : https://www.theartstory.org/data/content/dynamic_content/ai-card/definition/{re.sub('_', '-', artist_id)}'''
            
            
        if (main_element.find('name') is not None):
            name = main_element.find('name').text
            output_variable += f'''\nName : {name}'''

        if (main_element.find('start') is not None):
            start_date = main_element.find('start').text
            output_variable += f'''\n{name} Years Started : {start_date}'''
            
        if (main_element.find('pub_time') is not None):
            publish_date = main_element.find('pub_time').text
            output_variable += f'''\n{name} Content Publish Date: {publish_date}'''

    output_variable += "\n\nQuotes : "

    for quotes in root.iter('quotes'):
        if (quotes.find('q') is not None):
            for quote in quotes.findall('q'):
                output_variable += f'{quote.text}, '

    for article in root.iter('article'):
        synopsys = article.find('synopsys').text
        cleaned_synopsys = re.sub(r'<.*?>', '', synopsys)
        output_variable += f"\n\nSynopsis : {textwrap.dedent(str(cleaned_synopsys))}"

    output_variable += "\n\nKey Ideas : "
    for idea in root.iter('idea'):
        cleaned_key_ideas = re.sub(r'<.*?>', '', idea.text)
        output_variable += f"\"{cleaned_key_ideas}\", "

    for section in root.iter('section'):
        section_title = section.get('title')
        output_variable += f"\n\n{section_title} :"

        for subsection in section.iter('subsection'):
            subsection_title = subsection.get('title')
            output_variable += f"\n\n{subsection_title} : "
            for p_element in subsection.iter('p'):
                if p_element.get('type') == 'p':
                    p_text = ' '.join(p_element.itertext())
                    cleaned_p_text = re.sub(r'<.*?>', '', p_text.strip())
                    output_variable += f"{cleaned_p_text}"

    output_variable += "\n\nArtwork : "

    for artworks in root.iter('artworks'):
        for artwork in artworks.iter('artwork'):
            artwork_title = artwork.find('title').text
            output_variable += f"\n\nTitle : {artwork_title}"
            artwork_artist = artwork.find('artist').text
            output_variable += f"\n\nArtist : {artwork_artist}"
            artwork_year = artwork.find('year').text
            output_variable += f"\n\nProduced in the year : {artwork_year}"
            artwork_materials = artwork.find('materials').text
            output_variable += f"\n\nMaterial Used : {artwork_materials}"
            artwork_desc = artwork.find('desc').text
            output_variable += f"\n\nDescription  : {re.sub(r'<.*?>', '', textwrap.dedent(str(artwork_desc)))}"
            artwork_collection = artwork.find('collection').text
            output_variable += f"\n\nFound in Collection : {artwork_collection}"



    output_variable += "\n\nAmazon Links (Books) : \n" 
    for category in root.iter('category'):
        if category.get('name') == ('featured books'):
            for subcategory in category.iter('subcategory'):
                    for entry in subcategory.iter('entry'):
                            title = entry.find('title').text
                            info = entry.find('info').text
                            link = entry.find('link').text
                            amazon_link = f"https://www.amazon.com/gp/product/{link}?tag=tharst-20"
                            output_variable += f"Title : {title}\nAmazon Link : {amazon_link}\n\n"

    output_variable += "\n\nExtra Links (Websites) : \n"
    for category in root.iter('category'):
        if category.get('name') == ('web resources'):
            for subcategory in category.iter('subcategory'):
                    for entry in subcategory.iter('entry'):
                            title = entry.find('title').text
                            info = entry.find('info').text
                            link = entry.find('link').text
                            output_variable += f"Title : {title}\nLink : {link}\n\n"

    # output_variable = ""

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(output_variable)

    print(f"Output has been written to {output_file}")
    return name.lower()