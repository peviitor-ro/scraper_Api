import os
from ..constants import SCRAPER_PATH

def get_scrapers(folder): 
    """
    Get a dictionary of scrapers from the specified folder.

    Args:
        folder (str): The name of the folder containing the scrapers.

    Returns:
        dict: A dictionary where the keys are the names of the scrapers (without the file extension)
              and the values are the names of the scraper files.

    """
    path = os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.abspath(__file__)
                        )
                    )
                )
            , SCRAPER_PATH + '/' + folder)
    scrapers = dict()
    exclude = ['__init__.py']

    accepted_dirs = ['sites', 'spiders']

    for root, _ , files in os.walk(path):
        if root.split('/')[-1] in accepted_dirs:
            for file in files:
                if file not in exclude:
                    name = file.split('.')[0]
                    scrapers[name] = file
    return scrapers