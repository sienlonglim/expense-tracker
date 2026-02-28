attach '{backup_file}' as local_db;
copy from database expenses to local_db;
detach local_db;