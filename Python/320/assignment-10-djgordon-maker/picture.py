'''
Methods to access picture information for the social network project
'''
import string
from pathlib import Path
import logging
from functools import partial
from log import logit
import socialnetwork_model as sql
import users


logger = logging.getLogger('main.picture')
logger.setLevel(logging.INFO)
keys = ('picture_id', 'user_id', 'tags')
picture_zip = partial(zip, keys)
tag_filter = set(string.ascii_letters)
tag_filter.add('_')


@logit(logger)
def make_picture(picture_id, user_id, tags):
    '''
    Creates a dictionary with picture information
    '''
    if len(tags) > 100:
        logger.debug('Tag string %s cannot be longer than 100 characters', tags)
        return None
    return dict(picture_zip((picture_id, user_id, tags)))


@logit(logger)
def validate_tags(tags):
    '''
    Filters tags: tags can only contain upper and lower case letters and underscore
    '''
    tag_list = tags.replace('#', ' ').split()
    for tag in tag_list:
        tag_set = set(tag)
        if not tag_set.issubset(tag_filter):
            return None
    return f"#{' #'.join(tag_list)}"


@logit(logger)
def add_picture(user_id, tags):
    '''
    Adds a new picture to the dataset
    '''
    # Test for foreign key constraint
    if not users.check_for_user(user_id):
        logger.error('Foreign Key %s does not exist', user_id)
        return False
    # Foreign Key exists
    tags = validate_tags(tags)
    if not tags:
        logger.error('Tags contained invalid characters')
        return False
    tag_path = user_id / tags_to_path(tags)
    if not tag_path.exists():
        tag_path.mkdir(parents=True)
    with sql.connection(sql.PICTURE) as table:
        picture_id = len(table) + 1
        filename = id_to_filename(picture_id)
        (tag_path / filename).touch()
        new_picture = make_picture(picture_id, user_id, tags)
        if new_picture:
            table.insert(**new_picture)
            logger.info('Picture %s added to database', picture_id)
            return True
    logger.error('Picture did not meet requirements')
    return False


def tags_to_path(tags):
    '''
    Coverts a tag string to a file path
    '''
    tag_list = tags.replace('#', ' ').split()
    tag_list.sort()
    return Path('/'.join(tag_list))


def id_to_filename(picture_id):
    '''
    Coverts a number to a filename
    '''
    return f'{picture_id}.png'.zfill(9)


@logit(logger)
def list_user_images(user_id):
    '''
    Navigates the user's image directory and returns a list of tuples
    containing (user_id, path_to_image, image_name) for each image found
    '''
    files = collect_files(Path(user_id))
    if not files:
        logger.error('User %s does not own any images', user_id)
        return None
    images = []
    for file in files:
        images.append((user_id, str(file.parent), file.name))
    logger.info('Found % images', len(images))
    return images


@logit(logger)
def collect_files(path):
    '''
    Recursivly collect a list of file paths
    '''
    if not path.is_dir():
        return []
    files = []
    for child in path.iterdir():
        if child.is_file():
            files.append(child)
        else:
            files.extend(collect_files(child))
    return files


@logit(logger)
def reconcile_images(user_id):
    '''
    List images in the database but not the directory and vice versa
    '''
    try:
        files = set(list_user_images(user_id))
    except TypeError:  # list_user_images probably returned None
        files = set()
    database = set()
    result = dict()
    logger.debug('Contents of image directory: %s', files)
    with sql.connection(sql.PICTURE) as table:
        rows = table.find(user_id=user_id)
        for row in rows:
            tag_path = user_id / tags_to_path(row['tags'])
            database.add((row['user_id'],
                          str(tag_path),
                          id_to_filename(row['picture_id'])))
    logger.debug('Contents of database: %s', database)
    if len(files) == 0 and len(database) == 0:
        logger.error('User %s does not own any images', user_id)
        return None
    result['files-db'] = list(files.difference(database))
    result['db-files'] = list(database.difference(files))
    return result
