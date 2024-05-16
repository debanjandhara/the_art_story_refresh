def movement_xml(id_movement):
    import xml.etree.ElementTree as ET
    import re
    import sys
    import os
    import textwrap
    
    output_file = f"data/filtered_txts/movements/{id_movement}.txt"

    output_variable = ""

    if os.path.exists(output_file):
        # If the file exists, delete it
        os.remove(output_file)

    # Specify the path to your XML file
    xml_file_path = f"data/raw_xmls/movements/{id_movement}.xml"

    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Now you can access elements in the XML file using ElementTree methods
    for main_element in root.iter('main'):
        # Extract data from specific tags
        if (main_element.find('id') is not None):
            artist_id = main_element.find('id').text
            output_variable += f'''Id : {artist_id}
Source Link : https://www.theartstory.org/movement/{re.sub('_', '-', artist_id)}/
Dynamic Card Iframe Link : https://www.theartstory.org/data/content/dynamic_content/ai-card/movement/{re.sub('_', '-', artist_id)}'''
            
        if (main_element.find('name') is not None):
            name = main_element.find('name').text
            output_variable += f'''\nName : {name}'''
            
        if (main_element.find('years') is not None):
            years_worked = main_element.find('years').text
            output_variable += f'''\n{name} developed in (year) : {years_worked}'''
            
        if (main_element.find('description') is not None):
            description = main_element.find('description').text
            output_variable += f'''\n{name}'s Description : {description}'''
            
        if (main_element.find('art_title') is not None):
            art_title = main_element.find('art_title').text
            output_variable += f'''\n{name}'s Art Title : {art_title}'''
            
        if (main_element.find('art_description') is not None):
            art_description = main_element.find('art_description').text
            output_variable += f'''\n{name}'s Art Description : {art_description}'''
            
        if (main_element.find('bio_highlight') is not None):
            bio_highlight = main_element.find('bio_highlight').text
            output_variable += f'''\n{name}'s Biography Highlights : {re.sub(r'<.*?>', '', str(bio_highlight))}'''
            
        if (main_element.find('pub_time') is not None):
            publish_date = main_element.find('pub_time').text
            output_variable += f'''\n{name} Content Publish Date: {publish_date}'''


    output_variable += "\n\nQuotes : "

    for quotes in root.iter('quotes'):
        if (quotes.find('q') is not None):
            for quote in quotes.findall('q'):
                output_variable += f'{quote.text}, '

    for article in root.iter('article'):
        if (article.find('synopsys') is not None):
            synopsys = article.find('synopsys').text
            cleaned_synopsys = re.sub(r'<.*?>', '', synopsys)
            output_variable += f"\n\nSynopsis : {cleaned_synopsys}"

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
            output_variable += f"\n\nDescription  : {re.sub(r'<.*?>', '', textwrap.dedent(artwork_desc))}"
            artwork_collection = artwork.find('collection').text
            output_variable += f"\n\nFound in Collection : {artwork_collection}"

    output_variable += "\n\nRecommended Pages From the Art Story Page:\n"

    for category in root.iter('category'):
        if category.get('name') == ('art story website features'):
            for subcategory in category.iter('subcategory'):
                if subcategory.get('name') == ('not_to_show'):
                    for entry in subcategory.iter('entry'):
                            title = entry.find('title').text
                            info = entry.find('info').text
                            link = entry.find('link').text
                            theartstory_link = f"https://www.theartstory.org{link}"
                            output_variable += f"Title : {title}\nThe Art Story Link : {theartstory_link}\n\n"


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
        if category.get('name') == ('resources'):
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
