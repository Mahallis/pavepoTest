from config.general import conf


async def save_file(file, filename):
    filepath = conf.UPLOADS_PATH / filename
    with open(filepath, "wb") as f:
        while chunk := await file.read(conf.CHUNK_SIZE):
            f.write(chunk)
    return filepath
