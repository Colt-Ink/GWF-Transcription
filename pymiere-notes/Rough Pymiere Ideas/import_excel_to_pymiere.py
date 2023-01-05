"""

The purpose of this script is to get audio intelligence from the AssemblyAI API that helps automate some editing tasks, like assembling a rough cut in Premiere Pro using Auto Chapters and Speaker Labels, and also simplify metadata tagging to improve YouTube uploads for SEO. This can include using Auto Chapters as YouTube chapters. 

To further automate this process, we could create a Premiere Pro script that would import the Excel file and create a sequence with the Auto Chapters and Speaker Labels, among other potential data-driven editing methods. 

~~~~~~~~~~~~~~~~
A good way to do this is to use Pymiere: https://github.com/qmasingarbe/pymiere.
Pymiere is a Python wrapper for Adobe's Premiere Pro API, and can be installed with:

$ pip install pymiere

Then install the Pymiere Link extension: 
Install script: 
    https://raw.githubusercontent.com/qmasingarbe/pymiere/master/extension_installer_win.bat 

Or ZXP: 
    https://github.com/qmasingarbe/pymiere/blob/master/pymiere_link.zxp
~~~~~~~~~~~~~~~~

The Excel file can be imported into Premiere Pro using the following script.

The script can be run with the following command:

$ python import_excel_to_premiere.py

"""

# import_excel_to_premiere.py:

import pymiere
import pandas as pd

def import_excel_to_premiere(excel_file_path):
    """
    Imports an Excel file into Premiere Pro and creates a sequence with chapters and speaker labels.
    """
    premiere = pymiere.PyMiere()
    premiere.app.open_project(excel_file_path)
    premiere.app.import_file(excel_file_path)
    premiere.app.import_file(excel_file_path.replace(".xlsx", ".srt"))

    # Create sequence
    sequence = premiere.app.project.create_sequence("sequence")

    # Import Excel file
    excel_file = premiere.app.project.import_file(excel_file_path)[0]

    # Import srt file
    srt_file = premiere.app.project.import_file(excel_file_path.replace(".xlsx", ".srt"))[0]

    # Add srt file to sequence
    sequence.add_file(srt_file)

    # Create a dictionary of words
    words_df = pd.read_excel(excel_file_path, sheet_name="words")
    words = {}
    for index, row in words_df.iterrows():
        words[row["start"]] = row["text"]

    # Create a dictionary of chapters
    chapters_df = pd.read_excel(excel_file_path, sheet_name="chapters")
    chapters = {}
    for index, row in chapters_df.iterrows():
        chapters[row["start"]] = row["headline"]

    # Create a dictionary of entities
    entities_df = pd.read_excel(excel_file_path, sheet_name="entities")
    entities = {}
    for index, row in entities_df.iterrows():
        entities[row["start"]] = row["text"]

    # Create a dictionary of IAB categories
    iab_categories_df = pd.read_excel(excel_file_path, sheet_name="iab_categories")
    iab_categories = {}
    for index, row in iab_categories_df.iterrows():
        if row["labels"] in iab_categories:
            iab_categories[row["labels"]] += row["count"]
        else:
            iab_categories[row["labels"]] = row["count"]

    # Create a dictionary of highlights
    highlights_df = pd.read_excel(excel_file_path, sheet_name="highlights")
    highlights = {}
    for index, row in highlights_df.iterrows():
        highlights[row["start"]] = row["text"]

    # Create a dictionary of paragraphs
    paragraphs_df = pd.read_excel(excel_file_path, sheet_name="paragraphs")
    paragraphs = {}
    for index, row in paragraphs_df.iterrows():
        paragraphs[row["start"]] = row["text"]

    # Add chapters to sequence
    for chapter_start, chapter_headline in chapters.items():
        chapter_end = chapter_start
        chapter_start = float(chapter_start) * 1000
        chapter_end = float(chapter_end) * 1000
        sequence.add_chapter(chapter_start, chapter_end, chapter_headline)

"""
~~~~~~~~~~~~~~~~ Probably not useful, but possibly useful. If the use case arrives, then these would be useful. But probably not, ever, useful. ~~~~~~~~~~~~~~~~

    # Add words to sequence
    for word_start, word_text in words.items():
        word_end = word_start
        word_start = float(word_start) * 1000
        word_end = float(word_end) * 1000
        sequence.add_marker(word_start, word_end, word_text)

    # Add entities to sequence
    for entity_start, entity_text in entities.items():
        entity_end = entity_start
        entity_start = float(entity_start) * 1000
        entity_end = float(entity_end) * 1000
        sequence.add_marker(entity_start, entity_end, entity_text, color="red")

    # Add IAB categories to sequence
    for iab_category_start, iab_category_text in iab_categories.items():
        iab_category_end = iab_category_start
        iab_category_start = float(iab_category_start) * 1000
        iab_category_end = float(iab_category_end) * 1000
        sequence.add_marker(iab_category_start, iab_category_end, iab_category_text, color="green")

    # Add highlights to sequence
    for highlight_start, highlight_text in highlights.items():
        highlight_end = highlight_start
        highlight_start = float(highlight_start) * 1000
        highlight_end = float(highlight_end) * 1000
        sequence.add_marker(highlight_start, highlight_end, highlight_text, color="blue")

    # Add paragraphs to sequence
    for paragraph_start, paragraph_text in paragraphs.items():
        paragraph_end = paragraph_start
        paragraph_start = float(paragraph_start) * 1000
        paragraph_end = float(paragraph_end) * 1000
        sequence.add_marker(paragraph_start, paragraph_end, paragraph_text, color="yellow")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

    # Save project
    premiere.app.project.save_as(excel_file_path.replace(".xlsx", ".prproj"))

if __name__ == '__main__':
    import_excel_to_premiere("/path/to/file.xlsx")
