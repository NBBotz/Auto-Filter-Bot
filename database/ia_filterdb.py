import asyncio
from struct import pack
import re
import base64
from typing import Dict, List, Tuple, Optional
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import *
from utils import get_settings, save_group_settings, clean_filename
from collections import defaultdict
from datetime import datetime, timedelta
from logging_helper import LOGGER
import time
from functools import lru_cache

client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
instance = Instance.from_db(db)

client2 = AsyncIOMotorClient(DATABASE_URI2)
db2 = client2[DATABASE_NAME]
instance2 = Instance.from_db(db2)


@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)
    class Meta:
        indexes = ('$file_name', )
        collection_name = COLLECTION_NAME

@instance2.register
class Media2(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)
    class Meta:
        indexes = ('$file_name', )
        collection_name = COLLECTION_NAME


_db_size_cache = {
    'time': 0,
    'size': 0
}
DB_SIZE_CACHE_DURATION = 60 


@lru_cache(maxsize=512)
def get_regex_pattern(query):
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r"(\b|[\.\+\-_])" + re.escape(query) + r"(\b|[\.\+\-_])"
    else:
        parts = query.split(' ')
        new_parts = []
        for part in parts:
            new_parts.append(r"(\b|[\.\+\-_])" + re.escape(part) + r"(\b|[\.\+\-_])")
        raw_pattern = r".*[\s\.\+\-_()\[\]]".join(new_parts)
    try:
        return re.compile(raw_pattern, flags=re.IGNORECASE)
    except Exception:
        return None


async def check_db_size(silentdb):
    try:
        global _db_size_cache
        current_time = time.time()
        is_primary = False

        # Identify if it's the primary DB
        if hasattr(silentdb, 'name') and silentdb.name == db.name:
            is_primary = True
        elif hasattr(silentdb, 'db') and silentdb.db.name == db.name:
            is_primary = True

        if is_primary and (current_time - _db_size_cache['time'] < DB_SIZE_CACHE_DURATION):
            return _db_size_cache['size']

        stats = None
        if hasattr(silentdb, 'command'):
            stats = await silentdb.command("dbstats")
        elif hasattr(silentdb, 'db') and hasattr(silentdb.db, 'command'):
            stats = await silentdb.db.command("dbstats")
        elif hasattr(silentdb, 'collection') and hasattr(silentdb.collection.database, 'command'):
            stats = await silentdb.collection.database.command("dbstats")

        size = stats.get('dataSize', 0) if stats else 0

        if is_primary:
            _db_size_cache['time'] = current_time
            _db_size_cache['size'] = size
        return size
    except Exception as e:
        LOGGER.error(f"Error checking DB size: {e}")
        return 0
    
async def save_file(media) -> Tuple[bool, int]:
    try:
        file_id, file_ref = unpack_new_file_id(media.file_id)
        file_name = clean_filename(media.file_name)
        use_secondary = False
        saveMedia = Media

        if MULTIPLE_DB:
            primary_db_size = await check_db_size(db)
            db_change_limit_bytes = DB_CHANGE_LIMIT * 1024 * 1024
            if primary_db_size >= db_change_limit_bytes:
                saveMedia = Media2
                use_secondary = True

        if use_secondary:
            exists_in_primary, exists_in_secondary = await asyncio.gather(
                Media.find_one({'_id': file_id}),
                Media2.find_one({'_id': file_id})
            )
            if exists_in_primary or exists_in_secondary:
                LOGGER.info(f'{file_name} Is Already Saved In Database!')
                return False, 0
        else:
            exists = await Media.find_one({'_id': file_id})
            if exists:
                LOGGER.info(f'{file_name} Is Already Saved In Primary Database!')
                return False, 0

        file = saveMedia(
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
            caption=media.caption.html if media.caption else None,
        )
        await file.commit()
        LOGGER.info(f'{file_name} Saved Successfully In {"Secondary" if use_secondary else "Primary"} Database')
        return True, 1
    except ValidationError as e:
        LOGGER.error(f'Validation Error While Saving File: {e}')
        return False, 2
    except DuplicateKeyError:
        LOGGER.info(f'{file_name} Is Already Saved In {"Secondary" if use_secondary else "Primary"} Database')
        return False, 0
    except Exception as e:
        LOGGER.error(f"Unexpected error in save_file: {e}")
        return False, 3
            

async def get_search_results(chat_id, query, file_type=None, max_results=10, offset=0, filter=None) -> Tuple[List, int, int]:
    if chat_id is not None:
        settings = await get_settings(int(chat_id))
        try:
            user_max_btn = settings.get('max_btn')
            if user_max_btn:
                max_results = 10
            else:
                max_results = int(MAX_B_TN)
        except (KeyError, ValueError):
            await save_group_settings(int(chat_id), 'max_btn', False)
            max_results = int(MAX_B_TN)

    regex = get_regex_pattern(query)
    if not regex:
        return [], 0, 0

    if not isinstance(filter, dict):
        if USE_CAPTION_FILTER:
            filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
        else:
            filter = {'file_name': regex}
    if file_type:
        filter['file_type'] = file_type
    if max_results % 2 != 0:
        max_results += 1

    # Use field projection to reduce data transfer
    projection = {
        'file_name': 1,
        'file_size': 1,
        'file_id': 1,
        'file_type': 1,
        'caption': 1,
        '_id': 1
    }

    cursor1 = Media.find(filter, projection).sort('$natural', -1).skip(offset).limit(max_results)
    files = await cursor1.to_list(length=max_results)
    total_results = 0

    if not MULTIPLE_DB:
        if offset == 0 and len(files) < max_results:
            total_results = len(files)
        else:
            total_results = await Media.count_documents(filter)
    else:
        # Use asyncio.gather for concurrent counting
        count_db1_task = Media.count_documents(filter)
        count_db2_task = Media2.count_documents(filter)
        count_db1, count_db2 = await asyncio.gather(count_db1_task, count_db2_task)
        total_results = count_db1 + count_db2

        if len(files) < max_results:
            remaining_needed = max_results - len(files)
            if len(files) > 0:
                cursor2 = Media2.find(filter, projection).sort('$natural', -1).limit(remaining_needed)
                files2 = await cursor2.to_list(length=remaining_needed)
                files.extend(files2)
            else:
                if offset >= count_db1:
                    offset_db2 = offset - count_db1
                    cursor2 = Media2.find(filter, projection).sort('$natural', -1).skip(offset_db2).limit(max_results)
                    files = await cursor2.to_list(length=max_results)

    next_offset = offset + len(files)
    if next_offset >= total_results or len(files) == 0:
        next_offset = 0
    return files, next_offset, total_results
    
async def get_bad_files(query, file_type=None):
    regex = get_regex_pattern(query)
    if not regex:
        return [], 0

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}
    if file_type:
        filter['file_type'] = file_type

    if MULTIPLE_DB:
        # Fetch from both in parallel
        async def fetch_all(media_class):
            cursor = media_class.find(filter).sort('$natural', -1)
            count = await media_class.count_documents(filter)
            return await cursor.to_list(length=count)

        files1_task = fetch_all(Media)
        files2_task = fetch_all(Media2)
        files1, files2 = await asyncio.gather(files1_task, files2_task)
        files = files1 + files2
    else:
        cursor = Media.find(filter).sort('$natural', -1)
        count = await Media.count_documents(filter)
        files = await cursor.to_list(length=count)

    return files, len(files)
    

async def get_file_details(query):
    filter = {'file_id': query}
    if MULTIPLE_DB:
        result1, result2 = await asyncio.gather(
            Media.find(filter).to_list(length=1),
            Media2.find(filter).to_list(length=1)
        )
        return result1 if result1 else result2
    else:
        cursor = Media.find(filter)
        return await cursor.to_list(length=1)


def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref

_TITLE_PROJECTION = {'file_name': 1, 'caption': 1, '_id': 0}

async def siletxbotz_fetch_media(limit: int) -> List[dict]:
    try:
        if MULTIPLE_DB:
            half = limit // 2
            remainder = limit - half
            results = await asyncio.gather(
                Media.find({}, _TITLE_PROJECTION).sort("$natural", -1).limit(half).to_list(length=half),
                Media2.find({}, _TITLE_PROJECTION).sort("$natural", -1).limit(remainder).to_list(length=remainder)
            )
            return results[0] + results[1]

        files = await Media.find({}, _TITLE_PROJECTION).sort("$natural", -1).limit(limit).to_list(length=limit)
        return files
    except Exception as e:
        LOGGER.error(f"Error in siletxbotz_fetch_media: {e}")
        return []


async def silentxbotz_clean_title(filename: str, is_series: bool = False) -> str:
    try:
        if not filename:
            return ""
        filename = clean_filename(filename)
        year_match = re.search(r"^(.*?)(\b\d{4}\b)", filename, re.IGNORECASE)
        if year_match:
            title = year_match.group(1).strip()
            return title.title()
        if is_series:
            season_match = re.search(r"(.*?)(?:S(\d{1,2})|Season\s*(\d+))", filename, re.IGNORECASE)
            if season_match:
                title = season_match.group(1).strip()
                season_num = season_match.group(2) or season_match.group(3)
                return f"{title.title()} S{int(season_num):02}"
        return filename.strip().title()
    except Exception as e:
        LOGGER.error(f"Error in silentxbotz_clean_title: {e}")
        return filename


async def siletxbotz_get_movies(limit: int = 20) -> List[str]:
    try:
        candidates = await siletxbotz_fetch_media(limit * 2)
        results = set()
        pattern = r"(?:s\d{1,2}|season\s*\d+)(?:\s*e\d{1,2}|episode\s*\d+)?\b"
        for file in candidates:
            file_name = file.get("file_name") if isinstance(file, dict) else getattr(file, "file_name", "")
            caption = file.get("caption", "") if isinstance(file, dict) else getattr(file, "caption", "")
            if not file_name:
                continue
            if re.search(pattern, file_name, re.IGNORECASE) or (caption and re.search(pattern, caption, re.IGNORECASE)):
                continue
            title = await silentxbotz_clean_title(file_name, is_series=False)
            if title:
                results.add(title)
            if len(results) >= limit:
                break
        return sorted(list(results))[:limit]
    except Exception as e:
        LOGGER.error(f"Error in siletxbotz_get_movies: {e}")
        return []


async def siletxbotz_get_series(limit: int = 30) -> Dict[str, List[int]]:
    try:
        candidates = await siletxbotz_fetch_media(limit * 3)
        grouped = defaultdict(list)
        pattern = r"(.*?)(?:S(\d{1,2})|Season\s*(\d+))"
        for file in candidates:
            file_name = file.get("file_name") if isinstance(file, dict) else getattr(file, "file_name", "")
            caption = file.get("caption", "") if isinstance(file, dict) else getattr(file, "caption", "")
            if not file_name:
                continue
            match = re.search(pattern, file_name, re.IGNORECASE)
            if not match and caption:
                match = re.search(pattern, caption, re.IGNORECASE)
            if match:
                title_part = match.group(1)
                season_num = match.group(2) or match.group(3)
                title = await silentxbotz_clean_title(title_part, is_series=False)
                try:
                    s_num = int(season_num)
                    if s_num not in grouped[title]:
                        grouped[title].append(s_num)
                except ValueError:
                    continue
        result = {t: sorted(s) for t, s in grouped.items()}
        return dict(list(result.items())[:limit])
    except Exception as e:
        LOGGER.error(f"Error in siletxbotz_get_series: {e}")
        return {}
